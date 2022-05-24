from maya import cmds

from math3d.transformation import Transformation

from brigks.systems.systemBuilder import SystemBuilder
from brigks import config

class AverageSystemBuilder(SystemBuilder):

	# TODO, AVERAGE Should be replaced with a Basic with a AverageTransform connection

	def createObjects(self):
		# Transformation
		tfm = Transformation.lookAt(self.translations("Root"), self.directions("Root", "x"), self.directions("Root", "z"), "xz", self.negate())

		# Controller
		self.bfr = self.addBfr(None, "Average", tfm,)

		if self.settings("addControllers"):
			self.ctl = self.addCtl(self.bfr, "Average", self.guide().controllers("gde_Root"), tfm, color=self.colorFk())

	def createJoints(self):
		if self.settings("addControllers"):
			self.addJnt(self.ctl, 1)
		else:
			self.addJnt(self.bfr, 1)

	# ----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		if self.settings("blendAnimatable"):
			self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend"), 0, 1)

	# ----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		bfr = self.getObject(config.USE_BFR, "Average")
		if "Average" in self.connections():
			attr = self.blendAttr if self.settings("blendAnimatable") else None
			self.connections("Average").connect(bfr, attr)