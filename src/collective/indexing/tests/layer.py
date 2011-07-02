from Testing.ZopeTestCase import installPackage
from Products.Five import zcml, fiveconfigure
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer


class InstallationLayer(BasePTCLayer):
    """ basic layer for testing package (de)installation """

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from collective import indexing
        zcml.load_config('configure.zcml', package=indexing)
        fiveconfigure.debug_mode = False
        # after which it can be initialized...
        installPackage('collective.indexing', quiet=True)

installation = InstallationLayer(bases=[ptc_layer])
indexing = installation


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

combined = SubscriberIndexingLayer(bases=[subscribers, installation])
