from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class LookatSystemGuide(SystemGuide):

	markerNames = ("Root", "Eff", "Ctrl")
	markerPositions = dict(
		Root=Vector3([0,10,0]),
		Eff=Vector3([0,10,10]),
		Ctrl=Vector3([0,15,0]),
		)
	markerPicked = ("Root", "Eff")
	markerCurves = dict(
		DispCrv=("Root", "Eff")
		)

	def addSettings(self):
		self._settings["addLocalController"] = True
		self._settings["addTargetController"] = True
		self._settings["addUpVController"] = False
		self._settings["extraOffsetController"] = False
		self._settings["keepRotationOffset"] = False

	def connectionPorts(self):
		super(LookatSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Eff=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(LookatSystemGuide, self).connectionSlots()

		slots = dict(
			Direction=(config.USE_RIG, "Direction"),
			Local=(config.USE_RIG, "Local")
		)

		if self._settings["extraOffsetController"]:
			slots["Offset"] = (config.USE_RIG, "Offset")

		return slots
