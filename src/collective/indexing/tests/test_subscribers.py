from unittest import defaultTestLoader
from collective.indexing.tests.base import SubscriberTestCase
from collective.indexing.tests.test_lifecycle import LifeCycleTests

# test-specific imports go here...
from collective.indexing import subscribers


class SubscriberTests(SubscriberTestCase, LifeCycleTests):

    publish_attributes = None   # everything gets indexed... :(

    def afterSetUp(self):
        self.prepare()
        # trick the subscribers to use the mock indexer...
        self.original_getIndexer = subscribers.getIndexer
        subscribers.getIndexer = lambda: self.indexer

    def beforeTearDown(self):
        subscribers.getIndexer = self.original_getIndexer

    def testUpdateObject(self):
        self.file.update(title='Foo')
        # `update()` doesn't fire an event, so the queue remains empty
        self.assertEqual(self.queue, [])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
