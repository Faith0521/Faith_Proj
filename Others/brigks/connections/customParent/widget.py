import os.path
from Qt import QtCompat

from brigks.gui.pickObjectDialog import PickObjectDialog
from brigks.connections.systemConnectionWidget import SystemConnectionWidget


class CustomParentConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(CustomParentConnectionWidget, self).__init__(connection, system)
		# uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		# QtCompat.loadUi(uiPath, self)

	 	self.uiPickBTN.clicked.connect(self.pickCustom)
	# 	self.uiParentLINE.editingFinished.connect(self.saveSettings)

	# def loadSettings(self):
	# 	definitions = self._connection.settings["definitions"]
	# 	if definitions:
	# 		parent = "{parent}".format(**definitions[0])
	# 		self.uiParentLINE.setText(parent)

	# def saveSettings(self, parent):
	# 	definition = dict(
	# 		type="custom",
	# 		parent=self.uiParentLINE.text()
	# 		)

	# 	self._connection.settings["definitions"] = [definition]
	# 	self._system.coreGuide.dumps()

	def pickCustom(self):
		dialog = PickObjectDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		self.uiParentLINE.setText(dialog.object())
		self.saveSettings()
