from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class QuadrantSystemGuide(SystemGuide):	

	markerNames = ("Root",)
	markerPositions = dict(
		Root=Vector3([20,0,0]),
		)
	markerPicked = ("Root",)

	def addSettings(self):
		self._settings["north"] = True
		self._settings["south"] = True
		self._settings["east"] = True
		self._settings["west"] = True

		self._settings["push"] = 2.0

		self._settings["customLabel"] = False
		self._settings["label"] = "Label"
		self._settings["labelPosition"] = "North"

	def connectionPorts(self):
		super(QuadrantSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			)

		return ports

	def connectionSlots(self):
		super(QuadrantSystemGuide, self).connectionSlots()

		slots = dict(
			Ctl=(config.USE_CTL, "Root")
			)

		return slots
