from zope.interface import Interface
from zope.schema import Bool
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.indexing')


class IIndexingSchema(Interface):

    active = Bool(title=_(u'Active'), default=True,
        description=_(u'Check this to enable optimized indexing on the '
                       'commit boundary.'))

    auto_flush = Bool(title=_(u'Auto-flush queue'), default=True,
        description=_(u'Check to enable automatically processing all queued '
                       'up indexing operations just before a catalog query '
                       'is performed.'))


class IIndexingConfig(IIndexingSchema):
    """ utility to hold the configuration related to indexing """


class IIndexQueueSwitch(Interface):
    """ deprecated marker interface left in place for BBB reasons, i.e. to
        avoid breaking sites that have used versions before 1.0 final """


class IIndexing(Interface):
    """ interface for indexing operations, used both for the queue and
        the processors, which perform the actual indexing;  the queue gets
        registered as a utility while the processors (portal catalog, solr)
        are registered as named utilties """

    def index(obj, attributes=None):
        """ queue an index operation for the given object and attributes """

    def reindex(obj, attributes=None):
        """ queue a reindex operation for the given object and attributes """

    def unindex(obj):
        """ queue an unindex operation for the given object """


class IIndexQueue(IIndexing):
    """ a queue for storing and optimizing indexing operations """

    def setHook(hook):
        """ set the hook for the transaction manager;  this hook must be
            called whenever an indexing operation is added to the queue """

    def getState():
        """ get the state of the queue, i.e. its contents """

    def setState(state):
        """ set the state of the queue, i.e. its contents """

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

    def abort():
        """ called if processing of the queue needs to be aborted """


class IQueueReducer(Interface):
    """ Optimizing the queue by removing redundant queue entries """

    def optimize(queue):
        """ Remove redundant entries from the queue and return optimized queue
        The queue is a list of tuples with (operator, uid, attributes) """
