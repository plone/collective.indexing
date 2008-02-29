from unittest import TestSuite, makeSuite, main, TestCase

from zope.component import provideUtility
from zope.testing.cleanup import CleanUp

from collective.indexing.interfaces import IIndexQueue
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.reducer import QueueReducer
from collective.indexing.queue import IndexQueue
from collective.indexing.config import INDEX, REINDEX, UNINDEX
from collective.indexing.tests import util


class QueueTests(CleanUp, TestCase):

    def setUp(self):
        self.queue = IndexQueue()

    def testInterface(self):
        IIndexQueue.providedBy(self.queue)

    def testQueueProcessor(self):
        queue = self.queue
        proc = util.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        self.assertEqual(queue.process(), 1)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [(INDEX, 'foo', None)])
        self.assertEqual(proc.state, 'finished')

    def testMultipleQueueProcessors(self):
        queue = self.queue
        proc1 = util.MockQueueProcessor()
        proc2 = util.MockQueueProcessor()
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
        proc = util.MockQueueProcessor()
        provideUtility(proc, IIndexQueueProcessor)
        queue.index('foo')
        queue.reindex('foo')
        queue.unindex('foo')
        self.assertEqual(queue.process(), 3)    # also do the processing...
        self.assertEqual(queue.getState(), [])
        self.assertEqual(proc.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (UNINDEX, 'foo')])
        self.assertEqual(proc.state, 'finished')


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


def test_suite():
    return TestSuite([
        makeSuite(QueueTests),
        makeSuite(QueueReducerTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
