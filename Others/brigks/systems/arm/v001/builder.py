from itertools import izip
from collections import defaultdict

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

class ArmSystemBuilder(SystemBuilder):

	twp = ["Upr", "Lwr"]

	def createObjects(self):
		# SIZE
		size = self.translations("Root").distance(self.translations("Elbow"))
		fkSize = size * .5
		ikSize = size * .5
		upvSize = size * .125
		rootSize = size * .25

		# TRANSFORMATIONS
		positions = Vector3Array([self.translations("Root"), self.translations("Elbow"), self.translations("Wrist")])
		normal = Vector3.planeNormal(*positions)
		oriNormal = normal.copy()
		if self.negate():
			normal *= -1
		
		# distances
		d = [(positions[i],positions[i+1]) for i in range(2)]
		self.lengths = [Vector3.distance(a,b) for a,b in d]
		self.lengths.append(1)
		ratio = self.lengths[0] / sum(self.lengths[:2])
		self.setSettings(lengths=self.lengths[:2])
		
		# root
		rootTfm = Transformation.fromParts(translation=self.translations("Root"))

		# fk
		fkTfm = TransformationArray.chain(positions, normal, axis="xz", negativeSide=self.negate(), endTransform=False)
		direction = self.translations("Eff") - self.translations("Wrist")
		fk2Tfm = Transformation.lookAt(self.translations("Wrist"), direction, self.directions("Wrist", "z"), axis="xz", negativeSide=self.negate())
		fkTfm = fkTfm.appended(fk2Tfm)

		bfrTfm = [Transformation.fromParts(translation=tfm.translation, rotation=fkTfm[max(i-1,0)].rotation) for i, tfm in enumerate(fkTfm)]
		bfrTfm[0] = Transformation.lookAt(self.translations("Root"), constants.AXIS_X, constants.AXIS_Y, axis=self.sign()+"xz", negativeSide=self.negate())
		
		# ik
		ikbfrPos = Vector3([self.factor() * sum(self.lengths[:2]), 0, 0]) * rootTfm.asMatrix()
		ikbfrTfm = Transformation.fromParts(translation=ikbfrPos)
		ikTfm = Transformation.lookAt(self.translations("Wrist"), direction, self.directions("Wrist", "z"), axis=self.sign()+"xy", negativeSide=False)
		
		upvbfrTfm = Transformation.fromParts(translation=umath.upVector(self.translations("Root"), ikbfrPos, constants.AXIS_Y, ratio, self.negate()))
		upvTfm = Transformation.fromParts(translation=umath.upVector(self.translations("Root"), self.translations("Wrist"), oriNormal, ratio))
		
		# extras
		scale = Vector3([self.factor(), self.factor(), self.factor()])
		twisterTfm = {}
		interTfm = {}
		for i, (p, pos) in enumerate(izip(self.twp, positions[1:3])):
			twisterTfm[p] = [fkTfm[i].copy(scale=scale), fkTfm[i].copy(translation=pos, scale=scale)]
			interPos = twisterTfm[p][0].translation.lerp(twisterTfm[p][1].translation, .5)
			interTfm[p] = twisterTfm[p][0].copy(translation=interPos)
			
		ctrTfm = twisterTfm["Lwr"][0]

		# prop
		propTfm = Transformation.lookAt(self.translations("Prop"), self.directions("Prop", "y"), self.directions("Prop", "z"), axis="yz", negativeSide=False)


		# CONTROLLERS
		# Root 
		self.rootBfr = self.addBfr(None, "Root", rootTfm)
		self.rootCtl = self.addCtl(self.rootBfr, "Root", rootTfm, "sphere", size=rootSize, color=self.colorIk())
		# self.addToSubControllers(self.rootCtl)
		attributes.setKeyables(self.rootCtl, constants.ATTRS_T)
		
		# Fk Ref
		# Used as a reference for the upr start twist
		# We cannot use the fk1Bfr cause this one get constrained when fk ref changes
		self.fkRef = self.addRig(self.rootBfr, "FkRef", bfrTfm[0])

		# GinmbalController
		if self.settings("gimbalControllers"):
			fkBfr = self.addBfr(self.fkRef, "FkOff", tfm=bfrTfm[0])
			self.fkOffCtl = self.addCtl(fkBfr, "FkOff", bfrTfm[0], "cube", size=.9, so=[0,1,1], color=self.colorFk())
			# self.addToSubControllers(self.fkOffCtl)
			fkParent = self.fkOffCtl
			boneParent = self.fkOffCtl
		else:
			fkParent = self.fkRef
			boneParent = self.fkRef

		# FK Controlers and Bones
		self.fkBfr = []
		self.fkCtl = []
		self.bones = []
		self.stretches = []
		for i, (tfm, btfm) in enumerate(izip(fkTfm, bfrTfm), start=1):
			bfr = self.addBfr(fkParent, "Fk{}".format(i), btfm)
			ctl = self.addCtl(bfr, "Fk{}".format(i), tfm, "sphere", size=fkSize, so=(0,1,1), color=self.colorFk())

			if self.settings("lockElbowRotation") and i == 2:
				attributes.setRotOrder(ctl, "xyz")
				attributes.setKeyables(ctl, ["tx", "ty", "tz", "rz", "sx", "sy", "sz"], lock=True)
			else:
				attributes.setRotOrder(ctl, "xzy")
				attributes.setKeyables(ctl, constants.ATTRS_TRS)
			
			fkParent = ctl
			self.fkBfr.append(bfr)
			self.fkCtl.append(ctl)

			bone = self.addRig(boneParent, "Bone{}".format(i), tfm=tfm, icon="bone", so=(self.factor(), 1, 1))
			boneParent = bone
			self.bones.append(bone)
			
		# IK Controllers
		self.ikBfr = self.addBfr(None, "Ik", ikbfrTfm)
		self.ikCtl = self.addCtl(self.ikBfr, "Ik", ikTfm, "cube", size=ikSize, color=self.colorIk())

		attributes.setKeyables(self.ikCtl, constants.ATTRS_TRS)
		attributes.setRotOrder(self.ikCtl, "XZY")

		self.ikoffCtl = self.addCtl(self.ikCtl, "IkOffset", ikTfm, "null", size=ikSize, color=self.colorIk())
		# self.addToSubControllers(self.ikoffCtl)
		attributes.setKeyables(self.ikoffCtl, constants.ATTRS_TRS)
		self.ikRef = self.addRig(self.ikoffCtl, "IkRef", fkTfm[-1])
		attributes.setRotOrder(self.ikoffCtl, "XZY")

		self.upvBfr = self.addBfr(None, "Upv", upvbfrTfm)
		self.upvCtl = self.addCtl(self.upvBfr, "Upv", upvTfm, "diamond", size=upvSize, color=self.colorIk())
		attributes.setKeyables(self.upvCtl, constants.ATTRS_T)

		self.ctrBfr = self.addBfr(self.bones[0], "Center", ctrTfm)
		self.ctrCtl = self.addCtl(self.ctrBfr, "Center", ctrTfm, "sphere", size=upvSize, color=self.colorIk())
		# self.addToSubControllers(self.ctrCtl)
		attributes.setKeyables(self.ctrCtl, constants.ATTRS_TRS)

		self.upvCrv = create.cnsCurve(self.getObjectName(config.USE_RIG, "UpvCrv"), [self.upvCtl, self.ctrCtl])
		cmds.setAttr(self.upvCrv+".template", True)
	
		# Twisters
		self.twisters = defaultdict(list)
		for p in self.twp:
			for s, tfm, factor in izip(["Start", "End"], twisterTfm[p], [1,-1]):
				twisterBfr = self.addBfr(self.rootBfr, "Tw"+p+s, tfm )
				twister = self.addRig(twisterBfr, "Tw"+p+s, tfm, "pyramid")
				self.twisters[p].append(twister)

		# Inter
		self.inters = {}
		for p in self.twp:
			self.inters[p] = self.addRig(self.rootBfr, "Inter"+p, interTfm[p], "cube")

		# Prop Controller
		propBfr = self.addBfr(self.bones[-1], "Prop", propTfm)
		self.propCtl = self.addCtl(propBfr, "Prop", propTfm, "cube", color=self.colorIk())

	def createJoints(self):
		for p in self.twp:
			for s, twister in izip(["Start", "End"], self.twisters[p]):
				self.addJnt(twister,  "Tw"+p+s)
		
		self.addJnt(self.ctrCtl, "Center")
		self.addJnt(self.bones[2], "Hand")
	
	#-----------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend") == "IK", 0, 1)

		self.showCtrlAttr = self.addAnimAttr("showCtrl", "bool", False) 

		self.rollAttr = self.addAnimAttr("Roll", "float", 0, -180, 180)
		self.scaleAAttr = self.addAnimAttr("ScaleA", "float", 1)
		self.scaleBAttr = self.addAnimAttr("ScaleB", "float", 1)
		self.maxStretchAttr = self.addAnimAttr("MaxStretch", "float", self.settings("stretchDefault"), 1, None)
		self.slideAttr = self.addAnimAttr("Slide", "float", .5, 0, 1)
		self.reverseAttr = self.addAnimAttr("Reverse", "float", self.settings("reverseDefault"), 0, 1)
		self.softnessAttr = self.addAnimAttr("Softness", "float", 0, 0, 1)

		self.lengthAAttr = self.addSetupAttr("LengthA", "float", self.lengths[0])
		self.lengthBAttr = self.addSetupAttr("LengthB", "float", self.lengths[1])

	def createLayout(self): 
		pass
		
		
	#-----------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibility
		fkCompare = self.addCompound("compare", "FkVis", self.blendAttr, 1, "<")
		ikCompare = self.addCompound("compare", "IkVis", self.blendAttr, 0, ">")

		cmds.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
		cmds.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

		for ctl in self.fkCtl:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		if self.settings("gimbalControllers"):
			for shp in cmds.listRelatives(self.fkOffCtl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		for ctl in [self.rootCtl, self.ikCtl, self.ikoffCtl, self.upvCtl, self.upvCrv]:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		# Center
		attributes.inheritsTransform(self.ctrBfr, False)
		node = self.addNode("decomposeMatrix", "CtrDM")
		cmds.connectAttr(self.bones[1]+".worldMatrix[0]", node+".inputMatrix")
		cmds.connectAttr(node+".outputTranslate", self.ctrBfr+".translate")
		cns = self.addCompound("blendMatrix", "Center", self.ctrBfr, self.bones[:2], maintainOffset=False, translate=False, rotate=True, scale=False)
		cmds.setAttr(cns+".target[1].weight", .5)
		cmds.connectAttr(self.nodes("local")+".scale", self.ctrBfr+".scale")
		
		# Fk Ik Solver
		iks = [self.rootCtl, self.ikRef, self.upvCtl]
		ikfkNode = self.addCompound("fkik2Bones", "Arm", iks, self.fkCtl, self.bones, self.lengths[0], self.lengths[1], self.negate())
		cmds.connectAttr(self.blendAttr, ikfkNode+".blend")
		cmds.connectAttr(self.rollAttr, ikfkNode+".roll")
		cmds.connectAttr(self.scaleAAttr, ikfkNode+".scaleA")
		cmds.connectAttr(self.scaleBAttr, ikfkNode+".scaleB")
		cmds.connectAttr(self.maxStretchAttr, ikfkNode+".maxStretch")
		cmds.connectAttr(self.slideAttr, ikfkNode+".slide")
		cmds.connectAttr(self.reverseAttr, ikfkNode+".reverse")
		cmds.connectAttr(self.softnessAttr, ikfkNode+".softness")
		cmds.connectAttr(self.lengthAAttr, ikfkNode+".lengthA")
		cmds.connectAttr(self.lengthBAttr, ikfkNode+".lengthB") 

		# # Twisters
		self._twisterCns(self.twisters["Upr"][0], self.bones[0], self.ctrCtl, self.fkRef, self.bones[0], self.sign()+"xz", self.lengths[0])
		self._twisterCns(self.twisters["Upr"][1], self.ctrCtl, self.bones[0], self.ctrCtl, self.ctrBfr, self.nsign()+"xz", self.lengths[0], scaleComp=True)
		self._twisterCns(self.twisters["Lwr"][0], self.ctrCtl, self.bones[-1], self.ctrCtl, self.ctrBfr, self.sign()+"xz", self.lengths[1], scaleComp=True)
		self._twisterCns(self.twisters["Lwr"][1], self.bones[-1], self.ctrCtl, self.bones[2], self.bones[1], self.nsign()+"xy", self.lengths[1], pntAtDouble=False)
		
		# # Inter
		for p in self.twp:
			cmds.pointConstraint(self.twisters[p], self.inters[p])
			cns = self.addCompound("aimConstraint", p+"InterAim", self.inters[p], self.twisters[p][1], axis="x-z")
			self.addCompound("spinePointAt", p+"InterPtAt", cns, self.twisters[p][0], self.twisters[p][1], blend=.5, solver=1) 
		
	
	def _twisterCns(self, tws, pos, aim, pntAt, pntAtRef, axis, distance, pntAtDouble=True, scaleComp=False):
		attributes.inheritsTransform(tws, False)

		# Position
		node = self.addNode("decomposeMatrix", "TwsDM")
		cmds.connectAttr(pos+".worldMatrix[0]", node+".inputMatrix")
		cmds.connectAttr(node+".outputTranslate", tws+".translate")

		# Rotation 
		if pntAtDouble:
			cns = self.addCompound("aimConstraint", "TwsAim", tws, aim, axis=axis, upMaster=None, upVector=(0,0,1))
			self.addCompound("pointAtDoubleAxis", "TwsPtAt", cns, pntAtRef, pntAt, axis="z")
		else:
			cns = self.addCompound("aimConstraint", "TwsAim", tws, aim, axis=axis, upMaster=pntAt, upVector=(0,1,0))
			
		# Scaling
		dist_Node = self.addNode("distanceBetween", "twsScaleDist")
		cmds.connectAttr(pos+".worldMatrix[0]", dist_Node+".inMatrix1")
		cmds.connectAttr(aim+".worldMatrix[0]", dist_Node+".inMatrix2")
		div_Node = self.addNode("multiplyDivide", "twsScaleRatio")
		cmds.setAttr(div_Node+".operation", 2) # Division
		cmds.connectAttr(dist_Node+".distance", div_Node+".input1X")
		cmds.setAttr(div_Node+".input2X", distance)
		cmds.connectAttr(div_Node+".outputX", tws+".scaleX")

		if scaleComp:
			divNode = self.addNode("multiplyDivide", "Div")
			cmds.setAttr(divNode+".operation", 1)  # Multiply
			cmds.connectAttr(pos+".scale", divNode+".input1")
			cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2X")
			cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Y")
			cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Z")

			cmds.connectAttr(divNode+".outputY", tws+".scaleY")
			cmds.connectAttr(divNode+".outputZ", tws+".scaleZ")
		else:
			cmds.connectAttr(pos+".sy", tws+".scaleY")
			cmds.connectAttr(pos+".sz", tws+".scaleZ")


	#-----------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Root" in self.connections():
			obj = self.getObject(config.USE_BFR, "Root")
			self.connections("Root").connect(obj, attrName="RootParent")

		if "IK" in self.connections():
			obj = self.getObject(config.USE_BFR, "Ik")
			self.connections("IK").connect(obj, attrName="IKParent")

		if "UpVector" in self.connections():
			obj = self.getObject(config.USE_BFR, "Upv")
			self.connections("UpVector").connect(obj, attrName="UpVParent")
		
		# Fk Ref
		if "FK" in self.connections():
			part = "FkOff" if self.settings("gimbalControllers") else "Fk1"
			obj = self.getObject(config.USE_BFR, part)
			self.connections("FK").connect(obj, attrName="FKOrient")


