from itertools import product

from brigks.systems.systemWidget import SystemWidget


class BasicSystemWidget(SystemWidget):

	def connectWidgets(self, widgets):
		super(BasicSystemWidget, self).connectWidgets(widgets)

		self.uiKeyableAllBTN.clicked.connect(lambda:self.keyableAll(True))
		self.uiKeyableNoneBTN.clicked.connect(lambda:self.keyableAll(False))
		self.uiDynamic.clicked.connect(self.refresh)
		
	def keyableAll(self, value=True):
		for t, s in product("TRS", "xyz"):
			wdg = self.__dict__["ui{t}{s}".format(t=t, s=s)]
			wdg.setChecked(value)
		
		self.uiRotorder.setChecked(value)		
		self.commit()

	def refresh(self):
		self.uiDynamicDefaultWDG.setEnabled(self.uiDynamic.isChecked())
		
			