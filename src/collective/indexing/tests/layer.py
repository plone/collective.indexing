from Testing.ZopeTestCase import app, close, installPackage
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import PloneSite
from transaction import commit


class IndexingLayer(PloneSite):
    """ layer for integration tests with activated deferred indexing """

    @classmethod
    def setUp(cls):
        # install package, import profile...
        installPackage('collective.indexing', quiet=True)
        root = app()
        portal = root.plone
        profile = 'profile-collective.indexing:default'
        tool = getToolByName(portal, 'portal_setup')
        tool.runAllImportStepsFromProfile(profile, purge_old=False)
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass
