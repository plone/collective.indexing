from zope.component import adapts, queryUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm

from collective.indexing.interfaces import IIndexingSchema, _
from collective.indexing.interfaces import IIndexingConfig


class IndexingControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IIndexingSchema)

    def getActive(self):
        util = queryUtility(IIndexingConfig)
        return getattr(util, 'active', False)

    def setActive(self, value):
        util = queryUtility(IIndexingConfig)
        if util is not None:
            util.active = value

    active = property(getActive, setActive)

    def getAutoFlush(self):
        util = queryUtility(IIndexingConfig)
        return getattr(util, 'auto_flush', False)

    def setAutoFlush(self, value):
        util = queryUtility(IIndexingConfig)
        if util is not None:
            util.auto_flush = value

    auto_flush = property(getAutoFlush, setAutoFlush)


class IndexingControlPanel(ControlPanelForm):

    form_fields = FormFields(IIndexingSchema)

    label = _('Indexing settings')
    description = _('Settings to enable and configure queued indexing.')
    form_name = _('Indexing settings')
