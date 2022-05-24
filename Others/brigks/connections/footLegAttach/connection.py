from maya import cmds
from brigks.connections.systemConnection import SystemConnection
from brigks import config

class FootLegAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(FootLegAttachSystemConnection, self).__init__()
		self._settings = dict(
			key=None
			)

	def connect(self):
		parentSystem = self.getSystem(self._settings["key"])
		if parentSystem is None:
			return

		if parentSystem.type() in ["leg"]:
			parent_footRef = "IkRef"
			parent_footHook = "Bone3"
		elif parentSystem.type() in ["zleg"]:
			parent_footRef = "FootRef"
			parent_footHook = "Bone4"

		root = self._builder.getObject(config.USE_RIG, "Root")
		parent_ikoffCtl = parentSystem.getObject(config.USE_CTL, "IkOffset")
		self._parent(root, parent_ikoffCtl)

		lastbkCtl = self._builder.getObject(config.USE_CTL ,"Bk{}".format(self._builder.count("Part")))
		parent_footRef = parentSystem.getObject(config.USE_RIG, parent_footRef)
		self._parent(parent_footRef, lastbkCtl)

		fkRef = self._builder.getObject(config.USE_RIG, "FkRef")
		parent_footHook = parentSystem.getObject(config.USE_RIG, parent_footHook)
		self._parent(fkRef, parent_footHook)

		parent_blendAttr = parentSystem.getAttribute("Blend")
		blendAttr = self._builder.getAttribute("Blend")
		cmds.connectAttr(parent_blendAttr, blendAttr)

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []

	def split(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)
