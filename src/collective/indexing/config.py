from persistent import Persistent
from zope.interface import implements
from collective.indexing.interfaces import IIndexingConfig


# constants for indexing operations
UNINDEX = -1
REINDEX = 0
INDEX = 1


class IndexingConfig(Persistent):
    """ utility to hold the configuration related to indexing """
    implements(IIndexingConfig)

    def __init__(self):
        self.active = True
        self.auto_flush = True  # process indexing queue before every query

    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'indexing'
