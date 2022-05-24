import os.path

from Qt.QtWidgets import QDialog
from Qt import QtCompat

from brigks.gui.guideTreeWidget import GuideTreeWidget, SystemTreeWidgetItem, SubSystemTreeWidgetItem

class PickSlotDialog(QDialog):

	def __init__(self, parent, guide):
		super(PickSlotDialog, self).__init__(parent)
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "pickSlotDialog.ui")
		QtCompat.loadUi(uiPath, self)

		self._system = None
		self._slots = None

		self.uiGuideTREE = GuideTreeWidget(guide)
		self.uiGuideTREE.setSelectionMode(self.uiGuideTREE.SingleSelection)
		self.uiGuideTREE.itemSelectionChanged.connect(self.loadSlots)

		self.uiTreeWDG.layout().addWidget(self.uiGuideTREE)

	def loadSlots(self):
		self._system = None
		self._slots = None
		self.uiSlotLIST.clear()

		item = self.uiGuideTREE.selectedItems()[0]
		if not isinstance(item, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
			return

		self._system = item.object()
		self._slots = sorted(self._system.connectionSlots().keys())

		self.uiSlotLIST.addItems(self._slots)
		self.uiSlotLIST.setCurrentRow(0)

	def systemKey(self):
		if self._system:
			return self._system.key()

	def systemSlot(self):
		if self._slots:
			return self._slots[self.uiSlotLIST.currentRow()]
