from zope.interface import implements
from collective.indexing.interfaces import IIndexQueueProcessor
from Products.CMFCore.utils import getToolByName


# used instead of a lambda as ZODB dump does not know how to serialize those
def notifyModified(*args):
    pass


class IPortalCatalogQueueProcessor(IIndexQueueProcessor):
    """ an index queue processor for the standard portal catalog via
        the `CatalogMultiplex` and `CMFCatalogAware` mixin classes """


class PortalCatalogProcessor(object):
    implements(IPortalCatalogQueueProcessor)

    def index(self, obj, attributes=None):
        catalog = getToolByName(obj, 'portal_catalog', None)
        catalog._indexObject(obj)
        # if op is not None:
        #     op(obj)

    def reindex(self, obj, attributes=None, update_metadata=1):
        catalog = getToolByName(obj, 'portal_catalog', None)
        catalog._reindexObject(obj, idxs=attributes, update_metadata=update_metadata)
        # if op is not None:
        #     # prevent update of modification date during deferred reindexing
        #     od = obj.__dict__
        #     if not 'notifyModified' in od:
        #         od['notifyModified'] = notifyModified
        #     op(obj, attributes or [])
        #     if 'notifyModified' in od:
        #         del od['notifyModified']

    def unindex(self, obj):
        catalog = getToolByName(obj, 'portal_catalog', None)
        catalog._unindexObject(obj)
        # if op is not None:
        #     op(obj)

    def begin(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass

    @staticmethod
    def get_dispatcher(obj, name):
        """ return named indexing method according on the used mixin class """
        catalog = getToolByName(obj, 'portal_catalog', None)
        if catalog is None:
            return
        attr = getattr(catalog, '_{0}'.format(name), None)
        if attr is not None:
            method = attr.im_func
            return method
        return
