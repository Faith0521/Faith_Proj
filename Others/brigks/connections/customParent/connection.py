from maya import cmds
from brigks.connections.systemConnection import SystemConnection


class CustomParentSystemConnection(SystemConnection):

	def __init__(self):
		super(CustomParentSystemConnection, self).__init__()
		self._settings = dict(name=None)

	def connect(self, child, attrName=None):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		parent = self.getParentFromName(self.settings("name"))
		self._parent(child, parent)
