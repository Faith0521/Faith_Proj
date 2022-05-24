
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class CameraSystemGuide(SystemGuide):

	markerNames = ("Root",)
	markerPositions = dict(
		Root=Vector3([0,175,60]),
		)
	markerPicked = ("Root",)

	def createMarkers(self, matrices):
		parent = self.model()
		matrix = matrices["Root"] if "Root" in matrices else None
		self.addMarkerCamera("Root", parent=None, matrix=matrix)

	def addSettings(self):
		# Camera settings (such as FOV) are directly taken from the marker attributes
		pass

	def connectionPorts(self):
		super(CameraSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "multiParent", "customParent"],
			)

		return ports

	def connectionSlots(self):
		super(CameraSystemGuide, self).connectionSlots()