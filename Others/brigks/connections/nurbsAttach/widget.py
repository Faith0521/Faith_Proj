import os.path
from Qt import QtCompat

from brigks.gui.pickObjectDialog import PickObjectDialog
from brigks.connections.systemConnectionWidget import SystemConnectionWidget


class NurbsParentConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(NurbsParentConnectionWidget, self).__init__(connection, system)
		# uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		# QtCompat.loadUi(uiPath, self)

		self.uiPickBTN.clicked.connect(self.pickNurbs)
		# self.uiNurbsLINE.editingFinished.connect(self.saveSettings)
		# self.uiUSPN.valueChanged.connect(self.saveSettings)
		# self.uiVSPN.valueChanged.connect(self.saveSettings)
		# self.uiClosestCHK.clicked.connect(self.saveSettings)

	# def loadSettings(self):
	# 	definitions = self._connection.settings["definitions"]
	# 	if definitions:
	# 		parent = "{mesh}".format(**definitions[0])
	# 		self.uiNurbsLINE.setText(parent)

	# def saveSettings(self):
	# 	definition = dict(
	# 		type="nurbs",
	# 		mesh=self.uiNurbsLINE.text(),
	# 		u=self.uiUSPN.value(),
	# 		v=self.uiVSPN.value(),
	# 		useClosest=self.uiClosestCHK.isChecked(),
	# 		)

	# 	self._connection.settings["definitions"] = [definition]
	# 	self._system.coreGuide.dumps()

	def pickNurbs(self):
		dialog = PickObjectDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		self.uiNurbsLINE.setText(dialog.object())
		self.saveSettings()
