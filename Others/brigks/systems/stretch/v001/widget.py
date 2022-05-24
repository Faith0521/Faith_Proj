

from brigks.systems.systemWidget import SystemWidget


class StretchSystemWidget(SystemWidget):

	def connectWidgets(self, widgets):
		super(StretchSystemWidget, self).connectWidgets(widgets)
		self.uiTwist.clicked.connect(self.refresh)
		self.uiSquash.clicked.connect(self.refresh)
		self.uiStretch.clicked.connect(self.refresh)
		
	def refresh(self):
		self.uiTwistBlend.setEnabled(self.uiTwist.isChecked())
		self.uiSquashy.setEnabled(self.uiSquash.isChecked())
		self.uiSquashz.setEnabled(self.uiSquash.isChecked())
		self.uiStretchBlend.setEnabled(self.uiStretch.isChecked())