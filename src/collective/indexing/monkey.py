# this modules takes care of monkey-patching the `CatalogMultiplex` (from
# `Archetypes/CatalogMultiplex.py`) and `CMFCatalogAware` (from
# `CMFCore/CMFCatalogAware.py`) mixin classes, so that indexing operations
# will be added to the queue or, if disabled, directly dispatched to the
# default indexer (using the original methods)

from Acquisition import aq_base
from collective.indexing.indexer import catalogAwareMethods
from collective.indexing.indexer import catalogMultiplexMethods
from collective.indexing.indexer import monkeyMethods
from collective.indexing.queue import getQueue
from collective.indexing.queue import processQueue
from collective.indexing.subscribers import filterTemporaryItems
from logging import getLogger
# set up dispatcher containers for the original methods and
# hook up the new methods if that hasn't been done before...
from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
# patch CatalogTool.(unrestricted)searchResults to flush the queue
# before issuing a query
from Products.CMFPlone.CatalogTool import CatalogTool


logger = getLogger(__name__)
debug = logger.debug


def indexObject(self):
    obj = filterTemporaryItems(self)
    indexer = getQueue()
    if obj is not None and indexer is not None:
        indexer.index(obj)


def unindexObject(self):
    obj = filterTemporaryItems(self, checkId=False)
    indexer = getQueue()
    if obj is not None and indexer is not None:
        indexer.unindex(obj)


def reindexObject(self, idxs=None):
    # `CMFCatalogAware.reindexObject` also updates the modification date
    # of the object for the "reindex all" case.  unfortunately, some other
    # packages like `CMFEditions` check that date to see if the object was
    # modified during the request, which fails when it's only set on commit
    if idxs in (None, []) and hasattr(aq_base(self), 'notifyModified'):
        self.notifyModified()
    obj = filterTemporaryItems(self)
    indexer = getQueue()
    if obj is not None and indexer is not None:
        indexer.reindex(obj, idxs)


def reindexObjectSecurity(self, skip_self=False):
    if not filterTemporaryItems(self):
        return

    if not skip_self:
        self.reindexObject(idxs=self._cmf_security_indexes)

    def _reindex(obj, path):
        obj.reindexObject(idxs=self._cmf_security_indexes)

    self.ZopeFindAndApply(self, search_sub=True, apply_func=_reindex)


for module, container in ((CMFCatalogAware, catalogAwareMethods),
                          (CatalogMultiplex, catalogMultiplexMethods),
                          (BaseBTreeFolder, {})):
    if not container and module is not None:
        container.update({
            'index': module.indexObject,
            'reindex': module.reindexObject,
            'unindex': module.unindexObject,
            'reindexObjectSecurity': module.reindexObjectSecurity
        })
        module.indexObject = indexObject
        module.reindexObject = reindexObject
        module.unindexObject = unindexObject
        module.reindexObjectSecurity = reindexObjectSecurity
        debug('patched %s', str(module.indexObject))
        debug('patched %s', str(module.reindexObject))
        debug('patched %s', str(module.unindexObject))
        debug('patched %s', str(module.reindexObjectSecurity))

# also record the new methods in order to be able to compare them
monkeyMethods.update({
    'index': indexObject,
    'reindex': reindexObject,
    'unindex': unindexObject,
    'reindexObjectSecurity': reindexObjectSecurity,
})


def searchResults(self, REQUEST=None, **kw):
    """ flush the queue before querying the catalog """
    processQueue()
    return self.__af_old_searchResults(REQUEST, **kw)


def unrestrictedSearchResults(self, REQUEST=None, **kw):
    """ flush the queue before querying the catalog """
    processQueue()
    return self.__af_old_unrestrictedSearchResults(REQUEST, **kw)


def getCounter(self):
    """ return a counter which is increased on catalog changes """
    processQueue()
    return self.__af_old_getCounter()


def setupFlush():
    """ apply or revert monkey-patch for `searchResults`
        and `unrestrictedSearchResults` """
    if not hasattr(CatalogTool, '__af_old_searchResults'):
        CatalogTool.__af_old_searchResults = CatalogTool.searchResults
        CatalogTool.searchResults = searchResults
        CatalogTool.__call__ = searchResults
        debug('patched %s', str(CatalogTool.searchResults))
        debug('patched %s', str(CatalogTool.__call__))
    if not hasattr(CatalogTool, '__af_old_unrestrictedSearchResults'):
        CatalogTool.__af_old_unrestrictedSearchResults = CatalogTool.unrestrictedSearchResults
        CatalogTool.unrestrictedSearchResults = unrestrictedSearchResults
        debug('patched %s', str(CatalogTool.unrestrictedSearchResults))
    if not hasattr(CatalogTool, '__af_old_getCounter'):
        CatalogTool.__af_old_getCounter = CatalogTool.getCounter
        CatalogTool.getCounter = getCounter
        debug('patched %s', str(CatalogTool.getCounter))

setupFlush()


def unpatch():
    """Remove monkey-patches applied when importing this module

    This allows to cleanly remove all traces of collective.indexing,
    bringing back the original implementation.

    Mostly useful during testing, specially while tearing down a layer that
    was using collective.indexing (maybe indirectly through collective.solr).
    """
    # remove the indexing patches
    for module, container in ((CMFCatalogAware, catalogAwareMethods),
                              (CatalogMultiplex, catalogMultiplexMethods)):
        module.indexObject = container['index']
        module.reindexObject = container['reindex']
        module.unindexObject = container['unindex']
        module.reindexObjectSecurity = container['reindexObjectSecurity']

    # remove the searching patches
    if getattr(CatalogTool, '__af_old_searchResults', False):
        CatalogTool.searchResults = CatalogTool.__af_old_searchResults
        CatalogTool.__call__ = CatalogTool.__af_old_searchResults
    if getattr(CatalogTool, '__af_old_unrestrictedSearchResults', False):
        CatalogTool.unrestrictedSearchResults = CatalogTool.__af_old_unrestrictedSearchResults
    if getattr(CatalogTool, '__af_old_getCounter', False):
        CatalogTool.getCounter = CatalogTool.__af_old_getCounter
