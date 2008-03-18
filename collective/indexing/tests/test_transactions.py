from unittest import TestCase, TestSuite, makeSuite, main
from transaction import savepoint, commit, abort

from collective.indexing.transactions import QueueTM
from collective.indexing.config import INDEX, REINDEX
from collective.indexing.tests import utils


class QueueTransactionManagerTests(TestCase):

    def setUp(self):
        self.queue = utils.MockQueue()
        self.tman = QueueTM(self.queue)
        self.queue.hook = self.tman.register    # set up the transaction manager hook

    def testFlushQueueOnCommit(self):
        self.queue.index('foo')
        commit()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, [(INDEX, 'foo', None)])

    def testFlushQueueOnAbort(self):
        self.queue.index('foo')
        abort()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, None)

    def testUseSavePoint(self):
        self.queue.index('foo')
        savepoint()
        self.queue.reindex('bar')
        commit()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, [(INDEX, 'foo', None), (REINDEX, 'bar', None)])

    def testRollbackSavePoint(self):
        self.queue.index('foo')
        sp = savepoint()
        self.queue.reindex('bar')
        sp.rollback()
        commit()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, [(INDEX, 'foo', None)])


def test_suite():
    return TestSuite([
        makeSuite(QueueTransactionManagerTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')

