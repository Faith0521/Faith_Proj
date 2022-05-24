from maya import cmds
from brigks.connections.systemConnection import SystemConnection

class SlotParentSystemConnection(SystemConnection):

	def __init__(self):
		super(SlotParentSystemConnection, self).__init__()
		self._settings = dict(
			key=None,
			slot=None,
			)

	def connect(self, child, attrName=None):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		parent = self.getParentFromSlot(self.settings("key"), self.settings("slot"))
		self._parent(child, parent)

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []

	def split(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)
