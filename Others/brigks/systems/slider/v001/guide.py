from itertools import izip

from maya import cmds

from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class SliderSystemGuide(SystemGuide):	

	markerNames = ("Rail", "Pos", "Neg")
	markerMinMax = dict(
		Rail=(1,-1),
		Pos=(1,-1),
		Neg=(1,-1)
		)
	markerPositions = dict(
		Rail1=Vector3([0,0,0]),
		Pos1=Vector3([2,0,0]),
		Neg1=Vector3([-1,0,0]),
		)
	markerPicked = ("Rail",)

	def createMarkerCurves(self):
		for i in xrange(1, self.count("Rail")+1):
			markers = [self._markers["{}{}".format(x, i)].name() for x in ["Pos", "Rail", "Neg"]]
			self.addMarkerDispCurve("Crv{}".format(i), markers)

	def createMarkers(self, matrices):
		super(SliderSystemGuide, self).createMarkers(matrices)

		# Parenting the Ends to the Rail and making sure you can't translate them other than x
		for rail, pos, neg in izip(self.markers("Rail"), self.markers("Pos"), self.markers("Neg")):
			for end in [pos, neg]:
				end.setParent(rail.name())
				cmds.setAttr(end.name()+".ty", 0)
				cmds.setAttr(end.name()+".tz", 0)
				cmds.setAttr(end.name()+".ty", lock=True)
				cmds.setAttr(end.name()+".tz", lock=True)

	def addSettings(self):
		self._settings["addControllers"] = False

		for i in xrange(1, self.count("Rail")+1):
			self._settings["minRot{}".format(i)] = -90
			self._settings["maxRot{}".format(i)] = 90
			self._settings["axis{}".format(i)] = "Z"

	def connectionPorts(self):
		super(SliderSystemGuide, self).connectionPorts()
		
		ports = dict(
			Tracker=["rotationTracker"]
			)

		for i in xrange(1, self.count("Rail")+1):
			ports["Rail{}".format(i)] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]

		return ports

	def connectionSlots(self):
		super(SliderSystemGuide, self).connectionSlots()

		use = config.USE_CTL if self.settings("addControllers") else config.USE_RIG
		slots = dict()
		for i in xrange(1, self.count("Rail")+1):
			slots["Slider{}".format(i)] = (use, "Slider{}".format(i))

		return slots

			