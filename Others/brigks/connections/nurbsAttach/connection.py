from maya import cmds

from brigks.connections.systemConnection import SystemConnection

class NurbsAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(NurbsAttachSystemConnection, self).__init__()
		self._settings = dict(
			surface=None,
			u=.5,
			v=.5,
			useClosest=True,
			useOrientation=True,
			key=None,
			slot=None
			)

	def connect(self, child, attrName=None):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		kwargs = dict(
			position=cmds.xform(child, q=True, translation=True, worldSpace=True)
			)
		kwargs.update(self._settings)

		parent = self.getParentFromSurface(**kwargs)
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
