
from brigks.systems.systemGuide import SystemGuide


class TrackerSystemGuide(SystemGuide):

	def addSettings(self):
		self._settings["order"] = []
		self._settings["definitions"] = {}

	def connectionPorts(self):
		super(TrackerSystemGuide, self).connectionPorts()

		ports = dict(
			Tracker=["rotationTracker"]
			)

		return ports

	def connectionSlots(self):
		super(TrackerSystemGuide, self).connectionSlots()
