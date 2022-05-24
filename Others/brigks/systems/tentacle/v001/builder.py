from itertools import izip

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3

from brigks import config
from brigks.utils import attributes, create
from brigks.systems.systemBuilder import SystemBuilder

class TentacleSystemBuilder(SystemBuilder):
	
	def createObjects(self):

		# Settings
		self.isFk = "FK" in self.settings("kinematic")
		self.isIk = "IK" in self.settings("kinematic")
		self.isFkIk = self.isFk and self.isIk
		self.isNotIk = self.isFk and not self.isIk
		self.isNotFk = not self.isFk and self.isIk
		
		size = self.translations("Part")[0].distance(self.translations("Part")[1]) * 0.25
		
		# TRANSFORMATION
		# Normal
		if self.count("Part") > 2:
			normal = Vector3.planeNormal(*self.translations("Part")[:3])
			direction = self.translations("Part")[-1] - self.translations("Part")[0]
			if normal.length() < 1E-6:
				normal = self.directions("Part1", "z")
			if self.negate(): 
				normal *= -1
		else:
			direction = self.directions("Part1", "x")
			normal = self.directions("Part1", "z")

		boneTfm = TransformationArray.chain(self.translations("Part"), normal, negativeSide=self.negate(), endTransform=False)

		d = [(self.translations("Part")[i],self.translations("Part")[i+1]) for i in range(self.count("Part")-1)]
		self.distances = [Vector3.distance(a,b) for a,b in d]
		
		endTfm = boneTfm[-1].copy(translation=self.translations("Part")[-1])
		boneTfm = boneTfm.appended(endTfm)
		self.distances.append(0.0)

		# Create extra transforms on end points
		for i in xrange(self.settings("extraControllers")):
			extraPos = Vector(self.settings("extraControllerSpacing")*(i+1),0,0) * endTfm
			extraTfm = endTfm.copy(translation=extraPos)
			boneTfm = boneTfm.appended(extraTfm)
			self.distances.append(0.0)


		self.setSettings(count=len(self.distances), lengths=self.distances)

		self.initialCount = self.count("Part")
		
		if self.settings("setNeutralPose"):
			bfrTfm = boneTfm
		else:
			bfrTfm = [tfm.copy(rotation=boneTfm[max(i-1,0)].quaternion) for i, tfm in enumerate(boneTfm)]

		if self.settings("dynamic"):
			
			dynTfm = []
			for i, posA in enumerate(self.translations()[:-1]):
				posB = self.translations()[i+1]
				dynTfm.append(Transform.LookingAt(posA, posB, normal, self.nsign()+"yz", self.negate()))

		self.normal = normal.copy()
		self.normal.normalize()
		self.direction = direction.copy()
		self.direction.normalize()

		# OBJECTS

		# Root
		rootBfr = self.addBfr(None, "Root", tfm=boneTfm[0])
		if self.settings("addRootCtrl"):
			self._root = self.addCtl(rootBfr, "Root", boneTfm[0], "sphere", size=size*1.5, color=self.colorFk())
		else:
			self._root = rootBfr
		
		# FK Controllers -----------------------------------------
		if self.isFk:
			self.fkBfr = []
			self.fkCtl = []
			parent = self._root
				
			for i, (tfm, btfm, dist) in enumerate(izip(boneTfm, bfrTfm, self.distances), start=1):
				if self.negate():
					dist *= -1
				fkBfr = self.addBfr(parent, "Fk{}".format(i), tfm=btfm)
				fkCtl = self.addCtl(fkBfr, "Fk{}".format(i), tfm, "cube", po=[dist*0.5,0,0], so=[dist*0.9,size,size], color=self.colorFk())
										  
				# self.setInversedsettings(fkCtl, middle=["posz", "rotx", "roty"])
				attributes.setRotOrder(fkCtl, self.settings("defaultRotationOrder"))

				parent = fkCtl

				self.fkBfr.append(fkBfr)
				self.fkCtl.append(fkCtl)
		else:
			self.fkCtl = len(boneTfm) * [None]
				
		# IK Controllers --------------------------------------
		if self.isIk:
			self.ikBfr = []
			self.ikCtl = []
			self.ikRoot = self.addBfr(self._root, "IkRoot", boneTfm[0])
			
			for i, (tfm, btfm) in enumerate(izip(boneTfm, bfrTfm), start=1):
				if i == 1:
					parent = self._root
				else:
					parent = self.ikRoot
					
				ikBfr = self.addBfr(parent, "Ik{}".format(i), tfm=btfm)
				ikCtl = self.addCtl(ikBfr, "Ik{}".format(i), tfm, "sphere", size=size, color=self.colorIk())
				
				# self.setInversedsettings(ikCtl, middle=["posz","rotx","roty"])
				attributes.setRotOrder(ikCtl, self.settings("defaultRotationOrder"))
				
				self.ikBfr.append(ikBfr)
				self.ikCtl.append(ikCtl)
		else:
			self.ikCtl = len(boneTfm) * [None]

		# Bones -------------------------------
		if self.isFkIk or (self.isFk and self.settings("dynamic")):
			self.bones = []
			parent = self._root
			for i, (tfm, dist) in enumerate(izip(boneTfm, self.distances), start=1):
				if self.negate():
					dist *= -1
				bone = self.addRig(parent, "Bone{}".format(i), tfm, "cube", size=1, po=[dist*.5,0,0], so=[0,.5 * size,.5 * size])
				
				self.bones.append(bone)
				parent = bone
			
		elif self.isFk:
			self.bones = self.fkCtl
		else:
			self.bones = self.ikCtl
			
			
		# Dynamic ----------------------------
		if self.settings("dynamic"):
			self.dfmHost = []
			self.dynCns = []
			self.target = []
			self.harmonic = []
			self.dynBone = []
			parent = self._root
			for i, (bone, tfmA, tfmB) in enumerate(izip(self.bones[:-1], boneTfm[:-1], boneTfm[1:]), start=1):
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
			# Add the tip, since the tentacle has the tip
			dynBone = self.addRig(parent, "Dynamic{}".format(len(self.bones)), boneTfm[-1], "pyramid", size=1, ro=[0,0,-90], so=[1,self.factor(),1])
			self.dynBone.append(dynBone)
			self.dfmHost.append(dynBone)
		else:
			self.dfmHost = self.bones
			
		# Roll Controllers ----------------------------
		self.rollBfr = []
		self.rollCtl = []
		# self.upv = []
		if self.settings("addRoll"):
			for i, (bone, tfm) in enumerate(izip(self.dfmHost, boneTfm), start=1):
				if self.negate():
					rollScl = -2
				else:
					rollScl = 2
				rollBfr = self.addBfr(bone, "Roll{}".format(i), tfm=tfm)
				rollCtl = self.addCtl(rollBfr, "Roll{}".format(i), tfm, "pyramid", size=size, so=[1,rollScl,0], color=self.colorIk())
				
				# self.setInversedsettings(rollCtl, middle=["posz","rotx","roty"])
				attributes.setRotOrder(rollCtl, self.settings("defaultRotationOrder"))
				attributes.setKeyables(rollCtl, ["rotx"])
				
				# self.addToSubControllers(rollCtl)
				upvPar = rollCtl
				
				self.rollBfr.append(rollBfr)
				self.rollCtl.append(rollCtl)

		# UI Hosts ----------------------------
		self.hosts = []
		for i, (bone, btfm) in enumerate(izip(self.dfmHost, boneTfm), start=1):
			host = self.addCtl(bone, "Host{}".format(i), btfm, "gear", size=size*1.5, color=self.colorFk())
			attributes.setKeyables(host, [])

			self.hosts.append(host)

			
		# Tangents ----------------------------
		self.tangentBfr = []
		self.tangentSolvers = []
		self.tangentCtl = []
		self.tanCrvs = []
		points = []
		for i, (bone, btfm, dist) in enumerate(izip(self.dfmHost, boneTfm, self.distances)):
			tanBfrs = []
			tanSolvers = []
			tanCtls = []

			if i:
				tangent = self._createTangentObjects("InTangent", i, size, bone, btfm, -self.distances[i-1]*0.333, "cube")
				
				tanBfrs.append(tangent[0])
				tanSolvers.append(tangent[1])
				tanCtls.append(tangent[2])
			else:
				tanBfrs.append(None)
				tanSolvers.append(None)
				tanCtls.append(None)
			
			if i != len(self.bones)-1:
				tangent = self._createTangentObjects("OutTangent", i, size, bone, btfm, dist*0.333, "diamond")
				
				tanBfrs.append(tangent[0])
				tanSolvers.append(tangent[1])
				tanCtls.append(tangent[2])
			else:
				tanBfrs.append(None)
				tanSolvers.append(None)
				tanCtls.append(None)
				
			self.tangentBfr.append(tanBfrs)
			self.tangentSolvers.append(tanSolvers)
			self.tangentCtl.append(tanCtls)

			# Draw helper lines for the tangents. Start by filtering out empty entries from the centers list
			centers = [item for item in [tanCtls[0], bone, tanCtls[1]] if item]

			tanCrv = create.cnsCurve("TanCrv{}".format(i+1), centers, degree=1)
			cmds.setAttr(tanCrv+".template", True)
			self.tanCrvs.append(tanCrv)
			
		# Curve ----------------------------
		self.curvePar = self.addRig(None, "Curve")
		cmds.setAttr(self.curvePar+".template", True)

	def _createTangentObjects(self, prefix, i, size, bone, btfm, dist, icon):
		pos = Vector3([dist,0,0]) * btfm.asMatrix()
		tfm = btfm.copy(translation=pos)
		tanBfr = self.addBfr(bone, "{s}{i}".format(s=prefix,i=i+1), tfm=tfm)
		tanSolve = self.addRig(tanBfr, "{s}Solve{i}".format(s=prefix,i=i+1), tfm=tfm)
		tanCtl = self.addCtl(tanSolve, "{s}{i}".format(s=prefix,i=i+1), tfm, icon, size=size * 0.5, color=self.colorIk())
		attributes.setKeyables(tanCtl, ["posx","posy","posz"])
		
		# self.addToSubControllers(tanCtl)
		
		return tanBfr, tanSolve, tanCtl

	def createJoints(self):
		self.dfm = []
		for i in xrange(self.settings("jointsCount")):
			dfm = self.addJnt(self.curvePar, "Part{}".format(i+1))
			self.dfm.append(dfm)
		
		self.segDfm = []
		for i in xrange(self.settings("lowJointsCount")):
			dfm = self.addJnt(self.curvePar, "Low{}".format(i+1))
			self.segDfm.append(dfm)
		

	#----------------------------------------------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		if self.isFkIk:
			self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend")=="IK", 0, 1)
			self.showCtrlAttr = self.addAnimAttr("ShowCtrl", "bool", False)

		# Curve Attributes
		self.lengthAttr = self.addAnimAttr("LengthMultiply", "float", 1, sugMinimum=0, sugMaximum=2)
		self.slideAttr = self.addAnimAttr("Slide", "float", 0, sugMinimum=-1.0, sugMaximum=1.0)

		self.ctrlNumberAttr = self.addAnimAttr("ControlCount", "short", self.initialCount, 2, len(self.bones))
			
		# Bone Attributes
		# Build with the default attribute command rather than the harbie attribute command to preserve shorter names
		# This also allows the user to change the attributes of multiple objects at the same time
		self.tanVisAttr = []
		self.pinAttrs = []
		self.pinLocAttr = []
		self.useRollAttr = []
		currentLength = 0
		length = sum(self.distances)
		for i, (host, dist) in enumerate(izip(self.hosts, self.distances), start=1):
			self.tanVisAttr.append(self.addAttr(host, "TanVisible", "bool", False, writable=True, keyable=True))
			pinLoc = currentLength / length
			if i==1:
				weightVal = 1
			else:
				weightVal = 0
			pinWeightAttr = self.addAttr(host, "PinWeight", "float", weightVal, 0, 1, writable=True, keyable=True)
			pinLocAttr = self.addAttr(host, "PinLocation", "float", pinLoc, 0, 1, writable=True, keyable=True)
			self.pinAttrs.append({"paramValue":pinLocAttr, "paramWeight":pinWeightAttr})
			currentLength += dist
			self.useRollAttr.append(self.addAttr(host, "UseRoll", "float", 1, 0, 1, writable=True, keyable=True))

		# Tangent Attributes
		self.tangentAttrs = []
		for i,tanSet in enumerate(self.tangentCtl, start=1):
			attrSet = []
			for tangent in tanSet:
				if tangent:
					weightAttr = self.addAttr(tangent, "Weight", "float", 1, 0, 10, writable=True, keyable=True)
					smoothAttr = self.addAttr(tangent, "Smooth", "float", 1, 0, 1, writable=True, keyable=True)
					autoAttr = self.addAttr(tangent, "Auto", "float", 1, 0, 1, writable=True, keyable=True)

					attrSet.append({"weight":weightAttr, "smooth":smoothAttr, "auto":autoAttr})
				else:
					attrSet.append(None)
			self.tangentAttrs.append(attrSet)
		
		self.addSetupAttr("Count", "short", len(self.distances))

		for i, dist in enumerate(self.distances):
			attr = self.addSetupAttr("Length{}".format(i), "float", dist)

		# Dynamic Attributes
		if self.settings("dynamic"):
			self.dynamicAttr = self.addAnimAttr("dynamic", "bool", self.settings("dynActive"))
			self.globalAmplitudeAttr = self.addAnimAttr("globalAmplitude", "float", self.settings("amplitude"), 0, 5)
			self.localAmplitudeAttr = [self.addAnimAttr("localAmplitude{}".format(i), "float", 1, 0, 10) for i in xrange(1, self.count("Part"))]
			
			if self.settings("dynamicAnimatable"):
				self.axisAttr = self.addAnimAttr("axis", "vector", (self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))
				self.decayAttr = self.addAnimAttr("decay", "float", self.settings("decay"), 0, 10)
				self.terminationAttr = self.addAnimAttr("termination", "float", self.settings("termination"), 0, 1)
				self.frequencyAttr = self.addAnimAttr("frequency", "float", self.settings("frequency"), 0, 1)

	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		if not cmds.pluginInfo("TwistSpline", q=True, loaded=True):
			cmds.loadPlugin("TwistSpline")

		# Visiblities --------------------------------
		if self.isFkIk:
			fkCompare = self.addCompound("compare", "FkViz", self.blendAttr, 1, "<")
			ikCompare = self.addCompound("compare", "IkViz", self.blendAttr, 0, ">")

			self.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
			self.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

			for ctl in self.fkCtl:
				for shp in cmds.listRelatives(ctl, shapes=True):
					cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

			for ctl in self.ikCtl:
				for shp in cmds.listRelatives(ctl, shapes=True):
					cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		# Visibility based on the specified number of controllers
		compareNodes = []
		for i in xrange(len(self.bones)):
			visCompare = self.addCompound("compare", "Viz{}".format(i), self.ctrlNumberAttr, i+1, ">=")
			if self.isFk:
				cmds.connectAttr(visCompare+".outColorR", self.fkBfr[i]+".visibility")
			if self.isIk:
				cmds.connectAttr(visCompare+".outColorR", self.ikBfr[i]+".visibility")

			if self.isFkIk or (self.isFk and self.settings("dynamic")):
				cmds.connectAttr(visCompare+".outColorR", self.bones[i]+".visibility")

			compareNodes.append(visCompare)

		compareNodes.append(None)
		for i, tanBfr in enumerate(self.tangentBfr):
			if compareNodes[i+1] and tanBfr[1]:
				cmds.connectAttr(compareNodes[i+1]+".outColorR", tanBfr[1]+".visibility")

		# Bones --------------------------------------
		if self.isFkIk:
			for i, (bone, fkCtl, ikCtl) in enumerate(izip(self.bones, self.fkCtl, self.ikCtl)):
				cns = self.addCompound("blendMatrix", "IkFk()".format(i), bone, [fkCtl, ikCtl])
				cmds.connectAttr(self.blendAttr, cns+".target[1].weight")

		# Tangents -----------------------------------
		prevTwist = None
		self.twistTans = []
		for i, (bone, tangents, tanAttrs) in enumerate(izip(self.dfmHost, self.tangentSolvers, self.tangentAttrs), start=1):
			if i == 1:
				centers = [None, bone, self.bones[i]]
				# Disable smooth for half-tangent
				cmds.setAttr(tanAttrs[1]["smooth"], 0)
			elif i == len(self.bones):
				centers = [self.bones[i-2], bone, None]
				# Disable smooth for half-tangent
				cmds.setAttr(tanAttrs[0]["smooth"], 0)
			else:
				centers = [self.bones[i-2], bone, self.bones[i]]
			twistTans = self._createTangentOperators(centers, tangents, i, prevTwist, tanAttrs, compareNodes[i])
			self.twistTans.append(twistTans)
			prevTwist = twistTans[1]

		for tangents, tanCrv, visAttr in izip(self.tangentCtl, self.tanCrvs, self.tanVisAttr):
			for tanCtl in tangents:
				if tanCtl:
					for shp in cmds.listRelatives(tanCtl, shapes=True):
						cmds.connectAttr(visAttr, shp+".visibility")
			for shp in cmds.listRelatives(tanCrv, shapes=True):
				cmds.connectAttr(visAttr, shp+".visibility")

		# Curve ------------------------------
		# Delete the shape of the curve object and replace with a twistSpline node
		shapes = cmds.listRelatives(self.curvePar, shapes=True)
		cmds.delete(shapes)
		# Using maya createNode command rather than the self._createNode because we need to attach it to the curve transform
		name = self.getObjectName(config.USE_RIG, "CurveShape")
		self.curve = cmds.createNode("twistSpline", name=name, parent=self.curvePar)
		for i, (bone, tangent) in enumerate(izip(self.dfmHost, self.tangentCtl)):
			vertexAttr = "vertexData[{}]".format(i)
			cmds.connectAttr(bone+".worldMatrix", self.curve+".{}.controlVertex".format(vertexAttr))
			cmds.setAttr(self.curve+".{}.twistWeight".format(vertexAttr), 1.0)
			if tangent[0]:
				cmds.connectAttr(tangent[0]+".worldMatrix", self.curve+".{}.inTangent".format(vertexAttr))
			if tangent[1]:
				cmds.connectAttr(tangent[1]+".worldMatrix", self.curve+".{}.outTangent".format(vertexAttr))

		cmds.connectAttr(self.ctrlNumberAttr, self.curve+".maxVertices")

		# Connect the pin params after we know the full length of the curve
		curveLength = cmds.getAttr(self.curve+".splineLength")
		scalingMult = self.addNode("multDoubleLinear", "ScaleMult")
		cmds.setAttr(scalingMult+ ".input1", curveLength)
		cmds.connectAttr(self.nodes("local")+".sx", scalingMult+".input2")
		lengthMult = self.addNode("multDoubleLinear", "LengthMult")
		cmds.connectAttr(self.lengthAttr, lengthMult+".input1")
		cmds.connectAttr(scalingMult+".output", lengthMult+".input2")

		for i, (pinAttr,rollAttr) in enumerate(izip(self.pinAttrs, self.useRollAttr)):
			vertexAttr = "vertexData[%i]"%i
			cmds.connectAttr(pinAttr["paramWeight"], self.curve+".{}.paramWeight".format(vertexAttr))
			multNode = self.addNode("multDoubleLinear", "PinMult{}".format(i+1))
			cmds.connectAttr(lengthMult+".output", multNode+".input1")
			cmds.connectAttr(pinAttr["paramValue"], multNode+".input2")
			cmds.connectAttr(multNode+".output", self.curve+".{}.paramValue".format(vertexAttr))

			cmds.connectAttr(rollAttr, self.curve+".{}.twistWeight".format(vertexAttr))
			cmds.connectAttr(rollAttr, self.curve+".{}.useOrient".format(vertexAttr))

		# Deformers --------------------------------
		for res,dfmList,count in izip(["Seg","Skin"], [self.segDfm,self.dfm], [self.settings("lowJointsCount"),self.settings("jointsCount")]):
			riderCns = self.addNode("riderConstraint", "rider{}".format(res))
			cmds.connectAttr(self.curve+".outputSpline", riderCns+".inputSplines[0].spline")
			cmds.connectAttr(self.slideAttr, riderCns+".globalOffset")
			cmds.setAttr(riderCns+".useGlobalMin", True)

			cmds.connectAttr(self.curve+".splineLength", riderCns+".inputSplines[0].splineLength")
			cmds.connectAttr(self.curve+".vertexData[{}].paramValue".format(self.initialCount-1), riderCns+".inputSplines[0].endParam")

			for i,dfm in enumerate(dfmList):
				uVal = i / (count - 1.0)
				cmds.connectAttr(dfm+".parentInverseMatrix", riderCns+".params[{}].parentInverseMatrix".format(i))
				cmds.setAttr(riderCns+".params[{}].param".format(i), uVal)
				for trans in ["translate","rotate","scale"]:
					cmds.connectAttr(riderCns+".outputs[{i}].{t}".format(i=i,t=trans), dfm+"."+trans)

				# Setup minimum length on riders
				if self.settings("minimumLength") != 0:
					minParam = uVal * self.settings("minimumLength") / curveLength
					cmds.setAttr(riderCns+".params[{}].useMin",format(i), True)
					cmds.setAttr(riderCns+".params[{}].minParam",format(i), minParam)

		# Roll Setup ---------------------------------
		for i, (rollBfr, rollCtl, tangentSet) in enumerate(izip(self.rollBfr, self.rollCtl, self.twistTans)):
			vertexAttr = "vertexData[{}]".format(i)
			# Special setup for start and end points
			if not i or i == len(self.rollBfr)-1:
				if not i:
					aimTar = self.bones[1]
					aimUp = self.bones[0]
					aimAxis = "xy"
					prefix = "Start"

				else:
					aimTar = self.bones[-2]
					aimUp = self.bones[-1]
					aimAxis = "-xy"
					prefix = "End"
				aimCns = self.addCompound("aimConstraint", "Aim{}".format(i), rollBfr, aimTar, axis=aimAxis, upMaster=aimUp, upVector=(0,1,0))

				# Flip the effect of the rotation
				multNode = self.addNode("multDoubleLinear", "{}RollFlip".format(prefix))
				cmds.connectAttr(rollCtl+".rotateX", multNode+".input1")
				cmds.setAttr(multNode+".input2", -1)
				cmds.connectAttr(multNode+".output", self.curve+".{}.twistValue".format(vertexAttr))
				continue

			# Connect the roll to the curve
			cmds.connectAttr(rollCtl+".rotateX", self.curve+".{}.twistValue".format(vertexAttr))

			# Connect the twist tangent to the roll buffer
			decomp = self.addNode("decomposeMatrix", "TwistDecomp{}".format(i+1))
			cmds.connectAttr(tangentSet[0]+".outTwistMat", decomp+".inputMatrix")
			cmds.connectAttr(decomp+".outputRotate", rollBfr+".rotate")
		
		# Dynamics ----------------------------
		if self.settings("dynamic"):
			for i, (harmonic, target, dynCns, dynBone, bone) in enumerate(izip(self.harmonic, self.target, self.dynCns, self.dynBone, self.bones)):
				cns = self.addCompound("harmonic", "Dyn", harmonic, target, 
					amplitude=1.0, 
					decay=self.settings("decay"), 
					frequency=self.settings("frequency"), 
					termination=self.settings("termination"),
					amplitudeAxis=(self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")) 
					)

				if i%3 == 0:
					mulNode = self.addNode("multiplyDivide", "amplitudeGlobal{}".format(i))
					cmds.connectAttr(self.globalAmplitudeAttr, mulNode+".input1X")
					cmds.connectAttr(self.globalAmplitudeAttr, mulNode+".input1Y")
					cmds.connectAttr(self.globalAmplitudeAttr, mulNode+".input1Z")

					activeNode = self.addNode("multiplyDivide", "active{}".format(i))
					cmds.connectAttr(mulNode+".output", activeNode+".input1")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2X")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2Y")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2Z")

				axis = "XYZ"[i%3]
				cmds.connectAttr(self.localAmplitudeAttr[i], mulNode+".input2"+axis)
				cmds.connectAttr(activeNode+".output"+axis, cns+".amplitude")

				if self.settings("dynamicAnimatable"):
					cmds.connectAttr(self.axisAttr, cns+".axisAmp")
					cmds.connectAttr(self.decayAttr, cns+".decay")
					cmds.connectAttr(self.terminationAttr, cns+".termination")
					cmds.connectAttr(self.frequencyAttr, cns+".frequencyMult")

				cns = self.addCompound("aimConstraint", "DynAim", dynBone, harmonic, axis=self.sign()+"xy", upMaster=dynCns, upVector=(0,1,0), maintainOffset=False)
				cns = self.addCompound("blendMatrix", "DynCns", dynCns, [bone], translate=False, rotate=True, scale=False)
					
	def _createTangentOperators(self, centers, tangents, idx, opTwist, tanAttrs, compareNode):
		# Create the twistTangent for the tangents if they exist
		twistNodes = []
		for i,(tangent, prefix, verts, attrSet) in enumerate(izip(tangents, ["in","out"], [centers, centers[::-1]], tanAttrs)):
			if tangent:
				twistTan = self.addNode("twistTangent", "{s}TwistTan{i}".format(s=prefix, i=idx))
				cmds.connectAttr(verts[1]+".worldMatrix", twistTan+".currentVertex")
				if verts[0]:
					cmds.connectAttr(verts[0]+".worldMatrix", twistTan+".nextVertex")
				if verts[2]:
					cmds.connectAttr(verts[2]+".worldMatrix", twistTan+".previousVertex")

				# Connect the twistTangent to the opposing twistTangent for linear to work, if an in tangent
				if not i:
					cmds.connectAttr(twistTan+".outLinearTarget", opTwist+".inLinearTarget")
					cmds.connectAttr(opTwist+".outLinearTarget", twistTan+".inLinearTarget")

				# Connect it to the given transform node
				cmds.connectAttr(twistTan+".out", tangent+".translate")
				cmds.connectAttr(tangent+".parentInverseMatrix", twistTan+".parentInverseMatrix")

				# Add an aim constraint to better orient the tangents
				if prefix == "in":
					axis = "xy"
				else:
					axis = "-xy"
				self.addCompound("aimConstraint", "TanAim{}".format(i), tangent, verts[1], axis=axis, upMaster=verts[1], upVector=(0,1,0))

				# Connect the inTangent
				tanParent = cmds.listRelatives(tangent, parent=True)[0]
				cmds.connectAttr(tanParent+".worldMatrix", twistTan+".inTangent")

				# Connect the attributes
				for attrName, attr in attrSet.iteritems():
					# Special connections to convert in tangents into endpoints based on specified number of controllers
					if prefix == "in" and attrName == "smooth" and compareNode:
						smoothMult = self.addNode("multDoubleLinear", "SmoothTanMult{}".format(idx))
						cmds.connectAttr(attr, smoothMult+"input1")
						compareNode.connectResult((smoothMult, "input2"))
						cmds.connectAttr(smoothMult+".output", twistTan+"."+attrName)

						smoothInvert = self.addNode("plusMinusAverage", "EndPointSwitch{}".format(idx))
						cmds.setAttr(smoothInvert+ ".operation", 2)
						cmds.setAttr(smoothInvert+ ".input1D[0]", 1)
						compareNode.connectResult((smoothInvert, "input1D[1]"))
						cmds.connectAttr(smoothInvert+".output1D", twistTan+"endpoint")
					else:
						cmds.connectAttr(attr, twistTan+"."+attrName)

				twistNodes.append(twistTan)
			else:
				twistNodes.append(None)

		return twistNodes


	#----------------------------------------------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		if "Root" in self._connections:
			obj = self.getObject(config.USE_BFR, "Root")	
			self.connections("Root").connect(obj)

		if "Orient" in self._connections:
			obj = self.getObject(config.USE_BFR, "Fk1")	
			self.connections("Orient").connect(obj, attrName="FkOrient")

		if "IK" in self._connections:
			obj = self.getObject(config.USE_BFR, "IkRoot")	
			self.connections("IK").connect(obj, attrName="IkParent")
		
