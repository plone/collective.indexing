from logging import getLogger, DEBUG
from inspect import currentframe
from zope.component import queryUtility
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.queue import getQueue
from collective.indexing.queue import processQueue


log = getLogger(__name__).log
log_level = DEBUG


def getIndexer():
    """ look for and return an indexer """
    return getQueue()


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
    if isAutoFlushing() and getQueue().length():
        log(log_level, 'auto-flush via %s at `%s`: %r, %r',
            hint, framespec(3), request, kw)
        return processQueue()
