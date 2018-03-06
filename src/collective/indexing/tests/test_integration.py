# coding=utf-8
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.indexing.tests.base import IndexingTestCase
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.criteria.portaltype import ATPortalTypeCriterion
from Products.CMFCore.utils import getToolByName
from transaction import commit


def getEventSubject(self):
    """ helper for `testRecursiveProcessQueue`, see below """
    catalog = getToolByName(self, 'portal_catalog')
    count = len(catalog(portal_type='Event'))
    if count:
        return 'Socialized event'
    else:
        return 'Lonely event'


class ProcessQueueTests(IndexingTestCase):

    def testRecursiveProcessQueue(self):
        # an indexing helper using the catalog, thereby triggering queue
        # processing, used to potentially cause an infinite loop; hence
        # recursive queue processing must be prevented
        self.folder.invokeFactory('Event', id='bar')
        # monkey-patch a method to use the catalog...
        original = ATEvent.Subject
        ATEvent.Subject = getEventSubject
        # now we commit, which triggers indexing...
        commit()
        # un-monkey again in the end
        ATEvent.Subject = original

    def testGetCounter(self):
        catalog = self.portal.portal_catalog
        value = catalog.getCounter()
        self.folder.update(title='Bar')
        self.assertTrue(catalog.getCounter() > value)


class PathWrapperTests(IndexingTestCase):

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
        self.assertEqual(
            aq_parent(aq_inner(wrapper)),
            aq_parent(aq_inner(obj)),
        )
        # also check an extended aq-chain
        obj = self.folder.__of__(self.portal.news)
        wrapper = wrap(obj)
        self.assertEqual(aq_parent(wrapper), aq_parent(obj))
        # `aq_parent(aq_inner(...))` for an aq-chain other than the inner
        # chain won't work, because the wrapper cannot tell if it should
        # re-wrap itself in the parent's context or containment (aka "inner")
        # chain (in queue.py:70).  this can probably be fixed by using
        # `__parent__`, but not before zope 2.12...
        # self.assertEqual(
        #     aq_parent(aq_inner(wrapper)), aq_parent(aq_inner(obj))
        # )


class OverriddenIndexMethodTests(IndexingTestCase):

    def testIndexObjectCallingSuper(self):
        from collective.indexing.tests.content import addFoo
        addFoo(self.folder, 'foo')
        # an indexing loop will trigger the assertion in `tests/content.py`
        # so things are fine if the commit goes through...
        commit()

    def testGetOwnIndexMethod(self):
        from collective.indexing.indexer import getOwnIndexMethod
        self.setRoles(['Manager'])
        # a regular content object uses the standard methods...
        container = self.folder
        self.failIf(getOwnIndexMethod(container, 'indexObject'))
        self.failIf(getOwnIndexMethod(container, 'reindexObject'))
        self.failIf(getOwnIndexMethod(container, 'unindexObject'))
        news = self.portal.news
        self.failIf(getOwnIndexMethod(news, 'indexObject'))
        self.failIf(getOwnIndexMethod(news, 'reindexObject'))
        self.failIf(getOwnIndexMethod(news, 'unindexObject'))
        event = container[container.invokeFactory('Event', id='event')]
        self.failIf(getOwnIndexMethod(event, 'indexObject'))
        self.failIf(getOwnIndexMethod(event, 'reindexObject'))
        self.failIf(getOwnIndexMethod(event, 'unindexObject'))
        # while a criterion has private methods...
        container.invokeFactory('Collection', id='coll')
        crit = ATPortalTypeCriterion('crit')
        self.failUnless(getOwnIndexMethod(crit, 'indexObject'))
        self.failUnless(getOwnIndexMethod(crit, 'reindexObject'))
        self.failUnless(getOwnIndexMethod(crit, 'unindexObject'))
        # our sample class only has a private `indexObject`...
        from collective.indexing.tests.content import Foo
        foo = Foo('foo')
        self.failUnless(getOwnIndexMethod(foo, 'indexObject'))
        self.failIf(getOwnIndexMethod(foo, 'reindexObject'))
        self.failIf(getOwnIndexMethod(foo, 'unindexObject'))


class IntegrationTests(IndexingTestCase):

    def testReindexingUpdatesModificationDate(self):
        # `CMFCatalogAware.reindexObject` also updates the modification date
        # of the object for the "reindex all" case.  unfortunately, some other
        # packages like `CMFEditions` check that date to see if the object was
        # modified during the request, so we need to do the same...
        obj = self.folder
        date1 = obj.modified()
        # so on reindex the modification date should be updated
        self.folder.reindexObject()
        date2 = obj.modified()
        self.failUnless(date1 < date2)
        # this only happens when the object is fully reindexed
        self.folder.reindexObject(idxs=['Title'])
        date3 = obj.modified()
        self.assertEqual(date2, date3)
        # on commit the date should not get updated again
        commit()
        date4 = obj.modified()
        self.assertEqual(date2, date4)
