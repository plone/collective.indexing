from Products.PloneTestCase.layer import PloneSite


class IndexingLayer(PloneSite):
    """ layer for integration tests with activated deferred indexing """

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

