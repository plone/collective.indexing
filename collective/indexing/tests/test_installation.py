from unittest import defaultTestLoader
from Products.PloneTestCase import PloneTestCase as ptc

ptc.setupPloneSite()


# test-specific imports go here...
from transaction import commit
from collective.indexing.utils import isActive
from collective.indexing.monkey import setAutoFlush
from collective.indexing.config import AUTO_FLUSH


class InstallationTests(ptc.Sandboxed, ptc.PloneTestCase):

    def afterSetUp(self):
        # clear logs to avoid id collisions
        setup = self.portal.portal_setup
        setup.manage_delObjects(setup.objectIds())

    def beforeTearDown(self):
        # reset to default
        setAutoFlush(AUTO_FLUSH)

    def fileIds(self):
        catalog = self.portal.portal_catalog
        return [ brain.id for brain in catalog(portal_type='File') ]

    def create(self):
        self.failIf(self.folder.get('foo'), '"foo" exists?')
        self.folder.invokeFactory('File', id='foo', title='Foo')
        return self.fileIds()

    def remove(self):
        self.folder.manage_delObjects('foo')
        return self.fileIds()

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

