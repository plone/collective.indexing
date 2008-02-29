from threading import local
from zope.interface import implements
from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexQueue
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.interfaces import IQueueReducer
from collective.indexing.config import INDEX, REINDEX, UNINDEX


class IndexQueue(local):
    """ a thread-local indexing queue """
    implements(IIndexQueue)

    def __init__(self):
        self.queue = []
        self.hook = lambda: 42  # avoid need to check for `None` everywhere...

    def index(self, uid, attributes=None):
        assert uid is not None, 'invalid UID'
        self.queue.append((INDEX, uid, attributes))
        self.hook()

    def reindex(self, uid, attributes=None):
        assert uid is not None, 'invalid UID'
        self.queue.append((REINDEX, uid, attributes))
        self.hook()

    def unindex(self, uid):
        assert uid is not None, 'invalid UID'
        self.queue.append((UNINDEX, uid, None))
        self.hook()

    def setHook(self, hook):
        assert callable(hook), 'hook must be callable'
        self.hook = hook

    def getState(self):
        return list(self.queue)     # better return a copy... :)

    def setState(self, state):
        self.queue = state

    def optimize(self):
        reducer = queryUtility(IQueueReducer)
        if reducer is not None:
            self.queue = reducer.optimize(list(self.queue))

    def process(self):
        utilities = list(getUtilitiesFor(IIndexQueueProcessor))
        processed = 0
        for name, util in utilities:
            util.begin()
        for op, uid, attributes in self.queue:
            for name, util in utilities:
                if op == INDEX:
                    util.index(uid, attributes)
                elif op == REINDEX:
                    util.reindex(uid, attributes)
                elif op == UNINDEX:
                    util.unindex(uid)
                else:
                    raise 'InvalidQueueOperation', op
            processed += 1
        for name, util in utilities:
            util.commit()
        self.clear()
        return processed

    def clear(self):
        del self.queue[:]

