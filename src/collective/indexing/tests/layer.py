from Testing.ZopeTestCase import installPackage
from Products.Five import zcml, fiveconfigure
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer


class IndexingLayer(BasePTCLayer):

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from collective import indexing
        zcml.load_config('configure.zcml', package=indexing)
        fiveconfigure.debug_mode = False
        # after which it can be initialized...
        installPackage('collective.indexing', quiet=True)

indexing = IndexingLayer(bases=[ptc_layer])


class SubscriberLayer(BasePTCLayer):
    """ layer for integration tests with activated event subscribers """

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from collective import indexing
        zcml.load_config('subscribers.zcml', package=indexing)
        fiveconfigure.debug_mode = False

subscribers = SubscriberLayer(bases=[indexing])


class SubscriberIndexingLayer(BasePTCLayer):
    """ layer for integration tests with activated indexing & subscribers """

combined = SubscriberIndexingLayer(bases=[subscribers, indexing])
