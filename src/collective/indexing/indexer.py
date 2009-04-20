from zope.interface import implements
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
from collective.indexing.interfaces import IIndexQueueProcessor


# container to hold references to the original and "monkeyed" indexing methods
# these are populated by `collective.indexing.monkey`
catalogMultiplexMethods = {}
catalogAwareMethods = {}
monkeyMethods = {}


def getDispatcher(obj, name):
    """ return named indexing method according on the used mixin class """
    if isinstance(obj, CatalogMultiplex):
        op = catalogMultiplexMethods.get(name, None)
    elif isinstance(obj, CMFCatalogAware):
        op = catalogAwareMethods.get(name, None)
    else:
        op = None
    if callable(op):
        method = getattr(obj.__class__, op.__name__).im_func
        monkey = monkeyMethods.get(name, None)
        if monkey is not None and method is not monkey:
            op = method     # return object's own method to be used...
    return op


def index(obj, attributes=None):
    op = getDispatcher(obj, 'index')
    if op is not None:
        op(obj)


def reindex(obj, attributes=None):
    op = getDispatcher(obj, 'reindex')
    if op is not None:
        op(obj, attributes or [])


def unindex(obj):
    op = getDispatcher(obj, 'unindex')
    if op is not None:
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
