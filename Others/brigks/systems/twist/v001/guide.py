from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class TwistSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)
	markerPositions = dict(
		Part1=Vector3([5,10,0]),
		Part2=Vector3([5,30,0]),
		)
	markerPicked = ("Part",)
	markerCurves = dict(
		DispCrv=("Part",)
		)

	def addSettings(self):
		# ("spinePointAt", "blendedAxis")
		self._settings["twistMethod"] = "spinePointAt"

		self._settings["axis"] = "X" # (X, Y)
		
		self._settings["startDeformer"] = False
		self._settings["interDeformers"] = 3
		self._settings["endDeformer"] = False
		self._settings["untwistDeformers"] = False
		
		self._settings["startController"] = False
		self._settings["interControllers"] = True
		self._settings["endController"] = False
		
		self._settings["scaleWithCurve"] = False
		self._settings["scaleWithControllers"] = False
		self._settings["scaleWithInterControllers"] = False
		
		self._settings["parametric"] = True
		self._settings["preserveLength"] = False
		self._settings["tangent"] = True
		self._settings["tangentDistance"] = .25 
		self._settings["pushCurvePoints"] = False 

	def connectionPorts(self):
		super(TwistSystemGuide, self).connectionPorts()
		
		ports = {}
		for i in xrange(1, self.count("Part")+1):
			ports["Control{}".format(i)] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]

		ports["UI"] = ["uiHost"]

		return ports

	def connectionSlots(self):
		super(TwistSystemGuide, self).connectionSlots()

		slots = {}

		start_use = config.USE_CTL if self._settings["startController"] else config.USE_BFR
		slots["Start"] = (start_use, "Start")
		
		use = config.USE_CTL if self._settings["interControllers"] else config.USE_BFR
		for i in xrange(1, self.count("Part")-1):
			slots["Part%s"%i] = (use, "Part%s"%i)
				
		end_use = config.USE_CTL if self._settings["endController"] else config.USE_BFR
		slots["End"] = (end_use, "End")

		if self._settings["tangent"] and self._settings["untwistDeformers"]:
			slots["UntwistStart"] = (config.USE_RIG, "UntwistStart")
		
		# Divisions
		if self._settings["startDeformer"]:
			if self._settings["tangent"]: 
				slots["Start"] = (start_use, "Start")
			else:
				slots["Div0"] = ("Div0")
				if self._settings["untwistDeformers"]:
					slots["Untwist0"] = (config.USE_RIG, "Untwist0")
		
		for i in xrange(1, self._settings["interDeformers"]+1):
			slots["Div%s"%i] = (config.USE_RIG, "Div%s"%i)
			if self._settings["untwistDeformers"]:
				slots["Untwist%s"%i] = (config.USE_RIG, "Untwist%s"%i)
			
		if self._settings["endDeformer"]:
			if self._settings["tangent"]: 
				slots["End"] = (end_use, "End")
			else:
				slots["Div%s"%(self._settings["interDeformers"]+1)] = (config.USE_RIG, "Div%s"%(self._settings["interDeformers"]+1))
				if self._settings["untwistDeformers"]:
					slots["Untwist%s"%i(self._settings["interDeformers"]+1)] = (config.USE_RIG, "Untwist%s"%(self._settings["interDeformers"]+1))

		if self._settings["tangent"] and self._settings["untwistDeformers"]:
			slots["UntwistEnd"] = (config.USE_RIG, "UntwistEnd")
			

		return slots

		