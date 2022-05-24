from maya import cmds

from brigks.utils import attributes

from brigks.connections.systemConnection import SystemConnection

class MultiParentSystemConnection(SystemConnection):

	def __init__(self):
		super(MultiParentSystemConnection, self).__init__()
		self._settings = dict(definitions=[], default=0, key=None, slot=None)

	def connect(self, child, attrName="ParentBlend"):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		masters = []
		for definition in self._settings["definitions"]:
			cnxType = definition["type"]

			if cnxType == "slot":
				if "{key}:{slot}".format(**definition) == "self:Parent":
					master = cmds.listRelatives(child, parent=True, path=True)[0]
				else:
					master = self.getParentFromSlot(definition["key"], definition["slot"])
			elif cnxType == "custom":
				master = self.getParentFromName(definition["name"])
			elif cnxType == "mesh":
				kwargs = dict(
					componentType=COMPONENT_TYPES.index(definition["componentType"]),
					componentIndex=-1 if useClosest else definition["componentIndex"],
					position=cmds.xform(child, q=True, translation=True, worldSpace=True)
					)
				kwargs.update(definition)
				master = getParentFromMesh(**kwargs)
			elif cnxType == "nurbs":
				kwargs = dict(
					position=cmds.xform(child, q=True, translation=True, worldSpace=True)
					)
				kwargs.update(definition)
				master = self.getParentFromSurface(**kwargs)

			if master:
				masters.append(master)

		if len(masters) <= 1:
			return

		bmNode = self._parentConstraint(child, masters)

		# TODO Should be replaced with Enum
		attrType = "float" if len(masters) == 2 else "short"
		attr = self._builder.addAnimAttr(attrName, attrType, value=self.settings("default"), minValue=0, maxValue=len(masters)-1)

		if len(masters) == 2:
			cmds.connectAttr(attr, bmNode+".target[1].weight")
		elif len(masters) > 2:
			for i in range(len(masters)):
				cond = self.addCompound("compare", "CnxSwitch", attr, i, "==")
				cmds.connectAttr(cond+".outColorR", bmNode+".target[{}].weight".format(i))

	def getTargetSystems(self):
		keys = []
		for definition in self._settings["definitions"]:
			if "key" in definition["key"]:
				keys.append(definition["key"])
		return keys

	def split(self, location):
		definitions = []
		for definition in self._settings["definitions"]:
			if "key" in definition["key"]:
				key = definition["key"]

				part, otherLocation = key.split("_")
				if otherLocation != "X":
					continue

				definition["key"] = "{part}_{location}".format(part=part, location=location)

			definitions.append(definition)
		self._settings["definitions"] = definitions
