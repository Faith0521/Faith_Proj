from maya import cmds
import json
import xml.etree.cElementTree as etree
import getpass
import datetime
import logging

import naming
from layer import Layer
from builder import Builder
from utils import create
from config import DATA_ATTRIBUTE
from utils.xmldom import indent


scriptDefaultValue = '''# cmds returns the maya.cmds module
# this_model returns the root node
# this_guide returns the guide
'''

class Guide():
	'''Main Guide Class

	The Guide is the class holding the information on how to build a rig.
	The Guide has Layers that are containing the SystemGuides.
	The Guide also holds some global settings on how to build the rig.

	Settings
	version (3 int): The version number when the guide was generated
	preScriptPath (str): Path to the pre-script
	preScriptValue (str): Code of the pre-script. Saved in case the path is no longer accessible
	postScriptPath (str): Path to the post script
	postScriptValue (str): Code of the post-script. Saved in case the path is no longer accessible
	colorRFk (3 float): 0-1 RGB Default color for Fk controllers on the Right side 
	colorMFk (3 float): 0-1 RGB Default color for Fk controllers on the Middle side 
	colorLFk (3 float): 0-1 RGB Default color for Fk controllers on the Left side 	
	colorRIk (3 float): 0-1 RGB Default color for Fk controllers on the Right side 
	colorMIk (3 float): 0-1 RGB Default color for Fk controllers on the Middle side 
	colorLIk (3 float): 0-1 RGB Default color for Fk controllers on the Left side 
	groups (list of str): List of groups sotroed in the guide 
	stopAfter (str): Debug option to stop the build after a specific step
	hideRig (bool): Debug option to prevent hiding the rig object
	hideJoints (bool): Debug option to prevent hiding the joints
	'''

	def __init__(self, model=None):
		'''Guide Init

		Args:
			model (str||None): Pass a model to initialize existing guide. None to create a new one

		Returns:
			Guide
		'''
		self._model = None
		self._builder = None
		self._layers = []
		self._settings = dict(version=[1,0,0],
							preScriptPath="",
							preScriptValue=scriptDefaultValue,
							postScriptPath="",
							postScriptValue=scriptDefaultValue,
							colorRFk=[0,.25,.75], colorRIk=[0,.5,1], 
							colorMFk=[.5,.25,.5], colorMIk=[.85,.6,.85],
							colorLFk=[.6,.2,.2],  colorLIk=[1,.35,.35], 
							groups=dict(),
							stopAfter="Post Script",
							hideRig=True,
							hideJoints=True
							)

		# If we pass a model, then we load the settings
		# Otherwise we create a new Model
		if model:
			self._load(model)
		else:
			self._model = cmds.ls(create.transform("Guide"), long=True)[0]
			cmds.addAttr(self._model, longName="model", attributeType="bool")
			cmds.addAttr(self._model, longName="guide", attributeType="bool")
			cmds.addAttr(self._model, longName=DATA_ATTRIBUTE, dataType="string")

	def _load(self, model):
		'''Initialize the guide from given model

		Args:
			model (str): Pass a model to initialize existing guide. 
		'''
		self._model = cmds.ls(model, long=True)[0]
		if not cmds.ls(model+"."+DATA_ATTRIBUTE):
			raise RuntimeError("Invalide Guide. Missing Data Attribute.")

		# Load Settings
		data = json.loads(cmds.getAttr(model+"."+DATA_ATTRIBUTE))
		self._settings.update(data["settings"])

		# Load Layers
		for data in data["layers"]:
			layer = Layer(self, data["name"], data)
			self._layers.append(layer)

	def builder(self):
		'''Create or return the Builder from this guide

		The Builder is the class used to actually build the rig

		Returns:
			Builder
		'''
		if self._builder is None:
			self._builder = Builder(self)
		return self._builder

	def build(self, systemGuides=None):
		'''Build the rig from specified system guides

		Args:
			systemGuides (list of SystemGuide): SystemGuide to be built
		'''
		if systemGuides is None:
			systemGuides = self._getAllSystems()

		self.builder().build(systemGuides)

	def delete(self, systemGuides=None, deleteGuide=False):
		'''Delete specified systems

		Args:
			systemGuides (list of SystemGuide): SystemGuide to be deleted
			deleteGuide (bool): True to delete both the rig and guide. false to delete rig only
		'''
		if systemGuides is None:
			systemGuides = self._getAllSystems()

		self.builder().delete(systemGuides)

		if deleteGuide:
			for systemGuide in systemGuides:
				systemGuide.layer().popSystem(systemGuide)
				systemGuide.deleteMarkers()

			self.commit()

	def commit(self):
		'''Save the guide settings

		The settigns of all the layers and system are stored as one big json string 
		'''
		data = dict(settings=self._settings,
					layers=[layer.dumps() for layer in self._layers])
		data = json.dumps(data)

		# Saves settings to json in the model data attribute
		cmds.setAttr(self._model+"."+DATA_ATTRIBUTE, data, type="string")
		logging.debug("Brigks: Guide Settings Saved")

	# ----------------------------------------------------------------------------------
	# LAYERS, SYSTEMS
	# ----------------------------------------------------------------------------------
	def model(self):
		'''Returns the root node of the Guide

		Returns:
			str
		'''
		return self._model

	def setup(self):
		'''Returns the root node of the rig

		Returns:
			str
		'''
		connections = cmds.listConnections(self._model+".model", destination=False, type="transform")
		if connections:
			return connections[0]

	def settings(self, key=None):
		'''Returns the settings of the Guide 

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that setting value

		Returns:
			dictionary or setting value
		'''
		return self._settings if key is None else self._settings[key]

	def setSettings(self, **settings):
		'''Set a specific setting for the Guide

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that setting value

		Returns:
			dictionary or setting value
		'''
		self._settings.update(settings)

	def colors(self, key):
		'''Returns a specific color from the settings

		Args:
			key (str): RFk, MFk, LFk, RIk, MIk, LIk

		Returns:
			list of float: RGB 0-1 color 
		'''
		return self.settings("color"+key)

	def layers(self, name=None):
		'''Returns the top Layers of the Guide

		Args:
			name (None||str): None returns the whole dictionary, if a key is passed it returns that Layer

		Returns:
			dictionary or Layer
		'''
		layers = {layer.name():layer for layer in self._layers}
		if name is None:
			return layers
		return layers[name]

	def addLayer(self, name):
		'''Add a top Layer to the Guide

		Args:
			name (str): Name of the newly created Layer

		Returns:
			Layer
		'''
		layer = Layer(self, name)
		self._layers.append(layer)
		return layer

	def removeLayer(self, layer):
		'''Remove a top Layer from the Guide

		Args:
			name (str): Name of the Layer to remove

		Returns:
			Layer
		'''
		index = self._layers.index(layer)
		return self._layers.pop(index)

	def getLayersDepths(self, parent=None, depth=0):
		'''Returns all the layers and their depth in a list

		This is a recursive method
		If a guide has 2 top level layers and 2 sub Layer in the first Layer the output would be
		[(LayerA, 0), 
		(LayerAChildA, 1),
		(LayerAChildB, 1),
		(LayerB, 0)]

		Args:
			parent (Layer||Guide): 
			depth (int): Current depth, not meant to be used 

		Returns:
			list of tuple (int, Layer)
		'''
		if parent is None:
			parent = self
		layers = sorted(parent.layers().values(), key=lambda x:x.name())
		found = []
		for layer in layers:
			found.append((depth, layer))
			found += self.getLayersDepths(layer, depth+1)
		return found

	def findSystem(self, key):
		'''Return a specific system anywhere in the Guide

		Systems have a unique key which is the combination of their name and location.

		Args:
			key (str): Key of the system to retrieve

		Returns:
			SystemGuide
		'''
		for layer in self._layers:
			system = layer.findSystem(key)
			if system:
				return system

	def findNextSystemName(self, name, location):
		'''Return a new unique name for a system

		Args:
			name (str): Name of the system
			location (str): Location of the system

		Returns:
			str
		'''
		inputName = name
		i = 1
		key = naming.getSystemKey(location, name)
		while self.findSystem(key) is not None:
			name = inputName + str(i)
			key = naming.getSystemKey(location, name)
			i += 1
		return name

	def systemIsBuilt(self, key):
		'''Return True if given system key has been built

		Args:
			key (str): Key of the system to retrieve

		Returns:
			bool
		'''
		return key in self.builder().builtSettings().keys()

	def _getAllSystems(self):	
		'''Private Method. Returns all the system in the Guide

		Returns:
			list of SystemGuide
		'''
		systemGuides = []
		for layer in self._layers:
			systems = layer.systems().values()
			systemGuides.extend(systems)
		return systemGuides

	# ----------------------------------------------------------------------------------
	# GROUPS
	# ----------------------------------------------------------------------------------
	def groups(self, name=None):
		'''Returns the groups of the Guide 

		Groups are a way to store list of objects as part of the rig.
		This might be useful for you to organize your data and easily access specific objects in the rig.

		Args:
			name (None||str): None returns the whole dictionary, if a name is passed it returns that group value

		Returns:
			dictionary or group value
		'''
		return self._settings["groups"] if name is None else self._settings["groups"][name]

	def addGroup(self, name, members=[]):
		'''Add a group to the Guide

		Args:
			name (str): Name of the newly created group
			members (list of str): List of members 
		'''
		self.groups()[name] = value

	def removeGroup(self, name):
		'''Remove a group from the Guide

		Args:
			name (str): Name of the group to remove
		'''
		if name not in self.groups():
			msg = "No such group: {n}"
			raise ValueError(msg.format(n=name))
		return self.groups().pop(name)

	def renameGroup(self, name, newName):
		'''Rename a group from the Guide

		Args:
			name (str): Current name of the group
			newName (str): New Name of the group
		'''
		self.addGroup(newName, self.removeGroup(name))

	def addMembers(self, name, members):
		'''Add members to a group

		Args:
			name (str): Name of the group
			members (list of str): List of members 
		'''
		members += self.groups(name)
		members = set(members)
		self.groups()[name] = list(members)

	def removeMembers(self, name, members):
		'''Remove members from a group

		Args:
			name (str): Name of the group
			members (list of str): List of members 
		'''
		for member in members:
			if member in self.groups(name):
				index = self.groups(name).index(member)
				self.groups(name).pop(index)

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def write(self, path):
		'''Save the Guide definition to an xml

		The whole Guide with all its Layers, SystemGuides and marker positions can be saved to xml

		Args:
			path (str): Output path for the xml definition 
		'''
		xmlRoot = self.toXml()
		indent(xmlRoot)
		tree = etree.ElementTree(xmlRoot)
		tree.write(path)

	def toXml(self):
		'''Returns the Guide definition as an xml object

		Returns:
			etree.Element: the Xml object
		'''
		xmlRoot = etree.Element("Guide")
		xmlRoot.set("user", getpass.getuser())
		xmlRoot.set("date", str(datetime.datetime.now()))
		xmlRoot.set("settings", json.dumps(self._settings))

		for layer in self._layers:
			xmlRoot.append(layer.toXml())

		return xmlRoot

	@classmethod
	def fromXml(cls, path):
		'''Class Method. Creates a guide from an xml definition

		TODO Need to have a way to merge partial guides in exisiting one

		Args:
			path (str): Input path for the xml definition 
		
		Returns:
			Guide: The newly created Guide
		'''
		guide = cls()

		tree = etree.parse(path)
		xmlRoot = tree.getroot()

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", "{}"))
		# Filtering old Settings
		settings = {k:v for k,v in settings.iteritems() if k in guide._settings}
		guide.setSettings(**settings)

		# Load Layers
		for xmlLayer in xmlRoot:
			layer = Layer.fromXml(guide, xmlLayer)

		guide.commit()

		return guide
