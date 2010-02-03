collective.indexing
===================

Introduction
------------

`collective.indexing`_ is an approach to provide an abstract framework for
queuing and optimizing index operations in `Plone`_ as well as dispatching
them to various backends.  The default implementation aims to replace the
standard indexing mechanism of `CMF`_ to allow index operations to be handled
asynchronously in a backwards-compatible way.

Queuing these operations on a transaction level allows to get rid of redundant
indexing of objects and thereby providing a substantial performance
improvement.  By leveraging the component architecture and event system of
`zope3` `collective.indexing`_ also makes it much easier to use backends other
than or in addition to the standard portal catalog for indexing, such as
dedicated search engine solutions like `Solr`_, `Xapian`_ or `Google Search
Appliance`_.  One backend implementation designed to be used with this package
has already been started in the form of `collective.solr`_.

If you are using `CacheSetup`_ make sure that you have `CMFSquidTool`_ 1.5 or
later: older versions do not handle purge requests being generated during
transaction commit and will produce internal errors.

  .. _`collective.indexing`: http://plone.org/products/collective.indexing/
  .. _`Plone`: http://www.plone.org/
  .. _`CMF`: http://www.zope.org/Products/CMF/
  .. _`zope3`: http://wiki.zope.org/zope3/Zope3Wiki
  .. _`Solr`: http://lucene.apache.org/solr/
  .. _`Xapian`: http://www.xapian.org/
  .. _`Google Search Appliance`: http://www.google.com/enterprise/gsa/
  .. _`collective.solr`: http://plone.org/products/collective.solr/
  .. _`CacheSetup`: http://pypi.python.org/pypi/Products.CacheSetup/
  .. _`CMFSquidTool`: http://pypi.python.org/pypi/Products.CMFSquidTool/


Current Status
--------------

The implementation is considered to be ready for production.  The package can
be installed in a Plone 3.x site to enable indexing operations to be queued,
optimized and dispatched to the standard portal catalog on the zope
transaction boundary thereby improving the Plone's out-of-the-box
performance_.  A sample buildout_ is provided for your convenience.

  .. _performance: http://www.jarn.com/blog/plone-indexing-performance
  .. _buildout: http://svn.plone.org/svn/collective/collective.indexing/trunk/buildout.cfg

At the moment the package requires several "monkey patches", to the mixin classes
currently used to hook up indexing, i.e. ``CMFCatalogAware`` (from `CMF`_)
and ``CatalogMultiplex`` (from `Archetypes`_), the portal catalog as well as
to helper methods in `Plone`_ itself. It is planned to clear these up by
making the classes "pluggable" via adapterization, allowing
`collective.indexing`_ to hook in in clean ways. At least two `PLIPs`_ will be
proposed for inclusion into `Plone`_ 3.4.

  .. _`Archetypes`: http://plone.org/products/archetypes
  .. _`PLIPs`: http://plone.org/documentation/glossary/plip

In conjunction with `collective.solr`_ the package also provides a
working solution for integration of `Solr`_ with `Plone`_.  Based on a schema
`configurable`__ at `zc.buildout`_ level indexing operations can be dispatched
a `Solr`_ instance in addition or alternatively to the standard catalog.  This
allows for minimal and very efficient indexing of standard `Plone`_ content
items based on `Archetypes`_.  Providing support for other content types is
rather trivial and will be support soon.

  .. __: http://pypi.python.org/pypi/collective.recipe.solrinstance/
  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout

The code was written with emphasis on minimalism, clarity and maintainability.
It comes with extensive tests covering the code base at more than 95%. The
package is currently in use in several production sites and considered stable.

For outstanding issues and features remaining to be implemented please see the
`to-do list`__ included in the package as well as it's `issue tracker`__.

  .. __: http://svn.plone.org/svn/collective/collective.indexing/trunk/TODO.txt
  .. __: http://plone.org/products/collective.indexing/issues


Installation
------------

The easiest way to use this package is when working with installations
based on `zc.buildout`_.  Here you can simply add the package to your "eggs"
and "zcml" options, run buildout and restart your `Zope`_/`Plone`_ instance.

  .. _`Zope`: http://www.zope.org/

Alternatively you can use the following configuration file to extend your
existing buildout::

  [buildout]
  extends = buildout.cfg

  [instance]
  eggs += collective.indexing
  zcml += collective.indexing

After that and quick-installing the package the "Indexing" control panel
should show up, allowing to switch optimized indexing support as well as
processing of the indexing queue on catalog searches, a.k.a. auto-flushing,
on and off.


Subscriber Support
------------------

The package comes with support for queueing up and performing indexing
operations via event subscribers.  The idea behind this is to not rely on
explicit calls as defined in ``CMFCatalogAware`` alone, but instead make it
possible to phase them out eventually.  As the additional indexing operations
added via the subscribers are optimized away anyway, this only adds very
little processing overhead.

However, even though ``IObjectModifiedEvent`` has support for partial
reindexing by passing a list of descriptions/index names, this is currently
not used anywhere in `Archetypes`_ and/or `Plone`_.  Unfortunately that means
that partial reindex operations will be "upgraded" to full reindexes, e.g.
for ``IContainerModifiedEvent`` via the ``notifyContainerModified`` helper,
which is one reason why subscriber support is not enabled by default for now.

To activate please use::

    [instance]
    ...
    zcml = collective.indexing:subscribers.zcml

instead of just the package name itself, re-run buildout and restart your
`Zope`_/`Plone`_ instance.


FAQs / Troubleshooting
----------------------

The following tries to address some of the known issues.  Please also make
sure to check the package's `issue tracker`__ and use it to report new bugs
and/or discuss possible enhancements.  Alternatively, feedback via the
`"Plone Developers" mailing-list`__ or `direct mail`__ is also most welcome.

  .. __: http://plone.org/products/collective.indexing/issues
  .. __: mailto:plone-developers@lists.sourceforge.net
  .. __: mailto:witsch@plone.org


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
-------

This code was inspired by `enfold.indexing`_ and `enfold.solr`_ by `Enfold
Systems`_ as well as `work done at the snowsprint'08`__.  The
``TransactionManager`` pattern is taken from `enfold.solr`_.  Development was
kindly sponsored by `Elkjop`_.

  .. _`enfold.indexing`: https://svn.enfoldsystems.com/browse/public/enfold.solr/branches/snowsprint08-buildout/enfold.indexing/
  .. _`enfold.solr`: https://svn.enfoldsystems.com/browse/public/enfold.solr/branches/snowsprint08-buildout/enfold.solr/
  .. _`Enfold Systems`: http://www.enfoldsystems.com/
  .. __: http://tarekziade.wordpress.com/2008/01/20/snow-sprint-report-1-indexing/
  .. _`Elkjop`: http://www.elkjop.no/

