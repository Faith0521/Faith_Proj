from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class PsdSystemGuide(SystemGuide):	

	markerNames = ("Root", "Driver", "Inner", "Outer")
	markerMinMax = dict(Driver=(1,-1),
						Inner=(1,-1),
						Outer=(1,-1))
	markerPositions = dict(
		Root=Vector3([0,0,0]),
		Driver1=Vector3([0,0,0]),
		Inner1=Vector3([-2,0,0]),
		Outer1=Vector3([2,0,0]),
		)
	markerPicked = ("Root", "Driver",)

	def createMarkerCurves(self):
		for i in xrange(1, self.count("Driver")+1):
			markers = [self._markers["{}{}".format(x, i)].name() for x in ["Inner", "Driver", "Outer"]]
			curve = create.cnsCurve(self.getMarkerName("DispCrv{}".format(i)), markers, degree=1)
			cmds.setAttr(curve+".template", True)
			
	def addSettings(self):
		for i in xrange(1, self.count("Driver")+1):
			self._settings["drvName{}".format(i)] = "Driver{}".format(i)
			self._settings["interpType{}".format(i)] = "Linear"

		self._settings["twistAxis"] = "X"
		self._settings["twistInterp"] = "Linear"
		self._settings["twistMin"] = -90
		self._settings["twistMax"] = 90
		self._settings["twistSplit"] = True

	def connectionPorts(self):
		super(PsdSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Tracker=["rotationTracker"],
			Orient=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			)

		return ports

	def connectionSlots(self):
		super(PsdSystemGuide, self).connectionSlots()

		slots = dict(
			Root=(config.USE_RIG, "Root"))

		return slots
		