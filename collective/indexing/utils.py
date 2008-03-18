from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexing
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.queue import getQueue


def getIndexer():
    """ look for and return an indexer """
    switch = queryUtility(IIndexQueueSwitch)
    if switch is not None:          # when switched on...
        return getQueue()           # return a (thread-local) queue object...
    indexers = list(getUtilitiesFor(IIndexing))
    if len(indexers) == 1:
        return indexers[0][1]       # directly return unqueued indexer...
    elif not indexers:
        return None                 # or none...
    else:
        assert len(indexers) < 1, 'cannot use multiple direct indexers; please enable queueing'

