# this modules takes care of monkey-patching the `CatalogMultiplex` (from
# `Archetypes/CatalogMultiplex.py`) and `CMFCatalogAware` (from
# `CMFCore/CMFCatalogAware.py`) mixin classes, so that indexing operations
# will be added to the queue or, if disabled, directly dispatched to the
# default indexer (using the original methods)

from logging import getLogger
from Acquisition import aq_base
from collective.indexing.utils import isActive, getIndexer
from collective.indexing.indexer import catalogMultiplexMethods
from collective.indexing.indexer import catalogAwareMethods
from collective.indexing.indexer import monkeyMethods
from collective.indexing.indexer import index, reindex, unindex
from collective.indexing.subscribers import filterTemporaryItems

logger = getLogger(__name__)
info = logger.info


def indexObject(self):
    if not isActive():
        return index(self)
    obj = filterTemporaryItems(self)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.index(obj)


def unindexObject(self):
    if not isActive():
        return unindex(self)
    obj = filterTemporaryItems(self, checkId=False)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.unindex(obj)


def reindexObject(self, idxs=None):
    # `CMFCatalogAware.reindexObject` also updates the modification date
    # of the object for the "reindex all" case.  unfortunately, some other
    # packages like `CMFEditions` check that date to see if the object was
    # modified during the request, which fails when it's only set on commit
    if idxs in (None, []) and hasattr(aq_base(self), 'notifyModified'):
        self.notifyModified()
    if not isActive():
        return reindex(self, idxs)
    obj = filterTemporaryItems(self)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.reindex(obj, idxs)


# set up dispatcher containers for the original methods and
# hook up the new methods if that hasn't been done before...
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from collective.indexing.archetypes import CatalogMultiplex
from collective.indexing.archetypes import BaseBTreeFolder
for module, container in ((CMFCatalogAware, catalogAwareMethods),
                          (CatalogMultiplex, catalogMultiplexMethods),
                          (BaseBTreeFolder, {})):
    if not container and module is not None:
        container.update({
            'index': module.indexObject,
            'reindex': module.reindexObject,
            'unindex': module.unindexObject,
        })
        module.indexObject = indexObject
        module.reindexObject = reindexObject
        module.unindexObject = unindexObject
        info('patched %s', str(module.indexObject))
        info('patched %s', str(module.reindexObject))
        info('patched %s', str(module.unindexObject))

# also record the new methods in order to be able to compare them
monkeyMethods.update({
    'index': indexObject,
    'reindex': reindexObject,
    'unindex': unindexObject,
})



# patch CatalogTool.(unrestricted)searchResults to flush the queue
# before issuing a query
from Products.CMFPlone.CatalogTool import CatalogTool
from collective.indexing.utils import autoFlushQueue


def searchResults(self, REQUEST=None, **kw):
    """ flush the queue before querying the catalog """
    if isAutoFlushing():
        autoFlushQueue(hint='restricted search', request=REQUEST, **kw)
    return self.__af_old_searchResults(REQUEST, **kw)


def unrestrictedSearchResults(self, REQUEST=None, **kw):
    """ flush the queue before querying the catalog """
    if isAutoFlushing():
        autoFlushQueue(hint='unrestricted search', request=REQUEST, **kw)
    return self.__af_old_unrestrictedSearchResults(REQUEST, **kw)


def getCounter(self):
    """ return a counter which is increased on catalog changes """
    if isAutoFlushing():
        autoFlushQueue(hint='getCounter')
    return self.__af_old_getCounter()


def setupAutoFlush(enable=True):
    """ apply or revert monkey-patch for `searchResults`
        and `unrestrictedSearchResults` """
    if enable:
        if not hasattr(CatalogTool, '__af_old_searchResults'):
            CatalogTool.__af_old_searchResults = CatalogTool.searchResults
            CatalogTool.searchResults = searchResults
            CatalogTool.__call__ = searchResults
            info('patched %s', str(CatalogTool.searchResults))
            info('patched %s', str(CatalogTool.__call__))
        if not hasattr(CatalogTool, '__af_old_unrestrictedSearchResults'):
            CatalogTool.__af_old_unrestrictedSearchResults = CatalogTool.unrestrictedSearchResults
            CatalogTool.unrestrictedSearchResults = unrestrictedSearchResults
            info('patched %s', str(CatalogTool.unrestrictedSearchResults))
        if not hasattr(CatalogTool, '__af_old_getCounter'):
            CatalogTool.__af_old_getCounter = CatalogTool.getCounter
            CatalogTool.getCounter = getCounter
            info('patched %s', str(CatalogTool.getCounter))
    else:
        if hasattr(CatalogTool, '__af_old_searchResults'):
            CatalogTool.searchResults = CatalogTool.__af_old_searchResults
            CatalogTool.__call__ = CatalogTool.__af_old_searchResults
            delattr(CatalogTool, '__af_old_searchResults')
            info('removed patch from %s', str(CatalogTool.searchResults))
            info('removed patch from %s', str(CatalogTool.__call__))
        if hasattr(CatalogTool, '__af_old_unrestrictedSearchResults'):
            CatalogTool.unrestrictedSearchResults = CatalogTool.__af_old_unrestrictedSearchResults
            delattr(CatalogTool, '__af_old_unrestrictedSearchResults')
            info('removed patch from %s', str(CatalogTool.unrestrictedSearchResults))
        if hasattr(CatalogTool, '__af_old_getCounter'):
            CatalogTool.getCounter = CatalogTool.__af_old_getCounter
            delattr(CatalogTool, '__af_old_getCounter')
            info('removed patch from %s', str(CatalogTool.getCounter))

# (de)activate the auto-flush patches according to the setting...
from collective.indexing.utils import isAutoFlushing
setupAutoFlush(isAutoFlushing())


# in plone 3.x renaming an item triggers a call to `reindexOnReorder`,
# which uses the catalog to update the `getObjPositionInParent` index for
# all objects in the given folder;  with queued indexing any renamed object's
# id will still be present in the catalog at that time, but `getObject` will
# fail, of course;  however, since using the catalog for this sort of thing
# was a bad idea in the first place, the method is patched here and has should
# hopefully get fixed in plone 3.3 as well...
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.PloneTool import PloneTool


def reindexOnReorder(self, parent):
    """ Catalog ordering support """
    mtool = getToolByName(self, 'portal_membership')
    if mtool.checkPermission(ModifyPortalContent, parent):
        for obj in parent.objectValues():
            if isinstance(obj, CatalogMultiplex) or isinstance(obj, CMFCatalogAware):
                obj.reindexObject(['getObjPositionInParent'])

PloneTool.reindexOnReorder = reindexOnReorder
info('patched %s', str(PloneTool.reindexOnReorder))
