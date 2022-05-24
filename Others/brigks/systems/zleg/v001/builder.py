from itertools import izip
from collections import defaultdict

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks import config
from brigks.utils import constants, umath, attributes, create
from brigks.systems.systemBuilder import SystemBuilder


class ZlegSystemBuilder(SystemBuilder):

	twp = ["Upr", "Mid", "Lwr"]

	def createObjects(self):

		# TRANSFORMATIONS
		positions = Vector3Array([self.translations("Root"), self.translations("Knee"), self.translations("Ankle"), self.translations("Toe")])
		normal = Vector3.planeNormal(*positions[:3])
		oriNormal = normal.copy()
		if self.negate():
			normal *= -1
		
		d = [(positions[i],positions[i+1]) for i in range(3)]
		self.lengths = [Vector3.distance(a,b) for a,b in d]
		self.lengths.append(1)
		ratio = self.lengths[0] / sum(self.lengths[:2])
		self.setSettings(lengths=self.lengths[:3])
		
		# root
		rootTfm = Transformation.fromParts(translation=self.translations("Root"))

		# fk
		fkTfm = TransformationArray.chain(positions, normal, axis="xz", negativeSide=self.negate(), endTransform=False)
		lookAtEff = self.translations("Eff") - self.translations("Toe")
		fk3Tfm = Transformation.lookAt(self.translations("Toe"), lookAtEff, constants.AXIS_Y, "y-x", self.negate())
		fkTfm = fkTfm.appended(fk3Tfm)
		for tfm, dist in izip(fkTfm, self.lengths):
			tfm.scale = Vector3([dist * self.factor(), self.factor(), self.factor()])
		bfrTfm = [tfm.copy(rotation=fkTfm[max(i-1,0)].rotation) for i, tfm in enumerate(fkTfm)]
		bfrTfm[0] = Transformation.lookAt(self.translations("Root"), constants.AXIS_NY, constants.AXIS_X, "x"+self.nsign()+"z", self.negate())
		scale = bfrTfm[0].scale
		scale.x *= self.lengths[0]
		bfrTfm[0].scale = scale
		
		# ik
		ikbfrPos = Vector3([self.translations("Root").x, self.translations("Toe").y, self.translations("Root").z])
		ikbfrTfm = Transformation.fromParts(translation=ikbfrPos)
		ikTfm = Transformation.lookAt(self.translations("Toe"), lookAtEff, constants.AXIS_Y, "zy", False)
		
		upvbfrTfm = Transformation.fromParts(translation=umath.upVector(self.translations("Root"), ikbfrPos, constants.AXIS_NX, ratio, False))
		upvTfm = Transformation.fromParts(translation=umath.upVector(self.translations("Root"), self.translations("Ankle"), oriNormal, ratio))
		
		rollNormal = Vector3.planeNormal(self.translations("Root"), upvTfm.translation, self.translations("Toe"))
		if self.negate():
			rollNormal *= -1
		direction = self.translations("Root") - self.translations("Toe") 
		rollbfrTfm = Transformation.lookAt(self.translations("Toe"), direction, rollNormal, "y-x", self.negate())
		direction = self.translations("Ankle") - self.translations("Toe") 
		rollTfm = Transformation.lookAt(self.translations("Toe"), direction, normal, "y-x", self.negate())

		# extras
		scale = Vector3([self.factor(), self.factor(), self.factor()])
		twisterTfm = {}
		interTfm = {}
		for i, (p, pos) in enumerate(izip(self.twp, positions[1:4])):
			twisterTfm[p] = [fkTfm[i].copy(scale=scale), fkTfm[i].copy(translation=pos, scale=scale)]
			interPos = twisterTfm[p][0].translation.lerp(twisterTfm[p][1].translation, .5)
			interTfm[p] = twisterTfm[p][0].copy(translation=interPos)
			
		ctrATfm = twisterTfm["Mid"][0]
		ctrBTfm = twisterTfm["Lwr"][0]
		
		
		# CONTROLLERS
		# Root 
		self.rootBfr = self.addBfr(None, "Root", rootTfm)
		self.rootCtl = self.addCtl(self.rootBfr, "Root", rootTfm, "sphere", size=4, color=self.colorIk())
		# self.addToSubControllers(self.rootCtl)
		attributes.setKeyables(self.rootCtl, constants.ATTRS_T)
		# self.setInversedParameters(self.rootCtl, middle=["posx"], side=["posx"])
		
		# Fk Ref
		# Used as a reference for the upr start twist
		# We cannot use the fk1Bfr cause this one get constrained when fk ref changes
		self.fkRef = self.addRig(self.rootBfr, "FkRef", bfrTfm[0])

		# FK Controlers and Bones
		fkParent = self.fkRef
		boneParent = self.fkRef
		self.fkBfr = []
		self.fkCtl = []
		self.bones = []
		self.stretches = []
		for i, (tfm, btfm) in enumerate(izip(fkTfm, bfrTfm), start=1):
			
			bfr = self.addBfr(fkParent, "Fk%s"%i, btfm)
			ctl = self.addCtl(bfr, "Fk%s"%i, tfm, "sphere", size=8, so=[0,1,1], color=self.colorFk())
	
			if self.settings("lockKneeRotation") and i == 2:
				keyables = ["posx", "posy", "posz", "rotz", "sclx", "scly", "sclz"]
			else:
				keyables = constants.ATTRS_TRS

			if i == 1:
				attributes.setRotOrder(ctl, "XZY")
			attributes.setKeyables(ctl, keyables)
			# self.setInversedParameters(ctl, middle=["posz", "roty", "rotx"])
			
			
			fkParent = ctl
			self.fkBfr.append(bfr)
			self.fkCtl.append(ctl)
			
			bone = self.addRig(boneParent, "Bone{}".format(i), tfm=tfm, icon="bone", so=(self.factor(), 1, 1))
			boneParent = bone
			self.bones.append(bone)

			
		# IK Controllers
		self.rollBfr = self.addBfr(self.rootBfr, "Roll", rollbfrTfm)
		self.rollCtl = self.addCtl(self.rollBfr, "Roll", rollTfm, "jaw", size=1, ro=(-90,0,0), color=self.colorIk())
		#self.rollCtl = self.addCtl(self.rollBfr, "Roll", rollTfm, "jaw", size=2, po=(4,6,0), color=self.colorIk())
		# self.setNeutralPose(self.rollCtl)
		attributes.setKeyables(self.rollCtl, ["rotx", "roty", "rotz", "rotorder", "scly"])
		self.ikRef = self.addRig(self.rollCtl, "IkRef", fkTfm[-2])


		self.ikBfr = self.addBfr(None, "Ik", ikbfrTfm)
		self.ikCtl = self.addCtl(self.ikBfr, "Ik", ikTfm, "cube", size=6, color=self.colorIk())
		attributes.setKeyables(self.ikCtl, constants.ATTRS_TRS)
		# self.setInversedParameters(self.ikCtl, middle=["posx", "rotz", "roty"], side=["posx", "rotz", "roty"])
		attributes.setRotOrder(self.ikCtl, "XZY")

		self.ikoffCtl = self.addCtl(self.ikCtl, "IkOffset", ikTfm, "null", size=4, color=self.colorIk())
		# self.addToSubControllers(self.ikoffCtl)
		attributes.setKeyables(self.ikoffCtl, constants.ATTRS_TRS)
		# self.setInversedParameters(self.ikoffCtl, middle=["posx", "rotz", "roty"], side=["posx", "rotz", "roty"])
		attributes.setRotOrder(self.ikoffCtl, "XZY")

		self.upvBfr = self.addBfr(None, "Upv", upvbfrTfm)
		self.upvCtl = self.addCtl(self.upvBfr, "Upv", upvTfm, "diamond", size=2, color=self.colorIk())
		attributes.setKeyables(self.upvCtl, constants.ATTRS_T)
		# self.setInversedParameters(self.upvCtl, middle=["posx"], side=["posx"])

		self.ctrABfr = self.addBfr(self.bones[0], "CenterA", ctrATfm)
		self.ctrACtl = self.addCtl(self.ctrABfr, "CenterA", ctrATfm, "sphere", size=5, color=self.colorIk())
		# self.addToSubControllers(self.ctrACtl)
		attributes.setKeyables(self.ctrACtl, constants.ATTRS_TRS)
		# self.setInversedParameters(self.ctrACtl, middle=["posz", "roty", "rotx"])

		self.ctrBBfr = self.addBfr(self.bones[1], "CenterB", ctrBTfm)
		self.ctrBCtl = self.addCtl(self.ctrBBfr, "CenterB", ctrBTfm, "sphere", size=5, color=self.colorIk())
		# self.addToSubControllers(self.ctrBCtl)
		attributes.setKeyables(self.ctrBCtl, constants.ATTRS_TRS)
		# self.setInversedParameters(self.ctrBCtl, middle=["posz", "roty", "rotx"])
		
		self.upvCrv = create.cnsCurve(self.getObjectName(config.USE_RIG, "UpvCrv"), [self.upvCtl, self.ctrACtl])
		cmds.setAttr(self.upvCrv+".template", True)

		self.footRef = self.addRig(self.ikoffCtl, "FootRef", ikTfm)

		# Twisters
		self.twisters = defaultdict(list)
		for p in self.twp:
			for s, tfm, factor in izip(["Start", "End"], twisterTfm[p], [1,-1]):
				twister = self.addRig(self.rootBfr, "Tw"+p+s, tfm, "sphere", po=[factor,0,0], so=[2,1,1])
				# self.setNeutralPose(twister)
				self.twisters[p].append(twister)
		
		# Inter
		self.inters = {}
		for p in self.twp:
			self.inters[p] = self.addRig(self.rootBfr, "Inter"+p, interTfm[p], "pyramid")
			 
			
	def createJoints(self):
		for p in self.twp:
			for s, twister in izip(["Start", "End"], self.twisters[p]):
				self.addJnt(twister,  "Tw"+p+s)
			
		self.addJnt(self.ctrACtl, "CenterA")
		self.addJnt(self.ctrBCtl, "CenterB")
		self.addJnt(self.bones[3], "Foot")
		
		
	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend") == "IK", 0, 1)
		self.showCtrlAttr = self.addAnimAttr("ShowCtrl", "bool", False) 
		self.rollAttr = self.addAnimAttr("Roll", "float", 0, -180, 180)

		self.scaleAAttr = self.addAnimAttr("ScaleA", "float", 1, None, None)
		self.scaleBAttr = self.addAnimAttr("ScaleB", "float", 1, None, None)
		self.maxStretchAttr = self.addAnimAttr("MaxStretch", "float", self.settings("stretchDefault"), 1, None)
		self.slideAttr = self.addAnimAttr("Slide", "float", .5, 0, 1)
		self.reverseAttr = self.addAnimAttr("Reverse", "float", self.settings("reverseDefault"), 0, 1)
		self.softnessAttr = self.addAnimAttr("Softness", "float", 0, 0, 1)

		self.lengthAAttr = self.addSetupAttr("LengthA", "float", self.lengths[0])
		self.lengthBAttr = self.addSetupAttr("LengthB", "float", self.lengths[1])
		self.lengthCAttr = self.addSetupAttr("LengthC", "float", self.lengths[2])
			
	def createLayout(self): 
		pass
		
	# ------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibility
		fkCompare = self.addCompound("compare", "FkViz", self.blendAttr, 1, "<")
		ikCompare = self.addCompound("compare", "IkViz", self.blendAttr, 0, ">")

		cmds.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
		cmds.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

		for ctl in self.fkCtl:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		ikCtls = [self.rootCtl, self.ikCtl, self.ikoffCtl, self.upvCtl, self.upvCrv, self.rollCtl]
		if self.settings("rollUpVController"):
			ikCtls.append(self.rollUpvCtl)
		for ctl in ikCtls:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		#Fk Ik Solver
		iks = [self.rootCtl, self.ikRef, self.upvCtl]
		ikfkNode = self.addCompound("fkik2Bones", "ZLeg", iks, self.fkCtl, self.bones, 
									self.lengths[0], self.lengths[1], self.negate())
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

		# Roll
		self.addCompound("blendMatrix", "RollCns", self.rollBfr, [self.footRef], maintainOffset=True)
		axis = "{s}y{s}z".format(s=self.sign())
		if self.settings("rollUpVController"):
			self.addCompound("aimConstraint", "RollAim", self.rollBfr, self.rollUpvCtl, axis=axis, upMaster=self.upvCtl, maintainOffset=False)
		else:
			self.addCompound("aimConstraint", "RollAim", self.rollBfr, self.rootCtl, axis=axis, upMaster=self.upvCtl, maintainOffset=False)

		# Last Bone
		cns = self.addCompound("blendMatrix", "BoneCns", self.bones[-1], [self.fkCtl[-1], self.footRef], maintainOffset=True)
		cmds.connectAttr(self.blendAttr, cns+".target[1].weight")

		# Center
		for i, ctrBfr in enumerate([self.ctrABfr, self.ctrBBfr]):
			posBone = self.bones[i+1]
			oriBones = self.bones[i:i+2]
			attributes.inheritsTransform(ctrBfr, False)
			node = self.addNode("decomposeMatrix", "CtrDM")
			cmds.connectAttr(posBone+".worldMatrix[0]", node+".inputMatrix")
			cmds.connectAttr(node+".outputTranslate", ctrBfr+".translate")
			self.addCompound("orientConstraint", "CtrOri", ctrBfr, oriBones)
			cmds.connectAttr(self.nodes("local")+".scale", ctrBfr+".scale")

		# Twisters
		self._twisterCns(self.twisters["Upr"][0], self.bones[0], self.ctrACtl, self.fkRef, self.bones[0], self.sign() + "xz", self.lengths[0], pntAtDouble=False)
		self._twisterCns(self.twisters["Upr"][1], self.ctrACtl, self.bones[0], self.ctrACtl, self.ctrABfr, self.nsign() + "xz", self.lengths[0], pntAtDouble=False)

		self._twisterCns(self.twisters["Mid"][0], self.ctrACtl, self.ctrBCtl, self.ctrACtl, self.ctrABfr, self.sign() + "xz", self.lengths[1], pntAtDouble=False)
		self._twisterCns(self.twisters["Mid"][1], self.ctrBCtl, self.ctrACtl, self.ctrBCtl, self.ctrBBfr, self.nsign() + "xz", self.lengths[1], pntAtDouble=False)

		self._twisterCns(self.twisters["Lwr"][0], self.ctrBCtl, self.bones[-1], self.ctrBCtl, self.ctrBBfr, self.sign() + "xz", self.lengths[2], pntAtDouble=False)
		self._twisterCns(self.twisters["Lwr"][1], self.bones[-1], self.ctrBCtl, self.bones[3], self.bones[2], self.nsign() + "xy", self.lengths[2], pntAtDouble=False)

		# Inter
		for p in self.twp:
			cmds.pointConstraint(self.twisters[p], self.inters[p])
			cns = self.addCompound("aimConstraint", p+"InterAim", self.inters[p], self.twisters[p][1], axis="x-z")
			self.addCompound("spinePointAt", p+"InterPtAt", cns, self.twisters[p][0], self.twisters[p][1], blend=.5, solver=1) 

		
	def _twisterCns(self, tws, pos, aim, pntAt, pntAtRef, axis, distance, pntAtDouble=True):
		attributes.inheritsTransform(tws, False)

		# Position
		node = self.addNode("decomposeMatrix", "TwsDM")
		cmds.connectAttr(pos+".worldMatrix[0]", node+".inputMatrix")
		cmds.connectAttr(node+".outputTranslate", tws+".translate")

		# Rotation 
		if pntAtDouble:
			cns = self.addCompound("aimConstraint", "TwsAim", tws, aim, axis=axis, upMaster=None, upVector=(0,0,1), maintainOffset=False)
			self.addCompound("pointAtDoubleAxisNode", "TwsPtAt", cns, pntAtRef, pntAt, axis="z")
		else:
			self.addCompound("aimConstraint", "TwsAim", tws, aim, axis=axis, upMaster=pntAt, upVector=(0,0,1), maintainOffset=False)

		dist_Node = self.addNode("distanceBetween", "twsScaleDist")
		cmds.connectAttr(pos+".worldMatrix[0]", dist_Node+".inMatrix1")
		cmds.connectAttr(aim+".worldMatrix[0]", dist_Node+".inMatrix2")
		div_Node = self.addNode("multiplyDivide", "twsScaleRatio")
		cmds.setAttr(div_Node+".operation", 2) # Division
		cmds.connectAttr(dist_Node+".distance", div_Node+".input1X")
		cmds.setAttr(div_Node+".input2X", distance)
		cmds.connectAttr(div_Node+".outputX", tws+".scaleX")
		cmds.connectAttr(self.nodes("local")+".sx", tws+".scaleY")
		cmds.connectAttr(self.nodes("local")+".sx", tws+".scaleZ")

	#----------------------------------------------------------------------------
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
		
		# Fk Orient
		if "FK" in self.connections():
			obj = self.getObject(config.USE_BFR, "Fk1")
			self.connections("FK").connect(obj, attrName="FKOrient")