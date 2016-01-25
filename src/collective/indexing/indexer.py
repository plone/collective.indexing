from zope.interface import implements
from collective.indexing.interfaces import IIndexQueueProcessor


# used instead of a lambda as ZODB dump does not know how to serialize those
def notifyModified(*args):
    pass


class IPortalCatalogQueueProcessor(IIndexQueueProcessor):
    """ an index queue processor for the standard portal catalog via
        the `CatalogMultiplex` and `CMFCatalogAware` mixin classes """


class PortalCatalogProcessor(object):
    implements(IPortalCatalogQueueProcessor)

    def index(self, obj, attributes=None):
        op = self.get_dispatcher(obj, 'indexObject')
        if op is not None:
            op(obj)

    def reindex(self, obj, attributes=None):
        op = self.get_dispatcher(obj, 'reindexObject')
        if op is not None:
            # prevent update of modification date during deferred reindexing
            od = obj.__dict__
            if not 'notifyModified' in od:
                od['notifyModified'] = notifyModified
            op(obj, attributes or [])
            if 'notifyModified' in od:
                del od['notifyModified']

    def unindex(self, obj):
        op = self.get_dispatcher(obj, 'unindexObject')
        if op is not None:
            op(obj)

    def begin(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass

    @staticmethod
    def get_dispatcher(obj, name):
        """ return named indexing method according on the used mixin class """
        attr = getattr(obj, '_{0}'.format(name), None)
        if attr is not None:
            method = attr.im_func
            return method
        return
