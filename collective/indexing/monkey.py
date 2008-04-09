# this modules takes care of monkey-patching the `CatalogMultiplex` (from
# `Archetypes/CatalogMultiplex.py`) and `CMFCatalogAware` (from
# `CMFCore/CMFCatalogAware.py`) mixin classes, so that indexing operations
# will be added to the queue or, if disabled, directly dispatched to the
# default indexer (using the original methods)

from collective.indexing.utils import isActive, getIndexer
from collective.indexing.indexer import catalogMultiplexMethods
from collective.indexing.indexer import catalogAwareMethods
from collective.indexing.indexer import index, reindex, unindex
from collective.indexing.subscribers import filterTemporaryItems


def indexObject(self):
    if not isActive():
        return index(self)
    obj = filterTemporaryItems(self)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.index(obj)


def unindexObject(self):
    if not isActive():
        return unindex(self)
    obj = filterTemporaryItems(self)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.unindex(obj)


def reindexObject(self, idxs=None):
    if not isActive():
        return reindex(self, idxs)
    obj = filterTemporaryItems(self)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.reindex(obj, idxs)


# set up dispatcher containers for the original methods and
# hook up the new methods if that hasn't been done before...
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
for module, container in ((CMFCatalogAware, catalogAwareMethods),
                          (CatalogMultiplex, catalogMultiplexMethods)):
    if not container:
        container.update({
            'index': module.indexObject,
            'reindex': module.reindexObject,
            'unindex': module.unindexObject,
        })
        module.indexObject = indexObject
        module.reindexObject = reindexObject
        module.unindexObject = unindexObject

