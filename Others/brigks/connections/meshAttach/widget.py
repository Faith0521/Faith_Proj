import os.path
from Qt import QtCompat

from brigks.gui.pickObjectDialog import PickObjectDialog
from brigks.gui.pickSlotDialog import PickSlotDialog
from brigks.connections.systemConnectionWidget import SystemConnectionWidget


class MeshAttachConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(MeshAttachConnectionWidget, self).__init__(connection, system)
		# uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		# QtCompat.loadUi(uiPath, self)

		self.uiPickBTN.clicked.connect(self.pickMesh)
		self.uiClosestBTN.clicked.connect(self.closest)
		self.uiPickParentBTN.clicked.connect(self.pickSlot)
		# self.uiMeshLINE.editingFinished.connect(self.saveSettings)
		# self.uiComponentTypeCBOX.currentIndexChanged.connect(self.saveSettings)
		# self.uiComponentIndexSPN.valueChanged.connect(self.saveSettings)
		# self.uiUseOrientationCHK.clicked.connect(self.saveSettings)
		# self.uiClosestCHK.clicked.connect(self.saveSettings)

	def pickMesh(self):
		dialog = PickObjectDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		self.uiMeshLINE.setText(dialog.object())
		self.saveSettings()

	def closest(self):
		pass

	def pickSlot(self):
		dialog = PickSlotDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		self.uiKey.setText(dialog.systemKey())
		self.uiSlot.setText(dialog.systemSlot())
		self.saveSettings()