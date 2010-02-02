from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from Products.ATContentTypes.content.base import ATCTContent, registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema


class Foo(ATCTContent):
    """ sample content type for testing purposes """

    schema = ATContentTypeSchema.copy()
    portal_type = 'Foo'
    index_counter = 0

    def indexObject(self):
        """ overridden index method calling its super variant """
        super(Foo, self).indexObject()
        self.index_counter += 1
        assert self.index_counter < 42, 'indexing loop detected, see ' \
            'http://plone.org/products/collective.indexing/issues/3'


registerATCT(Foo, 'collective.indexing.tests')


def addFoo(container, id, **kwargs):
    """ at-constructor copied from ClassGen.py """
    obj = Foo(id)
    notify(ObjectCreatedEvent(obj))
    container._setObject(id, obj)
    obj = container._getOb(id)
    obj.initializeArchetype(**kwargs)
    notify(ObjectModifiedEvent(obj))
    return obj
