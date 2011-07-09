from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
from Testing.ZopeTestCase import installPackage
from Zope2.App import zcml


class IndexingLayer(BasePTCLayer):

    def afterSetUp(self):
        from collective import indexing
        zcml.load_config('configure.zcml', package=indexing)
        installPackage('collective.indexing', quiet=True)

indexing = IndexingLayer(bases=[ptc_layer])


class SubscriberLayer(BasePTCLayer):
    """ layer for integration tests with activated event subscribers """

    def afterSetUp(self):
        from collective import indexing
        zcml.load_config('subscribers.zcml', package=indexing)

subscribers = SubscriberLayer(bases=[indexing])
