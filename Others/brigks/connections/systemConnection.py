import json
import xml.etree.cElementTree as etree
import logging

from maya import cmds

from brigks import config

class SystemConnection(object):

	def __init__(self):
		self._settings = dict()
		self._builder = None

	def dumps(self):
		return dict(type=self.type(),
					settings=self._settings)

	def type(self):
		return self.__module__.split(".")[-2]

	def setBuilder(self, builder):
		self._builder = builder
		self.getObjectName = self._builder.getObjectName

	def setSettings(self, **settings):
		self._settings.update(settings)

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	# ----------------------------------------------------------------------------------
	# REIMPLEMENT
	# ----------------------------------------------------------------------------------
	def connect(self):
		pass

	def getTargetSystems(self):
		return []

	def split(self, location):
		pass

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def getSystem(self, key):
		if key in self._builder.coreBuilder.systems():
			return self._builder.coreBuilder.systems(key)

	def getParentFromSlot(self, key, slot, useDefault=True):
		parent = None
		if key in self._builder.coreBuilder.systems():
			system = self._builder.coreBuilder.systems(key)
			parent = system.getObjectFromSlot(slot)
		if parent is None and useDefault:
			tokens = dict(k=key, s=slot, sk=self._builder.key(), t=self._builder.type())
			msg = "Couldnt find slot {k}:{s} when connecting {sk} ({t})".format(**tokens)
			logging.warning(msg)
			parent = self._builder.nodes("local")
		return parent

	def getParentFromMesh(self, mesh, useClosest, useOrientation, componentType, componentIndex, key, slot, position):
		parent = self.getParentFromSlot(key, slot)

		if not cmds.objExists(mesh):
			return parent

		attachName = self.getObjectName(use=config.USE_RIG, part="MeshAttach")
		attach = cmds.createNode("transform", name=attachName)
		cmds.parent(attach, parent)
		cmds.xform(attach, translation=position, worldSpace=True)

		self.addCompound("meshMultiAttach", "MeshCnx", attach, mesh, componentType, componentIndex, useOrientation)
		return attach

	def getParentFromSurface(self, surface, useClosest, u, v, key, slot, position):
		parent = self.getParentFromSlot(key, slot)

		if not cmds.objExists(surface):
			return parent

		if useClosest:
			u, v = None, None

		attachName = self.getObjectName(use=config.USE_RIG, part="MeshAttach")
		attach = cmds.createNode("transform", name=attachName)
		cmds.parent(attach, parent)
		cmds.xform(attach, translation=position, worldSpace=True)

		self.addCompound("surfaceAttach", "SrfCnx", attach, surface, u, v)
		return attach

	def getParentFromName(self, name):
		model = self._builder.model()
		for name in [cmds.ls(name, long=True)]:
			if name.startswith(model):
				return name

	# ----------------------------------------------------------------------------------
	# CONNECTION HELPERS
	# ----------------------------------------------------------------------------------
	def addCompound(self, name, compoundType, *args, **kwargs):
		return self._builder.addCompound(name, compoundType, *args, **kwargs)

	def _parent(self, child, parent):
		if not parent:
			return

		# Making sure the object is not already a child of the parent
		# Otherwise Maya throws an error
		if child.split("|")[-1] in (cmds.listRelatives(parent, children=True) or []):
			return

		return cmds.parent(child, parent)[0]

	def _parentConstraint(self, slave, masters, translate=True, rotation=True, scale=True):
		name = "MultiParent"
		return self.addCompound("blendMatrix", "CnsCnx", slave, masters, maintainOffset=True, translate=translate, rotate=rotation, scale=scale)

	# ----------------------------------------------------------------------------------
	# XML IO
	# ----------------------------------------------------------------------------------
	def toXml(self, port):
		xmlRoot = etree.Element("Connection")
		xmlRoot.set("type", self.type())
		xmlRoot.set("port", port)
		xmlRoot.set("settings", json.dumps(self._settings))
		return xmlRoot

	# @classmethod
	# def fromXml(cls, xmlRoot):
	# 	connection = cls()

	# 	# Load Settings
	# 	settings = json.loads(xmlRoot.get("settings", {}))
	# 	connection.setSettings(**settings)

	# 	return connection
