from zope.interface import Interface


class IIndexing(Interface):
    """ interface for indexing operations, used both for the queue and
        the 'stores', which perform the actual indexing;  the queue gets
        registered as a utility while the indexers (portal catalog, solr)
        are registerd as adapters """

    def index(uid, attributes=None):
        """ queue an index operation for the given attributes """

    def reindex(uid, attributes=None):
        """ queue a reindex operation for the given attributes """

    def unindex(uid):
        """ queue an unindex operation """

