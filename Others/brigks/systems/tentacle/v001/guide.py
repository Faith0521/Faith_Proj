
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class TentacleSystemGuide(SystemGuide):

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)
	markerPositions = dict(
		Part1=Vector3([0,0,0]),
		Part2=Vector3([0,0,-10]),
		)
	markerCompatibility = dict(
		basic=dict(),
		chain=dict(),
		)
	markerPicked = ("Part",)
	markerCurves = dict(
		DispCrv=("Part",)
		)

	def addSettings(self):
		self._settings["kinematic"] = "FK" # FK, IK or FK/IK
		self._settings["blend"] = "FK"
		
		self._settings["setNeutralPose"] = True
		self._settings["defaultRotationOrder"] = "XYZ"

		self._settings["jointsCount"] = 20
		self._settings["lowJointsCount"] = 10

		self._settings["minimumLength"] = 0.0
		
		self._settings["addRootCtrl"] = False
		self._settings["addRoll"] = True
		self._settings["extraControllers"] = 0
		self._settings["extraControllerSpacing"] = 0.1
		
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
		super(TentacleSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "multiParent", "customParent"],
			Orient=["multiOrient"],
			IK=["slotParent", "meshAttach", "multiParent", "customParent"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(TentacleSystemGuide, self).connectionSlots()

		if self.settings("dynamic"):
			use = config.USE_RIG
			name = "Dynamic-{}-Bone1"
		elif self.settings("kinematic") == "FK/IK":
			name = "Bone{}"
			use = config.USE_RIG
		elif self.settings("kinematic") == "FK":
			name = "Fk{}"
			use = config.USE_CTL
		else:
			name = "Ik-Bone{}"
			use = config.USE_RIG
		
		slots = {}
		for i in xrange(1, self.count("Part")+1):
			slots["Bone{}".format(i)] = (use, name.format(i))

		return slots
