from unittest import TestSuite, makeSuite, main

from zope.component import provideUtility
from zope.interface import implements
from transaction import savepoint

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import collective.indexing
from collective.indexing.interfaces import IIndexing


class MockIndexer:
    implements(IIndexing)

    def __init__(self):
        self.queue = []

    def index(self, uid, attributes=None):
        self.queue.append(('index', uid, attributes))

    def reindex(self, uid, attributes=None):
        self.queue.append(('reindex', uid, attributes))

    def unindex(self, uid):
        self.queue.append(('unindex', uid))


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
        self.indexer = MockIndexer()
        self.queue = self.indexer.queue
        provideUtility(self.indexer)

    def testAddObject(self):
        self.portal.invokeFactory('File', id='foo', title='Foo')
        uid = self.portal.foo.UID()
        self.assert_(('index', uid, None) in self.queue)

    def testUpdateObject(self):
        self.file.update(title='Foo')
        self.assertEqual(self.queue, [])    # `update()` doesn't fire an event

    def testModifyObject(self):
        self.file.processForm({'title': 'Foo'})
        self.assertEqual(self.queue, [('reindex', self.file.UID(), None)])

    def testRemoveObject(self):
        uid = self.portal.file1.UID()
        self.portal.manage_delObjects('file1')
        self.assertEqual(self.queue, [('unindex', uid)])

    def testAddAndRemoveObject(self):
        self.portal.invokeFactory('File', id='foo', title='Foo')
        uid = self.portal.foo.UID()
        self.portal.manage_delObjects('foo')
        index = self.queue.index(('index', uid, None))
        unindex = self.queue.index(('unindex', uid))
        self.assert_(index < unindex)

    def testMoveObject(self):
        self.portal.folder1.invokeFactory('File', id='file2', title='File 2')
        self.portal.invokeFactory('Folder', id='folder2', title='Folder 2')
        self.queue[:] = []  # clear the queue...
        savepoint()         # need to create a savepoint, because!
        original_uid = self.portal.folder1.file2.UID()
        cookie = self.portal.folder1.manage_cutObjects(ids=('file2',))
        self.portal.folder2.manage_pasteObjects(cookie)
        self.assert_(('reindex', self.portal.folder1.UID(), None) in self.queue, self.queue)
        self.assert_(('reindex', self.portal.folder2.file2.UID(), None) in self.queue, self.queue)
        self.assert_(('reindex', self.portal.folder2.UID(), None) in self.queue, self.queue)
        # there should be no 'unindex', since it's still the same object...
        self.failIf(('unindex', original_uid) in self.queue, self.queue)
        self.assertEqual(original_uid, self.portal.folder2.file2.UID())

    def testCopyObject(self):
        cookie = self.portal.manage_copyObjects(ids=('file1',))
        self.folder.manage_pasteObjects(cookie)
        self.assert_(('index', self.folder.file1.UID(), None) in self.queue)
        self.assert_(('reindex', self.folder.UID(), None) in self.queue)

    def testRenameObject(self):
        savepoint()         # need to create a savepoint, because!
        uid = self.portal.file1.UID()
        self.portal.manage_renameObject('file1', 'foo')
        self.assertEqual(self.queue, [('reindex', uid, None)])

    def testPublishObject(self):
        uid = self.folder.UID()
        self.portal.portal_workflow.doActionFor(self.folder, 'publish')
        self.assertEqual(self.queue, [('reindex', uid, None)])


def test_suite():
    return TestSuite([
        makeSuite(SubscriberTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
