

from brigks.systems.systemWidget import SystemWidget


class LookatSystemWidget(SystemWidget):
	
	def connectWidgets(self, widgets):
		super(LookatSystemWidget, self).connectWidgets(widgets)
		
		self.uiAddLocalController.clicked.connect(self.refresh)
		self.uiExtraOffsetController.clicked.connect(self.refresh)
		
	def refresh(self):
		self.uiExtraOffsetController.setEnabled(self.uiAddLocalController.isChecked())
		self.uiExtraOffsetControllerLBL.setEnabled(self.uiAddLocalController.isChecked())
		
		self.uiKeepRotationOffset.setEnabled(self.uiExtraOffsetController.isChecked() and self.uiAddLocalController.isChecked())
		self.uiKeepRotationOffsetLBL.setEnabled(self.uiExtraOffsetController.isChecked() and self.uiAddLocalController.isChecked())
		