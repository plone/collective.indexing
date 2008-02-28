from logging import getLogger
from zope.component import queryUtility
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent, Attributes
from zope.app.container.contained import dispatchToSublocations
from Products.Archetypes.utils import shasattr
from collective.indexing.interfaces import IIndexing

logger = getLogger('collective.indexing.subscribers')


def getObjectUID(obj, subscriber_name):
    if not shasattr(obj, 'UID'):
        logger.debug('%s - object has no UID: %r', (subscriber_name, obj))
        return None
    uid = obj.UID()
    if not uid:
        logger.debug('%s - object has UID: %r', (subscriber_name, obj))
        return None
    return uid


def objectAdded(ev):
    uid = getObjectUID(ev.object, 'objectAdded')
    indexer = queryUtility(IIndexing, default=None)
    if uid is not None and indexer is not None:
        indexer.index(uid)


def objectModified(ev):
    uid = getObjectUID(ev.object, 'objectModified')
    indexer = queryUtility(IIndexing, default=None)
    if uid is None or indexer is None:
        return
    if ev.descriptions:     # not used by archetypes/plone atm...
        # build the list of to be updated attributes
        attrs = []
        for desc in ev.descriptions:
            if isinstance(desc, Attributes):
                attrs.extend(desc.attributes)
        indexer.reindex(uid, attrs)
        if 'allow' in attrs:    # dispatch to sublocations on security changes
            dispatchToSublocations(ev.object, ev)
    else:
        # with no descriptions (of changed attributes) just reindex all
        indexer.reindex(uid)


def objectCopied(ev):
    objectAdded(ev)


def objectRemoved(ev):
    uid = getObjectUID(ev.object, 'objectRemoved')
    indexer = queryUtility(IIndexing, default=None)
    if uid is not None and indexer is not None:
        indexer.unindex(uid)


def objectMoved(ev):
    if ev.newParent is None or ev.oldParent is None:
        # it's an IObjectRemovedEvent or IObjectAddedEvent
        return
    if ev.newParent is ev.oldParent:
        # it's a renaming operation
        dispatchToSublocations(ev.object, ev)
    uid = getObjectUID(ev.object, 'objectMoved')
    indexer = queryUtility(IIndexing, default=None)
    if uid is not None and indexer is not None:
        indexer.reindex(uid)


def dispatchObjectMovedEvent(ob, ev):
    """ dispatch events to sub-items when a folderish item has been renamed """
    if ob is not ev.object:
        if ev.oldParent is ev.newParent:
            notify(ObjectModifiedEvent(ob))


def objectTransitioned(ev):
    uid = getObjectUID(ev.object, 'objectTransitioned')
    indexer = queryUtility(IIndexing, default=None)
    if uid is not None and indexer is not None:
        indexer.reindex(uid)

