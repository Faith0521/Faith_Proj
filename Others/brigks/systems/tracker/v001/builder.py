from brigks.systems.systemBuilder import SystemBuilder


class TrackerSystemBuilder(SystemBuilder):

	def createAttributes(self):
		self.outrotAttr = self.addSetupAttr("OutRot", "float3", (0,0,0))

		self.driverAttrs = {}
		for driverName in self.settings("driverDefOrder"):
			definition = self.settings("driverDefs")[driverName]
			minAttr = self.addSetupAttr("%sMin"%driverName, "float", definition["min"])
			maxAttr = self.addSetupAttr("%sMax"%driverName, "float", definition["max"])
			valueAttr = self.addSetupAttr("%sValue"%driverName, "float", 0.0)
			self.driverAttrs[driverName] = {"min":minAttr, "max":maxAttr, "value":valueAttr}

	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		interpTypes = ["None","Linear","Smooth","Spline"]
		for driverName in self.settings("driverDefOrder"):
			definition = self.settings("driverDefs")[driverName]
			_attrs = self.driverAttrs[driverName]
			_interp = interpTypes.index(definition["interpolation"])
			_driver = self.outrotAttr.nativePointer().child("XYZ".index(definition["axis"]))
			# Check if there is a positive and negative angle, and if so set up two remap nodes
			if definition["min"] * definition["max"] < 0:
				add_Node = self.addNode("plusMinusAverage", name="add%s"%driverName)

				remapNeg_Node = self.addNode("remapValue", name="remap%sNeg"%driverName)
				cmds.connectAttr(_attrs["min"], remapNeg_Node+".inputMax")
				cmds.connectAttr(_driver, remapNeg_Node+".inputValue")
				cmds.setAttr(remapNeg_Node+".outputMax", -1.0)
				cmds.setAttr(remapNeg_Node+".value[0].value_Interp", _interp)
				cmds.connectAttr(remapNeg_Node+".outValue", add_Node+".input1D[0]")

				remapPos_Node = self.addNode("remapValue", name="remap%sPos"%driverName)
				cmds.connectAttr(_attrs["max"], remapPos_Node+".inputMax")
				cmds.connectAttr(_driver, remapPos_Node+".inputValue")
				cmds.setAttr(remapPos_Node+".value[0].value_Interp", _interp)
				cmds.connectAttr(remapPos_Node+".outValue", add_Node+".input1D[1]")

				cmds.connectAttr(add_Node+".output1D", _attrs["value"])

			else:
				remap_Node = self.addNode("remapValue", name="remap%s"%driverName)
				cmds.connectAttr(_attrs["min"], remap_Node+".inputMin")
				cmds.connectAttr(_attrs["max"], remap_Node+".inputMax")
				cmds.connectAttr(_driver, remap_Node+".inputValue")
				cmds.setAttr(remap_Node+".value[0].value_Interp", _interp)

				cmds.connectAttr(remap_Node+".outValue", _attrs["value"])


	#----------------------------------------------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		if "Tracker" in self.connections():
			outrotAttr = self.getAttributes("OutRot")
			cnx.connect(self.outrotAttr)
