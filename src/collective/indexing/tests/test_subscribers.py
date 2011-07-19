from collective.indexing import subscribers
from collective.indexing.tests.base import SubscriberTestCase
from collective.indexing.tests.test_lifecycle import LifeCycleTests


class SubscriberTests(SubscriberTestCase, LifeCycleTests):

    publish_attributes = None   # everything gets indexed... :(

    def setUp(self):
        self.prepare()
        # trick the subscribers to use the mock indexer...
        self.original_getIndexer = subscribers.getQueue
        subscribers.getQueue = lambda: self.indexer

    def tearDown(self):
        subscribers.getQueue = self.original_getIndexer

    def testUpdateObject(self):
        self.file.update(title='Foo')
        # `update()` doesn't fire an event, so the queue remains empty
        self.assertEqual(self.queue, [])
