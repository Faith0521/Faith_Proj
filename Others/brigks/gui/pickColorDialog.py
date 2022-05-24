
from functools import partial

from Qt import QtWidgets, QtGui, QtCore

COLORHUE = [0, .1, .15, .25, .4, .5, .62, .75, .87]

class PickColorDialog(QtWidgets.QDialog):
	
	def __init__(self, parent, color):	
		super(PickColorDialog, self).__init__(parent)
		
		self.color = color
		self.qcolor = QtGui.QColor()
		self.qcolor.setRgbF(self.color[0], self.color[1], self.color[2])
		
		self.setWindowTitle("Pick Color")
		self.setFixedSize(300, 150)
		
		self.uiMainLAY = QtWidgets.QGridLayout()
		self.uiMainLAY.setContentsMargins(3,3,3,3)
		self.setLayout(self.uiMainLAY)
		
		# Colors
		self.uiPresetGRP = QtWidgets.QGroupBox(" Presets ")
		self.uiColorLAY = QtWidgets.QGridLayout()
		self.uiColorLAY.setContentsMargins(3,3,3,3)
		self.uiColorLAY.setSpacing(3)
		
		# Custom Color
		self.uiColorGRP = QtWidgets.QGroupBox(" Color ")
		self.uiCustomLAY = QtWidgets.QVBoxLayout()
		self.uiCustomLAY.setContentsMargins(3,3,3,3)
		self.uiColorGRP.setLayout(self.uiCustomLAY)
		
		self.uiCustomBTN = QtWidgets.QPushButton("Pick Color")
		self.uiCustomBTN.setFixedHeight(85)
		
		self.setColor(self.qcolor)
		
		self.uiCustomLAY.addWidget(self.uiCustomBTN)
		
		# Button Box
		self.uiButtonBOX = QtWidgets.QDialogButtonBox()
		self.uiButtonBOX.setOrientation(QtCore.Qt.Horizontal)
		self.uiButtonBOX.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
		
		self.uiPresetGRP.setLayout(self.uiColorLAY)
		self.uiMainLAY.addWidget(self.uiPresetGRP, 0, 0)
		self.uiMainLAY.addWidget(self.uiColorGRP, 0, 1)
		self.uiMainLAY.addWidget(self.uiButtonBOX, 2, 0, 1, 0)
		
		# Color Buttons
		for i, hue in enumerate(COLORHUE):
			for j, lum in enumerate((.25,.5,.85)):
				btn = QtWidgets.QPushButton(self)
				btnColor = QtGui.QColor()
				btnColor.setHslF(hue, 1, lum)
				palette = QtGui.QPalette()
				palette.setColor(QtGui.QPalette.Button, btnColor)
				btn.setPalette(palette)
				
				row = j
				column = i
				self.uiColorLAY.addWidget(btn, row, column)
			
				btn.clicked.connect(partial(self.setColor, btnColor))
		
		for i in range(4):
			btn = QtWidgets.QPushButton(self)
			btnColor = QtGui.QColor()
			btnColor.setHslF(0, 0, i/3.0)
			palette = QtGui.QPalette()
			palette.setColor(QtGui.QPalette.Button, btnColor)
			btn.setPalette(palette)
			
			row = j+1
			column = i
			self.uiColorLAY.addWidget(btn, row, column)
			
			btn.clicked.connect(partial(self.setColor, btnColor))
			
		# Connections
		self.uiCustomBTN.clicked.connect(self.pickCustomColor)
		self.uiButtonBOX.accepted.connect(self.accept)
		self.uiButtonBOX.rejected.connect(self.reject)
		
	def pickCustomColor(self):
		palette = self.uiCustomBTN.palette()
		qcolor = palette.color(QtGui.QPalette.Button)
		
		colorDialog = QtWidgets.QColorDialog(qcolor, self)
		if not colorDialog.exec_():
			return
			
		self.setColor(colorDialog.currentColor())
		
	def setColor(self, qcolor):
		palette = self.uiCustomBTN.palette()
		palette.setColor(QtGui.QPalette.Button, qcolor)
		self.uiCustomBTN.setPalette(palette)
		
		self.qcolor = qcolor
		self.color = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
