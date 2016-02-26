Introduction
============

`collective.indexing`_ is an approach to provide an abstract framework for
queuing and optimizing index operations in `Plone`_ as well as dispatching
them to various backends. The default implementation aims to replace the
standard indexing mechanism of `CMF`_ to allow index operations to be handled
asynchronously in a backwards-compatible way.

Queuing these operations on a transaction level allows to get rid of redundant
indexing of objects and thereby providing a substantial performance
improvement.  By leveraging the component architecture and Zope event system
`collective.indexing`_ also makes it much easier to use backends other
than or in addition to the standard portal catalog for indexing, such as
dedicated search engine solutions like `Solr`_, `Xapian`_ or `Google Search
Appliance`_.  One backend implementation designed to be used with this package
has already been started in the form of `collective.solr`_.

  .. _`collective.indexing`: https://github.com/plone/collective.indexing
  .. _`Plone`: http://www.plone.org/
  .. _`CMF`: http://www.zope.org/Products/CMF/
  .. _`Solr`: http://lucene.apache.org/solr/
  .. _`Xapian`: http://www.xapian.org/
  .. _`Google Search Appliance`: http://www.google.com/enterprise/gsa/
  .. _`collective.solr`: https://github.com/collective/collective.solr


Current Status
==============

The implementation is considered to be ready for production. It can be
installed in a Plone 4.x site to enable indexing operations to be queued,
optimized and dispatched to the standard portal catalog on the Zope
transaction boundary thereby improving the Plone's out-of-the-box
performance_.

  .. _performance: http://www.jarn.com/blog/plone-indexing-performance

At the moment the package requires several "monkey patches", to the mixin
classes currently used to hook up indexing, i.e. ``CMFCatalogAware``
and ``CatalogMultiplex``, the portal catalog as well as to helper methods in
`Plone`_ itself. It is planned to clear these up by making the classes
"pluggable" via adapterization, allowing `collective.indexing`_ to hook in in
clean ways.

In conjunction with `collective.solr`_ the package also provides a
working solution for integration of `Solr`_ with `Plone`_.  Based on a schema
`configurable`__ at `zc.buildout`_ level indexing operations can be dispatched
a `Solr`_ instance in addition or alternatively to the standard catalog.  This
allows for minimal and very efficient indexing of standard `Plone`_ content
items based on Archetypes. Providing support for other content types is
rather trivial and will be support soon.

  .. __: http://pypi.python.org/pypi/collective.recipe.solrinstance/
  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout

The code was written with emphasis on minimalism, clarity and maintainability.
It comes with extensive tests covering the code base at more than 95%. The
package is currently in use in several production sites and considered stable.

For outstanding issues and features remaining to be implemented please see the
`issue tracker`__.

  .. __: https://github.com/plone/collective.indexing/issues


Subscriber Support
------------------

The package comes with support for queueing up and performing indexing
operations via event subscribers.  The idea behind this is to not rely on
explicit calls as defined in ``CMFCatalogAware`` alone, but instead make it
possible to phase them out eventually. As the additional indexing operations
added via the subscribers are optimized away anyway, this only adds very
little processing overhead.

However, even though ``IObjectModifiedEvent`` has support for partial
reindexing by passing a list of descriptions/index names, this is currently
not used anywhere in Plone. Unfortunately that means that partial reindex
operations will be "upgraded" to full reindexes, e.g. for
``IContainerModifiedEvent`` via the ``notifyContainerModified`` helper,
which is one reason why subscriber support is not enabled by default for now.

To activate please use::

    [instance]
    ...
    zcml = collective.indexing:subscribers.zcml

instead of just the package name itself, re-run buildout and restart your
Plone instance.


FAQs / Troubleshooting
======================

The following tries to address some of the known issues.  Please also make
sure to check the package's `issue tracker`__ and use it to report new bugs
and/or discuss possible enhancements.  Alternatively, feedback via the
`"Plone Developers" mailing-list`__ is also most welcome.

  .. __: https://github.com/plone/collective.indexing/issues
  .. __: mailto:plone-developers@lists.sourceforge.net


**"OFS.Uninstalled Could not import class '...' from module '...'" Warnings**

Symptom
  When loading your Plone site after a Zope restart, i.e. when browsing it,
  you're seeing warnings like::

    WARNING OFS.Uninstalled Could not import class 'PortalCatalogQueueProcessor' from module 'collective.indexing.indexer'
    WARNING OFS.Uninstalled Could not import class 'IndexQueueSwitch' from module 'collective.indexing.queue'
Problem
  Early versions of the package used persistent local utilities, which are
  still present in your ZODB.  These utilities have meanwhile been replaced
  and the old instances aren't needed anymore.
Solution
  Please simply re-install the package via Plone's control panel or the
  quick-installer.  Alternatively you can also use the ZMI "Components" tab
  on your site root object, typically located at
  http://localhost:8080/plone/manage_components, to remove the broken
  utilities from the XML.  Search for "broken".


Credits
=======

This code was inspired by enfold.indexing and enfold.solr by `Enfold
Systems`_ as well as `work done at the snowsprint'08`__.  The
``TransactionManager`` pattern is taken from enfold.solr.  Development was
kindly sponsored by `Elkjop`_.

  .. _`Enfold Systems`: http://www.enfoldsystems.com/
  .. __: http://tarekziade.wordpress.com/2008/01/20/snow-sprint-report-1-indexing/
  .. _`Elkjop`: http://www.elkjop.no/

