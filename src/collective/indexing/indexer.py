from logging import getLogger
from zope.interface import implements
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from collective.indexing.archetypes import CatalogMultiplex
from collective.indexing.interfaces import IIndexQueueProcessor

debug = getLogger(__name__).debug


# container to hold references to the original and "monkeyed" indexing methods
# these are populated by `collective.indexing.monkey`
catalogMultiplexMethods = {}
catalogAwareMethods = {}
monkeyMethods = {}


def getOwnIndexMethod(obj, name):
    """ return private indexing method if the given object has one """
    attr = getattr(obj.__class__, name, None)
    if attr is not None:
        method = attr.im_func
        monkey = monkeyMethods.get(name.rstrip('Object'), None)
        if monkey is not None and method is not monkey:
            return method


def getDispatcher(obj, name):
    """ return named indexing method according on the used mixin class """
    if isinstance(obj, CatalogMultiplex):
        op = catalogMultiplexMethods.get(name, None)
    elif isinstance(obj, CMFCatalogAware):
        op = catalogAwareMethods.get(name, None)
    else:
        op = None
    if callable(op):
        method = getOwnIndexMethod(obj, op.__name__)
        if method is not None:
            op = method     # return object's own method to be used...
    return op


def index(obj, attributes=None):
    op = getDispatcher(obj, 'index')
    if op is not None:
        debug('indexing %r', obj)
        op(obj)


def reindex(obj, attributes=None):
    op = getDispatcher(obj, 'reindex')
    if op is not None:
        debug('reindexing %r %r', obj, attributes or ())
        # prevent update of modification date during deferred reindexing
        od = obj.__dict__
        if not 'notifyModified' in od:
            od['notifyModified'] = lambda *args: None
        op(obj, attributes or [])
        if 'notifyModified' in od:
            del od['notifyModified']


def unindex(obj):
    op = getDispatcher(obj, 'unindex')
    if op is not None:
        debug('unindexing %r', obj)
        op(obj)


class IPortalCatalogQueueProcessor(IIndexQueueProcessor):
    """ an index queue processor for the standard portal catalog via
        the `CatalogMultiplex` and `CMFCatalogAware` mixin classes """


class PortalCatalogProcessor(object):
    implements(IPortalCatalogQueueProcessor)

    def index(self, obj, attributes=None):
        index(obj, attributes)

    def reindex(self, obj, attributes=None):
        reindex(obj, attributes)

    def unindex(self, obj):
        unindex(obj)

    def begin(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass
