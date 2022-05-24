
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class FootSystemGuide(SystemGuide):	

	markerNames = ("Root", "Part", "Heel", "In", "Out")
	markerMinMax = dict(
		Part=(2,-1)
		)
	markerPositions = dict(
		Root=Vector3([15,10,0]),
		Part1=Vector3([15,5,10]),
		Part2=Vector3([15,2,20]),
		Heel=Vector3([15,0,-5]),
		In=Vector3([8,0,3]),
		Out=Vector3([22,0,3]),
		)
	markerPicked = ("Root", "Part", "Heel")
	markerCurves = dict(
		DispCrv=("Root", "Part", "Heel"),
		SideCrv=("In", "Heel", "Out")
		)

	def addSettings(self):
		for i in range(self.count("Part")):
			self._settings["angle%s"%(i+1)] = 20
			
		self._settings["rollControl"] = "Slider" # Slider, Controller

	def connectionPorts(self):
		super(FootSystemGuide, self).connectionPorts()
		
		ports = dict(
			Root=["footLegAttach"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(FootSystemGuide, self).connectionSlots()

		slots = dict(
			Root=(config.USE_RIG, "FkRef")
			)

		for i in xrange(1, self.count("Part")):
			slots["Bone%s"%i] = (config.USE_CTL, "Fk%s"%i)

		return slots

		