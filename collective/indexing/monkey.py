# Override the indexObject methods, make them do nothing
from collective.indexing.utils import getIndexer

def indexObject(self):
    obj = self
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.index(obj)

def unindexObject(self):
    obj = self
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.unindex(obj)

def reindexObject(self, idxs=[]):
    obj = self
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.reindex(obj)

from Products.Archetypes.CatalogMultiplex import CatalogMultiplex

CatalogMultiplex.indexObject = indexObject
CatalogMultiplex.unindexObject = unindexObject
CatalogMultiplex.reindexObject = reindexObject