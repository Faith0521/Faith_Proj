import os.path
from maya import cmds

from Qt.QtWidgets import QDialog
from Qt import QtCompat

from brigks import Guide
from brigks.gui.guideTreeWidget import GuideTreeWidget, GuideTreeWidgetItem, LayerTreeWidgetItem, SystemTreeWidgetItem, SubSystemTreeWidgetItem
from brigks.gui.guideSettingsWidget import GuideSettingsWidget
from brigks.gui.layerSettingsWidget import LayerSettingsWidget
from brigks.gui.systemSettingsWidget import SystemSettingsWidget

class MainWindow(QDialog):

	def __init__(self, guide, parent=None):
		super(MainWindow, self).__init__(parent)
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "mainWindow.ui")
		QtCompat.loadUi(uiPath, self)

		self._guide = guide
		self._settingsWidget = None
		self._lastItem = None
		self._guideSettingsWidget = GuideSettingsWidget(self._guide)
		self._layerSettingsWidget = LayerSettingsWidget(None)
		self._systemSettingsWidget = SystemSettingsWidget(None)

		self.uiGuideTREE = GuideTreeWidget()
		self.uiTreeWDG.layout().addWidget(self.uiGuideTREE)

		self.uiGuideTREE.itemSelectionChanged.connect(self.loadSettings)
		self.uiGuideTREE.setGuide(self._guide)

		self.loadSettings()

			
	def loadSettings(self):
		# Clear
		if self._settingsWidget:
			self.uiSettingsWDG.layout().removeWidget(self._settingsWidget)
			self._settingsWidget.setVisible(False)

		if self._guide is None:
			return

		items = self.uiGuideTREE.selectedItems()
		if not items or len(items)>1 or isinstance(items[0], GuideTreeWidgetItem):
			self._settingsWidget = self._guideSettingsWidget

		else:
			item = items[0]
			# Disconnect Signals
			try:
				if isinstance(self._lastItem, LayerTreeWidgetItem):
					self._layerSettingsWidget.layerRenamed.disconnect(self._lastItem.setLayerName)
				elif isinstance(self._lastItem, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
					self._systemSettingsWidget.systemChanged.disconnect(self._lastItem.setSystem)
					self._systemSettingsWidget.systemRenamed.disconnect(self._lastItem.setSystemName)
			except RuntimeError:
				pass

			# Set Item and Connect
			if isinstance(item, LayerTreeWidgetItem):
				self._layerSettingsWidget.setLayer(item.object())
				self._layerSettingsWidget.layerRenamed.connect(item.setLayerName)
				self._settingsWidget = self._layerSettingsWidget
			elif isinstance(item, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
				self._systemSettingsWidget.setSystem(item.object())
				self._systemSettingsWidget.systemChanged.connect(item.setSystem)
				self._systemSettingsWidget.systemRenamed.connect(item.setSystemName)
				self._settingsWidget = self._systemSettingsWidget

			self._lastItem = item

		self.uiSettingsWDG.layout().addWidget(self._settingsWidget)
		self._settingsWidget.setVisible(True)
