from zope.interface import implements

from collective.indexing.interfaces import IIndexing, IIndexQueue
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.config import INDEX, REINDEX, UNINDEX


class TestHelpers(object):

    def fileIds(self):
        catalog = self.portal.portal_catalog
        return [brain.id for brain in catalog(portal_type='File')]

    def create(self):
        self.failIf(self.folder.get('foo'), '"foo" exists?')
        self.folder.invokeFactory('File', id='foo', title='Foo')
        return self.fileIds()

    def remove(self):
        self.folder.manage_delObjects('foo')
        return self.fileIds()


class MockIndexer(object):
    implements(IIndexing)

    def __init__(self):
        self.queue = []

    def index(self, obj, attributes=None):
        self.queue.append((INDEX, obj, attributes))

    def reindex(self, obj, attributes=None):
        self.queue.append((REINDEX, obj, attributes))

    def unindex(self, obj):
        self.queue.append((UNINDEX, obj, None))


class MockQueue(MockIndexer):
    implements(IIndexQueue)

    processed = None
    hook = lambda self: 42

    def index(self, obj, attributes=None):
        super(MockQueue, self).index(obj, attributes)
        self.hook()

    def reindex(self, obj, attributes=None):
        super(MockQueue, self).reindex(obj, attributes)
        self.hook()

    def unindex(self, obj):
        super(MockQueue, self).unindex(obj)
        self.hook()

    def getState(self):
        return list(self.queue)     # better return a copy... :)

    def setState(self, state):
        self.queue = state

    def optimize(self):
        pass

    def process(self):
        self.processed = self.queue
        self.clear()
        return len(self.processed)

    def clear(self):
        self.queue = []


class MockQueueProcessor(MockQueue):
    implements(IIndexQueueProcessor)

    state = 'unknown'

    def begin(self):
        self.state = 'started'

    def commit(self):
        self.state = 'finished'

    def abort(self):
        self.clear()
        self.state = 'aborted'
