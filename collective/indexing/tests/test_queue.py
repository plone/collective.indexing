from unittest import TestSuite, makeSuite, main, TestCase
from threading import Thread

from zope.interface import implements
from zope.component import provideUtility
from zope.testing.cleanup import CleanUp

from collective.indexing.interfaces import IIndexQueue
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.interfaces import IQueueReducer
from collective.indexing.reducer import QueueReducer
from collective.indexing.queue import IndexQueue, IndexQueueSwitch
from collective.indexing.config import INDEX, REINDEX, UNINDEX
from collective.indexing.utils import getIndexer
from collective.indexing.tests import utils


class QueueTests(CleanUp, TestCase):

    def setUp(self):
        self.queue = IndexQueue()

    def tearDown(self):
        self.queue.clear()

    def testInterface(self):
        self.failUnless(IIndexQueue.providedBy(self.queue))

    def testQueueHook(self):
        class CaptainHook:
            def __init__(self):
                self.hooked = 0
            def __call__(self):
                self.hooked += 1
        hook = CaptainHook()
        queue = self.queue
        queue.setHook(hook)
        self.assertEqual(hook.hooked, 0)
        queue.index('foo')
        queue.reindex('foo')
        queue.reindex('bar')
        self.assertEqual(len(queue.getState()), 3)
        self.assertEqual(hook.hooked, 3)
        self.assertEqual(queue.process(), 3)
        self.assertEqual(hook.hooked, 3)

    def testQueueState(self):
        queue = self.queue
        queue.index('foo')
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])
        state = queue.getState()
        queue.reindex('bar')
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None), (REINDEX, 'bar', None)])
        queue.setState(state)
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(queue.process(), 1)

    def testQueueProcessor(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        self.assertEqual(queue.process(), 1)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc.state, 'finished')

    def testMultipleQueueProcessors(self):
        queue = self.queue
        proc1 = utils.MockQueueProcessor()
        proc2 = utils.MockQueueProcessor()
        provideUtility(proc1, IIndexQueueProcessor, name='proc1')
        provideUtility(proc2, IIndexQueueProcessor, name='proc2')
        queue.index('foo')
        self.assertEqual(queue.process(), 1)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc1.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc2.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc1.state, 'finished')
        self.assertEqual(proc2.state, 'finished')

    def testQueueOperations(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        queue.unindex('foo')
        self.assertEqual(queue.process(), 3)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (UNINDEX, 'foo', None)])
        self.assertEqual(proc.state, 'finished')

    def testQueueReducer(self):
        class MessyReducer(object):
            implements(IQueueReducer)
            def optimize(self, queue):
                return [ op for op in queue if not op[0] == UNINDEX ]
        queue = self.queue
        queue.index('foo')
        queue.reindex('foo')
        queue.unindex('foo')
        queue.index('foo', 'bar')
        queue.optimize()
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (UNINDEX, 'foo', None), (INDEX, 'foo', 'bar')])
        provideUtility(MessyReducer())  # hook up the reducer
        queue.optimize()                # and try again...
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (INDEX, 'foo', 'bar')])

    def testRealQueueReducer(self):
        provideUtility(QueueReducer())
        queue = self.queue
        queue.index('foo')
        queue.reindex('foo')
        queue.unindex('foo')
        queue.index('foo', 'bar')
        queue.optimize()
        self.assertEqual(queue.getState(), [(INDEX, 'foo', None)])


class QueueReducerTests(TestCase):

    def testReduceQueue(self):
        reducer = QueueReducer()

        queue = [(REINDEX, 'A', None), (REINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

        queue = [(INDEX, 'A', None), (REINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(INDEX, 'A', None)])

        queue = [(INDEX, 'A', None), (UNINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [])

        queue = [(UNINDEX, 'A', None), (INDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

    def testReduceQueueWithAttributes(self):
        reducer = QueueReducer()

        queue = [(REINDEX, 'A', None), (REINDEX, 'A', ('a','b'))]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

        queue = [(REINDEX, 'A', ('a','b')), (REINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

        queue = [(REINDEX, 'A', ('a','b')), (REINDEX, 'A', ('b','c'))]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', ('a', 'c', 'b'))])

        queue = [(INDEX, 'A', None), (REINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(INDEX, 'A', None)])

        queue = [(REINDEX, 'A', ('a','b')), (UNINDEX, 'A', None), (INDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])


class QueueThreadTests(TestCase):
    """ thread tests modeled after zope.thread doctests """

    def testLocalQueues(self):
        provideUtility(IndexQueueSwitch(), IIndexQueueSwitch)
        me = getIndexer()               # first a queued indexer is set up...
        self.failUnless(IIndexQueue.providedBy(me), 'non-queued indexer found')
        log = []
        def runner():                   # and a callable for the thread to run...
            me.reindex('bar')
            log.extend(me.getState())
        thread = Thread(target=runner)  # another thread is created...
        thread.start()                  # and started...
        thread.join()                   # wait until it's finished and check...
        self.assertEqual(log, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])


def test_suite():
    return TestSuite([
        makeSuite(QueueTests),
        makeSuite(QueueReducerTests),
        makeSuite(QueueThreadTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
