import doctest
from unittest import TestSuite

from Testing import ZopeTestCase as ztc

from collective.indexing.tests.base import IndexingFunctionalTestCase
from collective.indexing.tests.base import SubscriberFunctionalTestCase

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite([
        ztc.FunctionalDocFileSuite(
           'browser.txt', package='collective.indexing.tests',
           test_class=SubscriberFunctionalTestCase, optionflags=optionflags),
        ztc.FunctionalDocFileSuite(
           'moveonwftransition.txt', package='collective.indexing.tests',
           test_class=IndexingFunctionalTestCase, optionflags=optionflags),
        ztc.FunctionalDocFileSuite(
           'move-in-subscriber.txt', package='collective.indexing.tests',
           test_class=IndexingFunctionalTestCase, optionflags=optionflags),
        ztc.FunctionalDocFileSuite(
           'change-notes.txt', package='collective.indexing.tests',
           test_class=IndexingFunctionalTestCase, optionflags=optionflags),
    ])
