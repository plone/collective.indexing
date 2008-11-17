from unittest import defaultTestLoader
from Products.PloneTestCase import PloneTestCase as ptc
from collective.indexing.tests.base import IndexingTestCase
from collective.indexing.tests.layer import IndexingLayer
from collective.indexing.tests.utils import TestHelpers


# test-specific imports go here...
from transaction import commit
from collective.indexing.utils import isActive
from collective.indexing.monkey import setAutoFlush
from collective.indexing.config import AUTO_FLUSH


class AutoFlushTests(IndexingTestCase, TestHelpers):

    layer = IndexingLayer

    def afterSetUp(self):
        # clear logs to avoid id collisions
        setup = self.portal.portal_setup
        setup.manage_delObjects(setup.objectIds())

    def beforeTearDown(self):
        # reset to default
        setAutoFlush(AUTO_FLUSH)

    def testNoAutoFlush(self):
        # without auto-flush we must commit to update the catalog
        ptc.installPackage('collective.indexing', quiet=True)
        self.failIf(isActive())
        setAutoFlush(False)
        # the profile gets applied, i.e. the package is quick-installed
        # again, things should get indexed, but only at transaction commit
        self.portal.portal_quickinstaller.installProduct('collective.indexing')
        self.failUnless(isActive())
        self.assertEqual(self.create(), [])
        commit()
        self.assertEqual(self.fileIds(), ['foo'])
        self.assertEqual(self.remove(), ['foo'])
        commit()
        self.assertEqual(self.fileIds(), [])

    def testAutoFlush(self):
        # with auto-flush enabled the catalog is always up-to-date
        ptc.installPackage('collective.indexing', quiet=True)
        self.failIf(isActive())
        setAutoFlush(True)
        # no commits required now
        self.portal.portal_quickinstaller.installProduct('collective.indexing')
        self.failUnless(isActive())
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.fileIds(), ['foo'])
        self.assertEqual(self.remove(), [])
        self.assertEqual(self.fileIds(), [])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

