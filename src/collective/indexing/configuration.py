from persistent import Persistent
from zope.interface import implements
from collective.indexing.interfaces import IIndexingConfig


class IndexingConfig(Persistent):
    """ utility to hold the configuration related to indexing """
    implements(IIndexingConfig)

    def __init__(self):
        self.active = True
        self.auto_flush = True  # process indexing queue before every query
