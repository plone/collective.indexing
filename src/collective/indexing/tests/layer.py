from Testing.ZopeTestCase import installPackage
from Products.Five import zcml, fiveconfigure
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer


class InstallationLayer(BasePTCLayer):
    """ basic layer for testing package (de)installation """

installation = InstallationLayer(bases=[ptc_layer])


class IndexingLayer(BasePTCLayer):
    """ layer for integration tests with activated deferred indexing """

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from collective import indexing
        zcml.load_config('configure.zcml', package=indexing)
        fiveconfigure.debug_mode = False
        # after which it can be initialized and quick-installed...
        installPackage('collective.indexing', quiet=True)
        self.addProfile('collective.indexing:default')

indexing = IndexingLayer(bases=[installation])


class SubscriberLayer(BasePTCLayer):
    """ layer for integration tests with activated event subscribers """

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from collective import indexing
        zcml.load_config('subscribers.zcml', package=indexing)
        fiveconfigure.debug_mode = False

subscribers = SubscriberLayer(bases=[installation])


class SubscriberIndexingLayer(BasePTCLayer):
    """ layer for integration tests with activated indexing & subscribers """

combined = SubscriberIndexingLayer(bases=[subscribers, indexing])
