
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class ChainSystemGuide(SystemGuide):

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)
	markerPositions = dict(
		Part1=Vector3([5,10,0]),
		Part2=Vector3([10,10,0]),
		)
	markerPicked = ("Part",)
	markerCurves = dict(
		DispCrv=("Part",)
		)
	markerCompatibility = dict(
		basic={},
		tentacle={},
		# basic=dict(Bone="Part")
		)

	def addSettings(self):
		self._settings["orientation"] = "Auto"  # Auto, Guide

		self._settings["kinematic"] = "FK"  # FK, IK or FK/IK
		self._settings["blend"] = "FK"

		self._settings["setNeutralPose"] = True
		self._settings["defaultRotationOrder"] = "XYZ"

		self._settings["strap"] = False
		self._settings["strapDeformers"] = 5

		self._settings["dynamic"] = False
		self._settings["dynActive"] = False
		self._settings["amplitude"] = 1.0

		self._settings["amplitudeX"] = 1.0
		self._settings["amplitudeY"] = 1.0
		self._settings["amplitudeZ"] = 1.0
		self._settings["decay"] = 8.0
		self._settings["frequency"] = .25
		self._settings["termination"] = 0.0

		self._settings["dynamicAnimatable"] = False

	def connectionPorts(self):
		super(ChainSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			FK=["multiOrient"],
			IK=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"],
			)

		return ports

	def connectionSlots(self):
		super(ChainSystemGuide, self).connectionSlots()

		if self._settings["dynamic"]:
			use = config.USE_RIG
			name = "Dynamic{}"
		elif self._settings["kinematic"] == "FK/IK":
			use = config.USE_RIG
			name = "Part{}"
		elif self._settings["kinematic"] == "FK":
			use = config.USE_CTL
			name = "Fk{}"
		else:
			use = config.USE_RIG
			name = "Ik{02d}"

		slots = dict()
		for i in xrange(1, self.count("Part")):
			slots["Bone{}".format(i)] = (use, name.format(i))

		return slots
