import os.path
from functools import partial

import maya.OpenMayaUI as mui
from maya import cmds

from Qt import QtCompat
from Qt.QtWidgets import QWidget, QInputDialog, QPushButton
from Qt.QtGui import QColor, QPalette
from Qt.QtCore import Qt

COLOR_HIDDEN = QColor(70,70,70)
COLOR_VISIBLE = QColor(82,133,166)

# TODO this widget slows down a bit the opening of the UI. Should we put that somewhere else? 


OPTIONS = ["gde", "rig", "jnt", "ctl"]

class GuideVisibilityWidget(QWidget):

	def __init__(self, guide):
		super(GuideVisibilityWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "guideVisibilityWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._visButtons = []
		self.setGuide(guide)

	def setGuide(self, guide):
		self._guide = guide
		if self._guide is None:
			return

		self.load()

	# ----------------------------------------------------------------------------------
	# VISIBILITIES
	# ----------------------------------------------------------------------------------
	def load(self):
		layout = self.layout()

		# Clear
		for btn in self._visButtons:
			layout.removeWidget(btn)
			btn.setVisible(False)
			#TODO sip delete?
		self._visButtons = []

		layers = self._guide.getLayersDepths()
		for i, (depth, layer) in enumerate(layers, start=1):
			btn = QPushButton("    "*depth+layer.name())
			btn.setStyleSheet("Text-align:left");
			btn.setMaximumHeight(20)
			layout.addWidget(btn, i, 0)
			self._visButtons.append(btn)

			for j, option in enumerate(OPTIONS, start=1):
				btn = QPushButton()
				btn.setFixedSize(30,20)
				kwargs = {x:option==x for x in OPTIONS}
				visible = layer.isVisible(**kwargs)
				self.setButtonColor(btn, visible)

				btn.clicked.connect(partial(self.toggleVisibility, btn, layer, option))

				layout.addWidget(btn, i, j)
				self._visButtons.append(btn)


	def setButtonColor(self, button, visible):
		pal = button.palette()
		color = COLOR_VISIBLE if visible else COLOR_HIDDEN
		pal.setColor(QPalette.Button, color)
		button.setAutoFillBackground(True)
		button.setPalette(pal)
		button.update()

	def toggleVisibility(self, button, layer, option):
		systemGuides = layer.systems().values()
		if not systemGuides:
			return 

		kwargs = {x:option==x for x in OPTIONS}
		visible = not layer.isVisible(**kwargs)
		layer.setVisible(visible, **kwargs)

		self.setButtonColor(button, layer.isVisible())
