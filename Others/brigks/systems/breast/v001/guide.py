from maya import cmds

from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class BreastSystemGuide(SystemGuide):	

	markerNames = ("Root", "Eff")
	markerPositions = dict(
		Root=Vector3([5,135,5]),
		Eff=Vector3([5,135,10]),
		)
	markerPicked = ("Root", "Eff")
	markerCurves = dict(
		DispCrv=("Root", "Eff")
		)

	def addSettings(self):
		self._settings["dynActive"] = False
		self._settings["amplitude"] = 1.0

		self._settings["amplitudeX"] = 0.0
		self._settings["amplitudeY"] = 1.0
		self._settings["amplitudeZ"] = 1.0
		self._settings["decay"] = 8.0
		self._settings["frequency"] = .25
		self._settings["termination"] = 0.0

		self._settings["dynamicAnimatable"] = False

	def connectionPorts(self):
		super(BreastSystemGuide, self).connectionPorts()
		
		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		return {}
