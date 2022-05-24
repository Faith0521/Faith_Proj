import math
from itertools import izip, product

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

class FootSystemBuilder(SystemBuilder):

	def createObjects(self):

		# TRANSFORMATIONS
		normal = Vector3.planeNormal(self.translations("Root"), self.translations("Part")[-1], self.translations("Heel"))
		if self.negate():
			normal *= -1

		rootTfm = Transformation.lookAt(self.translations("Root"), constants.AXIS_Y, normal, "y-x", self.negate())
		direction = self.translations("Part")[-1] - self.translations("Heel")
		heelTfm = Transformation.lookAt(self.translations("Heel"), direction, normal, "xz", self.negate())
		
		if self.count("Part") > 1:
			B = self.translations("Heel") - self.translations("Part")[-1]
			C = self.translations("Part")[0] - self.translations("Part")[-1]
			a = 1 - ((math.cos(B.angle(C)) * C.length()) / B.length())
		else:
			a = .5

		swivel_pos = self.translations("Heel").lerp(self.translations("Part")[-1], a)
		swivelTfm = heelTfm.copy(translation=swivel_pos)
		
		direction = self.translations("Part")[0] - self.translations("Root")
		fkrefTfm = Transformation.lookAt(self.translations("Root"), direction, normal, "xz", self.negate())
		
		fkTfm = TransformationArray.chain(self.translations("Part"), normal, axis="xz", negativeSide=self.negate(), endTransform=False)
		fkTfm = fkTfm.appended(heelTfm.copy(translation=self.translations("Part")[-1]))
		

		
		# CONTROLLERS
		# Root
		self._root = self.addRig(None, "Root", rootTfm)
		
		# Heel
		self.heelBfr = self.addBfr(self._root, "Heel", heelTfm)
		self.heelRol = self.addRig(self.heelBfr, "HeelRoll", tfm=heelTfm)
		self.heelCtl = self.addCtl(self.heelRol, "Heel", heelTfm, "sphere", so=[1,1,0], color=self.colorIk())
		attributes.setKeyables(self.heelCtl, constants.ATTRS_TR)
		# self.setInversedParameters(self.heelCtl, middle=["posz", "rotx", "roty"])

		# Swivel
		self.swivelBfr = self.addBfr(self.heelCtl, "Swivel", swivelTfm)
		self.swivelCtl = self.addCtl(self.swivelBfr, "Swivel", swivelTfm, "sphere", so=[3,0,3], color=self.colorIk())
		attributes.setKeyables(self.swivelCtl, constants.ATTRS_TR)
		# self.setInversedParameters(self.swivelCtl, middle=["posz", "rotx", "roty"])

		# Roll
		self.rollCtl = self.addCtl(self._root, "Roll", rootTfm, "sphere", color=self.colorIk(), so=[0,2,2])
		# self.addToSubControllers(self.rollCtl)					 
		attributes.setKeyables(self.rollCtl, ["rotx", "rotz"])
		# self.setInversedParameters(self.rollCtl, middle=["rotz"])

		# Backward Controllers
		parent = self.swivelCtl
		self.bkBfr = []
		self.bkRol = []
		self.bkCtl = []
		for i, tfm in enumerate(reversed(fkTfm)):
			
			index = i+1
			
			bkBfr = self.addBfr(parent, "Bk%s"%index, tfm=tfm)
			bkRol = self.addRig(bkBfr, "Bk%sRoll"%index, tfm=tfm)
			bkCtl = self.addCtl(bkRol, "Bk%s"%index, tfm, "sphere", color=self.colorIk(), so=[1,1,0])
			attributes.setKeyables(bkCtl, constants.ATTRS_R)
			# self.setInversedParameters(bkCtl, middle=["rotx", "roty"])

			self.bkBfr.append(bkBfr)
			self.bkRol.append(bkRol)
			self.bkCtl.append(bkCtl)
			parent = bkCtl
		
		# Forward Controllers
		self.fkRef = self.addRig(self.bkCtl[-1], "FkRef", fkrefTfm)
		
		self.fkBfr = []
		self.fkCtl = []
		parent = self.fkRef
		for i, (tfm, bkCtl) in enumerate(izip(fkTfm, self.bkCtl[:-1]), start=1):
			
			fkBfr = self.addBfr(parent, "Fk%s"%i, tfm=tfm)
			fkCtl = self.addCtl(fkBfr, "Fk%s"%i, tfm, "sphere", color=self.colorFk(), so=[0,2,4])
			attributes.setKeyables(fkCtl, [t+s for t, s in product(["scl", "rot", "pos"], "xyz")])
			# self.setInversedParameters(fkCtl, middle=["posz", "rotx", "roty"])

			parent = fkCtl
			self.fkBfr.append(fkBfr)
			self.fkCtl.append(fkCtl)
			
			
	def createJoints(self):
		for i, fkCtl in enumerate(self.fkCtl, start=1):
			self.addJnt(fkCtl, i)
			
	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.angleAttr = [self.addAnimAttr("Angle%s"%i, "float", 20, 0, None) for i in xrange(1, self.count("Part"))]
		self.blendAttr = self.addSetupAttr("Blend", "float", 1, 0, 1)

	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibilities
		ikCompare = self.addCompound("compare", "IkViz", self.blendAttr, 0, ">")
		for ctl in self.bkCtl + [self.heelCtl, self.swivelCtl, self.rollCtl]:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		# Reverse Controler offset
		self._createFootRollOperator()

	def _createFootRollOperator(self):
		bkBfrs = list(reversed(self.bkRol))
		bkCtls = list(reversed(self.bkCtl))
		fkBfrs = self.fkBfr
		heelBfr = self.heelRol

		angleAttr = self.angleAttr
		blendAttr = self.blendAttr

		# Roll / Bank
		rollAttr = self.rollCtl+".rotateX"
		bankAttr = self.rollCtl+".rotateZ"
		
		# # Bank pivot compensation
		outside = self.translations("Out").distanceToAxis(self.translations("Heel"), self.translations("Part")[-1])
		inside = self.translations("In").distanceToAxis(self.translations("Heel"), self.translations("Part")[-1])
		bankOffsets = [outside, inside]


		negNode = self.addNode("multiplyDivide", name="neg")
		cmds.connectAttr(rollAttr, negNode+".input1X")
		cmds.setAttr(negNode+".input2X", -1)

		prevNode = None
		aSumNodes = []
		for i in xrange(1, len(angleAttr)):
			adlNode = self.addNode("addDoubleLinear", name="angleSum")
			if i == 1:
				cmds.connectAttr(angleAttr[i-1], adlNode+".input1")
			else:
				cmds.connectAttr(prevNode+".output", adlNode+".input1")

			cmds.connectAttr(angleAttr[i], adlNode+".input2")

			prevNode = adlNode
			aSumNodes.append(adlNode)


		for i in xrange(len(angleAttr)+1):
			bkBfr = bkBfrs[i]

			adlNode = self.addNode("addDoubleLinear", name="rollAngleSum%s"%i)
			if i == 0:
				cmds.setAttr(adlNode+".input1", 0)
			elif i == 1:
				cmds.connectAttr(angleAttr[i-1], adlNode+".input1")
			else:
				cmds.connectAttr(aSumNodes[i-2]+".output", adlNode+".input1")

			cmds.connectAttr(negNode+".outputX", adlNode+".input2")


			clpNode = self.addNode("clamp", name="clamp%s"%i)
			cmds.connectAttr(adlNode+".output", clpNode+".inputR")
			cmds.setAttr(clpNode+".maxR", 0)
			if i < len(angleAttr):
				negANode = self.addNode("multiplyDivide", name="negAngle%s"%i)
				cmds.connectAttr(angleAttr[i], negANode+".input1X")
				cmds.setAttr(negANode+".input2X", -1)
				cmds.connectAttr(negANode+".outputX", clpNode+".minR")
			else:
				cmds.setAttr(clpNode+".minR", -360)

			cmds.connectAttr(clpNode+".outputR", bkBfrs[i]+".rotateZ")


			if i < len(angleAttr):
				adlXNode = self.addNode("addDoubleLinear", name="bkSumX%s"%i)
				adlYNode = self.addNode("addDoubleLinear", name="bkSumY%s"%i)
				adlZNode = self.addNode("addDoubleLinear", name="bkSumZ%s"%i)

				cmds.connectAttr(bkBfrs[i]+".rotateX", adlXNode+".input1")
				cmds.connectAttr(bkBfrs[i]+".rotateY", adlYNode+".input1")
				cmds.connectAttr(bkBfrs[i]+".rotateZ", adlZNode+".input1")

				cmds.connectAttr(bkCtls[i]+".rotateX", adlXNode+".input2")
				cmds.connectAttr(bkCtls[i]+".rotateY", adlYNode+".input2")
				cmds.connectAttr(bkCtls[i]+".rotateZ", adlZNode+".input2")

				negBkNode = self.addNode("multiplyDivide", name="negBk%s"%i)
				cmds.setAttr(negBkNode+".input2X", -1)
				cmds.setAttr(negBkNode+".input2Y", -1)
				cmds.setAttr(negBkNode+".input2Z", -1)
				cmds.connectAttr(adlXNode+".output", negBkNode+".input1X")
				cmds.connectAttr(adlYNode+".output", negBkNode+".input1Y")
				cmds.connectAttr(adlZNode+".output", negBkNode+".input1Z")

				mulNode = self.addNode("multiplyDivide", name="mulBlend%s"%i)
				cmds.connectAttr(negBkNode+".outputX", mulNode+".input1X")
				cmds.connectAttr(negBkNode+".outputY", mulNode+".input1Y")
				cmds.connectAttr(negBkNode+".outputZ", mulNode+".input1Z")
				cmds.connectAttr(blendAttr, mulNode+".input2X")
				cmds.connectAttr(blendAttr, mulNode+".input2Y")
				cmds.connectAttr(blendAttr, mulNode+".input2Z")

				cmds.connectAttr(mulNode+".output", fkBfrs[i]+".rotate")

				invRotOrdNode = self.addNode("InverseRotOrder", name="invRotOrd%s"%i)

				cmds.setAttr(fkBfrs[i]+".rotateOrder", lock=False)

				cmds.connectAttr(bkCtls[i]+".rotateOrder", invRotOrdNode+".rotationOrder")
				cmds.connectAttr(invRotOrdNode+".output", fkBfrs[i]+".rotateOrder")

		# Heel Roll
		negHeelNode = self.addNode("multiplyDivide", name="negHeel")
		cmds.setAttr(heelBfr+".minRotZLimitEnable", True)
		cmds.setAttr(heelBfr+".minRotZLimit", 0)
		cmds.connectAttr(rollAttr, negHeelNode+".input1X")
		cmds.setAttr(negHeelNode+".input2X", -1)
		cmds.connectAttr(negHeelNode+".outputX", heelBfr+".rotateZ")

		# Heel banking
		cmds.connectAttr(bankAttr, heelBfr+".rotateX")
		bankCondNode = self.addNode("condition", name="condHeel")
		cmds.connectAttr(bankAttr, bankCondNode+".firstTerm")
		cmds.setAttr(bankCondNode+".secondTerm", 0)
		if self.negate():
			cmds.setAttr(bankCondNode+".operation", 2)# Greater Than >
		else:
			cmds.setAttr(bankCondNode+".operation", 4)# Less Than <
		cmds.setAttr(bankCondNode+".colorIfTrueR", -bankOffsets[0]) 
		cmds.setAttr(bankCondNode+".colorIfFalseR", bankOffsets[1])
		cmds.connectAttr(bankCondNode+".outColorR", heelBfr+".rotatePivotZ")

	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Root" in self.connections():
			self.connections("Root").connect()