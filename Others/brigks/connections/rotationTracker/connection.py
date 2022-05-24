from maya import cmds

from brigks.connections.systemConnection import SystemConnection

class RotationTrackerSystemConnection(SystemConnection):

	def __init__(self):
		super(RotationTrackerSystemConnection, self).__init__()
		self._settings = dict(
			referenceKey=None,
			referenceSlot=None,
			trackerKey=None,
			trackerSlot=None,
			)

	def connect(self, attr):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		reference = self.getParentFromSlot(self._settings["referenceKey"], self._settings["referenceSlot"], useDefault=False)
		tracker = self.getParentFromSlot(self._settings["trackerKey"], self._settings["trackerSlot"], useDefault=False)

		if not reference or not tracker:
			return

		cns = self.addCompound("rotationTracker", "CnxTrk", attr, reference, tracker)

	def getTargetSystems(self):
		keys = []
		if self._settings["referenceKey"]:
			return keys.append(self._settings["referenceKey"])
		if self._settings["trackerKey"]:
			return keys.append(self._settings["trackerKey"])
		return keys

	def split(self, location):
		referenceKey = self._settings["referenceKey"]
		otherName, otherLocation = referenceKey.split("_")
		if otherLocation == "X":
			self._settings["referenceKey"] = "{n}_{l}".format(n=otherName, l=location)
		trackerKey = self._settings["trackerKey"]
		otherName, otherLocation = trackerKey.split("_")
		if otherLocation == "X":
			self._settings["trackerKey"] = "{n}_{l}".format(n=otherName, l=location)
