from unittest import TestSuite, makeSuite, main

from zope.component import provideUtility
from transaction import savepoint, commit, abort

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import collective.indexing
from collective.indexing.transactions import QueueTM
from collective.indexing.config import INDEX, REINDEX, UNINDEX
from collective.indexing.tests import util


class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.indexing)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class SubscriberTests(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', id='folder1', title='Folder 1')
        self.folder = self.portal.folder1
        self.portal.invokeFactory('File', id='file1', title='File 1')
        self.file = self.portal.file1
        self.indexer = util.MockIndexer()
        self.queue = self.indexer.queue
        provideUtility(self.indexer)

    def testAddObject(self):
        self.portal.invokeFactory('File', id='foo', title='Foo')
        self.assert_((INDEX, self.portal.foo, None) in self.queue)

    def testUpdateObject(self):
        self.file.update(title='Foo')
        self.assertEqual(self.queue, [])    # `update()` doesn't fire an event

    def testModifyObject(self):
        self.file.processForm({'title': 'Foo'})
        self.assertEqual(self.queue, [(REINDEX, self.file, None)])

    def testRemoveObject(self):
        file1 = self.portal.file1
        self.portal.manage_delObjects('file1')
        self.assert_((UNINDEX, file1, None) in self.queue, self.queue)
        self.assertRaises(AttributeError, getattr, self.portal, 'file1')

    def testAddAndRemoveObject(self):
        self.portal.invokeFactory('File', id='foo', title='Foo')
        foo = self.portal.foo
        self.portal.manage_delObjects('foo')
        index = self.queue.index((INDEX, foo, None))
        unindex = self.queue.index((UNINDEX, foo, None))
        self.assert_(index < unindex)
        self.assertRaises(AttributeError, getattr, self.portal, 'foo')

    def testMoveObject(self):
        self.portal.folder1.invokeFactory('File', id='file2', title='File 2')
        self.portal.invokeFactory('Folder', id='folder2', title='Folder 2')
        self.queue[:] = []  # clear the queue...
        savepoint()         # need to create a savepoint, because!
        original = self.portal.folder1.file2
        cookie = self.portal.folder1.manage_cutObjects(ids=('file2',))
        self.portal.folder2.manage_pasteObjects(cookie)
        self.assert_((REINDEX, self.portal.folder1, None) in self.queue, self.queue)
        self.assert_((REINDEX, self.portal.folder2.file2, None) in self.queue, self.queue)
        self.assert_((REINDEX, self.portal.folder2, None) in self.queue, self.queue)
        # there should be no 'unindex', since it's still the same object...
        self.failIf((UNINDEX, original, None) in self.queue, self.queue)
        self.assertEqual(original, self.portal.folder2.file2)

    def testCopyObject(self):
        cookie = self.portal.manage_copyObjects(ids=('file1',))
        self.folder.manage_pasteObjects(cookie)
        self.assert_((INDEX, self.folder.file1, None) in self.queue)
        self.assert_((REINDEX, self.folder, None) in self.queue)

    def testRenameObject(self):
        savepoint()         # need to create a savepoint, because!
        self.portal.manage_renameObject('file1', 'foo')
        self.assert_((REINDEX, self.portal.foo, None) in self.queue, self.queue)
        self.assertRaises(AttributeError, getattr, self.portal, 'file1')

    def testPublishObject(self):
        self.portal.portal_workflow.doActionFor(self.folder, 'publish')
        self.assertEqual(self.queue, [(REINDEX, self.folder, None)])


class QueueTransactionManagerTests(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.queue = util.MockQueue()
        self.tman = QueueTM(self.queue)
        self.queue.hook = self.tman._register   # set up the transaction manager hook

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
        makeSuite(SubscriberTests),
        makeSuite(QueueTransactionManagerTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
