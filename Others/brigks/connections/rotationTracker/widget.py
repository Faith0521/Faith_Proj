import os.path
from Qt import QtCompat

from brigks.connections.systemConnectionWidget import SystemConnectionWidget
from brigks.gui.pickSlotDialog import PickSlotDialog


class UiHostConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(UiHostConnectionWidget, self).__init__(connection, system)
		# uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		# QtCompat.loadUi(uiPath, self)

		self.uiPickReferenceBTN.clicked.connect(lambda: self.pickSlot("Reference"))
		self.uiPickTrackerBTN.clicked.connect(lambda: self.pickSlot("Tracker"))

	def pickSlot(self, target):
		dialog = PickSlotDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		uiKey = self.__dict__["ui{}Key".format(target)]
		uiSlot = self.__dict__["ui{}Slot".format(target)]
		uiKey.setText(dialog.systemKey())
		uiSlot.setText(dialog.systemSlot())

		self.saveSettings()
