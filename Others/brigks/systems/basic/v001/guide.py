from maya import cmds

from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class BasicSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(1,-1),
		)
	markerPositions = dict(
		Part1=Vector3([3,10,0]),
		)
	markerCompatibility = dict(
		chain={},
		tentacle={},
		#chain=dict(Part="Bone"), # This is how it should be formated if you had to rename markers
		)
	markerPicked = ("Part",)

	def addSettings(self):
		self._settings["addControllers"] = True
		self._settings["useIkColor"] = False
		self._settings["addJointReference"] = False

		self._settings["tx"] = True
		self._settings["ty"] = True
		self._settings["tz"] = True
		self._settings["rx"] = True
		self._settings["ry"] = True
		self._settings["rz"] = True
		self._settings["sx"] = True
		self._settings["sy"] = True
		self._settings["sz"] = True
		
		self._settings["rotorder"] = True
		self._settings["defaultRotationOrder"] = "XYZ"

		self._settings["splitRotation"] = False
		
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
		super(BasicSystemGuide, self).connectionPorts()
		
		ports = {}
		for part in self.markers().keys():
			# port = marker.split("_")[-1]
			ports[part] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent", "averageTransform", "multiOrient"]

		ports["UI"] = ["uiHost"]

		return ports

	def connectionSlots(self):
		super(BasicSystemGuide, self).connectionSlots()

		slots = {}
		for part in self.markers().keys():
			slots[part] = (config.USE_CTL, part)

		return slots

		