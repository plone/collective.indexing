from zope.interface import implements
from persistent import Persistent
from collective.indexing.interfaces import IIndexQueueProcessor
from Products.Archetypes.interfaces import IBaseContent


class ICatalogMultiplexQueueProcessor(IIndexQueueProcessor):
    """ an index queue processor for solr """


class CatalogMultiplexQueueProcessor(object):
    implements(ICatalogMultiplexQueueProcessor)

    def begin(self):
        pass

    def commit(self):
        pass

    def __url(self, obj):
        return '/'.join( obj.getPhysicalPath() )

    def index(self, obj, attributes=None):
        if IBaseContent.providedBy(obj):
            catalogs = obj.getCatalogs()
            url = self.__url(obj)
            for c in catalogs:
                c.catalog_object(obj, url)

    def reindex(self, obj, attributes=None):
        self.index(obj, attributes)

    def unindex(self, obj):
        if IBaseContent.providedBy(obj):
            catalogs = obj.getCatalogs()
            url = self.__url(obj)
            for c in catalogs:
                if c._catalog.uids.get(url, None) is not None:
                    c.uncatalog_object(url)
