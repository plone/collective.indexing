from setuptools import setup, find_packages
from os.path import join

version = open(join('src', 'collective', 'indexing', 'version.txt')).read()
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'collective.indexing',
      version = version,
      description = 'Abstract framework for queueing, optimizing and dispatching index operations for portal content.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'plone cmf zope indexing queueing catalog asynchronous',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://plone.org/products/collective.indexing',
      download_url = 'http://cheeseshop.python.org/pypi/collective.indexing/',
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
