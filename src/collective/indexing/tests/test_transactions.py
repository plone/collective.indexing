from unittest import defaultTestLoader, main, TestCase
from transaction import savepoint, commit, abort

from collective.indexing.transactions import QueueTM
from collective.indexing.config import INDEX, REINDEX
from collective.indexing.tests import utils


class QueueTransactionManagerTests(TestCase):

    def setUp(self):
        self.queue = utils.MockQueueProcessor()
        self.tman = QueueTM(self.queue)
        self.queue.hook = self.tman.register    # set up the transaction manager hook

    def testFlushQueueOnCommit(self):
        self.queue.index('foo')
        commit()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, [(INDEX, 'foo', None)])
        self.assertEqual(self.queue.state, 'finished')

    def testFlushQueueOnAbort(self):
        self.queue.index('foo')
        abort()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, None)
        self.assertEqual(self.queue.state, 'aborted')

    def testUseSavePoint(self):
        self.queue.index('foo')
        savepoint()
        self.queue.reindex('bar')
        commit()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, [(INDEX, 'foo', None), (REINDEX, 'bar', None)])
        self.assertEqual(self.queue.state, 'finished')

    def testRollbackSavePoint(self):
        self.queue.index('foo')
        sp = savepoint()
        self.queue.reindex('bar')
        sp.rollback()
        commit()
        self.assertEqual(self.queue.getState(), [])
        self.assertEqual(self.queue.processed, [(INDEX, 'foo', None)])
        self.assertEqual(self.queue.state, 'finished')


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    main(defaultTest='test_suite')
