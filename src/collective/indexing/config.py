from zope.interface import implements
from collective.indexing.interfaces import IIndexingConfig


# constants for indexing operations
UNINDEX = -1
REINDEX = 0
INDEX = 1


class IndexingConfig(object):

    implements(IIndexingConfig)

    def __init__(self):
        self.active = True
        self.auto_flush = True
