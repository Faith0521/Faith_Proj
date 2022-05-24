from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class NeckSystemGuide(SystemGuide):

	markerNames = ("Root", "Head", "Eff")
	markerPositions = dict(
		Root=Vector3([0,155,0]),
		Head=Vector3([0,170,3]),
		Eff=Vector3([0,185,3]),
		)
	markerPicked = ("Root", "Head", "Eff")
	markerCurves = dict(
		DispCrv=("Root", "Head", "Eff")
		)

	def addSettings(self):
		self._settings["kinematic"] = "FK/IK" # IK or FK/IK
		self._settings["blend"] = "IK" # FK, IK

		self._settings["stretch"] = 0.0
		self._settings["gimbalControllers"] = False
		self._settings["extraHeadController"] = False
		self._settings["orientToWorld"] = False

	def connectionPorts(self):
		super(NeckSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			IK=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Orient=["multiOrient"],
			UI=("uiHost")
		)

		return ports

	def connectionSlots(self):
		super(NeckSystemGuide, self).connectionSlots()

		slots = {}
		for i, s in enumerate(["Root", "Mid", "Head"], start=1):
			slots[s] = (config.USE_RIG, "Hook{}".format(i))

		return slots
