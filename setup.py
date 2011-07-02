from setuptools import setup, find_packages

version = '1.9'

setup(name = 'collective.indexing',
      version = version,
      description = 'Abstract framework for queueing, optimizing and '
          'dispatching index operations for Plone content.',
      long_description = open("README.txt").read() + '\n' +
                         open('CHANGES.txt').read(),
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
      keywords = 'plone cmf zope indexing queueing catalog asynchronous',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://plone.org/products/collective.indexing',
      license = 'GPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['collective'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = [
        'setuptools',
        'zope.app.container',
      ],
      extras_require = { 'test': [
        'collective.testcaselayer',
      ]},
      entry_points = '''
        [z3c.autoinclude.plugin]
        target = plone
      ''',
)
