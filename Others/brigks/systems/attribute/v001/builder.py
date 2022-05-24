from brigks.systems.systemBuilder import SystemBuilder


class AttributeSystemBuilder(SystemBuilder):


	def createAttributes(self):
		attrTypes = dict(Boolean="bool", 
						Float="float", 
						Integer="int",
						Proxy="Proxy" )

		for attrname in self.settings("order"):
			definition = self.settings("definitions")[attrname]
			scriptName = attrname.replace(" ", "-")

			type_ = attrTypes[definition["type"]]
			value = definition["value"]
			minValue = definition["min"] if definition["hasMin"] else None
			maxValue = definition["max"] if definition["hasMax"] else None
			uiMinValue = definition["uiMin"] if definition["hasUIMin"] else None
			uiMaxValue = definition["uiMax"] if definition["hasUIMax"] else None

			self.addAnimAttr(scriptName, type_, value, minValue, maxValue, uiMinValue, uiMaxValue)
