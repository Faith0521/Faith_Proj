from itertools import izip

from maya import cmds

from math3d.vectorN import Vector3

from brigks.systems.systemBuilder import SystemBuilder
from brigks import config

class PsdSystemBuilder(SystemBuilder):

	def preDeleteObjects(self):
		# Delete custom nodes in a dumb way to prevent a crash
		search = self.getObjectName("*", "*")
		solverNodes = cmds.ls(search, type="eccentricConePSD")
		search = self.getObjectName(config.USE_RIG, "*")
		looseNodes = [node for node in cmds.ls(search, type="transform", long=True) if not cmds.listRelatives(node, parent=True)]
		cmds.delete(looseNodes)

	def createObjects(self):
		# TRANSFORMATION
		rootTfm = self.transforms("Root")
		rootTfm.scale = self.scales("Root")
		drvTfm = self.transforms("Driver")
		innerTfm = self.transforms("Inner")
		outerTfm = self.transforms("Outer")
		sample_pos = Vector3([1,0,0]) * rootTfm.asMatrix()
		sampleTfm = rootTfm.copy(translation=sample_pos)
		
		self._root = self.addRig(None, "Root", rootTfm, "sphere", 1.0)
		self._sample = self.addRig(None, "Sample", sampleTfm, "null", 0.25)
		
		# Drivers
		self._drvs = []
		self._inners = []
		self._outers = []
		
		for i, (dtfm, itfm, otfm) in enumerate(izip(drvTfm, innerTfm, outerTfm), start=1):
			dtfm.scale = self.scales("Driver")[i-1]
			itfm.scale = self.scales("Inner")[i-1]
			otfm.scale = self.scales("Outer")[i-1]
			
			driver = self.addRig(self._root, "Driver%s"%i, dtfm, "pyramid", 0.5, None, [0,0,-90], None)
			outer = self.addRig(driver, "Outer%s"%i, otfm, "sphere", 2, None, None, [0,1,1])
			inner = self.addRig(outer, "Inner%s"%i, itfm, "sphere", 2, None, None, [0,1,1])

			
			self._drvs.append(driver)
			self._inners.append(inner)
			self._outers.append(outer)
			

	#----------------------------------------------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.outrotAttr = self.addSetupAttr("OutRot", "float3", (0,0,0))
		self.twistMin = self.addSetupAttr("TwistMin", "float", self.settings("twistMin"))
		self.twistMax = self.addSetupAttr("TwistMax", "float", self.settings("twistMax"))

		if self.settings("twistSplit"):
			self.twistValue = [self.addSetupAttr("Twist{}Value".format(direction), "float", 0) for direction in ["Out","In"]]
		else:
			self.twistValue = self.addSetupAttr("TwistValue", "float", 0)
		self.driverValues = [self.addSetupAttr(self.settings("drvName{}".format(i)), "float", 0, 0.0, 1.0) for i in xrange(1, self.count("Driver")+1)]		
		

	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		if not cmds.pluginInfo("EccentricConePSD", q=True, loaded=True):
			cmds.loadPlugin("EccentricConePSD")

		for i,(drv,inner,outer,drvAttr) in enumerate(izip(self._drvs, self._inners, self._outers, self.driverValues), start=1):
			label = drvAttr.split("_")[-1]
			solver = self.addNode("eccentricConePSD", name="%sCone"%label)
			cmds.connectAttr(inner+".worldMatrix[0]", solver+".innerMatrix")
			cmds.connectAttr(outer+".worldMatrix[0]", solver+".outerMatrix")
			cmds.connectAttr(drv+".worldInverseMatrix[0]", solver+".referenceInverseMatrix")

			point = self.addNode("pointMatrixMult", name="%sPointPosition"%label)
			cmds.connectAttr(self._sample+".worldMatrix[0]", point+".inMatrix")
			cmds.connectAttr(point+".output", solver+".point")

			# Setup falloff
			interpType = self.settings("interpType%s"%i)
			easeValue = {"Ease In":0.85, "Ease Out":0.15}
			if interpType == "Linear":
				cmds.connectAttr(solver+".value", drvAttr)
			else:
				interpNode = self.addNode("remapValue", name="%sRemap"%label)
				cmds.connectAttr(solver+".value", interpNode+".inputValue")
				cmds.connectAttr(interpNode+".outValue", drvAttr)

				if interpType == "Smooth":
					cmds.setAttr(interpNode+".value[0].value_Interp", 2)
				else:
					cmds.setAttr(interpNode+".value[0].value_Interp", 3)
					cmds.setAttr(interpNode+".value[2].value_Position", 0.5)
					cmds.setAttr(interpNode+".value[2].value_FloatValue", easeValue[interpType])
					cmds.setAttr(interpNode+".value[2].value_Interp", 3)
			
		# Setup the twist
		interpType = ["None","Linear","Smooth","Spline"].index(self.settings("twistInterp"))
		twistAxis = "XYZ".index(self.settings("twistAxis"))
		twistAttr = self.outrotAttr+str(twistAxis)
		remapNeg_Node = self.addNode("remapValue", name="remapTwistNeg")
		cmds.connectAttr(self.twistMin, remapNeg_Node+".inputMax")
		cmds.connectAttr(twistAttr, remapNeg_Node+".inputValue")
		cmds.setAttr(remapNeg_Node+".value[0].value_Interp", interpType)

		remapPos_Node = self.addNode("remapValue", name="remapTwistPos")
		cmds.connectAttr(self.twistMax, remapPos_Node+".inputMax")
		cmds.connectAttr(twistAttr, remapPos_Node+".inputValue")
		cmds.setAttr(remapPos_Node+".value[0].value_Interp", interpType)
		
		if self.settings("twistSplit"):
			cmds.connectAttr(remapNeg_Node+".outValue", self.twistValue[0])
			cmds.connectAttr(remapPos_Node+".outValue", self.twistValue[1])
		else:
			add_Node = self.addNode("plusMinusAverage", name="addTwist")
			cmds.setAttr(remapNeg_Node+".outputMax", -10)
			cmds.connectAttr(remapNeg_Node+".outValue", add_Node+".input1D[0]")
			cmds.connectAttr(remapPos_Node+".outValue", add_Node+".input1D[1]")
			cmds.connectAttr(add_Node+".output1D", self.twistValue)

	#----------------------------------------------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		if "Root" in self.connections():
			root = self.getObject(config.USE_RIG, "Root")
			self.connections("Root").connect(root)

		# sample = self.getObject("Sample", use="Rig")
		# self.connect_parenting(sample, "Tracker")
		
		# orientation = self.connectionObject("Orientation")
		
		# if orientation != self.root():
		# 	self.addOrientationConstraint(root, orientation, compensation=True)

		

		if "Tracker" in self.connections():
			outrotAttr = self.getAttributes("OutRot")
			cnx.connect(self.outrotAttr)
