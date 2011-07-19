from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName


class IndexingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        from collective import indexing
        self.loadZCML(package=indexing)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        workflowTool = getToolByName(portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        portal.invokeFactory('Folder', 'test-folder')
        portal.invokeFactory('Folder', 'news')



INDEXING_LAYER = IndexingLayer()
INDEXING_INTEGRATION = IntegrationTesting(
    bases=(INDEXING_LAYER, ), name="IndexingLayer:Integration")
INDEXING_FUNCTIONAL = FunctionalTesting(
    bases=(INDEXING_LAYER, ), name="IndexingLayer:Functional")


class SubscriberLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        from collective import indexing
        self.loadZCML('subscribers.zcml', package=indexing)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        workflowTool = getToolByName(portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        portal.invokeFactory('Folder', 'test-folder')


SUBSCRIBER_LAYER = SubscriberLayer()
SUBSCRIBER_INTEGRATION = IntegrationTesting(
    bases=(SUBSCRIBER_LAYER, ), name="SubscriberLayer:Integration")
SUBSCRIBER_FUNCTIONAL = FunctionalTesting(
    bases=(SUBSCRIBER_LAYER, ), name="SubscriberLayer:Functional")
