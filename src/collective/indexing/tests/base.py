from collective.indexing.tests import layer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser

import unittest


class Helper(unittest.TestCase):

    @property
    def portal(self):
        return self.layer['portal']

    @property
    def folder(self):
        return self.layer['portal']['test-folder']

    def setRoles(self, roles):
        setRoles(self.portal, TEST_USER_ID, roles)


class IndexingTestCase(Helper):

    layer = layer.INDEXING_INTEGRATION


class IndexingFunctionalTestCase(Helper):

    layer = layer.INDEXING_FUNCTIONAL

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser(self.layer['app'])
        if loggedIn:
            user = TEST_USER_NAME
            pwd = TEST_USER_PASSWORD
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser


class SubscriberTestCase(Helper):

    layer = layer.SUBSCRIBER_INTEGRATION


class SubscriberFunctionalTestCase(Helper):

    layer = layer.SUBSCRIBER_FUNCTIONAL
