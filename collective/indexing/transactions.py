from logging import getLogger
from threading import local
from transaction import get as getTransaction
from Shared.DC.ZRDB.TM import TM
from collective.indexing.interfaces import IIndexQueue

logger = getLogger('collective.indexing.transactions')


class QueueSavepoint:
    """ transaction savepoints using the IIndexQueue interface """

    def __init__(self, queue):
        self.queue = queue
        self.state = queue.getState()

    def rollback(self):
        self.queue.setState(self.state)


class QueueTM(TM, local):
    """ transaction manager hook for the indexing queue """

    _registered = False
    _finalize = False

    def __init__(self, queue):
        local.__init__(self)
        assert IIndexQueue.providedBy(queue), queue
        self.queue = queue

    def _register(self):
        if not self._registered:
            try:
                getTransaction().join(self)
                self._begin()
                self._registered = True
                self._finalize = False
            except:
                logger.exception('exception during _register '
                                 '(registered=%s, finalize=%s)' %
                                  (self._registered, self._finalize))

    def savepoint(self):
        return QueueSavepoint(self.queue)

    def _begin(self):
        self._reset()

    def _reset(self):
        pass

    def _abort(self):
        if self.queue.getState():
            logger.debug('emptying unprocessed queue due to abort()...')
            self.queue.clear()

    def _finish(self):
        try:
            self.queue.optimize()
            if self.queue.getState():
                logger.debug('processing queue...')
                processed = self.queue.process()
                logger.debug('%d item(s) processed during queue run', processed)
        except:
            logger.exception('exception during QueueTM._finish')

