from logging import getLogger, DEBUG
from inspect import currentframe
from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexing
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.queue import getQueue
from collective.indexing.queue import processQueue


log = getLogger(__name__).log
log_level = DEBUG


def isActive():
    config = queryUtility(IIndexingConfig)
    if config is not None:
        return config.active
    return False


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


def isAutoFlushing():
    config = queryUtility(IIndexingConfig)
    if config is not None:
        return config.auto_flush
    return True                     # on by default as a safety net...


def framespec(depth=1):
    """ formet the module, name & line for the frame at the given depth """
    frame = currentframe(depth)
    get = frame.f_globals.get
    name = get('__name__') or get('test') or get('__file__') or '?'
    line = frame.f_lineno
    func = frame.f_code.co_name
    return '%s/%s:%d' % (name, func, line)


def autoFlushQueue(hint='??', request=None, **kw):
    """ process the queue (for this thread) immediately if the
        auto-flush feature is enabled """
    if isActive() and isAutoFlushing() and getQueue().length():
        log(log_level, 'auto-flush via %s at `%s`: %r, %r',
            hint, framespec(3), request, kw)
        return processQueue()
