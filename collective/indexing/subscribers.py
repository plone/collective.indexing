from logging import getLogger
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from zope.app.container.contained import dispatchToSublocations
from collective.indexing.interfaces import IIndexing
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.queue import IndexQueue

logger = getLogger('collective.indexing.subscribers')


def getIndexer():
    """ look for and return an indexer """
    switch = queryUtility(IIndexQueueSwitch)
    if switch is not None:          # when switched on...
        return IndexQueue()         # return queue using indexer or...
    return queryUtility(IIndexing)  # directly return unqueued indexer...


def objectAdded(ev):
    obj = ev.object
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.index(obj)


def objectModified(ev):
    obj = ev.object
    indexer = getIndexer()
    if obj is None or indexer is None:
        return
    if ev.descriptions:     # not used by archetypes/plone atm...
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
    obj = ev.object
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.unindex(obj)


def objectMoved(ev):
    if ev.newParent is None or ev.oldParent is None:
        # it's an IObjectRemovedEvent or IObjectAddedEvent
        return
    if ev.newParent is ev.oldParent:
        # it's a renaming operation
        dispatchToSublocations(ev.object, ev)
    obj = ev.object
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.reindex(obj)


def dispatchObjectMovedEvent(ob, ev):
    """ dispatch events to sub-items when a folderish item has been renamed """
    if ob is not ev.object:
        if ev.oldParent is ev.newParent:
            notify(ObjectModifiedEvent(ob))


def objectTransitioned(ev):
    obj = ev.object
    indexer = getIndexer()
    if obj is not None and indexer is not None:
        indexer.reindex(obj)

