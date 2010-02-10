from logging import getLogger
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from zope.app.container.contained import dispatchToSublocations
from Acquisition import aq_parent, aq_inner, aq_base
from collective.indexing.utils import getIndexer

debug = getLogger('collective.indexing.subscribers').debug


def filterTemporaryItems(obj, checkId=True):
    """ check if the item has an acquisition chain set up and is not of
        temporary nature, i.e. still handled by the `portal_factory`;  if
        so return it, else return None """
    parent = aq_parent(aq_inner(obj))
    if parent is None:
        return None
    if checkId and getattr(obj, 'getId', None):
        if getattr(aq_base(parent), obj.getId(), None) is None:
            return None
    isTemporary = getattr(obj, 'isTemporary', None)
    if isTemporary is not None:
        try:
            if obj.isTemporary():
                return None
        except TypeError:
            return None # `isTemporary` on the `FactoryTool` expects 2 args
    return obj


def objectAdded(ev):
    obj = filterTemporaryItems(ev.object)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        debug('object added event for %r, indexing using %r', obj, indexer)
        indexer.index(obj)


def objectModified(ev):
    obj = filterTemporaryItems(ev.object)
    indexer = getIndexer()
    if obj is None or indexer is None:
        return
    debug('object modified event for %r, reindexing using %r', obj, indexer)
    if getattr(ev, 'descriptions', None):   # not used by archetypes/plone atm
        # build the list of to be updated attributes
        attrs = []
        for desc in ev.descriptions:
            if isinstance(desc, Attributes):
                attrs.extend(desc.attributes)
        indexer.reindex(obj, attrs)
        if 'allow' in attrs:    # dispatch to sublocations on security changes
            dispatchToSublocations(ev.object, ev)
    else:
        # with no descriptions (of changed attributes) just reindex all
        indexer.reindex(obj)


def objectCopied(ev):
    objectAdded(ev)


def objectRemoved(ev):
    obj = filterTemporaryItems(ev.object, checkId=False)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        debug('object removed event for %r, unindexing using %r', obj, indexer)
        indexer.unindex(obj)


def objectMoved(ev):
    if ev.newParent is None or ev.oldParent is None:
        # it's an IObjectRemovedEvent or IObjectAddedEvent
        return
    if ev.newParent is ev.oldParent:
        # it's a renaming operation
        dispatchToSublocations(ev.object, ev)
    obj = filterTemporaryItems(ev.object)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        debug('object moved event for %r, indexing using %r', obj, indexer)
        indexer.index(obj)


def dispatchObjectMovedEvent(ob, ev):
    """ dispatch events to sub-items when a folderish item has been renamed """
    if ob is not ev.object:
        if ev.oldParent is ev.newParent:
            notify(ObjectModifiedEvent(ob))


def objectTransitioned(ev):
    obj = filterTemporaryItems(ev.object)
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        debug('object transitioned event for %r, reindexing using %r', obj, indexer)
        indexer.reindex(obj)
