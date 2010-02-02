from Products.Five.testbrowser import Browser
from Products.PloneTestCase import ptc
from plone.app.controlpanel.tests.cptc import ControlPanelTestCase
from collective.indexing.tests import layer as testing
from collective.indexing.tests.utils import TestHelpers


ptc.setupPloneSite()


class InstallationTestCase(ptc.PloneTestCase, TestHelpers):
    """ base class for (de)installation tests """

    layer = testing.installation


class IndexingTestCase(ptc.Sandboxed, ptc.PloneTestCase, TestHelpers):
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


class IndexingControlPanelTestCase(ControlPanelTestCase):
    """ base class for control panel tests """

    layer = testing.indexing


class SubscriberTestCase(InstallationTestCase):
    """ base class for event subscriber tests """

    layer = testing.subscribers


class SubscriberFunctionalTestCase(IndexingFunctionalTestCase):
    """ base class for functional tests with active event subscribers """

    layer = testing.combined
