from zope.component import queryUtility
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase

from collective.indexing.interfaces import IIndexingConfig


class ConfigXMLAdapter(XMLAdapterBase):

    _LOGGER_ID = 'collective.indexing'

    def _exportNode(self):
        """ export the object as a DOM node """
        node = self._extractProperties()
        self._logger.info('settings exported.')
        return node

    def _importNode(self, node):
        """ import the object from the DOM node """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info('settings imported.')

    def _purgeProperties(self):
        self.context.active = False
        self.context.auto_flush = False

    def _initProperties(self, node):
        elems = node.getElementsByTagName('settings')
        if elems:
            assert len(elems) == 1
            settings = elems[0]
            for child in settings.childNodes:
                if child.nodeName == 'active':
                    value = str(child.getAttribute('value'))
                    self.context.active = self._convertToBoolean(value)
                elif child.nodeName == 'auto-flush':
                    value = str(child.getAttribute('value'))
                    self.context.auto_flush = self._convertToBoolean(value)

    def _createNode(self, name, value):
        node = self._doc.createElement(name)
        node.setAttribute('value', value)
        return node

    def _extractProperties(self):
        node = self._doc.createElement('object')
        node.setAttribute('name', 'indexing')
        settings = self._doc.createElement('settings')
        create = self._createNode
        node.appendChild(settings)
        append = settings.appendChild
        append(create('active', str(bool(self.context.active))))
        append(create('auto-flush', str(bool(self.context.auto_flush))))
        return node


def importSettings(context):
    """ import settings from an XML file """
    site = context.getSite()
    utility = queryUtility(IIndexingConfig, context=site)
    if utility is None:
        logger = context.getLogger('collective.indexing')
        logger.info('Nothing to import.')
        return
    importObjects(utility, '', context)


def exportSettings(context):
    """ export settings as an XML file """
    site = context.getSite()
    utility = queryUtility(IIndexingConfig, context=site)
    if utility is None:
        logger = context.getLogger('collective.indexing')
        logger.info('Nothing to export.')
        return
    exportObjects(utility, '', context)
