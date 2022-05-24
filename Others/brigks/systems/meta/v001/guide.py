from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class MetaSystemGuide(SystemGuide):

	markerNames = ("Part", "Eff")
	markerMinMax = dict(
		Part=(2,-1),
		Eff=(2,-1)
		)
	markerPositions = dict(
		Part1=Vector3([55,105,15]),
		Part2=Vector3([55,105,13]),
		Part3=Vector3([55,105,11]),
		Part4=Vector3([55,105,9]),
		Eff1=Vector3([60,105,15]),
		Eff2=Vector3([60,105,13]),
		Eff3=Vector3([60,105,11]),
		Eff4=Vector3([60,105,9]),
		)
	markerPicked = ("Part",)
	markerCurves = dict(
		DispCrv=("Part",)
		)

	def createMarkerCurves(self):
		for i in xrange(1, self.count("Part")+1):
			markers = [self._markers["{}{}".format(x, i)].name() for x in ["Part", "Eff"]]
			self.addMarkerDispCurve("Crv{}".format(i), markers)

	def addSettings(self):
		self._settings["startController"] = True
		self._settings["interController"] = False

	def connectionPorts(self):
		super(MetaSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			)

		return ports

	def connectionSlots(self):
		super(MetaSystemGuide, self).connectionSlots()

		slots = dict()
		for i in range(1, self.count("Part")+1):
			slots["Bone{}".format(i)] = (config.USE_CTL, "Part{}".format(i))

		return slots
