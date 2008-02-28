from unittest import TestSuite, makeSuite, main

from zope.component import provideUtility
from zope.interface import implements

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
        self.queue.append(('add', uid, attributes))

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
        self.assertEqual(self.queue, [('add', uid, None), ('reindex', uid, None)])


def test_suite():
    return TestSuite([
        makeSuite(SubscriberTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
