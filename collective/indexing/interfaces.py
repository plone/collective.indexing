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


class IIndexQueue(IIndexing):
    """ a queue for storing and optimizing indexing operations """

    def setHook(hook):
        """ set the hook for the transaction manager;  this hook must be
            called whenever an indexing operation is added to the queue """

    def getState():
        """ get the state of the queue, i.e. its contents """

    def setState(state):
        """ set the state of the queue, i.e. its contents """

    def optimize():
        """ optimize the queue, i.e. clean up duplicates etc """

    def process():
        """ process the contents of the queue, i.e. start indexing;
            returns the number of processed queue items """

    def clear():
        """ clear the queue's contents in an ordered fashion """


class IIndexQueueProcessor(IIndexing):
    """ a queue processor, i.e. an actual implementation of index operations
        for a particular search engine, e.g. the catalog, solr etc """

    def begin():
        """ called before processing of the queue is started """

    def commit():
        """ called after processing of the queue has ended """


class IQueueReducer(Interface):
    """ Optimizing the queue by removing redundant queue entries """

    def optimize(queue):
        """ Remove redundant entries from the queue and return optimized queue
        The queue is a list of tuples with (operator, uid, attributes) """

