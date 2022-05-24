from maya import cmds
from maya import OpenMaya as om

from brigks.connections.systemConnection import SystemConnection

COMPONENT_TYPES = ["vertex", "edge", "face"]

class MeshAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(MeshAttachSystemConnection, self).__init__()
		self._settings = dict(
			mesh=None,
			componentType="vertex",
			componentIndex=-1,
			useClosest=True,
			useOrientation=False,
			key=None,
			slot=None
			)

	def connect(self, child, attrName=None):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		kwargs = dict(
			componentType=COMPONENT_TYPES.index(self._settings["componentType"]),
			componentIndex=-1 if self._settings["useClosest"] else self._settings["componentIndex"],
			position=cmds.xform(child, q=True, translation=True, worldSpace=True)
			)
		kwargs.update(self._settings)

		parent = self.getParentFromMesh(**kwargs)
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




