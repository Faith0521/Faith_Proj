from maya import cmds

from math3d.transformation import TransformationArray
from math3d.vectorN import Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import attributes
from brigks import config

class StretchSystemBuilder(SystemBuilder):

	def createObjects(self):
		# TRANSFORMATION
		normal = self.directions("Root", "z")
		positions = Vector3Array([self.translations("Root"), self.translations("Eff")])
		ctlTfm = TransformationArray.chain(positions, normal, negativeSide=self.negate(), endTransform=True)

		self.length = self.translations("Root").distance(self.translations("Eff"))

		# CONTROLLERS
		startBfr = self.addBfr(None, "Start", ctlTfm[0])
		endBfr = self.addBfr(None, "End", ctlTfm[1])
		
		if self.settings("addControllers"):
			startCtl = self.addCtl(startBfr, "Start", ctlTfm[0], "cube", color=self.colorIk())
			attributes.setKeyables(startCtl, constants.ATTRS_TR)
			
			endCtl = self.addCtl(endBfr, "End", ctlTfm[1], "cube", color=self.colorIk())
			attributes.setKeyables(endCtl, constants.ATTRS_TR)
			
			self.centers = [startCtl, endCtl]
		else:
			self.centers = [startBfr, endBfr]

		# Stretch
		self.bone = self.addRig(self.centers[0], "Bone", ctlTfm[0], "cube", po=(self.length*.5,0,0), so=(self.length,1,1))

	def createJoints(self):
		self.addJnt(self.bone, "Bone")

	#----------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		if self.settings("twist"):
			self.twistBlendAttr = self.addAnimAttr("twistBlend", "float", self.settings("twistBlend"), 0, 1)

		if self.settings("squash"):
			self.squashAttr = [self.addAnimAttr("squash"+s, "float", self.settings("squash"+s), None, None) for s in "yz"]

		if self.settings("stretch"):
			self.stretchBlendAttr = self.addAnimAttr("stretchBlend", "float", self.settings("stretchBlend"), 0, 1)

		self.lengthRatioAttr = self.addAnimAttr("lengthRatio", "float", 1, 0, None)

	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		#Direction
		cns = self.addCompound("aimConstraint", "Aim", self.bone, self.centers[1], axis="xy", upMaster=self.centers[0], upVector=(0,0,1))

		# Twist
		if self.settings("twist"):
			pabaCns = self.addCompound("pointAtBlendedAxis", "Twst", cns, self.centers[0], self.centers[1], blend=self.settings("twistBlend"))
			cmds.connectAttr(self.twistBlendAttr, pabaCns+".blend")

		# length ratio
		if self.settings("stretch") or self.settings("squash"):
			multMatNode = self.addNode("multMatrix", "MultMat")
			cmds.connectAttr(self.centers[1]+".worldMatrix[0]", multMatNode+".matrixIn[0]")
			cmds.connectAttr(self.centers[0]+".worldInverseMatrix[0]", multMatNode+".matrixIn[1]")

			distNode = self.addNode("distanceBetween", "Distance")
			cmds.connectAttr(multMatNode+".matrixSum", distNode+".inMatrix2")

			divNode = self.addNode("multiplyDivide", "LengthRatio")
			cmds.setAttr(divNode+".operation", 2) # Divide
			cmds.connectAttr(distNode+".distance", divNode+".input1X")
			cmds.setAttr(divNode+".input2X", self.length)

			cmds.connectAttr(divNode+".outputX", self.lengthRatioAttr)

		# Scaling
		if self.settings("stretch"):
			negateNode = self.addNode("multiplyDivide", "Negate")
			cmds.setAttr(negateNode+".operation", 1) # Multiply
			cmds.connectAttr(self.stretchBlendAttr, negateNode+".input1X")
			cmds.setAttr(negateNode+".input2X", -1)

			addNode1 = self.addNode("addDoubleLinear", "Add")
			cmds.setAttr(addNode1+".input1", 1)
			cmds.connectAttr(negateNode+".outputX", addNode1+".input2")

			mulNode = self.addNode("multiplyDivide", "Multiply")
			cmds.setAttr(mulNode+".operation", 1) # Multiply
			cmds.connectAttr(self.lengthRatioAttr, mulNode+".input1X")
			cmds.connectAttr(self.stretchBlendAttr, mulNode+".input2X")

			addNode2 = self.addNode("addDoubleLinear", "Add")
			cmds.connectAttr(addNode1+".output", addNode2+".input1")
			cmds.connectAttr(mulNode+".outputX", addNode2+".input2")

			cmds.connectAttr(addNode2+".output", self.bone+".scaleX")

		if self.settings("squash"):
			divNode3 = self.addNode("multiplyDivide", "Divide")
			cmds.setAttr(divNode3+".operation", 2) # Divide
			cmds.setAttr(divNode3+".input1X", 1)
			cmds.connectAttr(self.lengthRatioAttr, divNode3+".input2X")

			powNode = self.addNode("multiplyDivide", "Power")
			cmds.setAttr(powNode+".operation", 3) # Power
			cmds.connectAttr(divNode3+".outputX", powNode+".input1Y")
			cmds.connectAttr(self.squashAttr[0], powNode+".input2Y")
			cmds.connectAttr(divNode3+".outputX", powNode+".input1Z")
			cmds.connectAttr(self.squashAttr[1], powNode+".input2Z")

			cmds.connectAttr(powNode+".outputY", self.bone+".scaleY")
			cmds.connectAttr(powNode+".outputZ", self.bone+".scaleZ")
			
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Start" in self.connections():
			child = self.getObject(config.USE_BFR, "Start")
			self.connections("Start").connect(child)

		if "End" in self.connections():
			child = self.getObject(config.USE_BFR, "End")
			self.connections("End").connect(child)
