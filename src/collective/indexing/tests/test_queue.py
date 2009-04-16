from unittest import defaultTestLoader, main, TestCase
from threading import Thread, currentThread
from time import sleep

from zope.interface import implements
from zope.component import provideUtility
from zope.testing.cleanup import CleanUp

from collective.indexing.interfaces import IIndexQueue
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.interfaces import IQueueReducer
from collective.indexing.reducer import QueueReducer
from collective.indexing.queue import IndexQueue
from collective.indexing.config import IndexingConfig
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
        self.assertEqual(proc.state, 'started') # the real queue won't update the state...
        queue.commit()
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
        self.assertEqual(proc1.state, 'started')    # the real queue won't...
        self.assertEqual(proc2.state, 'started')    # update the state...
        queue.commit()
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
        self.assertEqual(proc.state, 'started') # the real queue won't update the state...
        queue.commit()
        self.assertEqual(proc.state, 'finished')

    def testQueueReducer(self):
        class MessyReducer(object):
            implements(IQueueReducer)
            def optimize(self, queue):
                return [op for op in queue if not op[0] == UNINDEX]
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

    def testQueueAbortBeforeProcessing(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        self.assertNotEqual(queue.getState(), [])
        queue.abort()
        self.assertEqual(queue.process(), 0)    # nothing left...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [])
        self.assertEqual(proc.state, 'started') # the real queue won't update the state...

    def testQueueAbortAfterProcessing(self):
        queue = self.queue
        proc = utils.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        self.assertEqual(queue.process(), 2)    # also do the processing...
        self.assertNotEqual(proc.getState(), [])
        queue.abort()
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [])
        self.assertEqual(proc.state, 'aborted')


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

        queue = [(REINDEX, 'A', None), (REINDEX, 'A', ('a', 'b'))]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

        queue = [(REINDEX, 'A', ('a', 'b')), (REINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

        queue = [(REINDEX, 'A', ('a', 'b')), (REINDEX, 'A', ('b', 'c'))]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', ('a', 'c', 'b'))])

        queue = [(INDEX, 'A', None), (REINDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(INDEX, 'A', None)])

        queue = [(REINDEX, 'A', ('a', 'b')), (UNINDEX, 'A', None), (INDEX, 'A', None)]
        self.failUnlessEqual(reducer.optimize(queue), [(REINDEX, 'A', None)])

    def testReduceQueueSortsByOpcode(self):
        reducer = QueueReducer()

        queue = [(INDEX, 'C', None), (UNINDEX, 'B', None)]
        self.failUnlessEqual(reducer.optimize(queue),
            [(UNINDEX, 'B', None), (INDEX, 'C', None)])

        queue = [(REINDEX, 'A', None), (UNINDEX, 'B', None)]
        self.failUnlessEqual(reducer.optimize(queue),
            [(UNINDEX, 'B', None), (REINDEX, 'A', None)])

        queue = [(REINDEX, 'A', None), (UNINDEX, 'B', None), (INDEX, 'C', None)]
        self.failUnlessEqual(reducer.optimize(queue),
            [(UNINDEX, 'B', None), (REINDEX, 'A', None), (INDEX, 'C', None)])


class QueueThreadTests(TestCase):
    """ thread tests modeled after zope.thread doctests """

    def setUp(self):
        provideUtility(IndexingConfig(), IIndexingConfig)
        self.me = getIndexer()
        self.failUnless(IIndexQueue.providedBy(self.me), 'non-queued indexer found')

    def tearDown(self):
        self.me.clear()

    def testLocalQueues(self):
        me = self.me                    # get the queued indexer...
        other = []
        def runner():                   # and a callable for the thread to run...
            me.reindex('bar')
            other[:] = me.getState()
        thread = Thread(target=runner)  # another thread is created...
        thread.start()                  # and started...
        while thread.isAlive():
            pass                        # wait until it's done...
        self.assertEqual(other, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])
        me.index('foo')                 # something happening on our side...
        self.assertEqual(other, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(INDEX, 'foo', None)])
        thread.join()                   # finally the threads are re-united...

    def testQueuesOnTwoThreads(self):
        me = self.me                    # get the queued indexer...
        first = []
        def runner1():                  # and callables for the first...
            me.index('foo')
            first[:] = me.getState()
        thread1 = Thread(target=runner1)
        second = []
        def runner2():                  # and second thread
            me.index('bar')
            second[:] = me.getState()
        thread2 = Thread(target=runner2)
        self.assertEqual(first, [])     # clean table before we start...
        self.assertEqual(second, [])
        self.assertEqual(me.getState(), [])
        thread1.start()                 # do stuff here...
        sleep(0.01)                     # allow thread to do work
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [])
        self.assertEqual(me.getState(), [])
        thread2.start()                 # and there...
        sleep(0.01)                     # allow thread to do work
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])
        thread1.join()                  # re-unite with first thread and...
        me.unindex('f00')               # let something happening on our side
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(UNINDEX, 'f00', None)])
        thread2.join()                  # also re-unite the second and...
        me.unindex('f00')               # let something happening again...
        self.assertEqual(first, [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(UNINDEX, 'f00', None), (UNINDEX, 'f00', None)])

    def testManyThreads(self):
        me = self.me                    # get the queued indexer...
        queues = {}                     # container for local queues
        def makeRunner(name, idx):
            def runner():
                for n in range(idx):    # index idx times
                    me.index(name)
                queues[currentThread()] = me.queue
            return runner
        threads = []
        for idx in range(99):
            threads.append(Thread(target=makeRunner('t%d' % idx, idx)))
        for thread in threads:
            thread.start()
            sleep(0.01)                 # just in case
        for thread in threads:
            thread.join()
        for idx, thread in enumerate(threads):
            tid = 't%d' % idx
            queue = queues[thread]
            names = [name for op, name, attrs in queue]
            self.assertEquals(names, [tid] * idx)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    main(defaultTest='test_suite')
