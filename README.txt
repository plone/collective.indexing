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

  .. _`collective.indexing`: http://dev.plone.org/collective/browser/collective.indexing/
  .. _`Plone`: http://www.plone.org/
  .. _`CMF`: http://www.zope.org/Products/CMF/
  .. _`zope3`: http://wiki.zope.org/zope3/Zope3Wiki
  .. _`Solr`: http://lucene.apache.org/solr/
  .. _`Xapian`: http://www.xapian.org/
  .. _`Google Search Appliance`: http://www.google.com/enterprise/gsa/
  .. _`collective.solr`: http://dev.plone.org/collective/log/collective.solr/


.. Motivation
.. ----------
.. 
.. to be written...


Current Status
--------------

In conjunction with `collective.solr`_ the package currently provides a
working solution for integration of `Solr`_ with `Plone`_.  Based on a schema
`configurable`__ at `buildout`_ level indexing operations are queued,
optimized and dispatched to a `Solr`_ instance on the zope transaction
boundary.  This allows for minimal and very efficient indexing of standard
`Plone`_ content items based on `Archetypes`_.  Providing support for other
content types is rather trivial and will be support soon.

  .. __: http://svn.plone.org/svn/collective/buildout/collective.recipe.solrinstance/trunk/README.txt
  .. _`buildout`: http://pypi.python.org/pypi/zc.buildout
  .. _`Archetypes`: http://plone.org/products/archetypes

Other current plans are to support the default plone catalog as a backend to
allow `collective.indexing`_ to become a worthwhile add-on package for current
versions of `Plone`_, effectively speeding up write operations on hopefully
any given `Plone`_ site.  In addition, changes to the ``CMFCatalogAware``
(from `CMF`_) and ``CatalogMultiplex`` (from `Archetypes`_) mixin classes are
planned, making them "pluggable" by use of adapters.  That way these classes
will provide means for `collective.indexing` to hook in in clean ways.  The
changes will at first be provided by a "monkey patch", but later on proposed
as a `PLIP`_ for inclusion into `Plone`_ 3.2.

  .. _`PLIP`: http://plone.org/documentation/glossary/plip

For outstanding issues and features remaining to be implemented please see the
`to-do list`__ included in the package.

  .. __: http://dev.plone.org/collective/browser/collective.indexing/trunk/TODO.txt


Credits
-------

This code is inspired by `enfold.indexing`_ and `enfold.solr`_ by `Enfold
Systems`_ as well as `work done at the snowsprint'08`__.  The
``TransactionManager`` pattern is taken from `enfold.solr`_.  Development was
kindly sponsored by `Elkjøp`_.

  .. _`enfold.indexing`: https://svn.enfoldsystems.com/browse/public/enfold.solr/branches/snowsprint08-buildout/enfold.indexing/
  .. _`enfold.solr`: https://svn.enfoldsystems.com/browse/public/enfold.solr/branches/snowsprint08-buildout/enfold.solr/
  .. _`Enfold Systems`: http://www.enfoldsystems.com/
  .. __: http://tarekziade.wordpress.com/2008/01/20/snow-sprint-report-1-indexing/
  .. _`Elkjøp`: http://www.elkjop.no/

