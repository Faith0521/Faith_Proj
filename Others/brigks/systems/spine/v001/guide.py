from maya import cmds

from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class SpineSystemGuide(SystemGuide):

	markerNames = ("Root", "Eff")
	markerPositions = dict(
		Root=Vector3([0,100,0]),
		Eff=Vector3([0,135,0]),
		)
	markerPicked = ("Root", "Eff")
	markerCurves = dict(
		DispCrv=("Root", "Eff")
		)

	def createMarkers(self, matrices):
		super(SpineSystemGuide, self).createMarkers(matrices)
		
		# Auxiliaries to attach the twist spline
		aux25 = self.addMarker("Aux25", parent=self.markers("Root"))
		aux50 = self.addMarker("Aux50", parent=self.markers("Root"))
		aux75 = self.addMarker("Aux75", parent=self.markers("Root"))

		self.addCompound("twoPointsConstraint", "Aux25", aux25, self.markers("Root"), self.markers("Eff"), blend=.25, axis="x-z")
		self.addCompound("twoPointsConstraint", "Aux50", aux50, self.markers("Root"), self.markers("Eff"), blend=.50, axis="x-z")
		self.addCompound("twoPointsConstraint", "Aux75", aux75, self.markers("Root"), self.markers("Eff"), blend=.75, axis="x-z")
		
		for marker in [aux25, aux50, aux75]:
			cmds.setAttr(marker.name()+".template", True)

	def addSettings(self):
		self._settings["blend"] = "IK" # FK, IK
		self._settings["breathing"] = False
		self._settings["axis"] = "YZ"

	def connectionPorts(self):
		super(SpineSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"])

		return ports

	def connectionSlots(self):
		super(SpineSystemGuide, self).connectionSlots()

		slots = dict(
			Pelvis=(config.USE_CTL, "Ik1"),
			Lower=(config.USE_RIG, "Hook2"),
			Middle=(config.USE_RIG, "Hook3"),
			Upper=(config.USE_RIG, "Hook4"),
			Chest=(config.USE_RIG, "Hook5"),
			Breathing=(config.USE_CTL, "Breathing")
			)


		return slots
