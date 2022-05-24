from itertools import izip

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath
from brigks import config

class MetaSystemBuilder(SystemBuilder):

	def createObjects(self):
		self.setSettings(count=self.count("Part"))
		
		# TRANSFORMATIONS
		zipper = izip(self.translations("Part"), self.translations("Eff"), self.directions("Part", "z"))
		boneTfm = [Transformation.lookAt(posA, posB-posA, drt, "xz", self.negate()) for posA, posB, drt in zipper]

		# OBJECTS
		# Root 
		root = self.addRig(None, "Root", boneTfm[0])
		
		buildController = []
		if self.settings("startController"): 
			buildController.append(1)
		if self.settings("interController"): 
			buildController.extend(xrange(2,self.count("Part")))
		buildController.append(self.count("Part"))
		
		self.bones = []
		self.drivers = []
		for i, tfm in enumerate(boneTfm, start=1):
			bfr = self.addBfr(root, "Part{}".format(i), tfm)
			drv = self.addRig(bfr, "Part{}".format(i), tfm)
			if i in buildController:
				bone = self.addCtl(drv, "Part{}".format(i), tfm, "pyramid", po=(0,2.5,0), color=self.colorFk())
				self.bones.append(bone)
			else:
				self.bones.append(drv)
				
			self.drivers.append(drv)
			
			
	def createJoints(self):
		for i, bone in enumerate(self.bones, start=1):
			self.addJnt(bone, "Part{}".format(i))
						
	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		sRef = self.bones[0]
		eRef = self.bones[-1]
		for i, drv in enumerate(self.drivers[1:-1], start=1):
			d = i / (self.count("Part") - 1.0)

			self._createBlendTransformOperators(drv, sRef, eRef, "translate", d)
			self._createBlendTransformOperators(drv, sRef, eRef, "rotate", d)
			self._createBlendTransformOperators(drv, sRef, eRef, "scale", d)

	def _createBlendTransformOperators(self, drv, sRef, eRef, transform, blend):
		eNode = self.addNode("multiplyDivide", "endMul")
		cmds.connectAttr(eRef+"."+transform, eNode+".input1")
		cmds.setAttr(eNode+".input2X", blend)
		cmds.setAttr(eNode+".input2Y", blend)
		cmds.setAttr(eNode+".input2Z", blend)

		sNode = self.addNode("multiplyDivide", "startMul")
		cmds.connectAttr(sRef+"."+transform, sNode+".input1")
		cmds.setAttr(sNode+".input2X", 1-blend)
		cmds.setAttr(sNode+".input2Y", 1-blend)
		cmds.setAttr(sNode+".input2Z", 1-blend)

		addNodeX = self.addNode("addDoubleLinear", "addX")
		cmds.connectAttr(eNode+".outputX", addNodeX+".input1")
		cmds.connectAttr(sNode+".outputX", addNodeX+".input2")
		addNodeY = self.addNode("addDoubleLinear", "addY")
		cmds.connectAttr(eNode+".outputY", addNodeY+".input1")
		cmds.connectAttr(sNode+".outputY", addNodeY+".input2")
		addNodeZ = self.addNode("addDoubleLinear", "addZ")
		cmds.connectAttr(eNode+".outputZ", addNodeZ+".input1")
		cmds.connectAttr(sNode+".outputZ", addNodeZ+".input2")

		cmds.connectAttr(addNodeX+".output", drv+"."+transform+"X")
		cmds.connectAttr(addNodeY+".output", drv+"."+transform+"Y")
		cmds.connectAttr(addNodeZ+".output", drv+"."+transform+"Z")

			
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Root" in self.connections():
			root = self.getObject(config.USE_BFR, "Part1")
			self.connections("Root").connect(root)
