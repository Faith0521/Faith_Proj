
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class DrivenSystemGuide(SystemGuide):	

	markerNames = ("Rail", "Pos", "Neg")
	markerMinMax = dict(
		Rail=(1,-1), 
		Pos=(1,-1),
		Neg=(1,-1) 
		)
	markerPositions = dict(
		Rail1=Vector3([0,5,0]),
		Pos1=Vector3([0,5,2]),
		Neg1=Vector3([0,5,-2]),
		)
	markerPicked = ("Rail",)
	
	def createMarkerCurves(self):
		for i in xrange(1, self.count("Rail")+1):
			markers = [self._markers["{}{}".format(x, i)].name() for x in ["Pos", "Rail", "Neg"]]
			curve = create.cnsCurve(self.getMarkerName("DispCrv{}".format(i)), markers, degree=1)
			cmds.setAttr(curve+".template", True)
	
	def addSettings(self):
		self._settings["addControllers"] = True
		self._settings["useIkColor"] = False

		self._settings["addControllers"] = False
		self._settings["addDeformerRef"] = False
		
		for i in xrange(1, self.count("Rail")+1):
			self._settings["minRot%s"%i]= -90
			self._settings["maxRot%s"%i]= 90
			self._settings["axis%s"%i]= "Z"

	def connectionPorts(self):
		super(DrivenSystemGuide, self).connectionPorts()

		ports = {}
		for i in xrange(1, self.count("Rail")+1):
			self.port["Rail{}".format(i)] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			
		self.port["Tracker"] = ["rotationTracker"]

		return ports

	def connectionSlots(self):
		super(DrivenSystemGuide, self).connectionSlots()

		use = config.USE_CTL if self._settings("addControllers") else config.USE_RIG
		slots = dict()
		for i in xrange(1, self.count("Rail")+1):
			slots["Part%s"%i] = (use, "Part%s"%i)

		return slots