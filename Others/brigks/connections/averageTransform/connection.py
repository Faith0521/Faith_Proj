from maya import cmds
from brigks.connections.systemConnection import SystemConnection

class AverageTransformSystemConnection(SystemConnection):

	def __init__(self):
		super(AverageTransformSystemConnection, self).__init__()
		self._settings = dict(
			parentKey=None, parentSlot=None,
			masterAkey=None, masterASlot=None,
			masterBkey=None, masterBSlot=None, 
			position=True,
			rotation=True,
			scaling=True,
			blend=.5
			)

	def connect(self, child, attr=None):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		parent = self.getParentFromSlot(self.settings("parentKey"), self.settings("parentSlot"), useDefault=False)
		masterA = self.getParentFromSlot(self.settings("masterAkey"), self.settings("masterASlot"), useDefault=False)
		masterB = self.getParentFromSlot(self.settings("masterBkey"), self.settings("masterBSlot"), useDefault=False)

		if parent is None:
			parent = masterA
		
		child = self._parent(child, parent)
		if not masterA or not masterB:
			return

		cns = self.addCompound("blendMatrix", "AvgCnx", child, [masterA, masterB], maintainOffset=True,
													translate=self.settings("position"),
		 											rotate=self.settings("rotation"),
		 											scale=self.settings("scaling"))

		if attr:
			cmds.connectAttr(attr, cns+".target[1].weight")
			cmds.setAttr(attr, self.settings("blend"))
		else:		
			cmds.setAttr(cns+".target[1].weight", self.settings("blend"))

