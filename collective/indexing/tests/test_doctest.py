from unittest import TestSuite
from zope.testing import doctest
from Testing import ZopeTestCase as ztc
from collective.indexing.tests.base import IndexingFunctionalTestCase

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite([
        ztc.FunctionalDocFileSuite(
           'browser.txt', package='collective.indexing.tests',
           test_class=IndexingFunctionalTestCase, optionflags=optionflags),
    ])

