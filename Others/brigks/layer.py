from maya import cmds
import xml.etree.cElementTree as etree
import json

from brigks.systems import getSystemGuideClass
from brigks import naming

class Layer():
	'''Layer Class

	A Layer is an organization container for systems inside the Guide.
	A Layer can have sub Layers. 
	A Layewr also holds some global settings on how to build its children systems.

	Settings
	expanded (bool): For UI purposed, if the LayerTreeWidgetItem is expanded
	color (3 floats): 0-1 RGB Color of the markers in the layer
	useLayerColor (bool): Use the layer color for all the controllers 
	inheritColors (bool): Inherit the color from the parent Guide or Layer
	colorRFk (3 floats): 0-1 RGB Default color for Fk controllers on the Right side 
	colorMFk (3 floats): 0-1 RGB Default color for Fk controllers on the Middle side 
	colorLFk (3 floats): 0-1 RGB Default color for Fk controllers on the Left side 	
	colorRIk (3 floats): 0-1 RGB Default color for Fk controllers on the Right side 
	colorMIk (3 floats): 0-1 RGB Default color for Fk controllers on the Middle side 
	colorLIk (3 floats): 0-1 RGB Default color for Fk controllers on the Left side 
	'''

	def __init__(self, parent, name, data={}):
		'''Layer Init

		Args:
			parent (Guide||Layer): Parent object of the layer. 
			name (str): Name of the layer.
			data (dict): Extra data to initialize the layer with

		Returns:
			Layer
		'''
		self._parent = parent
		self._name = None
		self._layers = [] # Sub Layers
		self._systems = []
		self._settings = dict(expanded=False,
							 color=[.875,.875,.250],
							 useLayerColor=False,
							 inheritColors=True,
							 colorRFk=[0,.25,.75], colorRIk=[0,.5,1], 
							 colorMFk=[.5,.25,.5], colorMIk=[.85,.6,.85],
							 colorLFk=[.6,.2,.2],  colorLIk=[1,.35,.35],
							 )

		# Makes sure the name is unique
		self.setName(name)

		if data:
			self.load(data)

	def load(self, data):
		'''Load the settings and systems from the data provided

		Args:
			data (dict): Extra data to initialize the layer with
		'''
		self._settings.update(data["settings"])

		# Loading Systems
		for systemData in data["systems"]:
			SystemClass = getSystemGuideClass(systemData["systemType"])
			system = SystemClass.load(self, systemData)
			self._systems.append(system)

		# Loading Sub Layers
		for data in data["layers"]:
			layer = Layer(self, data["name"], data)
			self._layers.append(layer)

	def build(self):
		'''Build all the systems in the Layer
		'''
		self.guide().build(self._systems)

	def delete(self, deleteGuide=False):
		'''Delete all the systems of the Layer

		Args:
			deleteGuide (bool): Delete also the SystemGuides and the Layer itself
		'''
		self.guide().delete(self._systems, deleteGuide)
		if deleteGuide:
			self._parent.removeLayer(self)

	def dumps(self):
		'''Returns the Layer data

		Returns:
			dictionary
		'''
		data = dict(name=self._name,
					settings=self._settings,
					layers=[layer.dumps() for layer in self._layers],
					systems=[system.dumps() for system in self._systems] )
		return data

	def commit(self):
		'''Save the guide settings

		You cannot save just a single layer, so it will save all the guide definition
		'''
		self.guide().commit()

	# ----------------------------------------------------------------------------------
	# NAME and LAYERS
	# ----------------------------------------------------------------------------------
	def guide(self):
		'''Returns the Guide this Layer belongs to

		Returns:
			Guide
		'''
		if isinstance(self._parent, Layer):
			return self._parent.guide()
		else:
			return self._parent

	def settings(self, key=None):
		'''Returns the settings of the Layer 

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that setting value

		Returns:
			dictionary or setting value
		'''
		return self._settings if key is None else self._settings[key]

	def setSettings(self, **settings):
		'''Set a specific setting for the Layer

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that setting value

		Returns:
			dictionary or setting value
		'''
		self._settings.update(settings)

	def name(self):
		'''Returns the name of the Layer

		Returns:
			str: The name of the Layer
		'''
		return self._name

	def setName(self, name):
		'''Set the name of the Layer

		Layer name must be unique per parent

		Args:
			name (str): New name of the Layer.

		Returns:
			str: The name of the Layer
		'''
		if name == self._name:
			return self._name
		name = self._findUniqueName(name, self._parent.layers())
		self._name = name
		return self._name

	def _findUniqueName(self, name, layers):
		'''Private Method. Find the next unique name for the Layer

		Layer name must be unique per parent

		Args:
			name (str): New name of the Layer.
			layers (dict of Layer): The Layers to compare to.

		Returns:
			str: The unique name of the Layer
		'''
		inputName = name
		i = 1
		while name in layers:
			name = inputName + str(i)
			i += 1
		return name

	def layers(self, name=None):
		'''Returns the sub Layer or the Layer

		Args:
			name (None||str): None returns the whole dictionary, if a key is passed it returns that Layer

		Returns:
			dictionary or setting value
		'''
		layers = {layer.name():layer for layer in self._layers}
		return layers if name is None else layers[name]

	def addLayer(self, name):
		'''Add a sub Layer to the Layer

		Args:
			name (str): New name of the Layer.

		Returns:
			Layer
		'''
		layer = Layer(self, name)
		self._layers.append(layer)
		return layer

	def removeLayer(self, layer):
		'''Remove a sub Layer from the Layer

		Args:
			layer (Layer): The Layer to remove

		Returns:
			Layer
		'''
		index = self._layers.index(layer)
		return self._layers.pop(index)

	def setParent(self, parent=None):
		'''Set the parent of the layer

		This is to reparent a layer under another Layer or the Guide
		This mind result on the Layer being renamed if the name was not unique in the new parent.

		Args:
			parent (Layer||Guide): The new parent

		Returns:
			Layer
		'''
		if parent == self._parent:
			return 

		if parent is None:
			parent = self.guide()

		self._parent.removeLayer(self)

		self._parent = parent
		self.setName(self.name())
		self._parent._layers.append(self)

	def color(self):
		return self.settings("color")

	def colors(self, key):
		'''Returns a specific color from the settings

		Note that if useLayerColor is True, it will return the Layer color
		and if inheritColors is True it will return the parent colors

		Args:
			key (str): RFk, MFk, LFk, RIk, MIk, LIk

		Returns:
			list of float: RGB 0-1 color 
		'''
		if self.settings("useLayerColor"):
			return self.settings("color")
		elif self.settings("inheritColors"):
			return self._parent.colors(key)
		else:
			return self.settings("color"+key)

	def setVisible(self, visible=True, gde=True, rig=True, jnt=True, ctl=True):
		'''Set the visibility of all the objects of that system

		Args:
			visible (bool): Visibility
			gde (bool): True to update USE_GDE objects
			rig (bool): True to update USE_RIG objects
			jnt (bool): True to update USE_JNT objects
			ctl (bool): True to update USE_CTL objects
		'''
		for system in self._systems:
			system.setVisible(visible, gde, rig, jnt, ctl)

	def isVisible(self, gde=True, rig=True, jnt=True, ctl=True):
		'''Return True if the majority of objects of the specified use are visible

		Args:
			gde (bool): Returns the object of use config.USE_GDE
			rig (bool): Returns the object of use config.USE_RIG and USE_BFR
			jnt (bool): Returns the object of use config.USE_JNT
			ctl (bool): Returns the object of use config.USE_CTL

		Returns:
			bool
		'''
		objects  = []
		for system in self._systems:
			objects += system.getObjects(gde, rig, jnt, ctl)
		shapes = cmds.listRelatives(objects, shapes=True, path=True) or []
		joints = cmds.ls(objects, type="joint", long=True)
		visible = []
		for shp in shapes + joints:
			visible.append(cmds.getAttr(shp+".lodVisibility"))
		return visible.count(True) > visible.count(False)

	# ----------------------------------------------------------------------------------
	# SYSTEMS
	# ----------------------------------------------------------------------------------
	def systems(self, key=None):
		'''Returns the systems of that Layer

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that setting value

		Returns:
			dictionary or setting value
		'''
		systems = {system.key():system for system in self._systems}
		return systems if key is None else systems[key]

	def findSystem(self, key):
		'''Return a specific system in the Layer or SubLayers

		Systems have a unique key which is the combination of their name and location.
		TODO: I feel I could have a 'recursive' options on the systems() method

		Args:
			key (str): Key of the system to retrieve

		Returns:
			SystemGuide
		'''
		for system in self._systems:
			if system.key() == key:
				return system

		for layer in self._layers:
			system = layer.findSystem(key)
			if system:
				return system

	def addSystem(self, systemType, location, name, matrices={}, version=None):
		'''Add a new system guide to the layer

		Args:
		    systemType (str): Type of system to be create.
		    location (str): Location of the system (L/R/M/X).
		    name (str): Name of the system.
		    matrices (dict of matrix): Matrices are flat lists of coordonate.
		    version (int): Version of the system (-1 for latest).

		Returns:
		    SystemGuide: The newly created system.
		'''
		# Making sure the key of the system is unique to the guide
		name = self.guide().findNextSystemName(name, location)
		SystemClass = getSystemGuideClass(systemType, version)
		system = SystemClass.create(self, location, name, matrices)
		self._systems.append(system)

		return system

	def appendSystem(self, system):
		'''Append a system to the Layer

		Args:
		    system (SystemGuide): The System to add to the Layer
		'''
		self._systems.append(system)

	def popSystem(self, system):
		'''Remove a system from the Layer

		TODO: Rename to removeSystem for consistency

		Args:
		    system (SystemGuide): The System to remove from the Layer

		Returns:
			SystemGuide
		'''
		index = self._systems.index(system)
		return self._systems.pop(index)

	def swapSystem(self, oldSystem, systemType, version=None):
		'''Swap a system with another one

		This is used when swapping a system with a compatible one 

		Args:
		    oldSystem (SystemGuide): System to be replaced
		    systemType (str): New system type to be created
		    version (str||None): version of the system

		Returns:
			SystemGuide
		'''
		oldSystem.swapMarkers(systemType)
		self.popSystem(oldSystem)

		SystemClass = getSystemGuideClass(systemType, version)
		newSystem = SystemClass(self)
		newSystem.setSettings(**oldSystem.settings())

		self._systems.append(newSystem)
		return newSystem

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		'''Returns the Layer definition as an xml object

		Returns:
			etree.Element: the Xml object
		'''
		xmlRoot = etree.Element("Layer")
		xmlRoot.set("name", layer.name())
		xmlRoot.set("settings", json.dumps(self._settings))

		for layer in self._layers:
			xmlRoot.append(layer.toXml(layer))

		for system in self._systems:
			xmlRoot.append(system.toXml())

		return xmlRoot

	@classmethod
	def fromXml(cls, parent, xmlRoot):
		'''Class Method. Creates a Layer from an xml definition

		Args:
			parent (Guide||Layer): Parent of the new Layer 
			xmlRoot (etree.Element): Xml definition of the Layer 
		
		Returns:
			Layer: The newly created Layer
		'''
		name = xmlRoot.get("name")
		settings = json.loads(xmlRoot.get("settings", "{}"))

		layer = parent.addLayer(name)
		layer.setSettings(**settings)

		for xmlObject in xmlRoot:
			if xmlObject.tag == "Layer":
				name = xmlObject.get("name")
				subLayer = Layer.fromXml(layer, xmlObject)
				layer._layers.append(subLayer)
			elif xmlObject.tag == "System":
			 	key = xmlObject.get("key")
			 	systemType = xmlObject.get("type")
			 	systemVersion = xmlObject.get("version", None)
				SystemClass = getSystemGuideClass(systemType, systemVersion)
				system = SystemClass.fromXml(layer, xmlObject)
				layer._systems.append(system)

		return layer
