from itertools import izip

from maya import cmds

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

class ChainSystemBuilder(SystemBuilder):
	
	def createObjects(self):
		# Settings
		self.isFk = "FK" in self.settings("kinematic")
		self.isIk = "IK" in self.settings("kinematic")
		self.isFkIk = self.isFk and self.isIk
		
		# TRANSFORMATION
		# Positions 
		positions = self.translations("Part")

		# Normal
		if self.count("Part") > 2:
			normal = Vector3.planeNormal(*positions[:3])
			if normal.length() < 1E-6:
				normal = self.directions("Part1", "z")
			if self.negate(): 
				normal *= -1
		else:
			normal = self.directions("Part1", "z")

		boneTfm = TransformationArray.chain(positions, normal, axis="xz", negativeSide=self.negate(), endTransform=False)
		d = [(positions[i],positions[i+1]) for i in range(self.count("Part")-1)]
		boneLen = [Vector3.distance(a,b) for a,b in d]

		self.setSettings(count=len(boneLen), lengths=boneLen)
		
		if self.settings("setNeutralPose"):
			bfrTfm = boneTfm
		else:
			bfrTfm = [tfm.copy(rotation=boneTfm[max(i-1,0)].rotation) for i, tfm in enumerate(boneTfm)]
		
		if self.isIk:
			ikTfm = boneTfm[-1].copy(translation=positions[-1])
			
			# Up Vector
			if self.count("Part") > 2:
				upvTfm = Transformation.fromParts(translation=umath.upVector(positions[0], positions[2], normal, ratio=1, negate=self.negate()))
			else:
				upvTfm = Transformation.fromParts(translation=umath.upVector(positions[0], positions[1], normal, ratio=1, negate=self.negate()))
			

		if self.settings("dynamic"):
			tgtTfm = boneTfm[1:]
			tgtTfm = tgtTfm.appended(boneTfm[-1].copy(translation=positions[-1]))
			

		# OBJECTS

		# Root
		self._root = self.addRig(None, "Root", tfm=boneTfm[0])
		
		# FK Controllers -----------------------------------------
		if self.isFk:
			self.fkBfr = []
			self.fkCtl = []
			self.fkDir = []
			parent = self._root
			for i, (tfm, btfm, dist) in enumerate(izip(boneTfm, bfrTfm, boneLen), start=1):
				
				fkBfr = self.addBfr(parent, "Fk{}".format(i), tfm=btfm)
				fkCtl = self.addCtl(fkBfr, "Fk{}".format(i), tfm, "sphere", so=[0,1,1], color=self.colorFk())
										  
				# self.setInversedsettings(fkCtl, middle=["posz", "rotx", "roty"])
				attributes.setRotOrder(fkCtl, self.settings("defaultRotationOrder"))

				parent = fkCtl

				self.fkBfr.append(fkBfr)
				self.fkCtl.append(fkCtl)

				bone = self.addRig(fkCtl, "Dir{}".format(i), tfm, "pyramid", size=1, ro=[0,0,-90], so=[.5,self.factor()*dist,.5])

				self.fkDir.append(bone)

			# Add the end reference for ikfk matching
			tfm = boneTfm[-1].copy(translation=positions[-1])
			self._tip = self.addRig(self.fkCtl[-1], "Tip", tfm)
				
		# IK Controllers --------------------------------------
		if self.isIk:
			# Ik Controller
			self.ikBfr = self.addBfr(self._root, "Ik", tfm=ikTfm)
			self.ikCtl = self.addCtl(self.ikBfr, "Ik", ikTfm, "cube",  size=2, color=self.colorIk())
			attributes.setKeyables(self.ikCtl, constants.ATTRS_TR)

			# UpVector Controller
			self.upvBfr = self.addBfr(self._root, "UpV", upvTfm)
			self.upvCtl = self.addCtl(self.upvBfr, "UpV", upvTfm, "diamond", color=self.colorIk())
			attributes.setKeyables(self.upvCtl, constants.ATTRS_T)

			# Ik Chain
			self.ikBones, self.effector, self.handle = create.chain(self.getObjectName(config.USE_RIG, "Ik"), self._root, positions, normal, negate=self.negate())
			
			self.upvCrv = create.cnsCurve([self.ikChn.root(), self.upvCtl, self.ikChn.effector()], "UpvCrv")
			cmds.setAttr(self.upvCrv+".template", True)

		# Bones -------------------------------
		if self.isFkIk:# or (self.isFk and self.settings("dynamic")):
			self.bones = []
			parent = self._root
			for i, (tfm, dist) in enumerate(izip(boneTfm, boneLen), start=1):
				bone = self.addRig(parent, "Bone{}".format(i), tfm, "cube", size=1, po=[self.factor()*dist*.5,0,0], so=[dist,.5,.5])

				self.bones.append(bone)
				parent = bone

		elif self.isFk:
			self.bones = self.fkCtl
		else:
			self.bones = self.ikChn.bones()

		# Dynamic ----------------------------
		if self.settings("dynamic"):
			self.dfmHost = []
			self.dynCns = []
			self.target = []
			self.harmonic = []
			self.dynBone = []
			parent = self._root
			for i, (bone, tfmA, tfmB) in enumerate(izip(self.bones, boneTfm, tgtTfm), start=1):

				dynCns = self.addRig(parent, "DynCns{}".format(i), tfmA, "cube", size=1)
				self.dynCns.append(dynCns)
				target = self.addRig(dynCns, "Target{}".format(i), tfmB, "null", size=1)
				self.target.append(target)
				harmonic = self.addRig(target, "Harmonic{}".format(i), tfmB, "diamond", size=1)
				self.harmonic.append(harmonic)
			
				dynBone = self.addRig(parent, "Dynamic{}".format(i), tfmA, "pyramid", size=1, ro=[0,0,-90], so=[1,self.factor(),1])
				self.dynBone.append(dynBone)
				parent = dynBone
				self.dfmHost.append(dynBone)
		else:
			self.dfmHost = self.bones


		# Strap ----------------------------
		if self.settings("strap"):
			endTfm = boneTfm[-1].copy(translation=positions[-1])
			self.end = self.addRig(self.dfmHost[-1], "End", endTfm)

	def createJoints(self):
		centers = [self.addJnt(master, i) for i, master in enumerate(self.dfmHost, start=1)]
			
		# Strap ----------------------------
		if self.settings("strap"):
			centers.append(self.addJnt(self.end, "End"))

			name = self.getObjectName(config.USE_RIG, "Strap")
			surface = create.cnsSurface(name, self._root, centers, width=1.0, tangent=.25)
		 	self.addSurfaceJnts(surface, self.settings("strapDeformers"))

	#----------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		# Settings
		self.isFk = "FK" in self.settings("kinematic")
		self.isIk = "IK" in self.settings("kinematic")
		self.isFkIk = self.isFk and self.isIk

		if self.isFkIk:
			self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend")=="IK", 0, 1)
			self.showCtrlAttr = self.addAnimAttr("showCtrl", "bool", False) 

			self.addSetupAttr("Count", "short", len(self.fkCtl))
		
		if self.isIk:
			self.rollAttr = self.addAnimAttr("Roll", "float", 0, -180, 180)

		if self.settings("dynamic"):
			self.dynamicAttr = self.addAnimAttr("Dynamic", "bool", self.settings("dynActive"))
			self.globalAmplAttr = self.addAnimAttr("GlobalAmplitude", "float", self.settings("amplitude"), 0, 5)
			self.localAmplAttr = [self.addAnimAttr("LocalAmplitude{}".format(i), "float", 1, 0, 10) for i in xrange(1, self.count("Part"))]
			
			if self.settings("dynamicAnimatable"):
				self.axisAttr = self.addAnimAttr("Axis", "double3", (self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))
				self.decayAttr = self.addAnimAttr("Decay", "float", self.settings("decay"), 0, 10)
				self.terminationAttr = self.addAnimAttr("Termination", "float", self.settings("termination"), 0, 1)
				self.frequencyAttr = self.addAnimAttr("Frequency", "float", self.settings("frequency"), 0, 1)

	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibilities
		if self.isFkIk:
			fkCompare = self.addCompound("compare", "FkViz", self.blendAttr, 1, "<")
			ikCompare = self.addCompound("compare", "IkViz", self.blendAttr, 0, ">")

			cmds.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
			cmds.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

			for ctl in self.fkCtl:
				for shp in cmds.listRelatives(ctl, shapes=True):
					cmds.connectAttr(fkCompare+".outColorR", shp+".visibility", force=True)

			for ctl in [self.ikCtl, self.upvCtl, self.upvCrv]:
				for shp in cmds.listRelatives(ctl, shapes=True):
					cmds.connectAttr(ikCompare+".outColorR", shp+".visibility", force=True)

		# IK Chain
		if self.isIk:
			# Constraint and up vector
			cmds.poleVectorConstraint(self.upvCtl, self.handle)
			cmds.connectAttr(self.rollAttr, self.handle+".twist")

			mmNode = cmds.createNode("multMatrix")
			dmNode = cmds.createNode("decomposeMatrix")

			cmds.connectAttr(self.ikCtl+".worldMatrix[0]", mmNode+".matrixIn[0]")
			cmds.connectAttr(self.handle+".parentInverseMatrix[0]", mmNode+".matrixIn[1]")
			cmds.connectAttr(mmNode+".matrixSum", dmNode+".inputMatrix")
			cmds.connectAttr(dmNode+".outputTranslate", self.handle+".translate")

		if self.isFk:
			for i, (fkBone, fkCtl) in enumerate(izip(self.fkDir, self.fkCtl)):
				if i < (len(self.bones)-1):
					master = self.fkCtl[i+1]
				else:
					master = self._tip
					
				self.addCompound("aimConstraint", "FkAim", fkBone, master, axis=self.sign()+"xy", upMaster=fkCtl, upVector=(0,1,0))
				
		# # Bones -----------------------------------------
		if self.isFkIk:# or (self.isFk and self.settings("dynamic")):
			for i, (bone, fkDir, ikBone) in enumerate(izip(self.bones, self.fkDir, self.ikBones)):
				slave = bone
				masters = [fkDir, ikBone]

				bmNode = self.addCompound("blendMatrix", "FkIk", slave, masters, maintainOffset=False)
				cmds.connectAttr(self.blendAttr, bmNode+".target[1].weight")

					
		if self.settings("dynamic"):
			for i, (harmonic, target, dynCns, dynBone, bone) in enumerate(izip(self.harmonic, self.target, self.dynCns, self.dynBone, self.bones)):
				cns = self.addCompound("harmonic", "Dyn{}".format(i), harmonic, target, 
					amplitude=1.0, 
					decay=self.settings("decay"), 
					frequency=self.settings("frequency"), 
					termination=self.settings("termination"), 
					amplitudeAxis=(self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))

				if i%3 == 0:
					mulNode = self.addNode("multiplyDivide", name="AmplitudeGlobal{}".format(i))

					# Connect to Attributes
					mulNode = self.getObjectName(config.USE_NDE, "AmplitudeGlobal{}".format(i))
					cmds.connectAttr(self.globalAmplAttr, mulNode+".input1X")
					cmds.connectAttr(self.globalAmplAttr, mulNode+".input1Y")
					cmds.connectAttr(self.globalAmplAttr, mulNode+".input1Z")

					activeNode = self.addNode("multiplyDivide", name="Active{}".format(i))
					cmds.connectAttr(mulNode+".output", activeNode+".input1")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2X")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2Y")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2Z")

				axis = "XYZ"[i%3]
				cmds.connectAttr(self.localAmplAttr[i], mulNode+".input2"+axis)
				cmds.connectAttr(activeNode+".output"+axis, cns+".amplitude")

				if self.settings("dynamicAnimatable"):
					cmds.connectAttr(self.axisAttr, cns+".axisAmp")
					cmds.connectAttr(self.decayAttr, cns+".decay")
					cmds.connectAttr(self.terminationAttr, cns+".termination")
					cmds.connectAttr(self.frequencyAttr, cns+".frequencyMult")

				cns = self.addCompound("aimConstraint", "DynAim", dynBone, harmonic, axis=self.sign()+"xy", upMaster=dynCns, upVector=(0,1,0))
				self.addCompound("blendMatrix", "DynCns", dynCns, [bone], translate=False, rotate=True, scale=False)

	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Root" in self._connections:
			obj = self.getObject(config.USE_RIG, "Root")
			self.connections("Root").connect(obj, attrName="RootParent")

		if "IK" in self._connections:
			obj = self.getObject(config.USE_BFR, "Ik")	
			self.connections("IK").connect(obj, attrName="IKParent")

		if "UpVector" in self._connections:
			obj = self.getObject(config.USE_BFR, "UpV")	
			self.connections("UpVector").connect(obj, attrName="UpVParent")

		if "FK" in self._connections:
			obj = self.getObject(config.USE_BFR, "Fk1")
			self.connections("FK").connect(obj, attrName="FKOrient")


