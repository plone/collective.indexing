from logging import getLogger
from persistent import Persistent
from zope.interface import implements
from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexQueue
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.interfaces import IQueueReducer
from collective.indexing.config import INDEX, REINDEX, UNINDEX
from collective.indexing.local import getLocal, setLocal
from collective.indexing.transactions import QueueTM

debug = getLogger('collective.indexing.queue').debug


class IndexQueue(object):
    """ an indexing queue """
    implements(IIndexQueue)

    def __init__(self):
        tm = getLocal('tm')
        if tm is None:
            tm = QueueTM(self)          # create a transaction manager...
            setLocal('tm', tm)          # remember it...
            self.setHook(tm._register)  # and set up the hook...

    @property
    def queue(self):
        """ return a thread-local list used to hold the queue items """
        return getLocal('queue', list)

    @property
    def hook(self):
        """ return a thread-local variable used to hold the tm hook;
            the default is set to an arbitrary callable to avoid having
            to check for `None` everywhere the hook is called """
        return getLocal('hook', lambda: lambda: 42)

    def index(self, obj, attributes=None):
        assert obj is not None, 'invalid object'
        debug('adding index operation for %r', obj)
        self.queue.append((INDEX, obj, attributes))
        self.hook()

    def reindex(self, obj, attributes=None):
        assert obj is not None, 'invalid object'
        debug('adding reindex operation for %r', obj)
        self.queue.append((REINDEX, obj, attributes))
        self.hook()

    def unindex(self, obj):
        assert obj is not None, 'invalid object'
        debug('adding unindex operation for %r', obj)
        self.queue.append((UNINDEX, obj, None))
        self.hook()

    def setHook(self, hook):
        assert callable(hook), 'hook must be callable'
        debug('setting hook to %r', hook)
        setLocal('hook', hook)

    def getState(self):
        return list(self.queue)     # better return a copy... :)

    def setState(self, state):
        assert isinstance(state, list), 'state must be a list'
        debug('setting queue state to %r', state)
        setLocal('queue', state)

    def optimize(self):
        reducer = queryUtility(IQueueReducer)
        if reducer is not None:
            self.setState(reducer.optimize(self.getState()))

    def process(self):
        utilities = list(getUtilitiesFor(IIndexQueueProcessor))
        debug('processing queue using %r', utilities)
        processed = 0
        for name, util in utilities:
            util.begin()
        # TODO: must the queue be handled independently for each processor?
        self.optimize()
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
            debug('committing queue using %r', util)
            util.commit()
        debug('finished processing %d items...', processed)
        self.clear()
        return processed

    def clear(self):
        debug('clearing %d queue item(s)', len(self.queue))
        del self.queue[:]
        setLocal('tm', None)    # release transaction manager...


class IndexQueueSwitch(Persistent):
    """ marker utility for switching queued indexing on/off """
    implements(IIndexQueueSwitch)

