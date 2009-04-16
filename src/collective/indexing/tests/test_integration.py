from unittest import defaultTestLoader
from collective.indexing.tests.base import IndexingTestCase
from collective.indexing.tests.layer import IndexingLayer
from collective.indexing.tests.utils import TestHelpers


# test-specific imports go here...
from transaction import commit
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.event import ATEvent
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.utils import isActive


def getEventType(self):
    """ helper for `testRecursiveAutoFlush`, see below """
    catalog = getToolByName(self, 'portal_catalog')
    count = len(catalog(portal_type='Event'))
    if count:
        return 'Socialized event'
    else:
        return 'Lonely event'


class AutoFlushTests(IndexingTestCase, TestHelpers):

    layer = IndexingLayer

    def afterSetUp(self):
        # clear logs to avoid id collisions
        setup = self.portal.portal_setup
        setup.manage_delObjects(setup.objectIds())
        self.config = getUtility(IIndexingConfig)

    def beforeTearDown(self):
        self.config.auto_flush = True       # reset to default

    def testNoAutoFlush(self):
        # without auto-flush we must commit to update the catalog
        self.failUnless(isActive())
        self.config.auto_flush = False
        self.assertEqual(self.create(), [])
        commit()
        self.assertEqual(self.fileIds(), ['foo'])
        self.assertEqual(self.remove(), ['foo'])
        commit()
        self.assertEqual(self.fileIds(), [])

    def testAutoFlush(self):
        # with auto-flush enabled the catalog is always up-to-date
        self.failUnless(isActive())
        self.config.auto_flush = True
        # no commits required now
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.fileIds(), ['foo'])
        self.assertEqual(self.remove(), [])
        self.assertEqual(self.fileIds(), [])

    def testRecursiveAutoFlush(self):
        # an indexing helper using the catalog, thereby triggering queue
        # processing via auto-flush, used to potentially cause an infinite
        # loop;  hence recursive auto-flushing must be prevented...
        self.failUnless(isActive())
        self.config.auto_flush = True
        foo = self.folder[self.folder.invokeFactory('Event', id='foo')]
        # monkey-patch foo's `sortable_title` method to use the catalog...
        original = ATEvent.getEventType
        ATEvent.getEventType = getEventType
        # now we commit, which triggers indexing...
        commit()
        # un-monkey again in the end
        ATEvent.getEventType = original


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
