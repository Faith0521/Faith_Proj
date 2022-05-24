from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

class TwistSystemBuilder(SystemBuilder):

	def createObjects(self):

		self.axis = self.settings("axis").lower()

		# TRANSFORMATIONS
		positions = self.translations("Part")

		# Normal
		if self.count("Part") > 2:
			normal = Vector3.planeNormal(*positions[:3])
			if normal.length() < 1E-6:
				normal = self.directions("Part1", "z")
		else:
			normal = self.directions("Part1", "z")

		ctlTfm = TransformationArray.chain(positions, normal, axis=self.axis+"z", negativeSide=self.negate(), endTransform=True)

		divTfm = Transformation()
		if self.negate():
			divTfm.scaling = Vector3([-1,-1,-1])

		length = self.translations("Part1").distance(self.translations("Part2")) / 5.0


		# CONTROLLERS
		self._centers = []

		# Left this dictionary in here, just in case we wanna revert back
		shdScl = [length,length,length]
		shdScl["xyz".index(self.axis)] = 0

		se_keyableParameters = list(constants.ATTRS_TR)
		int_keyableParameters = list(constants.ATTRS_T)

		if self.settings("scaleWithControllers"):
			se_keyableParameters += ["scl"+s for s in "xyz" if s != self.axis]

		if self.settings("scaleWithInterControllers"):
			int_keyableParameters += ["scl"+s for s in "xyz" if s != self.axis]

		# Start Controller
		bfr = self.addBfr(None, "Start", ctlTfm[0])
		if self.settings("startController"):
			ctl = self.addCtl(bfr, "Start", ctlTfm[0], "sphere", so=shdScl, color=self.colorFk())
			attributes.setKeyables(ctl, se_keyableParameters)
			self._centers.append(ctl)
		else:
			self._centers.append(bfr)

		# Inter Controller
		for i, tfm in enumerate(ctlTfm[1:-1], start=1):

			bfr = self.addBfr(None, "Part%s"%i, tfm)

			if self.settings("interControllers"):
				ctl = self.addCtl(bfr, "Part%s"%i, tfm, "cube", size=2, so=shdScl, color=self.colorFk())
				attributes.setKeyables(ctl, int_keyableParameters)
				self._centers.append(ctl)
			else:
				self._centers.append(bfr)

		# End Controller
		bfr = self.addBfr(None, "End", ctlTfm[-1])
		if self.settings("endController"):
			ctl = self.addCtl(bfr, "End", ctlTfm[-1], "sphere", so=shdScl, color=self.colorFk())
			attributes.setKeyables(ctl, se_keyableParameters)
			self._centers.append(ctl)
		else:
			self._centers.append(bfr)


		# CURVE
		# tangent = self.settings("tangentDistance") if self.settings("tangent") else None
		self.crv = create.cnsCurve(self.getObjectName(config.USE_RIG, "Crv"), self._centers, closed=False, degree=3)
		self.length = cmds.arclen(self.crv)

		# DIVISIONS
		parent = self._centers[0]
		self.start_iter = 0 if self.settings("startDeformer") and not self.settings("tangent") else 1
		if self.settings("tangent"):
			self.interDiv = [self.addRig(parent, "Div%s"%i, divTfm, "cube", size=2) for i in xrange(1, self.settings("interDeformers")+1)]
			if self.settings("untwistDeformers"):
				self.unTwistDiv = [self.addRig(parent, "Untwist%s"%i, divTfm, "cube", size=1) for i in xrange(1, self.settings("interDeformers")+1)]
				self.unTwistStart = self.addRig(self._centers[0], "UntwistStart", ctlTfm[0], "cube", size=1)
				self.unTwistEnd = self.addRig(self._centers[-1], "UntwistEnd", ctlTfm[-1], "cube", size=1)
		else:
			div_count = self.settings("interDeformers") + self.settings("startDeformer") + self.settings("endDeformer")
			self.interDiv = [self.addRig(parent, "Div%s"%i, divTfm, "cube", size=2) for i in xrange(self.start_iter, div_count+self.start_iter)]
			if self.settings("untwistDeformers"):
				self.unTwistDiv = [self.addRig(parent, "Untwist%s"%i, divTfm, "cube", size=1) for i in xrange(self.start_iter, div_count+self.start_iter)]

	def createJoints(self):
		if self.settings("tangent"):
			if self.settings("startDeformer"):
				self.addJnt(self._centers[0], "0")

			for i, interDiv in enumerate(self.interDiv, start=1):
				self.addJnt(interDiv, str(i))

			if self.settings("endDeformer"):
				self.addJnt(self._centers[-1], len(self.interDiv)+1)

		else:
			for i, interDiv in enumerate(self.interDiv, start=self.start_iter):
				self.addJnt(interDiv, str(i))

		if self.settings("untwistDeformers"):
			for i, untwist in enumerate(self.unTwistDiv, start=self.start_iter):
				dfm = self.addJnt(untwist, "Untwist%s"%i)
			if self.settings("tangent") and self.settings("startDeformer"):
				dfm = self.addJnt(self.unTwistStart, "Untwist0")
			if self.settings("tangent") and self.settings("endDeformer"):
				dfm = self.addJnt(self.unTwistEnd, "Untwist%i"%(len(self.interDiv)+1))

	# --------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		if self.settings("scaleWithCurve") or self.settings("preserveLength"):
			self.crvLengthAttr = self.addSetupAttr("curveLength", "float", self.length, 0, None)

		step = 1.0 / (self.settings("interDeformers") + 1.0)
		self.scaleAttrs = [None] * 100
		for i, div in enumerate(self.interDiv, start=self.start_iter):
			u = i*step
			attr = self.addSetupAttr("Scale%s"%i, "float", 1-u, None, None)
			self.scaleAttrs[i] = attr

	# --------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Curve
		if self.settings("scaleWithCurve") or self.settings("preserveLength"):
			ciNode = self.addNode("curveInfo", "CurveInfo")
			shape = cmds.listRelatives(self.crv, shapes=True)[0]
			cmds.connectAttr(shape+".worldSpace[0]", ciNode+".inputCurve")

		align = self.axis[0]+"-z"

		if self.settings("scaleWithCurve") or self.settings("preserveLength"):
			scaleNode = self.addNode("multDoubleLinear", "LengthRescale")
			cmds.setAttr(scaleNode+".input1", self.length)
			cmds.connectAttr(self.nodes("local")+".sx", scaleNode+".input2")

			lengthRatioNode = self.addNode("multiplyDivide", "LengthRatio")
			cmds.setAttr(lengthRatioNode+".operation", 2) # Division

			cmds.connectAttr(ciNode+".arcLength", lengthRatioNode+".input1X")
			cmds.connectAttr(scaleNode+".output", lengthRatioNode+".input2X")

			cmds.connectAttr(lengthRatioNode+".input1X", lengthRatioNode+".input2Y")
			cmds.connectAttr(lengthRatioNode+".input2X", lengthRatioNode+".input1Y")

		# Divisions
		step = 1.0 / (self.settings("interDeformers") + 1.0)
		for i, div in enumerate(self.interDiv, start=self.start_iter):
			u = i*step

			# Position
			if self.settings("parametric"):
				cns = self.addCompound("curveConstraints", "CrvCns", div, self.crv, axis=align, parametric=True, u=u, percentageToU=True)
			else:
				cns = self.addCompound("curveConstraints", "CrvCns", div, self.crv, axis=align, parametric=False, u=u)
				if self.settings("preserveLength"):
					mulNode = self.addNode("multiplyDivide", "Mul")
					cmds.setAttr(mulNode+".operation", 1) # Multiply
					cmds.setAttr(mulNode+".input1X", u)
					cmds.connectAttr(lengthRatioNode+".outputY", mulNode+".input2X")
					cmds.connectAttr(mulNode+".outputX", cns+".uValue")

			# Rotation
			if self.settings("twistMethod") == "spinePointAt":
				self.addCompound("spinePointAt", "Twist", cns, self._centers[0], self._centers[-1], blend=u, solver=1)
			else:
				self.addCompound("pointAtBlendedAxis", "Twist", cns, self._centers[0], self._centers[-1], blend=u)

			# Scaling
			if self.settings("scaleWithCurve"):
				if self.negate():
					negNode = self.addNode("multiplyDivide", "Neg")
					cmds.setAttr(negNode+".operation", 1) # Multiply
					cmds.connectAttr(lengthRatioNode+".outputX", negNode+".input1X")
					cmds.setAttr(negNode+".input2X", -1)
					cmds.connectAttr(negNode+".outputX", div+".scale"+self.axis.upper())
				else:
					cmds.connectAttr(lengthRatioNode+".outputX", div+".scale"+self.axis.upper())


			if self.settings("scaleWithControllers"):
				if self.settings("scaleWithInterControllers"):
					dt = Vector3(cmds.xform(div, q=True, worldSpace=True, translation=True))
					ct = [cmds.xform(ctr, q=True, worldSpace=True, translation=True) for ctr in self._centers]
					ct = [Vector3(x) for x in ct]

					lengths = [dt.distance(v) for v in ct]
					sortedLengths = sorted(lengths)

					refA = lengths.index(sortedLengths[0])
					refB = lengths.index(sortedLengths[1])
					refA = self._centers[refA]
					refB = self._centers[refB]

					refADmNode = self.addNode("decomposeMatrix", "DM")
					cmds.connectAttr(refA+".worldMatrix[0]", refADmNode+".inputMatrix")

					if sortedLengths[0] < 1E-6:
						divNode = self.addNode("multiplyDivide", "Div")
						cmds.setAttr(divNode+".operation", 2) # Divide
						cmds.connectAttr(refADmNode+".outputScale", divNode+".input1")
						cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2X")
						cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Y")
						cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Z")

						output = divNode
					else:
						blend = sortedLengths[1] / sum(sortedLengths[:2])

						refBDmNode = self.addNode("decomposeMatrix", "DM")
						cmds.connectAttr(refB+".worldMatrix[0]", refBDmNode+".inputMatrix")

						blendNode = self.addNode("blendColors", "Blend")
						cmds.connectAttr(self.scaleAttrs[i], blendNode+".blender")
						cmds.connectAttr(refADmNode+".outputScale", blendNode+".color1")
						cmds.connectAttr(refBDmNode+".outputScale", blendNode+".color2")

						divNode = self.addNode("multiplyDivide", "Div")
						cmds.setAttr(divNode+".operation", 2) # Divide
						cmds.connectAttr(blendNode+".output", divNode+".input1")
						cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2X")
						cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Y")
						cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Z")

						output = divNode

				else:
					refADmNode = self.addNode("decomposeMatrix", "DM")
					cmds.connectAttr(self._centers[0]+".matrix", refADmNode+".inputMatrix")
					refBDmNode = self.addNode("decomposeMatrix", "DM")
					cmds.connectAttr(self._centers[-1]+".matrix", refBDmNode+".inputMatrix")

					blendNode = self.addNode("blendColors", "Blend")
					cmds.connectAttr(self.scaleAttrs[i], blendNode+".blender")
					cmds.connectAttr(refADmNode+".outputScale", blendNode+".color1")
					cmds.connectAttr(refBDmNode+".outputScale", blendNode+".color2")

					divNode = self.addNode("multiplyDivide", "Div")
					cmds.setAttr(divNode+".operation", 1) # Multiply
					cmds.connectAttr(blendNode+".output", divNode+".input1")
					cmds.setAttr(divNode+".input2X", 1)
					cmds.setAttr(divNode+".input2Y", 1)
					cmds.setAttr(divNode+".input2Z", 1)

					output = divNode

				for s in "xyz":
					if s == self.axis:
						continue

					cmds.connectAttr(output+".output"+s.title(), div+".scale"+s.title())

		# Untwist
		if self.settings("untwistDeformers"):
			if self.settings("tangent"):
				slaves = [self.unTwistStart] + self.unTwistDiv + [self.unTwistEnd]
				masters = [self._centers[0]] + self.interDiv + [self._centers[-1]]
			else:
				slaves = self.unTwistDiv
				masters = self.interDiv
			for div,untwist in izip(masters, slaves):
				poseCnsCompound = self._createCompound("poseConstraint2", untwist, [div])

				negNode = self.addNode("unitConversion", "Negate")
				cmds.setAttr(negNode+".conversionFactor", -1)
				cmds.connectAttr(div+".rotate%s"%self.axis.title(), negNode+".input")

				cnx = ".input[0].localOffsetTransform.localOffsetRotate.localOffsetRotate%s"%self.axis.title()
				cmds.connectAttr(negNode+".output", poseCnsCompound.nodes("PoseCns")+cnx)

	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		sbfr = self.getObject(config.USE_BFR, "Start")
		bfrs = [self.getObject(config.USE_BFR, "Part{}".format(i)) for i in xrange(1, self.count("Part")-1)]
		ebfr = self.getObject(config.USE_BFR, "End")
		buffers = [sbfr] + bfrs + [ebfr]

		for i, bfr in enumerate(buffers):
			port = "Control{}".format(i+1)
			if port in self.connections():
				self.connections(port).connect(bfr)

			# TODO: Twists must all be under the same parent for SpinePoint At to work properly
			# self.connect_parenting(bfr, "Control1")
			# self.connect_constraining(bfr, )
