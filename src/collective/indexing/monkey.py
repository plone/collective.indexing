# this modules takes care of monkey-patching the `CatalogMultiplex` (from
# `Archetypes/CatalogMultiplex.py`) and `CMFCatalogAware` (from
# `CMFCore/CMFCatalogAware.py`) mixin classes, so that indexing operations
# will be added to the queue or, if disabled, directly dispatched to the
# default indexer (using the original methods)

from logging import getLogger

logger = getLogger(__name__)
debug = logger.debug


# patch CatalogTool.(unrestricted)searchResults to flush the queue
# before issuing a query
from Products.CMFPlone.CatalogTool import CatalogTool
from collective.indexing.queue import processQueue


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
