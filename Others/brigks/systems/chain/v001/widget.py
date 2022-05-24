

from brigks.systems.systemWidget import SystemWidget


class ChainSystemWidget(SystemWidget):

	def connectWidgets(self, widgets):
		super(ChainSystemWidget, self).connectWidgets(widgets)

		self.uiKinematic.currentIndexChanged.connect(self.refresh)
		self.uiDynamic.clicked.connect(self.refresh)
		self.uiStrap.clicked.connect(self.refresh)
		self.refresh()
		
	def refresh(self):
		self.uiBlend.setEnabled(str(self.uiKinematic.currentText()) == "FK/IK")
		self.uiDynamicDefaultWDG.setEnabled(self.uiDynamic.isChecked())
		self.uiStrapDeformers.setEnabled(self.uiStrap.isChecked())
		self.uiStrapDeformersLBL.setEnabled(self.uiStrap.isChecked())
				