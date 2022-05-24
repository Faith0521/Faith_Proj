import os.path
import logging

from Qt import QtCompat
from Qt.QtCore import Signal
from Qt.QtWidgets import QWidget
from Qt.QtGui import QColor, QPalette

from brigks.gui.pickColorDialog import PickColorDialog

class LayerSettingsWidget(QWidget):

	layerRenamed = Signal(str)

	def __init__(self, layer):
		super(LayerSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "layerSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._layer = None

		self.connectWidgets()

		self.setLayer(layer)

	def setLayer(self, layer):
		self._layer = layer
		if self._layer is None:
			return 

		self.settings = self._layer.settings

		self._blocked = True
		self.uiNameLINE.setText(self._layer.name())

		# Colors
		self.uiUseLayerColor.setChecked(self.settings("useLayerColor"))
		self.uiInheritColors.setChecked(self.settings("inheritColors"))
		self.loadColors()

		self._blocked = False

	def connectWidgets(self):
		self._blocked = True

		self.uiNameLINE.editingFinished.connect(self.rename)

		# Colors
		self.uiUseLayerColor.clicked.connect(self.saveSettings)
		self.uiUseLayerColor.clicked.connect(self.loadColors)
		self.uiInheritColors.clicked.connect(self.saveSettings)
		self.uiInheritColors.clicked.connect(self.loadColors)

		self.uiColor.clicked.connect(lambda:self.pickColor(self.uiColor, "color"))

		self.uiColorRFk.clicked.connect(lambda:self.pickColor(self.uiColorRFk, "colorRFk"))
		self.uiColorRIk.clicked.connect(lambda:self.pickColor(self.uiColorRIk, "colorRIk"))
		self.uiColorMFk.clicked.connect(lambda:self.pickColor(self.uiColorMFk, "colorMFk"))
		self.uiColorMIk.clicked.connect(lambda:self.pickColor(self.uiColorMIk, "colorMIk"))
		self.uiColorLFk.clicked.connect(lambda:self.pickColor(self.uiColorLFk, "colorLFk"))
		self.uiColorLIk.clicked.connect(lambda:self.pickColor(self.uiColorLIk, "colorLIk"))

		self._blocked = False

	def saveSettings(self):
		self._layer.setSettings(
			useLayerColor=self.uiUseLayerColor.isChecked(),
			inheritColors=self.uiInheritColors.isChecked(),
			)
		self.commit()

	def commit(self):
		if self._blocked:
			return 
		self._layer.commit()

	# ----------------------------------------------------------------------------------
	# FIRST TAB
	# ----------------------------------------------------------------------------------
	def rename(self):
		name = self.uiNameLINE.text()
		name = self._layer.setName(name)
		self._layer.commit()
		self.layerRenamed.emit(name)

	def loadColors(self):
		self.setButtonColor(self.uiColor, self.settings("color"))
		for key in ["RFk", "RIk", "MFk", "MIk", "LFk", "LIk"]:
			btn = self.__dict__["uiColor"+key]
			value = self._layer.colors(key)
			self.setButtonColor(btn, value)

	def pickColor(self, button, setting):
		color = self.settings(setting)
		
		dialog = PickColorDialog(self, color)
		dialog.exec_()
		if not dialog.result():
			return

		self.setButtonColor(button, dialog.color)
		self._guide.setSettings(**{setting:dialog.color})
		self.commit()

	def setButtonColor(self, button, color):
		qcolor = QColor()
		qcolor.setRgbF(color[0], color[1], color[2])
		
		palette = QPalette()
		palette.setColor(QPalette.Button, qcolor)
		button.setPalette(palette)