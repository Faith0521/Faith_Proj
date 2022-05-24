
from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

class LookatSystemBuilder(SystemBuilder):

	def createObjects(self):
		# Search for optional Upv marker to determine normal
		if "Upv" in self.translations():
			upv_pos = self.translations("Upv")
			normal = self.translations("Upv") - self.translations("Root")
		else:
			normal = self.directions("Root", "z")
			upv_pos = None
		
		# Transformation
		direction = self.translations("Eff") - self.translations("Root")
		dirTfm = Transformation.lookAt(self.translations("Root"), direction, normal, "xz", self.negate())
		ctlTfm = Transformation.lookAt(self.translations("Ctrl"), self.directions("Ctrl", "x"), self.directions("Ctrl", "z"),
												 "xz", self.negate())
		trgTfm = Transformation.lookAt(self.translations("Eff"), self.directions("Eff", "x"), self.directions("Eff", "z"),
												 "xz", self.negate())
		rigTfm = ctlTfm.copy(translation=self.translations("Root"))
		
		if self.settings("extraOffsetController") and self.settings("keepRotationOffset"):
			offTfm = Transformation.lookAt(self.translations("Root"), self.directions("Root", "x"), self.directions("Root", "z"),
												 "zy", self.negate())
			offctlTfm = offTfm.copy(translation=self.translations("Ctrl"))
		else:
			offTfm = rigTfm
			offctlTfm = ctlTfm

		if not upv_pos:
			upv_pos = Vector3([0,0,10]) * dirTfm.asMatrix()
		upvTfm = dirTfm.copy(translation=upv_pos)
					

		# Direction
		self.dirRig = self.addRig(None, "Direction", dirTfm)

		# Up Vector
		upvBfr = self.addBfr(None, "Upv", upvTfm)
		if self.settings("addUpVController"):
			self.parentUpv = self.addCtl(upvBfr, "Upv", upvTfm, "diamond", size=.5, color=self.colorIk())
			# self.addToSubControllers(self.parentUpv)
		else:
			self.parentUpv = upvBfr
		
		# Target
		self.targetBfr = self.addBfr(None, "Target", trgTfm)

		if self.settings("addTargetController"):
			# Target
			self.targetCtl = self.addCtl(self.targetBfr, "Target", trgTfm, "cube", size=1, color=self.colorIk())
			# self.addToSubControllers(self.targetCtl)
			attributes.setKeyables(self.targetCtl, constants.ATTRS_T)	
			# self.setInversedsettings(self.targetCtl, middle=["posy"])
				
		if self.settings("addLocalController"):
			# Local Controller
			localBfr = self.addBfr(self.dirRig, "LocalNP", rigTfm)
			self.localRig = self.addRig(localBfr, "Local", rigTfm, "cube")
			# self.setNeutralPose(self.localRig)
			localBfr = self.addBfr(None, "Local", ctlTfm)
			self.localCtl = self.addCtl(localBfr, "Local", ctlTfm, "sphere", size=1, color=self.colorFk())
			# self.setInversedsettings(self.localCtl, middle=["posx", "roty", "rotz"])
		
			# Extra Offset Controller
			if self.settings("extraOffsetController"):
				self.offsetRig = self.addRig(self.localRig, "Offset", offTfm, "cube", size=.5)
				self.offsetCtl = self.addCtl(self.localCtl, "Offset", offctlTfm, "sphere", size=.5, color=self.colorIk())
				# self.addToSubControllers(self.offsetCtl)
				# self.setInversedsettings(self.offsetCtl, middle=["posx", "roty", "rotz"])
		
		
	def createJoints(self):
		if not self.settings("addLocalController"):
			self.addJnt(self.dirRig, "Part1")
		elif self.settings("extraOffsetController"):
			self.addJnt(self.offsetRig, "Part1")
		else:
			self.addJnt(self.localRig, "Part1")
		
			
	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		target = self.targetCtl if self.settings("addTargetController") else self.targetBfr
		self.addCompound("aimConstraint", "Aim", self.dirRig, target, axis=self.sign()+"xz", upMaster=self.parentUpv)
		
		if not self.settings("addLocalController"):
			return

		cmds.connectAttr(self.localCtl+".translate", self.localRig+".translate")
		cmds.connectAttr(self.localCtl+".rotate", self.localRig+".rotate")
		cmds.connectAttr(self.localCtl+".scale", self.localRig+".scale")
			
		if self.settings("extraOffsetController"):
			cmds.connectAttr(self.offsetCtl+".translate", self.offsetRig+".translate")
			cmds.connectAttr(self.offsetCtl+".rotate", self.offsetRig+".rotate")
			cmds.connectAttr(self.offsetCtl+".scale", self.offsetRig+".scale")
		
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		if "Root" in self.connections():
			obj = self.getObject(config.USE_RIG, "Direction")
			self.connections("Root").connect(obj)

		if "Eff" in self.connections():
			obj = self.getObject(config.USE_BFR, "Target")
			self.connections("Eff").connect(obj)

		if "UpVector" in self.connections():
			obj = self.getObject(config.USE_BFR, "Upv")
			self.connections("UpVector").connect(obj)

		if not self.settings("addLocalController"):
			return

		if "Local" in self.connections():
			obj = self.getObject(config.USE_BFR, "Local")
			self.connections("Local").connect(obj)
		