import os.path
import itertools
from collections import OrderedDict

from maya import cmds

from brigks.utils import attributes, create, compounds, script
from brigks import naming, config

class SystemBuilder():
	'''System Builder Class

	This is the core class for all system builders. It defines the main methods and all the systems are inheriting from this class 

	coreBuilder (Builder):
	nodes (dict of str):
	model (str):
	guide (SystemGuide):
	settings (dict):
	_connections (dict of Connection):
	attributeNames (list str):
	_uiHosts ():

	key (str):
	type (str):

	steps (OrderedDict):
	'''

	def __init__(self, coreBuilder, guide):
		'''Builder Init

		Args:
			coreBuilder (Builder): The main Builder
			guide (SystemGuide): The SystemGuide to build from

		Returns:
			SystemBuilder
		'''
		self.coreBuilder = coreBuilder
		self.nodes = self.coreBuilder.nodes
		self.model = self.coreBuilder.model
		self.guide = guide
		self.settings = self.guide.settings
		self.setSettings = self.guide.setSettings
		self._connections = self.guide._connections
		self.attributeNames = []
		self._uiHosts = {}

		self.key = self.guide.key
		self.type = self.guide.type
		self.colorIk = self.guide.colorIk
		self.colorFk = self.guide.colorFk
		self.markers = self.guide.markers
		self.transforms = self.guide.transforms
		self.translations = self.guide.translations
		self.directions = self.guide.directions
		self.scales = self.guide.scales
		self.count = self.guide.count

		# Building Steps
		# For each system we're building, each step will be processed for all the systems
		# before running the next step. This ensure all the objects have been created 
		# before we start connecting systems together.
		# Having Attributes created after the Operators, allow us to recreate and reconnect attributes if needed
		self.steps = OrderedDict()
		self.steps["Pre Script"] = self.stepPreScript
		self.steps["Create Objects"] = self.stepObjects
		self.steps["Create Attributes"] = self.stepAttributes
		self.steps["Create Operators"] = self.stepOperators
		self.steps["Connect System"] = self.stepConnections
		self.steps["Post Script"] = self.stepPostScript

	# ----------------------------------------------------------------------------------
	#  SETTINGS
	# ----------------------------------------------------------------------------------
	def negate(self):
		'''Returns True if the system is on the negative side

		Returns:
			bool
		'''
		return self.settings("location") == "R"

	def sign(self):
		'''Returns "-" if the system is on the negative side

		Returns:
			str
		'''
		return "-" if self.negate() else ""

	def nsign(self):
		'''Returns "-" if the system is on the positive side

		Returns:
			str
		'''
		return "" if self.negate() else "-"

	def factor(self):
		'''Returns -1 if the system is on the negative side

		Returns:
			int
		'''
		return -1 if self.negate() else 1

	def connections(self, key=None, includeUIHosts=False):
		'''Returns the Connections of the systems

		# TODO This method could be moved to the guide
		Not sure the uiHost management is the right way

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that connection value
			includeUIHosts (bool): True to include UIHost connections

		Returns:
			int
		'''
		if includeUIHosts:
			connections = self._connections
		else:
			connections = {k:v for k, v in self._connections.iteritems() if v.type() != "uiHost"}
		return connections if key is None else connections[key]
		
	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def stepPreScript(self):
		'''Building Step. Runs the pre script 
		'''
		script.execute(self.settings("preScriptPath"), self.settings("preScriptValue"),
			dict(cmds=cmds, this_model=self.model(), this_guide=self.guide))

	def stepObjects(self):
		'''Building Step. Delete and create objects 
		'''
		self.preDeleteObjects()
		self.deleteObjects()
		self.createObjects()
		if self.settings("createJoints"):
			self.createJoints()

	def stepOperators(self):
		'''Building Step. Create the operators and utilities nodes
		'''
		self.createOperators()

	def stepAttributes(self):
		'''Building Step. Create the attributes
		'''
		self.deleteAttributes()

		# Get UIHost
		for port, cnx in self._connections.iteritems():
			if cnx.type() == "uiHost":
				cnx.setBuilder(self)
				self._uiHosts[port] = cnx.getHost()

		self.createAttributes()

	def stepConnections(self):
		'''Building Step. Create the connections
		'''
		# Init Connections
		for slot, cnx in self.connections(includeUIHosts=False).iteritems():
			cnx.setBuilder(self)
		self.createConnections()

	def stepPostScript(self):
		'''Building Step. Runs the post script 
		'''
		script.execute(self.settings("postScriptPath"), self.settings("postScriptValue"),
			dict(cmds=cmds, this_model=self.model(), this_guide=self.guide))

	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def preDeleteObjects(self):
		'''Reimplement. Ran before deleting objects

		Can be used to store information before deleting a system
		'''
		pass
		
	def deleteObjects(self):
		'''Delete all the objects of that system
		'''
		search = self.getObjectName("*", "*")
		parent = cmds.ls(self.nodes("local"), long=True)[0]
		toDelete = [x for x in cmds.ls(search, type="transform", long=True) if x.startswith(parent)]
		if toDelete:
			# Unparent all the children
			children = cmds.listRelatives(toDelete, children=True, type="transform", path=True)
			children = [x for x in cmds.ls(children, long=True) if x not in toDelete]
			if children:
				cmds.parent(children, self.nodes("local"))

			# Delete objects
			cmds.delete(cmds.ls(toDelete, long=True))

		# Delete Utility Nodes
		search = self.getObjectName(config.USE_NDE, "*")
		toDelete = cmds.ls(search, long=True)
		if toDelete:
			cmds.delete(toDelete)

	def createObjects(self):
		'''Reimplement. Create the objects for that specific system
		'''
		pass

	def deleteJoints(self):
		'''Delete all the joints of that system
		'''
		search = self.getObjectName(config.USE_JNT, "*")
		parent = cmds.ls(self.nodes("local"), long=True)[0]
		toDelete = [x for x in cmds.ls(search, type="joint", long=True) if x.startswith(parent)]
		if toDelete:
			# Unparent all the children
			children = cmds.listRelatives(toDelete, children=True, type="transform", path=True)
			children = [x for x in cmds.ls(children, long=True) if x not in toDelete]
			if children:
				cmds.parent(children, self.nodes("local"))

			# Delete objects
			cmds.delete(toDelete)

	def createJoints(self):
		'''Reimplement. Create the joints for that specific system
		'''
		pass

	def createOperators(self):
		'''Reimplement. Create the operators for that specific system
		'''
		pass

	def deleteAttributes(self):
		'''Delete all the attributes of that system
		'''
		if self.key() in self.coreBuilder.builtSettings():
			settings = self.coreBuilder.builtSettings(self.key())
			for name in settings["attributes"]:
				attr = cmds.ls("*."+name)
				if attr:
					cmds.deleteAttr(attr)

	def createAttributes(self):
		'''Reimplement. Create the attributes for that specific system
		'''
		pass

	def createConnections(self):
		'''Reimplement. Create the connections for that specific system
		'''
		pass

	def delete(self):
		'''Delete all the objects, joints and attributes of the system
		'''
		self.deleteObjects()
		self.deleteJoints()
		self.deleteAttributes()

	# ----------------------------------------------------------------------------------
	#  HELPERS to CREATE OBJECTS / ATTRIBUTES
	# ----------------------------------------------------------------------------------
	def addTransform(self, parent, part, use, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		'''Helper Method. Create a new transform node
		
		You shouldn't use this method directly. You should instead use addBfr, addRig, addCtl, addJnt

		Args:
			parent (str): Parent node
			part (str): Unique part name of the system object
			use (str): Use of the system object (config.USE_BFR, CTL, JNT, RIG)
			tfm (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
			icon (str): Type of nurbscurve shape 
			size (float): Size of the shape
			po (triplet of float): Position offset of the shape
			ro (triplet of float): Rotation offset of the shape
			so (triplet of float): Scale offset of the shape
			color (triplet of float): Color of the shape

		Returns:
			str
		'''
		parent = parent if parent is not None else self.nodes("local")
		name = self.getObjectName(use, part)
		node = create.transform(name, parent, tfm, color=color)
		if icon:
			create.icon(icon, node, size, po, ro, so)
		return node

	def addCtl(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		'''Helper Method. Create a new controller node

		Args:
			parent (str): Parent node
			part (str): Unique part name of the system object
			tfm (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
			icon (str): Type of nurbscurve shape 
			size (float): Size of the shape
			po (triplet of float): Position offset of the shape
			ro (triplet of float): Rotation offset of the shape
			so (triplet of float): Scale offset of the shape
			color (triplet of float): Color of the shape

		Returns:
			str
		'''
		return self.addTransform(parent, part, config.USE_CTL, tfm, icon, size, po, ro, so, color)

	def addBfr(self, parent, part, tfm=None):
		'''Helper Method. Create a new Buffer node

		Args:
			parent (str): Parent node
			part (str): Unique part name of the system object
			tfm (math3d.Transformation||math3d.Matrix4||list of float): The world transformation

		Returns:
			str
		'''
		icon = "cube"
		size = .2
		color = [0,0,0]
		return self.addTransform(parent, part, config.USE_BFR, tfm, icon, size, color=color)

	def addRig(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		'''Helper Method. Create a new Rig node

		Args:
			parent (str): Parent node
			part (str): Unique part name of the system object
			tfm (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
			icon (str): Type of nurbscurve shape 
			size (float): Size of the shape
			po (triplet of float): Position offset of the shape
			ro (triplet of float): Rotation offset of the shape
			so (triplet of float): Scale offset of the shape
			color (triplet of float): Color of the shape

		Returns:
			str
		'''
		color = [0,0,0]
		return self.addTransform(parent, part, config.USE_RIG, tfm, icon, size, po, ro, so, color)

	def addJnt(self, parent, part, reference=None):
		'''Helper Method. Create a new Joint node

		Args:
			parent (str): Parent node
			part (str): Unique part name of the system object
			reference (str): Object to be used for the reference bindpose of the joint

		Returns:
			str
		'''
		name = self.getObjectName(config.USE_JNT, part)
		parent = parent if parent is not None else self.nodes("local")
		matrix = cmds.xform(parent, q=True, matrix=True, worldSpace=True)
		color = [1,0,0]

		jnt = create.joint(name, parent, matrix, color, radius=.5)

		# Bind Pose reference
		if reference:
			attr = jnt+"."+config.BINDPOSE_ATTRIBUTE
			if not cmds.ls(attr):
				cmds.addAttr(jnt, longName=config.BINDPOSE_ATTRIBUTE, dataType="matrix")

			cmds.connectAttr(reference+".worldInverseMatrix[0]", attr, force=True)

			done = []
			for connection in cmds.listConnections(jnt, type="skinCluster", plugs=True) or []:
				skinCluster, skinClusterAttr = connection.split(".") 
				if skinCluster in done:
					continue
				index = int(skinClusterAttr.split("[")[-1][:-1])
				cmds.connectAttr(attr, skinCluster+".bindPreMatrix[{}]".format(index), force=True)
				done.append(skinCluster)

		return jnt

	def addCamera(self, parent, part, tfm=None, color=None, **kwargs):
		'''Helper Method. Create a new Rig node

		Args:
			parent (str): Parent node
			part (str): Unique part name of the system object
			tfm (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
			color (triplet of float): Color of the shape
			kwargs (dict): Extra settings of the camera (see brigks.utils.create.camera())

		Returns:
			str
		'''
		name = self.getObjectName(config.USE_CTL, part)
		parent = parent if parent is not None else self.nodes("local")

		return create.camera(name, parent, matrix=tfm, color=color, **kwargs)

	def addSurfaceJnts(self, surface, count, part="Strap"):
		'''Helper Method. Create joints attached to a surface

		Args:
			surface (str): Surface to attach to
			count (int): Number of joint to create (always evenly distributed)
			part (str): Unique part name of the system object

		Returns:
			list of str
		'''
		parent = surface
		joints = [self.addJnt(parent, "{}{}".format(part,i)) for i in xrange(1, count+1)]
		
		# Disconnect the deformer if there is a left over constraint
		for jnt in joints:
			connections = cmds.listConnections(jnt, destination=True)
			if connections:
				srfAttach = [node for node in connections if cmds.nodeType(node) == "SurfaceMultiAttach"]
				if srfAttach:
					cmds.delete(srfAttach)

		# 0 Parametric, 1 Percentage, 2 Fixed Length
		self.addCompound("surfaceMultiAttach", "JntSrf", [joints], surface, attach=0, evenly=True)

		for jnt in joints:
			cmds.connectAttr(self.nodes("local")+".sx" ,jnt+".sx")
			cmds.connectAttr(self.nodes("local")+".sx" ,jnt+".sy")
			cmds.connectAttr(self.nodes("local")+".sx" ,jnt+".sz")

		return joints

	def addAttr(self, host, name, attrType, value=None, minValue=None, maxValue=None,
			keyable=False, writable=True, readable=True, channelBox=True):
		'''Helper Method. Create a new attributes on a given node
		
		You shouldn't use this method directly. You should instead use addAnimAttr or addSetupAttr

		Args:
			host (str): Node to create the attribute on
			name (str): Unique part name of the system object
			attrType (str): 'bool', 'string', 'short', 'float'...
			value (): Default value matching the type defined 
			minValue (float||int): Minimum value of the attribute (for float and integer)
			maxValue (float||int): Maximum value of the attribute (for float and integer)
			keyable (bool): Is keyable
			writable (bool): Is writable
			readable (bool): Is readable
			channelBox (bool): Is visible in the channelBox

		Returns:
			str
		'''
		longName = self.getObjectName(config.USE_RIG, name)
		a = attributes.create(host, longName, attrType, value, minValue, maxValue,
					keyable, writable, readable, channelBox, name)
		self.attributeNames.append(longName)
		return a

	def addAnimAttr(self, name, attrType, value,
			minValue=None, maxValue=None, keyable=True):
		'''Helper Method. Create a new Animation attributes
		
		This attribute is meant to be accessible by animators

		Args:
			name (str): Unique part name of the system object
			attrType (str): 'bool', 'string', 'short', 'float'...
			value (): Default value matching the type defined 
			minValue (float||int): Minimum value of the attribute (for float and integer)
			maxValue (float||int): Maximum value of the attribute (for float and integer)
			keyable (bool): Is keyable

		Returns:
			str
		'''

		# For now we only support one UIHost, but we could 
		# pass an argument for which host to crete the attr to
		if "UI" not in self._uiHosts:
			self._uiHosts["UI"] = self.addRig(self.nodes("setup"), "Anim")
			attributes.setKeyables(self._uiHosts["UI"], [])

		a = self.addAttr(self._uiHosts["UI"], name, attrType, value,
					minValue, maxValue, keyable, writable=True)
		return a

	def addSetupAttr(self, name, attrType, value,
			minValue=None, maxValue=None, keyable=True, writable=True):
		'''Helper Method. Create a new Animation attributes
		
		This attribute is NOT meant to be accssible by animators

		Args:
			name (str): Unique part name of the system object
			attrType (str): 'bool', 'string', 'short', 'float'...
			value (): Default value matching the type defined 
			minValue (float||int): Minimum value of the attribute (for float and integer)
			maxValue (float||int): Maximum value of the attribute (for float and integer)
			keyable (bool): Is keyable
			writable (bool): Is writable

		Returns:
			str
		'''
		if "Setup" not in self._uiHosts:
			self._uiHosts["Setup"] = self.addRig(self.nodes("setup"), "Setup")
			attributes.setKeyables(self._uiHosts["Setup"], [])

		a = self.addAttr(self._uiHosts["Setup"], name, attrType, value,
					minValue, maxValue, keyable, writable)
		return a

	def addNode(self, nodeType, name):
		'''Helper Method. Create a Maya node with the right naming convention
		
		Args:
			nodeType (str): Node type
			name (str): Unique part name of the system object

		Returns:
			str
		'''
		name = self.getObjectName(config.USE_NDE, name)
		return cmds.createNode(nodeType, name=name)

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
		method = compounds.__dict__[compoundType]
		name = self.getObjectName(config.USE_NDE, name+"{node}")
		return method(name, *args, **kwargs)

	# ----------------------------------------------------------------------------------
	# GET OBJECTS and NAMES
	# ----------------------------------------------------------------------------------
	def getObjectName(self, use, part):
		'''Helper Method. Return an object name matching the naming convention
		
		Args:
			use (str): Use of the system object (config.USE_BFR, CTL, JNT, RIG)
			part (str): Unique part name of the system object

		Returns:
			str
		'''
		return naming.getObjectName(
			use=use,
			location=self.settings("location"),
			name=self.settings("name"),
			part=part)

	def getObject(self, use, part):
		'''Returns the system object if existing
		
		Args:
			use (str): Use of the system object (config.USE_BFR, CTL, JNT, RIG)
			part (str): Unique part name of the system object

		Returns:
			str
		'''
		name = self.getObjectName(use, part)
		objects = [x for x in cmds.ls(name, type="transform", long=True) if x.startswith(self.model())]
		if objects:
			return cmds.ls(objects)[0]

	def getObjectFromSlot(self, slot):
		'''Returns the system object attached to a specific slot for connection
		
		Args:
			slot (str): Slot name

		Returns:
			str
		'''
		slots = self.guide.connectionSlots()
		if slot in slots:
			use, part = slots[slot]
			return self.getObject(use, part)

	def getAttribute(self, name):
		'''Returns the system attributes whereever it has been created
		
		Args:
			name (str): Attribute Name

		Returns:
			str
		'''
		longName = self.getObjectName(config.USE_RIG, name)
		attributes = [x for x in cmds.ls("*."+longName, long=True) if x.startswith(self.model())]
		if attributes:
			return attributes[0]

