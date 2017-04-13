import warnings

warnings.warn(
    '2.0 was the last release of collective.indexing. '
    'Starting with Plone 5.1.0 its code has already merged in. '
    'For more information and upgrade information, see its PLIP: '
    'https://github.com/plone/Products.CMFPlone/issues/1343',
    DeprecationWarning,
)

def initialize(context):
    # apply the monkey patches...
    from collective.indexing import monkey
    monkey  # make pyflakes happy...
