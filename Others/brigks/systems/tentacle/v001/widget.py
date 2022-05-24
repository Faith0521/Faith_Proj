

from brigks.systems.systemWidget import SystemWidget


class TentacleSystemWidget(SystemWidget):

	def connectWidgets(self, widgets):
		super(TentacleSystemWidget, self).connectWidgets(widgets)
		self.uiKinematic.currentIndexChanged.connect(self.refresh)
		self.uiDynamic.clicked.connect(self.refresh)
		
	def refresh(self):
		self.uiBlend.setEnabled(str(self.uiKinematic.currentText()) == "FK/IK")
		self.uiDynamicDefaultWDG.setEnabled(self.uiDynamic.isChecked())
		
				