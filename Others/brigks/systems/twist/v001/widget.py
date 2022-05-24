

from brigks.systems.systemWidget import SystemWidget


class TwistSystemWidget(SystemWidget):
	
	def connectWidgets(self, widgets):
		super(TwistSystemWidget, self).connectWidgets(widgets)
		self.uiTangent.clicked.connect(self.refresh)
		self.uiParametric.clicked.connect(self.refresh)
		
	def refresh(self):
		self.uiTangentDistance.setEnabled(self.uiTangent.isChecked())
		self.uiPreserveLength.setEnabled(not self.uiParametric.isChecked())