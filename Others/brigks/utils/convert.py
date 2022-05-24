'''Convert Module

This convert rigguide definition to Brigks
Currently only support Harbie. harbie is Blur's Rig Builder
This code is messy and is not meant to be very reusable. It's a patch to help the transition to Brigks
'''
import json
import getpass
import datetime
import xml.etree.cElementTree as etree

from math3d.transformation import Transformation
from math3d.quaternion import Quaternion
from math3d.vectorN import Vector3

HARBIE_TYPES = dict(
		arm01="arm",
		basic01="basic",
		bean01="quadrant",
		breast01="breast",
		camera01="camera",
		chain01="chain",
		foot01="foot",
		leg01="leg",
		leg3bones01="zleg",
		lookAt01="lookat",
		meta01="meta",
		neck01="neck",
		params01="attribute",
		psdDriver01="psd",
		piston="piston",
		slider01="slider",
		spine01="spine",
		stretch01="stretch",
		tracker01="tracker",
		transformAverage01="average",
		transformDriven01="driven",
		transformMulti01="multi",
		twistSpline01="twist",
		tentacle01="tentacle"
	)

MARKER_NAMES = dict(
	lookAt01=dict(
		Target="Eff",
		),
	breast01=dict(
		Tip="Eff"
		),
	piston=dict(
		End="Eff"
		),
	stretch01=dict(
		End="Eff"
		),
	)

SETTINGS_NAMES = dict(
	basic01=dict(
		addDeformerReferences="addJointReference",
		),
	params01=dict(
		paramDefOrder="order",
		paramDefs="definitions",
		),
	tracker01=dict(
		driverDefOrder="order",
		driverDefs="definitions",
		),
	tentacle01=dict(
		deformers="jointsCount",
		segDeformers="lowJointsCount",
		),
	)


PORT_NAMES = dict(
	chain01=dict(
		FkRef="FK",
		),
	lookAt01=dict(
		Target="Eff",
		),
	neck01=dict(
		IkRef="IK",
		OriRef="Orient",
		),
	basic01=dict(
		Control="Part"
		),
	leg01=dict(
		IkRef="IK",
		FkRef="FK",
		),
	arm01=dict(
		IkRef="IK",
		FkRef="FK",
		),
	leg3bones01=dict(
		IkRef="IK",
		FkRef="FK",
		),
	)

COMPONENT_TYPES = dict(
	pntSubComponent="vertex",
	edgeSubComponent="edge",
	polySubComponent="face",
	)


# ----------------------------------------------------------------------------------
# 
# ----------------------------------------------------------------------------------
def convertXmlHarbie(xmlHarbie, useSymmetrySystems=False):
	xmlRoot = etree.Element("Guide")
	xmlRoot.set("user", getpass.getuser())
	xmlRoot.set("date", str(datetime.datetime.now()))

	# Settings
	xmlHarbieParameters = xmlHarbie.find("Parameters")
	settings = json.loads(xmlHarbieParameters.get("value", {}))
	if settings["stopAfter"] == "All":
		settings["stopAfter"] = "Post Script"
	xmlRoot.set("settings", json.dumps(settings))

	# Layers
	xmlHarbieLayers = xmlHarbie.find("Layers")
	for xmlHarbieLayer in xmlHarbieLayers:
		xmlLayer = _convertXmlLayer(xmlHarbieLayer, useSymmetrySystems)
		xmlRoot.append(xmlLayer)

	return xmlRoot


# ----------------------------------------------------------------------------------
# LAYERS
# ----------------------------------------------------------------------------------
def _convertXmlLayer(xmlHarbieLayer, useSymmetrySystems):
	xmlLayer = etree.Element("Layer")
	xmlLayer.set("name", xmlHarbieLayer.get("name"))

	xmlHarbieParameters = xmlHarbieLayer.find("Parameters")
	settings = json.loads(xmlHarbieParameters.get("value", {}))
	settings["color"] = settings.pop("layerColor")
	xmlLayer.set("settings", json.dumps(settings))

	xmlHarbieSystems = xmlHarbieLayer.find("Systems")
	for xmlHarbieSystem in xmlHarbieSystems:
		xmlSystem = _convertXmLSystem(xmlHarbieSystem, useSymmetrySystems)
		if xmlSystem:
			xmlLayer.append(xmlSystem)

	return xmlLayer

# ----------------------------------------------------------------------------------
# SYSTEMS
# ----------------------------------------------------------------------------------
def _convertXmLSystem(xmlHarbieSystem, useSymmetrySystems):
	systemKey = xmlHarbieSystem.get("key")
	systemType = xmlHarbieSystem.get("type")
	if systemType not in HARBIE_TYPES:
		print "Unknow type", systemKey, systemType
		return None

	xmlHarbieParameters = xmlHarbieSystem.find("Parameters")
	settings = json.loads(xmlHarbieParameters.get("value", {}))
	if systemType in SETTINGS_NAMES:
		for k, v in SETTINGS_NAMES[systemType].iteritems():
			settings[v] = settings.pop(k)

	if settings["location"] == "X":
		settings["location"] = "M"

	settings["location"] = settings["location"].replace("-", "")
	if len(settings["location"]) > 1:
		suffix = settings["location"][1:]
		settings["location"] = settings["location"][0]
		settings["name"] = settings["name"] + suffix

	if useSymmetrySystems:
		if settings["location"] == "L":
			settings["location"] = "X"
		elif settings["location"] == "R":
			return

	systemKey = "{n}_{l}".format(n=settings["name"], l=settings["location"])

	xmlSystem = etree.Element("System")
	xmlSystem.set("key", systemKey)
	xmlSystem.set("type", HARBIE_TYPES[systemType])

	connectionType = settings.pop("connectionType")
	connectionData = settings.pop("connections")
	xmlSystem.set("settings", json.dumps(settings))

	xmlConnections = _convertXmlConnection(connectionType, connectionData, systemType, useSymmetrySystems)
	xmlSystem.extend(xmlConnections)

	xmlHarbieMarkers = xmlHarbieSystem.find("Markers")
	for xmlHarbieMarker in xmlHarbieMarkers:
		name = xmlHarbieMarker.get("name")
		if "Crv" in name:
			continue
		xmlMarker = _convertXmlMarker(xmlHarbieMarker, systemType)
		xmlSystem.append(xmlMarker)

	return xmlSystem

# ----------------------------------------------------------------------------------
# CONNECTIONS
# ----------------------------------------------------------------------------------
def _convertXmlConnection(connectionType, connectionData, systemType, useSymmetrySystems):
	xmlConnections = []
	if connectionType == "standard":
		rotationTracker = {}
		average = {}
		for port, data in connectionData.iteritems():
			if "keyslots" not in data or not data["keyslots"]:
				continue

			# Renaming ports
			if systemType in PORT_NAMES:
				if port in PORT_NAMES[systemType]:
					port = PORT_NAMES[systemType][port]
				else:
					for xport, nport in PORT_NAMES[systemType].iteritems():
						if port.startswith(xport):
							port = port.replace(xport, nport)
							break

			if systemType == "foot01" and port == "Root":
				# Foot Attach
				xmlConnection = _convertXmlConnectionFootAttach(port, data, useSymmetrySystems)
				xmlConnections.append(xmlConnection)
			elif port == "UI":
				xmlConnection = _convertXmlConnectionUI(port, data, useSymmetrySystems)
				xmlConnections.append(xmlConnection)
			elif systemType in ["transformDriven01", "slider01", "rotationalSlider01", "tracker01"]\
				and port in ["Reference", "Tracker"]:
				rotationTracker[port] = data["keyslots"][0]
			elif systemType in ["transformAverage01"]\
				and port in ["Parent", "MasterA", "MasterB"]:
				average[port] = data["keyslots"][0]
			else:
				xmlConnection = _convertXmlConnectionStandard(port, data, useSymmetrySystems)
				xmlConnections.append(xmlConnection)

		if rotationTracker:
			xmlConnection = _convertXmlConnectionRotationTracker(rotationTracker, useSymmetrySystems)
			xmlConnections.append(xmlConnection)

		if average:
			xmlConnection = _convertXmlConnectionAverage(average, useSymmetrySystems)
			xmlConnections.append(xmlConnection)

	elif connectionType == "obj2cls":
		for port, data in connectionData.iteritems():
			if "geometry" not in data or not data["geometry"]:
				continue

			if "Cls" in port:
				port = port.replace("Cls", "")

			if systemType in PORT_NAMES:
				if port in PORT_NAMES[systemType]:
					port = PORT_NAMES[systemType][port]
				else:
					for xport, nport in PORT_NAMES[systemType].iteritems():
						if port.startswith(xport):
							port = port.replace(xport, nport)
							break

			xmlConnection = _convertXmlConnectionObj2Cls(port, data, useSymmetrySystems)
			xmlConnections.append(xmlConnection)

	return xmlConnections

def _convertXmlConnectionStandard(port, data, useSymmetrySystems):
	keyslots = _renamePorts(data["keyslots"])

	if port in ["FK", "Orient"]:
		cnxType = "multiOrient"

		definitions = []
		for key, slot in keyslots:
			definition = dict(
				type="slot",
				key=_renameKey(key, useSymmetrySystems),
				slot=slot)
			definitions.append(definition)

		settings = dict(definitions=definitions)
	elif len(keyslots) == 1:
		cnxType = "slotParent"
		key, slot = keyslots[0]

		settings = dict(
				key=_renameKey(key, useSymmetrySystems),
				slot=slot)
	else:
		cnxType = "multiParent"

		definitions = []
		for key, slot in keyslots:
			definition = dict(
				type="slot",
				key=_renameKey(key, useSymmetrySystems),
				slot=slot)
			definitions.append(definition)

		settings = dict(definitions=definitions)

	if port.startswith("Control"):
		port.replace("Control", "Part")

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", cnxType)
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection


def _convertXmlConnectionUI(port, data, useSymmetrySystems):
	keyslots = _renamePorts(data["keyslots"])

	key, slot = keyslots[0]
	settings = dict(
		key=_renameKey(key, useSymmetrySystems),
		slot=slot)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", "uiHost")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection


def _convertXmlConnectionFootAttach(port, data, useSymmetrySystems):
	keyslots = data["keyslots"]
	key, slot = keyslots[0]
	settings = dict(
		key=_renameKey(key, useSymmetrySystems),
		slot=slot)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", "footLegAttach")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection

def _convertXmlConnectionRotationTracker(data, useSymmetrySystems):
	refKey, refSlot = data["Reference"]
	trkKey, trkSlot = data["Tracker"]
	settings = dict(
		referenceKey=_renameKey(refKey, useSymmetrySystems),
		referenceSlot=refSlot,
		trackerKey=_renameKey(trkKey, useSymmetrySystems),
		trackerSlot=trkSlot)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", "Tracker")
	xmlConnection.set("type", "rotationTracker")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection

def _convertXmlConnectionAverage(data, useSymmetrySystems):
	parentKey, parentSlot = data.get("Parent", (None, None))
	masterAKey, masterASlot = data["MasterA"]
	masterBKey, masterBSlot = data["MasterB"]
	settings = dict(
		parentKey=_renameKey(parentKey, useSymmetrySystems), parentSlot=parentSlot,
		masterAkey=_renameKey(masterAKey, useSymmetrySystems), masterASlot=masterASlot,
		masterBkey=_renameKey(masterBKey, useSymmetrySystems), masterBSlot=masterBSlot )

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", "Average")
	xmlConnection.set("type", "averageTransform")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection

def _convertXmlConnectionObj2Cls(port, data, useSymmetrySystems):

	keyslots = _renamePorts([data["oriReference"]])

	settings = dict(
		mesh=data["geometry"].replace("-", ""),
		componentType=COMPONENT_TYPES[data["clusterType"]],
		componentIndex=data["componentIndex"],
		key=_renameKey(keyslots[0][0], useSymmetrySystems),
		slot=keyslots[0][1],
		useOrientation=data["useClusterOrientation"],
		useClosest=data["componentIndex"] == "" or data["componentIndex"] is None
	)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", "meshAttach")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection

def _renameKey(key, useSymmetrySystems):
	if key is None:
		return
	if key == "self":
		return key

	key = key.replace("-", "")

	if key.endswith("_X"):
		return key[:-2]+"_M"

	name, loc = key.split("_")
	if loc > 1:
		suffix = loc[1:]
		loc = loc[0]
		name = name + suffix
		key = "_".join([name, loc])

	if key.endswith("_L") and useSymmetrySystems:
		key = key[:-2] + "_X"

	return key

def _renamePorts(keyslots):
	# Renaming Slots
	for i, (key, slot) in enumerate(keyslots):
		if "-" in slot:
			slot = slot.replace("-", "")

		if slot.startswith("Ctrl"):
			slot = slot.replace("Ctrl", "Part")
		elif slot == "IkCtrl":
			slot = "IK"
		elif slot == "01Pelvis":
			slot = "Pelvis"
		elif slot == "02Lower":
			slot = "Lower"
		elif slot == "03Middle":
			slot = "Middle"
		elif slot == "04Upper":
			slot = "Upper"
		elif slot == "05Chest":
			slot = "Chest"

		keyslots[i] = (key, slot)
	return keyslots

# ----------------------------------------------------------------------------------
# MARKERS
# ----------------------------------------------------------------------------------
def _convertXmlMarker(xmlHarbieMarker, systemType):
	xmlMarker = etree.Element("Marker")
	name = xmlHarbieMarker.get("name")

	if systemType in MARKER_NAMES and name in MARKER_NAMES[systemType]:
		name = MARKER_NAMES[systemType][name]

	xmlMarker.set("name", name)

	# Transform
	transform = json.loads(xmlHarbieMarker.get("transform"))
	matrix = _convertTransformToMatrix(**transform)
	xmlMarker.set("matrix", json.dumps(list(matrix)))

	return xmlMarker


def _convertTransformToMatrix(translation, rotation, scaling):
	rotation = rotation[1:] + rotation[:1]

	translation = Vector3(translation)
	rotation = Quaternion(rotation)
	scaling = Vector3(scaling)

	transform = Transformation.fromParts(translation, rotation, scaling)
	return transform.asMatrix().flattened()
