from unittest import defaultTestLoader
from collective.indexing.tests.base import IndexingTestCase
from collective.indexing.tests.layer import IndexingLayer
from collective.indexing.tests.utils import TestHelpers


# test-specific imports go here...
from transaction import commit
from zope.component import getUtility
from Acquisition import aq_parent, aq_inner, aq_base
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.event import ATEvent
from Products.CMFPlone.CatalogTool import CatalogTool
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

    def testAutoFlushMonkeyPatchChaining(self):
        # (de)activating auto-flushing shouldn't cause other monkey
        # patches to be masqueraded or otherwise disabled...
        # first let's set up another monkey patch...
        log = []
        original = CatalogTool.searchResults
        def searchResults(self, REQUEST=None, **kw):
            log.append('monkey called')
            return original(self, REQUEST, **kw)
        CatalogTool.searchResults = searchResults
        # next we search something and make sure the monkey's in place...
        self.assertEqual(len(self.portal.portal_catalog.searchResults(Title='news')), 2)
        self.assertEqual(log, ['monkey called'])
        # auto-flushing get deactivated and then activated again...
        self.config.auto_flush = False
        self.config.auto_flush = True
        # after which another search should still our monkey patch...
        self.assertEqual(len(self.portal.portal_catalog.searchResults(Title='news')), 2)
        self.assertEqual(log, ['monkey called'] * 2)

    def testGetCounterWithoutAutoFlush(self):
        # without auto-flush we must commit to update the catalog counter
        self.failUnless(isActive())
        self.config.auto_flush = False
        catalog = self.portal.portal_catalog
        value = catalog.getCounter()
        self.folder.update(title='Foo')
        self.assertEqual(catalog.getCounter(), value)
        commit()
        self.assertTrue(catalog.getCounter() > value)

    def testGetCounterWithAutoFlush(self):
        # with auto-flush enabled the catalog counter is always up-to-date
        self.failUnless(isActive())
        self.config.auto_flush = True
        # no commits required now
        catalog = self.portal.portal_catalog
        value = catalog.getCounter()
        self.folder.update(title='Foo')
        self.assertTrue(catalog.getCounter() > value)


class PathWrapperTests(IndexingTestCase):

    layer = IndexingLayer

    def testWrapperAttributes(self):
        from collective.indexing.queue import wrap
        obj = self.folder
        wrapper = wrap(obj)
        self.assertEqual(wrapper.title, obj.title)
        self.assertEqual(wrapper.Title(), obj.Title())
        self.assertEqual(wrapper.modified(), obj.modified())
        # stripping away acquisition shouldn't make a difference...
        self.assertEqual(aq_base(wrapper).title, obj.title)
        self.assertEqual(aq_base(wrapper).Title(), obj.Title())

    def testWrapperRequest(self):
        from collective.indexing.queue import wrap
        obj = self.folder
        self.assertEqual(wrap(obj).REQUEST, obj.REQUEST)

    def testWrapperPath(self):
        from collective.indexing.queue import wrap
        obj = self.folder
        self.assertEqual(wrap(obj).getPhysicalPath(), obj.getPhysicalPath())

    def testWrapperHash(self):
        from collective.indexing.queue import wrap
        obj = self.folder
        self.assertEqual(hash(wrap(obj)), hash(obj))

    def testWrapperAcquisitionParent(self):
        from collective.indexing.queue import wrap
        obj = self.folder
        wrapper = wrap(obj)
        self.assertEqual(aq_parent(wrapper), aq_parent(obj))
        self.assertEqual(aq_parent(aq_inner(wrapper)), aq_parent(aq_inner(obj)))
        # also check an extended aq-chain
        obj = self.folder.__of__(self.portal.news)
        wrapper = wrap(obj)
        self.assertEqual(aq_parent(wrapper), aq_parent(obj))
        # `aq_parent(aq_inner(...))` for an aq-chain other than the inner
        # chain won't work, because the wrapper cannot tell if it should
        # re-wrap itself in the parent's context or containment (aka "inner")
        # chain (in queue.py:70).  this can probably be fixed by using
        # `__parent__`, but not before zope 2.12...
        # self.assertEqual(aq_parent(aq_inner(wrapper)), aq_parent(aq_inner(obj)))


class OverriddenIndexMethodTests(IndexingTestCase):

    layer = IndexingLayer

    def testIndexObjectCallingSuper(self):
        from collective.indexing.tests.content import addFoo
        addFoo(self.folder, 'foo')
        # an indexing loop will trigger the assertion in `tests/content.py`
        # so things are fine if the commit goes through...
        commit()


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
