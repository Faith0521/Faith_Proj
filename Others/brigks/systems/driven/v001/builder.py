from itertools import izip

from maya import cmds

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

class DrivenSystemBuilder(SystemBuilder):

	def createObjects(self):
		# TRANSFORMATION
		rootTfm = self.transforms("Rail")
		posTfm = self.transforms("Pos")
		negTfm = self.transforms("Neg")

		for i, (root,pos,neg) in enumerate(izip(rootTfm,posTfm,negTfm), start=1):
			root.scale = self.scales("Rail{}".format(i))
			pos.scale = self.scales("Pos{}".format(i))
			neg.scale = self.scales("Neg{}".format(i))
		
		# CONTROLLERS
		self._rails = []
		self._psts = []
		self._ngts = []
		self._slds = []
		self._bfrs = []
		for i, (rtfm, ptfm, ntfm) in enumerate(izip(rootTfm, posTfm, negTfm), start=1):
			rail = self.addRig(None, "Rail{}".format(i), rtfm, "cube", size=1)
			pos = self.addRig(rail, "Pos{}".format(i), ptfm, "null", size=1)
			neg = self.addRig(rail, "Neg{}".format(i), ntfm, "cube", size=1)

			bfr = self.addBfr(rail, "Slider{}".format(i), rtfm)
			if self.settings("addControllers"):
				slider = self.addCtl(bfr, "Part{}".format(i), rtfm, "sphere", color=self.colorIk())
				attributes.setKeyables(slider)
			else:
				slider = self.addRig(bfr, "Part{}".format(i), rtfm, "sphere", size=1)

			create.cnsCurve("Crv{}".format(i), [neg,rail,pos], degree=1)

			self._bfrs.append(bfr)
			self._rails.append(rail)
			self._slds.append(slider)
			self._psts.append(pos)
			self._ngts.append(neg)
		

	def createJoints(self):
		for i, (slider,rail) in enumerate(izip(self._slds, self._rails), start=1):
			if self.settings("addDeformerRef"):
				ref = rail
			else:
				ref = None
			self.addJnt(slider, str(i), reference=ref)

	#----------------------------------------------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.outrotAttr = self.addSetupAttr("OutRot", "float3", (0,0,0))
		self.slideAttr = [self.addSetupAttr("Slide{}".format(i), "float", 0, -1.0, 1.0) for i in xrange(1, self.count("Rail")+1)]


	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		axis = ["XYZ".index(self.settings("axis{}".format(i))) for i in xrange(1, self.count("Rail")+1)]
		rots = [(self.settings("minRot{}".format(i)), self.settings("maxRot{}".format(i))) for i in xrange(1, self.count("Rail")+1)]

		for rail, pos, neg, slider, rot, a, slide in izip(self._rails, self._psts, self._ngts, self._bfrs, rots, axis, self.slideAttr):
			# Slider Op
			cns = self.addCompound("rotationToSlider", "RailTrk", slide, rotMin=rot[0], rotMax=rot[1], slideMin=-1, slideMax=1)
			cmds.connectAttr(self.outrotAttr+str(a), cns+".angle")

			# Blending Constraints
			bmNode = self.addCompound("blendMatrix", "RailCns", slider, [rail, pos, neg])

			# Positive Expression
			# Returns Maximum Value (There's no min/max node in Maya)
			condPosNode = self.addNode("condition", name="CondPos")
			cmds.setAttr(condPosNode+".operation", 2)# Greater Than >
			cmds.connectAttr(slide, condPosNode+".firstTerm")
			cmds.connectAttr(slide, condPosNode+".colorIfTrueR")
			cmds.setAttr(condPosNode+".secondTerm", 0)
			cmds.setAttr(condPosNode+".colorIfFalseR", 0)

			# Negative Expression
			# Returns Negative Value (There's no neg node in Maya)
			negNode = self.addNode("multiplyDivide", name="Neg")
			cmds.connectAttr(slide, negNode+".input1X")
			cmds.setAttr(negNode+".input2X", -1)

			# Returns Maximum Value (There's no min/max node in Maya)
			condNegNode = self.addNode("condition", name="CondNeg")
			cmds.setAttr(condNegNode+".operation", 2)# Greater Than >
			cmds.connectAttr(negNode+".outputX", condNegNode+".firstTerm")
			cmds.connectAttr(negNode+".outputX", condNegNode+".colorIfTrueR")
			cmds.setAttr(condNegNode+".secondTerm", 0)
			cmds.setAttr(condNegNode+".colorIfFalseR", 0)

			cmds.connectAttr(condPosNode+".outColorR", bmNode+".target[1].weight")
			cmds.connectAttr(condNegNode+".outColorR", bmNode+".target[2].weight")

	#----------------------------------------------------------------------------------------------------------------
	# CONNECTIONS
	def createConnections(self):
		for port, cnx in self.connections().iteritems():
			if port == "Tracker":
				cnx.connect(self.outrotAttr)
			else:
				child = self.getObject(config.USE_RIG, port)
				cnx.connect(child)
			