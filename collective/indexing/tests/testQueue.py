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
