from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexing
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.queue import getQueue


def isActive():
    return queryUtility(IIndexQueueSwitch) is not None


def getIndexer():
    """ look for and return an indexer """
    if isActive():                  # when switched on...
        return getQueue()           # return a (thread-local) queue object...
    indexers = list(getUtilitiesFor(IIndexing))
    if len(indexers) == 1:
        return indexers[0][1]       # directly return unqueued indexer...
    elif not indexers:
        return None                 # or none...
    else:
        assert len(indexers) < 1, 'cannot use multiple direct indexers; please enable queueing'


# patch CatalogTool.searchResults to flush the queue before issuing a query
from collective.indexing.queue import processQueue
from Products.CMFPlone.CatalogTool import CatalogTool


def searchResults(self, REQUEST=None, **kw):
    """Flush the queue before querying the catalog"""
    if isActive():
        processQueue()

    return self.__af_old_searchResults(REQUEST, **kw)


def enableAutoFlush(enable):
    """Monkey-patch searchResults"""
    if enable:
        if not hasattr(CatalogTool, '__af_old_searchResults'):
            CatalogTool.__af_old_searchResults = CatalogTool.searchResults
            CatalogTool.searchResults = searchResults
            CatalogTool.__call__ = searchResults
    else:
        if hasattr(CatalogTool, '__af_old_searchResults'):
            CatalogTool.searchResults = CatalogTool.__af_old_searchResults
            CatalogTool.__call__ = CatalogTool.__af_old_searchResults
            delattr(CatalogTool, '__af_old_searchResults')

