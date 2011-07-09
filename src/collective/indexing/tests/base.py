from Products.PloneTestCase import ptc
from Testing.testbrowser import Browser

from collective.indexing.tests import layer as testing

ptc.setupPloneSite()


class IndexingTestCase(ptc.Sandboxed, ptc.PloneTestCase):
    """ base class for integration tests """

    layer = testing.indexing


class IndexingFunctionalTestCase(ptc.FunctionalTestCase):
    """ base class for functional tests """

    layer = testing.indexing

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = ptc.default_user
            pwd = ptc.default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser


class SubscriberTestCase(IndexingTestCase):
    """ base class for event subscriber tests """

    layer = testing.subscribers


class SubscriberFunctionalTestCase(IndexingFunctionalTestCase):
    """ base class for functional tests with active event subscribers """

    layer = testing.subscribers
