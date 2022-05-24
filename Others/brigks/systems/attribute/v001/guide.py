
from brigks.systems.systemGuide import SystemGuide

class AttributeSystemGuide(SystemGuide):

	def addSettings(self):
		self._settings["order"] = []
		self._settings["definitions"] = {}

	def connectionPorts(self):
		super(AttributeSystemGuide, self).connectionPorts()

		ports = dict(
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(AttributeSystemGuide, self).connectionSlots()
