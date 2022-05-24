
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class AverageSystemGuide(SystemGuide):	

	markerNames = ("Root",)
	markerPositions = dict(
		Root=Vector3([0,10,0]),
		)
	markerPicked = ("Root",)

	def addSettings(self):
		self._settings["addControllers"] = False
		self._settings["blendAnimatable"] = False

		self._settings["blend"] = .5
		self._settings["position"] = True
		self._settings["rotation"] = True
		self._settings["scaling"] = True

	def connectionPorts(self):
		super(AverageSystemGuide, self).connectionPorts()
		
		ports = dict(
			Average=["averageTransform"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(AverageSystemGuide, self).connectionSlots()

		use = config.USE_CTL if self.settings("addControllers") else config.USE_BFR
		slots = dict(
			Average=(use, "Average")
			)

		return slots
