Changelog
=========

2.1 (unreleased)
----------------

- reindexObjectSecurirty operations are handled by the queue (#14)
  [ale-rt]
- Test the package against Plone 4.3
  [ale-rt]

2.0 (2017-04-13)
----------------

- Add a method to remove the monkey patches.
  [gforcada]

- End Of Life: starting with Plone 5.1.0 release collective.indexing has been merged into Plone core.
  The functionality provided by it is already available
  [gforcada]


2.0b1 - 2013-02-16
------------------

- Compensate for changes in ZCML configuration ordering
  [rockfruit]


2.0a3 - 2011-08-22
------------------

- Added back `IIndexQueueSwitch` marker interface for better uninstall support
  for 1.x versions. Fixes https://github.com/Jarn/collective.indexing/issues/2.
  [hannosch, dholth]

2.0a2 - 2011-07-19
------------------

- Use `plone.app.testing` instead of `c.testcaselayer`.
  [hannosch]

- Use getSiteManager to look for all IIndexQueueProcessor's to capture the ones
  registered in local site managers.
  [hannosch]

2.0a1 - 2011-07-09
------------------

**Upgrade note**: This version requires Plone 4.1 but no longer requires any
persistent configuration or does it have any UI. Please deactivate the add-on
in the add-ons control panel. The functionality will be present as long as the
package is available on the Python path.

- Use `dispatchToSublocations` from zope.container.
  [hannosch]

- Optimize the queue before calling `begin` on index processors, thus avoiding
  the extra setup cost if the queue is optimized to contain no items.
  [hannosch]

- Removed `reindexOnReorder` patch, which isn't required anymore in Plone 4.
  [hannosch]

- Removed the conditional auto_flush feature and instead always enable it.
  [hannosch]

- Merged `QueueReducer` into the `queue.optimize` method.
  [hannosch]

- Remove the `utils.getIndexer` indirection.
  [hannosch]

- Remove `utils.isActive` - when installed we are always active.
  [hannosch]

- Remove Plone 3 backwards compatibility code. This version requires Plone 4.
  [hannosch]

- Remove GenericSetup profile, Plone control panel and move configuration to
  global utility.
  [hannosch]

- Add uninstall profile.
  [kiorky]


1.8 - Released July 20th, 2010
------------------------------

* Moved patching log calls to debug level.
  [hannosch]

* Fix broken pickling caused by the lambda introduced by the fix for
  http://plone.org/products/collective.indexing/issues/11
  [gotcha]

* Add danish translations for control panel strings.
  [stonor]


1.7 - Released April 16th, 2010
-------------------------------

* Prevent multiple updates of an object's modification date on full reindex.
  This fixes http://plone.org/products/collective.indexing/issues/11
  [witsch]

* Ensure that errors during queue processing won't leave behind the queue in
  the module global processing set, thereby preventing any further indexing.
  [hannosch]

* Change the dependency on Archetypes into a soft one.
  [witsch]

* Also monkey-patch Archetypes' `BaseBTreeFolder`, which keeps references
  to the methods from `CMFCatalogAware` as it is usually initialized before
  the patched methods are in place.
  [witsch]

* Adjust test to the changes related to PLIP 4379.
  [witsch]

* Add helper method to determine if a given object has its own copy of a
  given indexing method, e.g. `reindexObject`.
  [witsch]


1.6 - Released March 6th, 2010
------------------------------

* Clean up and split out test-only dependencies.
  [witsch]


1.5 - Released March 4th, 2010
------------------------------

* Immediately update an object's modification date on full reindex.
  This fixes http://plone.org/products/collective.indexing/issues/4
  [do3cc, witsch]

* Add "z3c.autoinclude.plugin" entry point, so in Plone 3.3+ you can avoid
  loading the ZCML file.
  [hannosch]


1.4 - Released February 11th, 2010
----------------------------------

* Ensure indexing for "lifecycle" operations works in (nearly) the same
  way with and without event subscribers.
  [witsch]


1.3 - Released February 2nd, 2010
---------------------------------

* Don't activate event subscriber support by default as it can have
  performance implications.
  [witsch]

* Make the wrapper used for unindexing return the correct acquisition parent.
  This fixes http://plone.org/products/collective.indexing/issues/6 as well
  as http://dev.plone.org/plone/ticket/10088
  [witsch]


1.2 - Released January 23rd, 2010
---------------------------------

* Improve logging of auto-flushes for easier performance tuning.
  [witsch]

* Add support for Zope 2.12.
  [wichert]

* Made all but one test work on both Plone 3 and 4 by relying on fewer internal
  details of the functions under test.
  [hannosch]

* Adjusted tests to set a site explicitly in the layer.
  [hannosch]

* Changed zope.app.event imports to zope.lifecycleevent. The former was
  deprecated since Zope 2.10.
  [hannosch]

* Fix event subscriber for `IObjectModified` events without a description.
  [gweis]


1.1 - Released June 9th, 2009
-----------------------------

* Patch `CatalogTool.getCounter` to process the indexing queue before
  returning the counter indicating catalog changes (aka auto-flush).
  [witsch]


1.0 - Released May 8th, 2009
----------------------------

* Register import and export steps using ZCML.
  [witsch]


1.0rc5 - Released April 20th, 2009
----------------------------------

* Add support for GenericSetup.
  [witsch]

* Add configlet to allow TTW activation and configuration.
  [witsch]

* Update code to (almost) comply to PEP8 style guide lines.
  [witsch]

* Added logging to monkey patches.
  [swampmonkey]


1.0rc4 - Released December 8th, 2008
------------------------------------

* Provide a workaround for an issue with indexing objects using stale
  acquisition chains after moving them in an event subscriber.
  [witsch]

* Optimize "auto flushing" to prevent unnecessary component lookups.
  [witsch]


1.0rc3 - Released November 19th, 2008
-------------------------------------

* Also patch `unrestrictedSearchResults` to flush queued indexing
  operations before querying the catalog.  This fixes
  http://plone.org/products/collective.indexing/issues/2
  [mr_savage]


1.0rc2 - Released November 17th, 2008
-------------------------------------

* Fix issue where, when the "auto flush" feature is enabled, an indexing
  helper could cause an infinite loop by using the catalog.
  [witsch]

* Restore and extend test regarding package installation.
  [witsch]


1.0rc1 - Released November 5th, 2008
------------------------------------

* Restored processQueue function as it is conceptually important.
  [stefan]


1.0b5 - Released October 16th, 2008
-----------------------------------

* Fix transaction handling to properly abort indexing operations.
  [witsch]

* Refactor helper method for auto-flushing the queue to make it more easily
  re-usable.
  [witsch]

* Enable the monkey patch for `PloneTool.reindexOnReorder` in all versions
  of Plone 3.x as it's not been ported upstream yet.  This fixes
  http://plone.org/products/collective.indexing/issues/1
  [witsch]

* Refactor auto-flush monkey-patch to not interfere with testing.
  [witsch]

* Patched CatalogTool.searchResults to process the indexing queue before
  issuing a query (aka auto-flush).
  [stefan]

* Fix test isolation issues and improve test setup.
  [witsch]

* Made sure QueueReducer sorts results by opcode. Unindex operations must
  be handled before (re)index operations.
  [stefan]

* Added processQueue function to process a queue immediately.
  [stefan]

* Fixed testModifyObject in Plone 3.1 by clearing the file's creation flag
  in afterSetUp.
  [stefan]

* Fixed testQueuesOnTwoThreads on Linux by sleeping for a moment so threads
  can do their work.
  [stefan]


1.0b4 - Released June 30th, 2008
--------------------------------

* Perform processing of the queue during "active" state of the transaction
  as additional changes are forbidden in "committing" state.  Those changes
  can for example be caused by indexes writing back data to content items,
  such as the modification time.
  [witsch, mj]


1.0b3 - Released June 18th, 2008
--------------------------------

* Fix an issue where objects providing their own `__setattr__` could
  potentially not be deleted.
  [witsch]


1.0b2 - Released June 2nd, 2008
-------------------------------

* Add `aq_inner` to prevent infinite recursion with `safe_hasattr`.
  [witsch]


1.0b1 - Released May 28, 2008
-----------------------------

* Make sure we get REQUEST correctly in PathWrapper.
  [tesdal]


1.0a3 - Released May 28, 2008
-----------------------------

* Respect overridden indexing methods to prevent erroneous indexing and
  generally allow special handling.
  [witsch]

* Fix leftover index entry after renaming an object.
  [witsch]

* The bad monkey smacked back with a vengeance, but was finally tamed.
  [witsch]

* Smacked a bad monkey that was checking for nonexisting attribute
  getObjPositionInParent.
  [tesdal]


1.0a2 - Released May 25, 2008
-----------------------------

* Fix bug regarding different types in the queue reducer logic.
  [fschulze]

* Fixed renaming of content items by replacing `PloneTool.reindexOnReorder`
  with a saner version that doesn't rely on the catalog.
  [witsch]

* Various fixes, cleanups and optimizations.
  [witsch]

* Fixed monkey patches so that normal indexing remains functional when queued
  indexing has been deactivated (or the GS profile had not been applied yet).
  [witsch]


1.0a1 - Released March 31, 2008
-------------------------------

* Initial release
  [tesdal, witsch]
