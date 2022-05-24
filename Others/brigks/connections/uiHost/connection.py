from maya import cmds
from brigks.connections.systemConnection import SystemConnection

class UiHostSystemConnection(SystemConnection):

	def __init__(self):
		super(UiHostSystemConnection, self).__init__()
		self._settings = dict(
			key=None,
			slot=None,
			)

	def connect(self):
		pass

	def getHost(self):
		return self.getParentFromSlot(self._settings["key"], self._settings["slot"])

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []

	def split(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)
