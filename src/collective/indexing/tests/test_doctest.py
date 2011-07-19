import doctest
from unittest import TestSuite

from plone.testing import layered

from collective.indexing.tests import layer

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite([
        layered(doctest.DocFileSuite('browser.txt',
            package='collective.indexing.tests', optionflags=optionflags),
            layer=layer.SUBSCRIBER_FUNCTIONAL),
        layered(doctest.DocFileSuite('moveonwftransition.txt',
            package='collective.indexing.tests', optionflags=optionflags),
            layer=layer.INDEXING_FUNCTIONAL),
        layered(doctest.DocFileSuite('change-notes.txt',
            package='collective.indexing.tests', optionflags=optionflags),
            layer=layer.INDEXING_FUNCTIONAL),
    ])
