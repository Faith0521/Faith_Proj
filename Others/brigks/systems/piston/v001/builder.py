
from maya import cmds

from math3d.transformation import Transformation

from brigks.systems.systemBuilder import SystemBuilder

class PistonSystemBuilder(SystemBuilder):

	def createObjects(self):
	
		# Normal
		normal = self.directions("Root", "y")
		
		distance = self.translations("Root").distance(self.translations("Eff"))
		
		# Transformations
		direction = self.translations("Eff") - self.translations("Root")
		startTfm = Transformation.lookAt(self.translations("Root"), direction, normal, "xy", self.negate())
		endTfm = startTfm.copy(translation=self.translations("Eff"))
		
		# Controllers
		startBfr = self.addBfr(None, "Start", startTfm)
		if self.settings("addControllers"):
			ctl = self.addCtl(startBfr, "Start", startTfm, "sphere", size=.5, color=self.colorIk())
			attributes.setKeyables(ctl)
			self.startParent = ctl
		else:
			self.startParent = startBfr

		endBfr = self.addBfr(None, "End", endTfm)
		if self.settings("addControllers"):
			self.endCtl = self.addCtl(endBfr, "End", endTfm, "sphere", size=.5, color=self.colorIk())
			attributes.setKeyables(self.endCtl)
			self.endParent = self.endCtl
		else:
			self.endParent = endBfr

		# Stretch
		self.startRig = self.addRig(self.startParent, "StretchStart", startTfm, "cube", size=1, 
					po=(distance*.25,0,0), so=(distance*.5, 1, 1))
					
		self.endRig = self.addRig(self.endParent, "StretchEnd", endTfm, "cube", size=1, 
					po=(distance*-.25,0,0), so=(distance*.5, 1, 1))

		self.interDiv = [self.addRig(self.startParent, "Div%s"%i, startTfm, "cube", self.size()) for i in xrange(1, self.settings("interDeformers")+1)]


	def createJoints(self):
		self.addJnt(self.startRig, "Start")
		self.addJnt(self.endRig, "End")
		for i, interDiv in enumerate(self.interDiv, start=1):
			self.addJnt(interDiv, str(i))

		
	#---------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		aimCns = self.addCompound("aimConstraint", "AimStart", self.startRig, self.endParent, 
			axis="xz", upMaster=self.startParent, upVector=(0,0,1), maintainOffset=False)

		aimCns = self.addCompound("aimConstraint", "AimEnd", self.endRig, self.startParent, 
			axis="-xz", upMaster=self.endParent, upVector=(0,0,1), maintainOffset=False)

		count = len(self.interDiv) + 1.0
		for i, interDiv in enumerate(self.interDiv, start=1):
			poseCns = self.addCompound("blendMatrix", "Inter", interDiv, [self.startRig, self.endRig])
			cmds.setAttr(cns+".target[1].weight", i / count)

	#---------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		if "Start" in self.connections():
			root = self.getObject(config.USE_BFR, "Start")
			self.connections("Start").connect(root)

		if "End" in self.connections():
			root = self.getObject(config.USE_BFR, "End")
			self.connections("End").connect(root)
