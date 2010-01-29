from unittest import defaultTestLoader
from zope.component import getUtility
from Products.GenericSetup.tests.common import TarballTester
from StringIO import StringIO

from collective.indexing.tests.base import IndexingTestCase
from collective.indexing.interfaces import IIndexingConfig


class SetupToolTests(IndexingTestCase, TarballTester):

    def afterSetUp(self):
        config = getUtility(IIndexingConfig)
        config.active = False
        config.auto_flush = False

    def testImportStep(self):
        profile = 'profile-collective.indexing:default'
        tool = self.portal.portal_setup
        result = tool.runImportStepFromProfile(profile, 'indexing')
        self.assertEqual(result['steps'], [u'componentregistry', 'indexing'])
        output = 'collective.indexing: settings imported.'
        self.failUnless(result['messages']['indexing'].endswith(output))
        config = getUtility(IIndexingConfig)
        self.assertEqual(config.active, True)
        self.assertEqual(config.auto_flush, True)

    def testExportStep(self):
        tool = self.portal.portal_setup
        result = tool.runExportStep('indexing')
        self.assertEqual(result['steps'], ['indexing'])
        self.assertEqual(result['messages']['indexing'], None)
        tarball = StringIO(result['tarball'])
        self._verifyTarballContents(tarball, ['indexing.xml'])
        self._verifyTarballEntryXML(tarball, 'indexing.xml', INDEXING_XML)


INDEXING_XML = """\
<?xml version="1.0"?>
<object name="indexing">
  <settings>
    <active value="False" />
    <auto-flush value="False" />
  </settings>
</object>
"""


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
