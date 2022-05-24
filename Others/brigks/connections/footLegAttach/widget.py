import os.path
from Qt import QtCompat

from brigks.connections.systemConnectionWidget import SystemConnectionWidget
from brigks.gui.pickSlotDialog import PickSlotDialog


class FootLegAttachConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(FootLegAttachConnectionWidget, self).__init__(connection, system)
		# uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		# QtCompat.loadUi(uiPath, self)

		self.uiPickBTN.clicked.connect(self.pickSlot)

	def pickSlot(self):
		dialog = PickSlotDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		self.uiKey.setText(dialog.systemKey())
		self.uiSlot.setText(dialog.systemSlot())
		self.saveSettings()