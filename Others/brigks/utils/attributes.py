'''Attributes Module

This modules provides convinient method for attributes creation and manipulation
'''

from maya import cmds

from math3d.transformation import TransformationArray, Transformation
from math3d.vectorN import Vector3
from math3d.matrixN import Matrix4

from brigks.utils import constants

# ----------------------------------------------------------------------------------
# ATTRIBUTES
# ----------------------------------------------------------------------------------
def create(node, longName, dataType="bool", value=True, minValue=None, maxValue=None,
					keyable=False, writable=True, readable=True, channelBox=True, displayName=None):
	'''Creates an attribute.

	Args:
		node (str): Node to add the attribute to.
		longName (str): Attribute Name
		dataType (str): "bool", "shot", "float", "float3", "string"...
		value (): Must be a valid type for this attribute
		keyable (bool): is keyable
		writable (bool): is writable
		readable (bool): is readable
		channelBox (bool): Shows up in the channel box
		displayName (str|None): Display Name of the parameter. Same as longName if None

	Returns:
		str: The newly created attribute path

	Raises:
		ValueError: if attibute with same name already exists
	'''
	longName = str(longName)
	displayName = longName if displayName is None else str(displayName)

	if cmds.attributeQuery(longName, node=node, exists=True):
		raise ValueError("Node already has an attribute with that name")

	kwargs = dict(
		longName=longName,
		niceName=displayName,
		attributeType=dataType,
		keyable=keyable,
		writable=writable,
		readable=readable )

	# For some reason string needs to be created with dataType and not attributeType
	if dataType == "string":
		kwargs["dataType"] = kwargs.pop("attributeType")

	isNumeric = dataType not in ["string", "enum"]

	if isNumeric:
		if value is not None and dataType[-1] not in "23":
			kwargs["defaultValue"] = value
		kwargs["hasMinValue"] = minValue is not None
		kwargs["hasMaxValue"] = maxValue is not None
		if minValue is not None:
			kwargs["minValue"] = minValue
		if maxValue is not None:
			kwargs["maxValue"] = maxValue

	if dataType == "enum":
		kwargs["enumName"] = ":".join(minValue)
		if isinstance(value, str):
			if value in minValue:
				value = minValue.index(value)
			else:
				raise ValueError("Value %s must be an int or in %s"%(value, minValue))
		kwargs["defaultValue"] = value

	# Process
	cmds.addAttr(node, **kwargs)

	if dataType.endswith("2") or dataType.endswith("3"):
		count = int(dataType[-1])
		kwargs["attributeType"] = dataType[:-1]
		for i in range(count):
			kwargs["longName"] = longName+str(i)
			kwargs["niceName"] = displayName+str(i)
			if value is not None:
				kwargs["defaultValue"] = value[i]
			cmds.addAttr(node, parent=longName, **kwargs)

	if not isNumeric:
		cmds.setAttr(node+"."+longName, value)

	return node+"."+longName

def setKeyables(node, attrs=None, lock=True):
	'''Set the transform attribute keyables on given transform node

	Args:
		node (str): Node to update
		attrs (list of str): The transform attributes to make keyable. The attribute not in this list will be non-keyable
	'''
	if attrs is None:
		attrs = constants.ATTRS_TRS

	for attrName in constants.ATTRS_TRS:
		keyable = attrName in attrs
		cmds.setAttr(node+"."+attrName, lock=not keyable and lock)
		cmds.setAttr(node+"."+attrName, keyable=keyable)
		if not keyable:
			cmds.setAttr(node+"."+attrName, channelBox=keyable)

def setRotOrder(node, rotOrder):
	'''Set the rotation order on given node

	This ensure the global transform of the node are unchanged

	Args:
		node (str): Node to update
		rotOrder (str): rotation order ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]
	'''
	matrix = cmds.xform(node, q=True, matrix=True, worldSpace=True)
	cmds.setAttr(node+".rotateOrder", constants.ROT_ORDERS.index(rotOrder.lower()))
	cmds.xform(node, matrix=matrix, worldSpace=True)

def inheritsTransform(node, inherit):
	'''Set the 'inheritsTransform' attr for the given node

	This ensure the global transform of the node are unchanged

	Args:
		node (str): Node to update
		inherit (bool): 
	'''
	matrix = cmds.xform(node, q=True, matrix=True, worldSpace=True)
	cmds.setAttr(node+".inheritsTransform", inherit)
	cmds.xform(node, matrix=matrix, worldSpace=True)
	
def setLimits(node, attrs, minimum=None, maximum=None):
	'''Set the limit for the the given transform attributes

	Args:
		node (str): Node to update
		attrs (list of str): Attributes to update
		minimum (float): Minimum value
		maximum (float): Maximum value
	'''
	for attr in attrs:
		cmds.setAttr(node+".min"+attr+"LimitEnable", minimum is not None)
		cmds.setAttr(node+".max"+attr+"LimitEnable", maximum is not None)
		if minimum is not None:
			cmds.setAttr(node+".min"+attr+"Limit", minimum)
		if maximum is not None:
			cmds.setAttr(node+".max"+attr+"Limit", maximum)

def setColor(node, color):
	''' Set the color of given node

	Args:
		node (str): Node to update
		color (int|float triplet): color as index or rgb(0-1)
	'''
	if color is None:
		cmds.setAttr(node+".overrideEnabled", False)
		return 

	isIndex = isinstance(color, int)
	if not isIndex and not [isinstance(c, float) for c in list(color)]:
		raise ValueError("Given color must be index or float triplet")


	cmds.setAttr(node+".overrideEnabled", True)
	cmds.setAttr(node+".overrideRGBColors", not isIndex)

	if isIndex:
		cmds.setAttr(node+".overrideColor", color)
	else:
		cmds.setAttr(node+".overrideColorR", color[0])
		cmds.setAttr(node+".overrideColorG", color[1])
		cmds.setAttr(node+".overrideColorB", color[2])

def setMatrix(node, matrix, worldSpace=True):
	''' Set the matrix of a given node
	
	Set the matrix of the node regardless how it's described

	Args:
		node (str): Node to update
		matrix (math3d.Transformation||math3d.Matrix4||list of float): The transformation matrix
	'''
	if isinstance(matrix, Transformation):
		matrix = matrix.asMatrix().flattened()
	elif isinstance(matrix, Matrix4):
		matrix = matrix.flattened()

	cmds.xform(node, matrix=matrix, worldSpace=worldSpace)