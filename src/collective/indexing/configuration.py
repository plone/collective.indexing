from persistent import Persistent
from zope.interface import implements
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.monkey import setupAutoFlush


class IndexingConfig(Persistent):
    """ utility to hold the configuration related to indexing """
    implements(IIndexingConfig)

    def __init__(self):
        self.active = True
        self.auto_flush = True  # process indexing queue before every query

    def getAutoFlush(self):
        return self.__dict__['auto_flush']

    def setAutoFlush(self, value):
        self.__dict__['auto_flush'] = value
        setupAutoFlush(value)

    auto_flush = property(getAutoFlush, setAutoFlush)
