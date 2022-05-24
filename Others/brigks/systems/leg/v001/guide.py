
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class LegSystemGuide(SystemGuide):	

	markerNames = ("Root", "Knee", "Ankle", "Eff")
	markerPositions = dict(
		Root=Vector3([15,100,0]),
		Knee=Vector3([15,50,5]),
		Ankle=Vector3([15,10,0]),
		Eff=Vector3([15,10,5]),
		)
	markerPicked = ("Root", "Knee", "Wrist", "Eff")
	markerCurves = dict(
		DispCrv=("Root", "Knee", "Wrist", "Eff")
		)

	def addSettings(self):
		self._settings["blend"] = "IK" # FK, IK

		self._settings["lockKneeRotation"] = False

		self._settings["stretchDefault"] = 1.5
		self._settings["reverseDefault"] = 0.0

		self._settings["ankleUpVector"] = "World Y" # World Y, Guide Z

	def connectionPorts(self):
		super(LegSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			FK=["multiOrient"],
			IK=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"],
			)

		return ports

	def connectionSlots(self):
		super(LegSystemGuide, self).connectionSlots()

		slots = dict(
			TwUprStart=(config.USE_RIG, "TwUprStart"),
			InterUpr=(config.USE_RIG, "InterUpr"),
			TwUprEnd=(config.USE_RIG, "TwUprEnd"),
			TwLwrStart=(config.USE_RIG, "TwLwrStart"),
			InterLwr=(config.USE_RIG, "InterLwr"),
			TwLwrEnd=(config.USE_RIG, "TwLwrEnd"),
			Foot=(config.USE_RIG, "Bone3"),
			Center=(config.USE_CTL, "Center"),
			IK=(config.USE_CTL, "Ik"),
			)

		return slots