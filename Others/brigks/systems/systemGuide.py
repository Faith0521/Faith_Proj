from maya import cmds
import copy
import xml.etree.cElementTree as etree
import json

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3Array

from brigks.connections import getSystemConnectionClass
from brigks import naming, config
from brigks.utils import create, pick, compounds
from brigks.systems.systemMarker import SystemMarker, checkMarkersMinMax


scriptDefaultValue = '''# cmds returns the maya.cmds module
# this_model returns the root node
# this_guide returns the system guide
'''

class SystemGuide(object):
	'''System Guide Class

	This is the core class for all system guides. It defines the main methods and all the systems are inheriting from this class 

	Attributes:
		markerNames (list of str)
		markerPicked (list of str)
		markerMinMax (dict of 2 int)
		markerPositions (dict of math3d.Vector3)
		markerCurves (dict of str)
		markerCompatibility (dict of dict of str)
			Key is the type of systems compatible
			Value is a dictionary of markers to rename
			ie: markerCompatibility = dict(basic=dict(Bone="Part"))
			In this example the system is compatible with the chain, but markers 'Bone', must be renamed to 'Part'
		compatibles ?

		_layer (Layer): The parent Layer of the system
		_settings (dict): Dictionary of settings for that guide
			preScriptPath (str): Path to the pre-script
			preScriptValue (str): Code of the pre-script. Saved in case the path is no longer accessible
			postScriptPath (str): Path to the post script
			postScriptValue (str): Code of the post-script. Saved in case the path is no longer accessible
			name (str): Name of the system
			location (str): Location of the system
			split (bool): Tells if the system has been split from an X symmetrical system
			inheritColors (bool): True to inherit colors from parent Layer
			colorFk (3 float): 0-1 RGB Default color for Fk controllers
			colorFk (3 float): 0-1 RGB Default color for Fk controllers 
			createJoints (bool): True to create joints
		_markers
		_multiMarkers
		_connections
		guide (Guide): The Parent Guide
		model (str): The guide model
	'''
	markerNames = ()
	markerPicked = ()
	markerMinMax = {}
	markerPositions = {}
	markerCurves = {}
	markerCompatibility = {}
	compatibles = ()

	def __init__(self, layer, name="Name", location="M"):
		'''Guide Init

		Args:
			layer (Layer): The parent layer for that system
			name (str): The system name
			location (str): The system location

		Returns:
			SystemGuide
		'''
		self._layer = layer
		self._settings = dict(
					preScriptPath="",
					preScriptValue=scriptDefaultValue,
					postScriptPath="",
					postScriptValue=scriptDefaultValue,
					name=name,
					location=location,
					split=False,
					inheritColors=True,
					colorIk=[1,0,0],
					colorFk=[0,0,1],
					createJoints=True)
		self._markers = None
		self._multiMarkers = dict() 
		self._connections = {}
		self.addSettings()

		self.guide = self._layer.guide
		self.model = self.guide().model

	@classmethod
	def create(cls, layer, location, name, matrices=None):
		'''Create System Guide

		Args:
		    systemType (str): Type of system to be create.
		    location (str): Location of the system (L/R/M/X).
		    name (str): Name of the system.
		    version (int): Version of the system (-1 for latest).
		    matrices (dict of matrix): Matrices are flat lists of coordonate.

		Returns:
		    SystemGuide: The newly created system.
		'''
		system = cls(layer)
		system._settings["location"] = location
		system._settings["name"] = name

		# Create Markers
		system.createMarkers(matrices)

		return system

	@classmethod
	def load(cls, layer, data):
		system = cls(layer)
		system.setSettings(**data["settings"])

		for slot, connectionData in data["connections"].iteritems():
			Connection = getSystemConnectionClass(connectionData["type"])
			connection = Connection()
			connection.setSettings(**connectionData["settings"])
			system._connections[slot] = connection

		return system


	def dumps(self):
		'''
		Returns:
		    dictionary: System settings, including connections.
		'''
		data = dict(systemType=self.type(),
					settings=self._settings,
					connections={slot:cnx.dumps() for slot, cnx in self._connections.iteritems()})
		return data

	def commit(self):
		self.guide().commit()

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def key(self):
		return naming.getSystemKey(self._settings["location"], self._settings["name"])

	def type(self):
		return self.__module__.split(".")[-3]

	def version(self):
		return self.__module__.split('.')[-2]

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def setSettings(self, **settings):
		self._settings.update(settings)

	def layer(self):
		return self._layer

	def setLayer(self, layer):
		if layer == self._layer:
			return 

		self._layer.popSystem(self)
		layer._systems.append(self)
		self._layer = layer

	def isBuilt(self):
		return self.guide().systemIsBuilt(self.key())

	def colorIk(self):
		if self.settings("inheritColors"):
			side = "M" if self.settings("location") not in "LR" else self.settings("location")
			return self._layer.colors("{}Ik".format(side))
		else:
			return self.settings("colorIk")

	def colorFk(self):
		if self.settings("inheritColors"):
			side = "M" if self.settings("location") not in "LR" else self.settings("location")
			return self._layer.colors("{}Fk".format(side))
		else:
			return self.settings("colorFk")

	# ----------------------------------------------------------------------------------
	# BUILD / DELETE / DUPLICATE
	# ----------------------------------------------------------------------------------
	def build(self):
		self.guide().build([self])

	def delete(self, deleteGuide=False):
		self.guide().delete([self], deleteGuide)

	def duplicate(self, mirror=False):
		self.loadMarkers(force=True)
		matrices = {part:marker.transformWithScale() for part, marker in self.markers().iteritems()}
		location = self._settings["location"]
		name = self._settings["name"]
		layer = self.layer()
		if mirror:
			if location not in "LR":
				raise RuntimeError("Can't Mirror Central Guide")

			matrices = {p:m.mirrored() for p, m in matrices.iteritems()}
			location = "R" if location == "L" else "L"

		name = self.guide().findNextSystemName(name, location)
		dupSystem = self.create(layer, location, name, matrices)
		settings = copy.deepcopy(self.settings())
		settings.pop("name")
		settings.pop("location")
		dupSystem.setSettings(**settings)

		self.layer().appendSystem(dupSystem)

		return dupSystem

	def mirror(self, duplicate=True):
		if location not in "LR":
			return 

		self.loadMarkers(force=True)
		location = self._settings["location"]
		location = "R" if location == "L" else "L"
		name = self._settings["name"]

		mirrorGuide = self.guide().findSystem(naming.getSystemKey(location, name))
		if not mirrorGuide:
			if duplicate:
				return self.duplicate(mirror=True)
			return

		mirrorGuide.loadMarkers(force=True)
		matrices = {part:marker.transformWithScale().mirrored() for part, marker in self.markers().iteritems()}

		for part, marker in mirrorGuide.markers().iteritems():
			if part in matrices:
				marker.setTransform(matrices[part])

		mirrorGuide.setSettings(**self.settings())
		mirrorGuide.setSettings(location=location)

		return mirrorGuide

	def split(self):
		# This is the Method that create two symmetrical system out of one X system
		if self._settings["location"] != "X":
			raise RuntimeError("Can't split non-X System") 

		leftSystem = copy.deepcopy(self)
		rightSystem = copy.deepcopy(self)

		leftSystem.setSettings(location="L", split=True)
		rightSystem.setSettings(location="R", split=True)

		# Make sure connections are pointing to the left and right systems
		for connection in leftSystem.connections().values():
			connection.split("L")
		for connection in rightSystem.connections().values():
			connection.split("R")

		for part, marker in rightSystem.markers().iteritems():
			rightSystem.markers()[part].setMirrored(True)

		return leftSystem, rightSystem

	def builder(self, parentBuilder):
		from brigks.systems import getSystemBuilderClass
		SystemBuilder = getSystemBuilderClass(self.type())
		return SystemBuilder(parentBuilder, self)

	def setVisible(self, visible=True, gde=True, rig=True, jnt=True, ctl=True):
		'''Set the visibility of the system's objects per use

		Args:
			visible (bool): Visibility
			gde (bool): Returns the object of use config.USE_GDE
			rig (bool): Returns the object of use config.USE_RIG and USE_BFR
			jnt (bool): Returns the object of use config.USE_JNT
			ctl (bool): Returns the object of use config.USE_CTL
		'''
		objects = self.getObjects(gde, rig, jnt, ctl)
		shapes = cmds.listRelatives(objects, shapes=True, path=True) or []
		joints = cmds.ls(objects, type="joint", long=True)
		for shp in shapes + joints:
			for attr in ["lodVisibility", "visibility"]:
				if cmds.listConnections(shp+"."+attr) or cmds.getAttr(shp+"."+attr, lock=True):
					continue
				cmds.setAttr(shp+"."+attr, visible)

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
		objects = self.getObjects(gde, rig, jnt, ctl)
		shapes = cmds.listRelatives(objects, shapes=True, path=True) or []
		joints = cmds.ls(objects, type="joint", long=True)
		visible = []
		for shp in shapes + joints:
			visible.append(cmds.getAttr(shp+".lodVisibility"))
		return visible.count(True) > visible.count(False)

	def getObjects(self, gde=True, rig=True, jnt=True, ctl=True):
		'''Get the objects of the system per use

		Args:
			gde (bool): Returns the object of use config.USE_GDE
			rig (bool): Returns the object of use config.USE_RIG and USE_BFR
			jnt (bool): Returns the object of use config.USE_JNT
			ctl (bool): Returns the object of use config.USE_CTL

		Returns:
			list of str
		'''
		uses = {config.USE_GDE:gde, config.USE_RIG:rig, config.USE_BFR:rig,
			config.USE_JNT:jnt, config.USE_CTL:ctl }

		objects = []
		for use, b in uses.iteritems():
			if not b:
				continue
			search = naming.getObjectName(use, self.settings("location"), self.settings("name"), "*")
			objects += cmds.ls(search, type="transform", long=True) or []
		return objects


	# ----------------------------------------------------------------------------------
	# CONNECTIONS
	# ----------------------------------------------------------------------------------
	def connections(self, key=None):
		return self._connections if key is None else self._connections[key]

	def addConnection(self, port, connectionType, **settings):
		if port not in self.connectionPorts():
			msg = "No such port ({p} - {x}) for this system ({k} - {t})"
			raise ValueError(msg.format(p=port, x=connectionType, k=self.key(), t=self.type()))
		elif connectionType not in self.connectionPorts()[port]:
			msg = "{st}:{p} connection has invalid type ({x}), supported types {ct}"
			raise ValueError(msg.format(st=self.type(), p=port, x=connectionType, ct=self.connectionPorts()[port]))

		Connection = getSystemConnectionClass(connectionType)
		connection = Connection()
		connection.setSettings(**settings)
		self._connections[port] = connection
		return connection

	def deleteConnection(self, port):
		if port in self._connections:
			self._connections.pop(port)

	def connectionPorts(self):
		# Returns the ports as a dictionary of portName, connectionsTypes
		self.loadMarkers()
		return {}

	def connectionSlots(self):
		# Returns the slots as a dictionary of slotName, objectuse/objectPart
		self.loadMarkers()
		return {}

	# ----------------------------------------------------------------------------------
	# MARKERS
	# ----------------------------------------------------------------------------------
	@classmethod
	def pickMarkerPositions(cls):
		guides = []
		matrices = {}
		for part in cls.markerPicked:
			if part in cls.markerMinMax:
				pickMin, pickMax = cls.markerMinMax[part]
			else:
				pickMin, pickMax = 1, 1

			pp = pick.PickPositions(pickMin, pickMax, show=True, delete=False, messages=[part], returnAsMatrix=True)
			pp.start()
			result = pp.positions()
			guides += pp.guides()

			# TODO: Add an option to get the matrices to lookAt the next one
			# That will be useful for chains, arms, legs

			if not result:
				matrices = {}
				break

			if part in cls.markerMinMax:
				for i, matrix in enumerate(result):
					matrices["{}{}".format(part, i+1)] = result[i]
			else:
				matrices[part] = result[0]

		if guides:
			cmds.delete(guides)
		
		return matrices

	def createMarkers(self, matrices):
		'''Create the Markers 
		
		If the no matrices is defined for a given marker, it will first try to use the default
		value, as defined in self.markerPositions, otherwise it will just create it at origin
	
		Args:
			matrices (dict of Matrix): The matrix of the markers
		'''
		parent = None
		markers = []
		for part, matrix in checkMarkersMinMax(matrices, self.markerNames, self.markerMinMax):
			marker = self.addMarker(part, parent, matrix)
			parent = marker
			markers.append(marker.name())

		self.loadMarkers(force=True)
		self.addSettings()

		self.createMarkerCurves()

	def createMarkerCurves(self):
		'''Create the Marker Display curves from the definition in self.markerCurves
		'''
		for name, parts in self.markerCurves.iteritems():
			markers = []
			for part in parts:
				search = part+"*" if part in self.markerNames else part
				result = cmds.ls(self.getMarkerName(search), type="transform", long=True)
				result = [x for x in result if x.startswith(self.model())]
				result = sorted(result, key=lambda x:x.split("|")[-1])
				markers += result

			if len(markers) > 1:
				self.addMarkerDispCurve(name, markers)

	def deleteMarkers(self):
		self.loadMarkers(force=True)
		markers = [m.name() for m in self._markers.values()]
		if markers:
			cmds.delete(markers)

	def addMarker(self, part, parent=None, matrix=None):
		'''Create a single SystemMarker

		Args:
			part (str): Unique part of the system object
			parent (str): Marker to be parented under
			matrix (Matrix): The matrix of the markers
		
		Returns:
			SystemMarker
		'''
		parent = self.model() if parent is None else parent
		name = self.getMarkerName(part)
		if matrix is None and part in self.markerPositions:
			position = self.markerPositions[part]
			matrix = Transformation.fromParts(translation=position)
		return SystemMarker.create(name, self, parent, matrix)

	def addMarkerDispCurve(self, part, markers):
		'''Create a display curve. 

		This is just a curve constrained to the markers to help visualize there relation

		Args:
			part (str): Unique part of the system object
			markers (list of str): 
		
		Returns:
			str: The constrained curve
		'''
		curve = create.cnsCurve(self.getMarkerName(part), markers, degree=1)
		cmds.setAttr(curve+".template", True)
		return curve

	def addMarkerCamera(self, part, parent=None, matrix=None):
		parent = self.model() if parent is None else parent
		name = self.getMarkerName(part)
		if matrix is None:
			position = self.markerPositions[part]
			matrix = Transformation.fromParts(translation=position)
		return SystemMarker.createCamera(name, self, parent, matrix)

	def getMarkerName(self, part, location=None, name=None):
		location = location if location is not None else self._settings["location"]
		name = name if name is not None else self._settings["name"]
		return naming.getObjectName(config.USE_GDE, location, name, part)

	def rename(self, location, name):
		self.loadMarkers(force=True)

		for part, marker in self._markers.iteritems():
			newName = self.getMarkerName(part, location, name)
			marker.rename(newName)

		self._settings["location"] = location
		self._settings["name"] = name

		# TODO Rename Connections
		# # Connections
		# for system in self.guide().systems():
		# 	pass

		self.guide().commit()

	def loadMarkers(self, force=False):
		if self._markers is None or force:
			self._markers = dict()
			self._multiMarkers = dict()
			search = self.getMarkerName("*")
			markers = cmds.ls(search, type="transform", long=True)
			markers = [m for m in markers if m.startswith(self.model())]
			for marker in markers:
				part = marker.split("_")[-1]
				self._markers[part] = SystemMarker(marker, self)

	def markers(self, name=None):
		self.loadMarkers()
		if name is None:
			return self._markers
		elif name in self.markerMinMax:
			if name not in self._multiMarkers:
				self._multiMarkers[name] = []
				markerMin, markerMax = self.markerMinMax[name]
				limit = lambda x: x <= markerMax if markerMax > 0 else lambda i: True
				i = 1
				while limit(i):
					part = "{}{}".format(name, i)
					if part not in self._markers:
						break
					self._multiMarkers[name].append(self._markers[part])
					i += 1
			return self._multiMarkers[name]
		else:
			return self._markers[name]

	def swapMarkers(self, systemType):
		for oldPart, newPart in self.markerCompatibility[systemType].iteritems():
			if oldPart in self.markerMinMax:
				markerMin, markerMax = self.markerMinMax[oldPart]
				limit = lambda x: x <= markerMax if markerMax > 0 else lambda i: True
				i = 1
				while limit(i):
					oldName = self.getMarkerName("{}{}".format(oldPart, i))
					newName = self.getMarkerName("{}{}".format(newPart, i))
					if not cmds.objExists(oldName):
						break
					cmds.rename(oldName, newName)
					i += 1
			else:
				oldName = self.getMarkerName(oldPart)
				newName = self.getMarkerName(newPart)
				if cmds.objExists(oldName):
					cmds.rename(oldName, newName)

	# ----------------------------------------------------------------------------------
	# MARKER TRANSFORMS
	# ----------------------------------------------------------------------------------
	def transforms(self, name=None):
		if name is None:
			return {k:m.transform() for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return TransformationArray([m.transform() for m in self.markers(name)])
		else:
			return self.markers(name).transform()

	def translations(self, name=None):
		if name is None:
			return {k:m.translation() for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return Vector3Array([m.translation() for m in self.markers(name)])
		else:
			return self.markers(name).translation()

	def directions(self, name=None, axis="x"):
		if name is None:
			return {k:m.direction(axis) for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return Vector3Array([m.direction(axis) for m in self.markers(name)])
		else:
			return self.markers(name).direction(axis)

	def scales(self, name=None):
		if name is None:
			return {k:m.scale() for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return Vector3Array([m.scale() for m in self.markers(name)])
		else:
			return self.markers(name).scale()

	def count(self, part):
		'''Returns the number of multiMarker found
		
		Args:
			part (str): Unique part of the system object

		Returns:
			int
		'''
		if part not in self.markerMinMax:
			raise RuntimeError("Can't count single Markers")
		return len(self.markers(part))

	# ----------------------------------------------------------------------------------
	# MISC
	# ----------------------------------------------------------------------------------
	def addCompound(self, compoundType, name, *args, **kwargs):
		'''Helper Method. Create a compound with the right naming convention

		The compounds are methods in brigks.utils.compounds
		
		Args:
			compoundType (str): Node type
			name (str): Unique part name of the system object
			args (): Extra arguments for the method
			kwargs (): Extra arguments for the method

		Returns:
			str
		'''
		nArgs = []
		for arg in args:
			if isinstance(arg, SystemMarker):
				arg = arg.name()
			nArgs.append(arg)

		nKwargs = {}
		for key, value in kwargs.iteritems():
			if isinstance(value, SystemMarker):
				value = value.name()
			nKwargs[key] = value


		method = compounds.__dict__[compoundType]
		name = self.getMarkerName(name+"{node}")
		return method(name, *nArgs, **nKwargs)

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		self.loadMarkers()

		xmlRoot = etree.Element("System")
		xmlRoot.set("type", self.type())
		xmlRoot.set("version", self.version())
		xmlRoot.set("key", self.key())
		xmlRoot.set("settings", json.dumps(self._settings))

		for port, connection in self._connections.iteritems():
			xmlRoot.append(connection.toXml(port))

		for markerName, position in self._markers.iteritems():
			xmlMarker = etree.SubElement(xmlRoot, "Marker")
			xmlMarker.set("name", markerName)
			xmlMarker.set("position", json.dumps(position))

		return xmlRoot

	@classmethod
	def fromXml(cls, layer, xmlRoot):
		# system = cls(layer)

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", {}))

		# Markers Transforms
		xmlMarkers = xmlRoot.findall("Marker")
		matrices = {}
		for xmlMarker in xmlMarkers:
			name = xmlMarker.get("name")
			matrix = json.loads(xmlMarker.get("matrix"))
			matrices[name] = matrix

		name = settings["name"]
		location = settings["location"]

		# Create the system
		system = cls.create(layer, location, name, matrices)
		settings = {k:v for k,v in settings.iteritems() if k in system._settings}
		system.setSettings(**settings)

		# Connections
		xmlConnections = xmlRoot.findall("Connection")
		xmlConnections = {xmlCnx.get("port"):xmlCnx for xmlCnx in xmlConnections}
		for port, xmlConnection in xmlConnections.iteritems():
		 	connectionType = xmlConnection.get("type")
		 	settings = json.loads(xmlConnection.get("settings"))
			cnx = system.addConnection(port, connectionType)
			cnx.setSettings(**settings)

			# Connection = getSystemConnectionClass(connectionType)
			# connection = Connection.fromXml(xmlConnection)
			# system._connections[port] = connection

		return system
