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

    def index(self, obj, attributes=None):
        assert obj is not None, 'invalid object'
        self.queue.append((INDEX, obj, attributes))
        self.hook()

    def reindex(self, obj, attributes=None):
        assert obj is not None, 'invalid object'
        self.queue.append((REINDEX, obj, attributes))
        self.hook()

    def unindex(self, obj):
        assert obj is not None, 'invalid object'
        self.queue.append((UNINDEX, obj, None))
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
        for op, obj, attributes in self.queue:
            for name, util in utilities:
                if op == INDEX:
                    util.index(obj, attributes)
                elif op == REINDEX:
                    util.reindex(obj, attributes)
                elif op == UNINDEX:
                    util.unindex(obj)
                else:
                    raise 'InvalidQueueOperation', op
            processed += 1
        for name, util in utilities:
            util.commit()
        self.clear()
        return processed

    def clear(self):
        del self.queue[:]

