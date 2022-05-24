import os.path
import logging

from Qt import QtCompat
from Qt.QtCore import Signal
from Qt.QtWidgets import QWidget

from maya import cmds

from brigks.utils import gui
from brigks.guide import Guide
from brigks.systems.systemGuide import SystemGuide

class ScriptWidget(QWidget):

	updated = Signal(dict)

	def __init__(self, name):
		super(ScriptWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "scriptWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._name = name

		self.uiGRP.setTitle(name.title()+" Build Script")

		self.uiScriptTEXT = gui.addScriptWidget(name+"TempWindow")
		self.uiScriptValueWDG.layout().addWidget(self.uiScriptTEXT)

		self.uiScriptPathBTN.clicked.connect(self.browseScript)
		self.uiReloadScriptBTN.clicked.connect(self.reloadScript)
		self.uiExecScriptBTN.clicked.connect(self.executeScript)
		self.uiSaveScriptBTN.clicked.connect(self.saveScript)

		self.uiScriptTEXT.textChanged.connect(self.setWarning)

	def setObject(self, object):
		self.blockSignals(True)
		self._object = object
		self.uiScriptPathLINE.setText(self._object.settings(self._name+"ScriptPath"))
		self.uiScriptTEXT.setPlainText(self._object.settings(self._name+"ScriptValue"))
		self.blockSignals(False)

	def blockSignals(self, block):
		self.uiScriptTEXT.blockSignals(block)

	def setWarning(self, warning=True):
		if warning:
			self.uiSaveScriptBTN.setStyleSheet("background-color: rgb(200, 58, 58);");
		else:
			self.uiSaveScriptBTN.setStyleSheet("");

	# ----------------------------------------------------------------------------------
	# SCRIPTS
	# ----------------------------------------------------------------------------------
	def browseScript(self):
		filePath = self.uiScriptPathLINE.text()
		if os.path.exists(filePath):
			initPath = os.path.dirname(filePath)
		else:
			initPath = None

		path = gui.fileDialog(self, "Script", initPath, ["py"], save=False)		
		if not path:
			return

		self.uiScriptPathLINE.setText(path)
		self.reloadScript()

	def reloadScript(self):
		path = self.uiScriptPathLINE.text()
		if not os.path.exists(path):
			return

		with open(path, "r") as f:
			value = f.read()

		self.uiScriptTEXT.setPlainText(value)

		self.saveScript()

	def executeScript(self):
		path = self.uiScriptPathLINE.text()
		if os.path.exists(path):
			with open(path, "r") as f:
				value = f.read()
		else:
			value = self.uiScriptTEXT.toPlainText()

		if isinstance(self._object, Guide):
			model = self._object.setup()
		else:
			model = self._object.guide().setup()

		args = dict(
			cmds=cmds,
			this_model=model,
			this_guide=self._object,
			#this_builder=self,
			)
		exec(value, args, args)

	def saveScript(self):
		path = self.uiScriptPathLINE.text()

		value = self.uiScriptTEXT.toPlainText()
		try:
			with open(path, "w") as f:
				f.write(value)
		except IOError:
			logging.warning("File path is invalid. Can't save script to file. Script was saved inside the guide")
			pass

		settings = {
			self._name+"ScriptPath":path,
			self._name+"ScriptValue":value
			}

		self.updated.emit(settings)
		self.setWarning(False)

