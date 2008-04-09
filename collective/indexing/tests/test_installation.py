from unittest import TestSuite, makeSuite, main
from Products.PloneTestCase import PloneTestCase as ptc

ptc.setupPloneSite()


# test-specific imports go here...
from transaction import commit
from collective.indexing.utils import isActive


class InstallationTests(ptc.PloneTestCase):

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
        ptc.installPackage('collective.indexing')
        self.failIf(isActive())
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])
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
        self.portal.portal_quickinstaller.uninstallProducts(('collective.indexing',))
        commit()


def test_suite():
    return TestSuite([
        makeSuite(InstallationTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')

