

from brigks.systems.systemWidget import SystemWidget


class QuadrantSystemWidget(SystemWidget):

	def connectWidgets(self, widgets):
		super(QuadrantSystemWidget, self).connectWidgets(widgets)

		self.uiNorth.clicked.connect(self.changeFrameDisplay)
		self.uiSouth.clicked.connect(self.changeFrameDisplay)
		self.uiEast.clicked.connect(self.changeFrameDisplay)
		self.uiWest.clicked.connect(self.changeFrameDisplay)

	def changeFrameDisplay(self):
		north = self.uiNorth.isChecked()
		south = self.uiSouth.isChecked()
		east = self.uiEast.isChecked()
		west = self.uiWest.isChecked()

		scly = 2 * (north + south) if (north or south) else 0
		sclx = 2 * (east + west) if (east or west) else 0
		offy = 1 * (north - south)
		offx = 1 * (east - west)
		
		marker = self.markers("Root")
		marker.setDisplay( [dict(icon="sphere"),
							dict(icon="cube", so=[sclx,scly,0], po=[offx, offy, 0])],
							replace=True )

		color = self.layer().color()
		marker.setColor(color)
			