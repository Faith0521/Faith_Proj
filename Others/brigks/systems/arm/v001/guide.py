from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class ArmSystemGuide(SystemGuide):	

	markerNames = ("Root", "Elbow", "Wrist", "Eff", "Prop")
	markerPositions = dict(
		Root=Vector3([17,145,0]),
		Elbow=Vector3([38,125,0]),
		Wrist=Vector3([55,110,12]),
		Eff=Vector3([61,98,17]),
		Prop=Vector3([57,100,14]),
		)
	markerPicked = ("Root", "Elbow", "Wrist", "Eff")
	markerCurves = dict(
		DispCrv=("Root", "Elbow", "Wrist", "Eff")
		)

	def addSettings(self):
		self._settings["blend"] = "FK" # FK, IK

		self._settings["lockElbowRotation"] = False
		self._settings["gimbalControllers"] = False

		self._settings["stretchDefault"] = 1.5
		self._settings["reverseDefault"] = 0.0

	def connectionPorts(self):
		super(ArmSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "multiParent", "customParent"],
			FK=["multiOrient"],
			IK=["slotParent", "meshAttach", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "multiParent", "customParent"],
			UI=["uiHost"],
			)

		return ports

	def connectionSlots(self):
		super(ArmSystemGuide, self).connectionSlots()

		slots = dict(
			TwUprStart=(config.USE_RIG, "TwUprStart"),
			InterUpr=(config.USE_RIG, "InterUpr"),
			TwUprEnd=(config.USE_RIG, "TwUprEnd"),
			TwLwrStart=(config.USE_RIG, "TwLwrStart"),
			InterLwr=(config.USE_RIG, "InterLwr"),
			TwLwrEnd=(config.USE_RIG, "TwLwrEnd"),
			Hand=(config.USE_RIG, "Bone3"),
			Center=(config.USE_CTL, "Center"),
			Prop=(config.USE_CTL, "Prop"),
			IK=(config.USE_CTL, "Ik"),
			)

		return slots