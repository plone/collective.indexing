from unittest import defaultTestLoader
from Products.PloneTestCase import ptc
from collective.indexing.tests.base import InstallationTestCase

# test-specific imports go here...
from transaction import commit
from zope.component import getUtility, getUtilitiesFor
from zope.component import provideUtility, getGlobalSiteManager
from collective.indexing.interfaces import IIndexQueue, IIndexing
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.config import IndexingConfig
from collective.indexing.utils import isActive, isAutoFlushing
from collective.indexing.utils import getIndexer
from collective.indexing.tests import utils


class InstallationTests(InstallationTestCase):

    def testInstallation(self):
        # without the product indexing should happen normally...
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])
        # now the package is installed, which shouldn't change things,
        # even though queued indexing hasn't been activated yet...
        ptc.installPackage('collective.indexing', quiet=True)
        self.failIf(isActive())
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])
        # the profile gets applied, i.e. the package is quick-installed
        # again, things should get indexed, but only at transaction commit
        self.portal.portal_quickinstaller.installProduct('collective.indexing')
        # for this test we first want to turn off auto-flushing, though...
        getUtility(IIndexingConfig).auto_flush = False
        self.failUnless(isActive())
        self.failIf(isAutoFlushing())
        self.assertEqual(self.create(), [])
        commit()
        self.assertEqual(self.fileIds(), ['foo'])
        self.assertEqual(self.remove(), ['foo'])
        commit()
        self.assertEqual(self.fileIds(), [])
        # after un-installing the package indexing should be immediate again
        self.portal.portal_quickinstaller.uninstallProducts(['collective.indexing'])
        commit()
        self.failIf(isActive())
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])


class UtilityTests(InstallationTestCase):

    def testGetIndexer(self):
        # no indexer should be found initially...
        indexer = getIndexer()
        self.failIf(indexer, 'indexer found?')
        # a direct indexer is provided...
        direct_indexer = utils.MockIndexer()
        provideUtility(direct_indexer, name='indexer')
        indexer = getIndexer()
        self.failUnless(indexer, 'no indexer found')
        self.assertEqual(indexer, direct_indexer, 'who are you?')
        # a second direct indexer is provided...
        mock_indexer = utils.MockIndexer()
        provideUtility(mock_indexer, name='rexedni')
        self.assertRaises(AssertionError, getIndexer)
        # queued indexing is enabled...
        config = IndexingConfig()
        provideUtility(config, IIndexingConfig)
        indexer = getIndexer()
        self.failUnless(indexer, 'no indexer found')
        self.failUnless(IIndexQueue.providedBy(indexer), 'non-queued indexer found')
        # and we've got two indexers to dispatch things to...
        indexers = list(getUtilitiesFor(IIndexing))
        self.assertEqual(len(indexers), 2)
        # finally, clean up registrations
        unregister = getGlobalSiteManager().unregisterUtility
        unregister(direct_indexer, name='indexer')
        unregister(mock_indexer, name='rexedni')
        unregister(config, IIndexingConfig)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
