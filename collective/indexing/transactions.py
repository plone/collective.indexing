from logging import getLogger
from threading import local
from transaction.interfaces import ISavepointDataManager
from transaction import get as getTransaction
from zope.interface import implements
from collective.indexing.interfaces import IIndexQueue

logger = getLogger('collective.indexing.transactions')


class QueueSavepoint:
    """ transaction savepoints using the IIndexQueue interface """

    def __init__(self, queue):
        self.queue = queue
        self.state = queue.getState()

    def rollback(self):
        self.queue.setState(self.state)


class QueueTM(local):
    """ transaction manager hook for the indexing queue """
    implements(ISavepointDataManager)

    def __init__(self, queue):
        logger.debug('initializing tm %r for queue %r...', self, queue)
        local.__init__(self)
        self.registered = False
        self.vote = False
        assert IIndexQueue.providedBy(queue), queue
        self.queue = queue

    def register(self):
        if not self.registered:
            try:
                transaction = getTransaction()
                transaction.join(self)
                transaction.addBeforeCommitHook(self.before_commit)
                self.registered = True
                logger.debug('registered tm %r (queue %r).', self, self.queue)
            except:
                logger.exception('exception during register (registered=%s)', self.registered)

    def savepoint(self):
        return QueueSavepoint(self.queue)

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def before_commit(self):
        if self.queue.getState():
            logger.debug('processing queue...')
            processed = self.queue.process()
            logger.debug('%d item(s) processed during queue run', processed)
        self.queue.clear()

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.queue.commit()
        self.registered = False

    def tpc_abort(self, transaction):
        self.queue.abort()
        if self.queue.getState():
            logger.debug('emptying unprocessed queue due to abort()...')
        self.queue.clear()
        self.registered = False

    abort = tpc_abort

    def sortKey(self):
        return id(self)
