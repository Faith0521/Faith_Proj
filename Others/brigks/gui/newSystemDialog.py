import os.path

from Qt.QtWidgets import QDialog
from Qt import QtCompat

from brigks.systems import getSystemList, getSystemListByCategory

class NewSystemDialog(QDialog):

	def __init__(self, parent, guide, defaultLayer=None):
		super(NewSystemDialog, self).__init__(parent)
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "newSystemDialog.ui")
		QtCompat.loadUi(uiPath, self)

		self._guide = guide
		self._defaultLayer = defaultLayer
		self._layers = []
		self._systemsByCategory = {}
		self.loadLayers()

		self.uiSystemTypeLIST.itemDoubleClicked.connect(self.accept)

		self.uiCategoryCBOX.currentIndexChanged.connect(self.setSystemList)

	def loadLayers(self):
		layers = self._guide.getLayersDepths()
		
		self.uiLayerCBOX.clear()
		default = 0
		for depth, layer in layers:
			self.uiLayerCBOX.addItem("    "*depth+layer.name())
			self._layers.append(layer)
		if self._defaultLayer in self._layers:
			self.uiLayerCBOX.setCurrentIndex(self._layers.index(self._defaultLayer))

		self._systemsByCategory = getSystemListByCategory()
		categories = sorted(self._systemsByCategory.keys())
		self.uiCategoryCBOX.clear()
		self.uiCategoryCBOX.addItems(categories)
		self.uiCategoryCBOX.setCurrentIndex(categories.index("ALL"))

		self.setSystemList()

	def setSystemList(self):
		category = self.uiCategoryCBOX.currentText()
		systems = sorted(self._systemsByCategory[category])

		self.uiSystemTypeLIST.clear()
		self.uiSystemTypeLIST.addItems(systems)
		self.uiSystemTypeLIST.setCurrentRow(0)

	# ----------------------------------------------------------------------------------
	# RETURN
	# ----------------------------------------------------------------------------------
	def layer(self):
		return self._layers[self.uiLayerCBOX.currentIndex()]

	def systemType(self):
		return self.uiSystemTypeLIST.currentItem().text()

	def pickPositions(self):
		return self.uiPickPositionCHK.isChecked()
