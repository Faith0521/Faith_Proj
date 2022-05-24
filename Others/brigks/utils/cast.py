'''Cast Module

Cast any object to any other object if possible. 
Return None if that doesn't work. 

Supported type
om.MObject
om.MFnBase
om.MDagPath
om.MObjectHandle
om.MPlug
str(path)
'''

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

_classes = (om.MObject, om.MObjectHandle, om.MDagPath, om.MFnBase, om.MPlug, str, unicode)


# ----------------------------------------------------------------
# CAST
# ----------------------------------------------------------------
def toMObject(source):
	'''	Attempt to cast any source to MObject.

	Returns None if casting has failed. 
	Only works with the following type: 
	om.MObject, om.MObjectHandle, om.MDagPath, om.MFnBase, om.MPlug, str

	Args:
		source: Object to cast

	Returns:
		MObject
	'''
	if isinstance(source, om.MObject):
		return source
	elif isinstance(source, om.MFnBase):
		return source.object()
	elif isinstance(source, om.MDagPath):
		return source.node()
	elif isinstance(source, om.MObjectHandle):
		return source.object()
	elif isinstance(source, (str, unicode)):
		mobj = om.MObject()
		selectionList = om.MSelectionList()
		try:
			selectionList.add(str(source))
		except:
			return None
		selectionList.getDependNode(0,mobj)
		return mobj
	elif isinstance(source, om.MPlug):
		return source.attribute()


def toMObjectHandle(source):
	'''	Attempt to cast any source to MObjectHandle.

	Returns None if casting has failed. 
	Only works with the following type: 
	om.MObject, om.MObjectHandle, om.MDagPath, om.MFnBase, om.MPlug, str

	Args:
		source: Object to cast

	Returns:
		MObjectHandle
	'''
	if isinstance(source, om.MObjectHandle):
		return source
	elif isinstance(source, _classes):
		mObject = toMObject(source)
		return om.MObjectHandle(mObject)


def toMFn(source):
	'''	Attempt to cast any source to MFnBase.

	Returns None if casting has failed. 
	Only works with the following type: 
	om.MObject, om.MObjectHandle, om.MDagPath, om.MFnBase, om.MPlug, str

	Args:
		source: Object to cast

	Returns:
		MFnBase
	'''
	if isinstance(source, om.MFnBase):
		return source
	elif isinstance(source, _classes):
		mObject = toMObject(source)
		MFnClass = _getFunctionSet(mObject)
		if MFnClass:
			return MFnClass(mObject)
		else:
			try:
				return om.MFnDependencyNode(mObject)
			except:
				pass


def toMDagPath(source):
	'''	Attempt to cast any source to MDagPath.

	Returns None if casting has failed. 
	Only works with the following type: 
	om.MObject, om.MObjectHandle, om.MDagPath, om.MFnBase, om.MPlug, str

	Args:
		source: Object to cast (if str: fullPathName)

	Returns:
		MDagPath
	'''
	if isinstance(source, om.MDagPath):
		return source
	
	elif isinstance(source, str):
		dagPath = om.MDagPath()
		mSel = om.MSelectionList()
		mSel.add(source)    
		mSel.getDagPath(0, dagPath)
		return dagPath

	elif isinstance(source, om.MFnDagNode):
		dagPath = om.MDagPath()
		source.getPath(dagPath)
		return dagPath
	
	elif isinstance(source, _classes):
		source = toMFn(source)
		if isinstance(source, om.MFnDagNode):
			return toMDagPath(source)
		

def toPath(source):
	'''	Attempt to cast any source to str (path).
	
	Returns None if casting has failed. 
	Only works with the following type: 
	om.MObject, om.MObjectHandle, om.MDagPath, om.MFnBase, om.MPlug, str

	Args:
		source: Object to cast

	Returns:
		str: dag path of the node
	'''
	if isinstance(source, (str, unicode)):
		return source

	elif isinstance(source, om.MDagPath):
		return source.fullPathName()

	elif isinstance(source, _classes):
		if isinstance(source, om.MPlug):
			# This fails if the node of the attribute is not a Dag node
			dp = toMDagPath(source.node())
			if dp:
				path = dp.fullPathName().split("|")
				path[-1] = source.name()
				return "|".join(path)
			else:
				return source.name()
		else:
			source = toMFn(source)
			if isinstance(source, om.MFnDagNode):
				return toMDagPath(source).fullPathName()
			elif isinstance(source, om.MFnDependencyNode):
				return source.name()



# def toMPlug(source):
# 	'''
#		I couldn't find a way to get the MPlug from a given MObject or MFnAttribute

# 		Args:
# 			source: Object to cast

# 		Returns:
# 			MPlug
# 	'''

# 	if isinstance(source, om.MPlug):
# 		return source
# 	elif isinstance(source, om.MFnAttribute):
# 		mObject = toMObject(source)
# 		return om.MPlug(mObject)


# ----------------------------------------------------------------
# CAST LISTS
# ----------------------------------------------------------------
def toMObjects(sources):
	return _castList(sources, toMObject)

def toMObjectHandles(sources):
	return _castList(sources, toMObjectHandle)

def toMFns(sources):
	return _castList(sources, toMFn)

def toMPlugs(sources):
	return _castList(sources, toMPlug)

def toMDagPaths(sources):
	return _castList(sources, toMDagPath)

def toPaths(sources):
	return _castList(sources, toPath)

def _castList(sources, method):
	if isinstance(sources, om.MDagPathArray):
		sources = [sources[i] for i in xrange(sources.length())]

	try:
		sources = iter(sources)
	except:
		sources = [sources]

	return [method(x) for x in sources if x]

# ----------------------------------------------------------------
# PRIVATE
# ----------------------------------------------------------------
def _getFunctionSet(source):
	''' Retrieve the corresponding Function Set class.

	Args:
		source(MObject)

	Returns:
		MFnBase Class
	'''
	if not isinstance(source, om.MObject):
		raise ValueError("Given source must be of type MObject")

	className = 'MFn{0}'.format(source.apiTypeStr()[1:])

	if className[3:] in ["Joint"]:
		className = "MFn" + "Ik"+ className[3:]
	elif className.endswith("Constraint"):
		className = "MFnTransform"
	elif className.endswith("SkinClusterFilter"):
		className = "MFnSkinCluster"
	elif className.endswith("Component"):
		className = "MFnComponent"
	elif className.endswith("Locator") or className.endswith("LocatorNode"):
		className = "MFnDagNode"
	elif className.endswith("DagContainer"):
		className = "MFnContainerNode"

	if hasattr(om, className):
		return getattr(om, className)
	elif hasattr(oma, className):
		return getattr(oma, className)


	
