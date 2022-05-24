'''Cast Module

This modules provides convinient method to create complex set of nodes and connections
'''
from itertools import izip, product
import math

from maya import cmds
from maya import OpenMaya as om

from math3d.matrixN import Matrix4

from brigks.utils import attributes, cast

POINTAT_AXIS = ["X", "Y", "Z", "-X", "-Y", "-Z"]
COMPARE_OPS = ["==", "!=", ">", ">=", "<", "<="]

def compare(name, first, second, operation):
	'''	Create a Compare nodes compound

	Args:
		name (str): name of the nodes
		first (str||float||int): First value to compare
		second (str||float||int): Second value to compare
		operation (str): ["==", "!=", ">", ">=", "<", "<="]

	Returns:
		str: The condition node
	'''
	if operation not in COMPARE_OPS:
		raise ValueError("Given operation must be in {}".format(COMPARE_OPS))

	if "{node}" not in name:
		name += "{node}"

	node = cmds.createNode("condition", name=name.format(node="Cond"))

	if isinstance(first, float) or isinstance(first, int):
		cmds.setAttr(node+".firstTerm", first)
	else:
		cmds.connectAttr(first, node+".firstTerm")

	if isinstance(second, float) or isinstance(second, int):
		cmds.setAttr(node+".secondTerm", second)
	else:
		second = attribute.get(*second)
		cmds.connectAttr(second, node+".secondTerm")

	cmds.setAttr(node+".operation", COMPARE_OPS.index(operation))

	cmds.setAttr(node+".colorIfTrueR", 1)
	cmds.setAttr(node+".colorIfFalseR", 0)

	return node

# ----------------------------------------------------------------------------------
# TRANSFORMS - CONSTRAINTS
# ----------------------------------------------------------------------------------
def blendMatrix(name, slave, masters, maintainOffset=False, translate=True, rotate=True, scale=True, useJointOrient=False):
	'''	Create a BlendMatrix nodes compound

	Args:
		name (str): Name of the nodes
		slave (str): The node to constraint
		masters (list of str): The nodes that will drive the constraint
		maintainOffset (bool): True to maintain original offset
		translate (bool): True to connect the translation
		rotate (bool): True to connect the rotate
		scale (bool): True to connect the scale
		useJointOrient (bool): For joints, True to connect the rotation to the jointOrient instead of the rotate

	Returns:
		str: The blendMatrix node
	'''
	if "{node}" not in name:
		name += "{node}"

	bmNode = cmds.createNode("blendMatrix", name=name.format(node="BlendMatrix"))
	mmNode = cmds.createNode("multMatrix", name=name.format(node="MulMatrix"))
	dmNode = cmds.createNode("decomposeMatrix", name=name.format(node="DcpMatrix"))

	cmds.connectAttr(bmNode+".outputMatrix", mmNode+".matrixIn[0]")
	cmds.connectAttr(slave+".parentInverseMatrix[0]", mmNode+".matrixIn[1]")
	cmds.connectAttr(mmNode+".matrixSum", dmNode+".inputMatrix")

	# Input
	slaveMatrix = cmds.xform(slave, q=True, matrix=True, worldSpace=True)
	slaveMatrix = Matrix4(slaveMatrix)
	for i, master in enumerate(masters):
		if maintainOffset:
			masterMatrix = cmds.xform(master, q=True, matrix=True, worldSpace=True)
			masterMatrix = Matrix4(masterMatrix)
			offset = slaveMatrix * masterMatrix.inverse()

			offNode = cmds.createNode("multMatrix", name=name+"{i}".format(node="Offset", i=i))
			cmds.setAttr(offNode+".matrixIn[0]", offset.flattened(), type="matrix")
			cmds.connectAttr(master+".worldMatrix[0]", offNode+".matrixIn[1]")
			cmds.connectAttr(offNode+".matrixSum", bmNode+".target[{}].targetMatrix".format(i))
		else:
			cmds.connectAttr(master+".worldMatrix[0]", bmNode+".target[{}].targetMatrix".format(i))

	# Output
	if translate:
		cmds.connectAttr(dmNode+".outputTranslate", slave+".translate", force=True)
	if rotate:
		if cmds.nodeType(slave) == "joint" and useJointOrient:
			cmds.connectAttr(dmNode+".outputRotate", slave+".jointOrient", force=True)
		else:
			cmds.connectAttr(dmNode+".outputRotate", slave+".rotate", force=True)

	if scale:
		cmds.connectAttr(dmNode+".outputScale", slave+".scale", force=True)
		cmds.connectAttr(dmNode+".outputShear", slave+".shear", force=True)

	return bmNode


def fkik2Bones(name, iks, fks, bones, lenA, lenB, neg):
	'''	Create a fkik2Bones nodes compound

	Args:
		name (str): Name of the nodes
		iks (list of str): In order - root, effector, upvector
		fks (list of str): In order - fk1, 2 and 3
		lenA (float): Initial length of the first bone
		lenB (float): Initial length of the second bone
		neg (bool): Build for negative side

	Returns:
		str: The FkIk2Bones node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	fkikNode = cmds.createNode("FkIk2Bones", name=name.format(node="FKIK"))

	for ctl, attr in izip(iks, ["Root", "effector", "upVector"]):
		cmds.connectAttr(ctl+".worldMatrix[0]", fkikNode+"."+attr+"[0]")

	for ctl, attr in izip(fks, ["FkA", "FkB", "FkC"]):
		cmds.connectAttr(ctl+".worldMatrix[0]", fkikNode+"."+attr+"[0]")

	cmds.setAttr(fkikNode+".lengthA", lenA)
	cmds.setAttr(fkikNode+".lengthB", lenB)
	cmds.setAttr(fkikNode+".negate", neg)


	for bone, s in izip(bones, "ABC"):
		attributes.inheritsTransform(bone, False)
		cmds.setAttr(bone+".shearXY", 0)
		cmds.setAttr(bone+".shearXZ", 0)
		cmds.setAttr(bone+".shearYZ", 0)

		dmNode = cmds.createNode("decomposeMatrix", name=name+"{s}".format(node="FKIKDcpMat", s=s))

		cmds.connectAttr(fkikNode+".bone{}Tfm".format(s), dmNode+".inputMatrix")

		cmds.connectAttr(dmNode+".outputTranslate", bone+".translate")
		cmds.connectAttr(dmNode+".outputRotate", bone+".rotate")
		cmds.connectAttr(dmNode+".outputScale", bone+".scale")

	return fkikNode

def aimConstraint(name, slave, master, axis="xy", upMaster=None, upVector=None, maintainOffset=False):
	'''	Create a Aim Constraint nodes compound

	TODO Replace with aimMatrix

	Args:
		name (str): Name of the nodes
		slave (str): The node to constraint
		master (str): The node that will drive the constraint
		axis (str): "xy", "zx", "-xy"... First the axis to point At, then the one used for the upvector
		upMaster ():
		upVector ():
		maintainOffset (bool): True to maintain original offset


	Returns:
		str: The aimConstraint node
	'''
	# No master, we point to a vector
	if upMaster is None:
		upType = "vector"
		upVector = upVector if upVector else (0,1,0)
	# Master defined, but no axis, we point to the object position
	elif upVector is None:
		upType = "object"
	# Master and Axis defined, we point to the orientation of the object
	else:
		upType = "objectrotation"
		upVector = upVector

	skip = [s for s in "xyz" if cmds.getAttr(slave+".r"+s, lock=True)] or "none"
	cns = cmds.aimConstraint(master, slave, worldUpType=upType, maintainOffset=maintainOffset, name=name.format(node="AimCns"), skip=skip)[0]

	# UpVector
	if upVector is None:
		dmNode = cmds.createNode("decomposeMatrix", name=name.format(node="DcpMatrix"))
		cmds.connectAttr(upMaster+".worldMatrix[0]", dmNode+".inputMatrix")
		cmds.connectAttr(dmNode+".outputTranslate", cns+".worldUpVector")
	else:
		cmds.setAttr(cns+".worldUpVectorX", upVector[0])
		cmds.setAttr(cns+".worldUpVectorY", upVector[1])
		cmds.setAttr(cns+".worldUpVectorZ", upVector[2])

	if upMaster is not None:
		cmds.connectAttr(upMaster+".worldMatrix[0]", cns+".worldUpMatrix")

	# Direction Axis
	aimAttr = ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ"]
	a = axis.replace("-", "")
	out = [0]*6
	out["xyz".index(a[0])] = -1 if axis[0] == "-" else 1
	out["xyz".index(a[1])+3] = -1 if axis[-2] == "-" else 1
	for attr, value in izip(aimAttr, out):
		cmds.setAttr(cns+"."+attr, value)

	return cns

def orientConstraint(name, slave, masters, maintainOffset=False):
	'''	Create a Orient Constraint nodes compound

	We actually use a Parent constraint without the translation

	Args:
		name (str): Name of the nodes
		slave (str): The node to constraint
		masters (list of str): The node that will drive the constraint
		maintainOffset (bool): True to maintain original offset

	Returns:
		str: The parentConstraint node
	'''
	cns = cmds.parentConstraint(masters, slave, maintainOffset=maintainOffset, skipTranslate=["x", "y", "z"], name=name.format(node="OriCns"))[0]
	return cns

def twoPointsConstraint(name, slave, masterA, masterB, blend=.5, axis="x-z"):
	'''	Create a Point Constraint with two master and a SpinePointAt compound

	Args:
		name (str): Name of the nodes
		slave (str): The node to constraint
		masterA (str): The node that will drive the constraint
		masterB (str): The node that will drive the constraint
		blend (float): 0-1
		axis (str): 

	Returns:
		str: The pointConstraint node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	cns = cmds.pointConstraint(masterA, masterB, slave, weight=blend, maintainOffset=False, name=name.format(node="TwoPnt"))
	cmds.pointConstraint(masterB, slave, weight=blend, edit=True)
	cmds.pointConstraint(masterA, slave, weight=1-blend, edit=True)

	aim = aimConstraint(name+"Aim", slave, masterB, axis)
	spinePointAt(name+"PtAt", aim, masterA, masterB, blend, "-Z")

	return aim

def harmonic(name, slave, master, amplitude=1.0, decay=8.0, frequency=0.5, termination=0.0, amplitudeAxis=(1,1,1)):
	'''	Create a Harmonic compound

	Harmonic is a dynamic constraint to create secondary animation automatically

	Args:
		name (str): Name of the nodes
		slave (str): The node to constraint
		master (str): The node that will drive the constraint
		amplitude (float): 0-1
		decay (float): 
		frequency (float): 
		termination (float): 
		amplitudeAxis (triplet of float): 

	Returns:
		str: The harmonics node
	'''
	if not cmds.pluginInfo("harmonics", q=True,  loaded=True):
		cmds.loadPlugin("harmonics")

	hNode = cmds.createNode("harmonics", name=name.format(node="Harmonic"))

	cmds.connectAttr(hNode+".output", slave+".translate")
	cmds.connectAttr(master+".wm", hNode+".input")
	cmds.connectAttr(master+".pim", hNode+".parentInverse")
	cmds.connectAttr("time1.o", hNode+".timeIn")

	cmds.setAttr(hNode+".update", True)
	cmds.setAttr(hNode+".amplitude", amplitude)
	cmds.setAttr(hNode+".axisAmp0", amplitudeAxis[0])
	cmds.setAttr(hNode+".axisAmp1", amplitudeAxis[1])
	cmds.setAttr(hNode+".axisAmp2", amplitudeAxis[2])
	cmds.setAttr(hNode+".decay", decay)
	cmds.setAttr(hNode+".frequencyMult", frequency)
	cmds.setAttr(hNode+".termination", termination)

	return hNode

# ----------------------------------------------------------------------------------
# POINT AT
# ----------------------------------------------------------------------------------
def pointAtDoubleAxis(name, cns, masterA, masterB, axis="z"):
	'''	Create a pointAtDoubleAxis compound
	
	This is mean to be used for UpVector direction with a aimConstraint or similar

	Args:
		name (str): Name of the nodes
		cns (str): The constraint node to connect to
		masterA (str): The node that will drive the constraint
		masterB (str): The node that will drive the constraint
		axis (str): 

	Returns:
		str: The PointAtDoubleAxis node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	node = cmds.createNode("PointAtDoubleAxis", name=name.format(node="PtAtDouble"))
	cmds.connectAttr(masterA+".worldMatrix[0]", node+".ref")
	cmds.connectAttr(masterB+".worldMatrix[0]", node+".trk")
	cmds.setAttr(node+".axis", "zy".index(axis))

	cmds.setAttr(cns+".worldUpType", 3)
	cmds.connectAttr(node+".out", cns+".worldUpVector")

def pointAtBlendedAxis(name, cns, masterA, masterB, blend=.5, axis="Z"):
	'''	Create a pointAtBlendedAxis compound
	
	This is mean to be used for UpVector direction with a aimConstraint or similar

	Args:
		name (str): Name of the nodes
		cns (str): The constraint node to connect to
		masterA (str): The node that will drive the constraint
		masterB (str): The node that will drive the constraint
		blend (float): 0-1
		axis (str): 

	Returns:
		str: The PointAtBlendedAxis node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	node = cmds.createNode("PointAtBlendedAxis", name=name.format(node="PtAtBlended"))
	cmds.connectAttr(masterA+".worldMatrix[0]", node+".mA")
	cmds.connectAttr(masterB+".worldMatrix[0]", node+".mB")

	cmds.setAttr(node+".axis", POINTAT_AXIS.index(axis))
	cmds.setAttr(node+".blend", blend)

	cmds.setAttr(cns+".worldUpType", 3)
	cmds.connectAttr(node+".out", cns+".worldUpVector")

	return node

def spinePointAt(name, cnsNode, masterA, masterB, blend=.5, axis="-Z", solver=0):
	'''	Create a spinePointAt compound
	
	This is mean to be used for UpVector direction with a aimConstraint or similar
	This is the Maya version of the Softimage Isner Spine Point At solver

	Args:
		name (str): Name of the nodes
		cns (str): The constraint node to connect to
		masterA (str): The node that will drive the constraint
		masterB (str): The node that will drive the constraint
		blend (float): 0-1
		axis (str): 
		solver (int): 0.SpinepointAt 1.Slerp

	Returns:
		str: The SpinePointAt node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	spaNode = cmds.createNode("SpinePointAt", name=name.format(node="SpPtAt"))

	cmds.setAttr(spaNode+".blend", blend)
	cmds.setAttr(spaNode+".axis", POINTAT_AXIS.index(axis))
	# 
	cmds.setAttr(spaNode+".alg", solver)

	cmds.connectAttr(masterA+".worldMatrix[0]", spaNode+".tfmA")
	cmds.connectAttr(masterB+".worldMatrix[0]", spaNode+".tfmB")

	# Outputs
	cmds.setAttr(cnsNode+".worldUpType", 3)

	cmds.connectAttr(spaNode+".pointAt", cnsNode+".worldUpVector")

	return spaNode

# ----------------------------------------------------------------------------------
# ROTATION TRACKER
# ----------------------------------------------------------------------------------
def rotationTracker(name, attr, reference, tracker):
	'''	Create a rotationTracker compound

	Args:
		name (str): Name of the nodes
		attr (str): Output Attribute to connect to
		reference (str): The reference node that will drive the constraint
		tracker (str): The tracker node that will drive the constraint

	Returns:
		str: The RotationTracker node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	node = cmds.createNode("RotationTracker", name=name.format(node="RotTrk"))

	cmds.connectAttr(reference+".worldMatrix[0]", node+".reference")
	cmds.connectAttr(tracker+".worldMatrix[0]", node+".tracker")

	# Offset
	tMatrix = Matrix4(cmds.xform(tracker, q=True, matrix=True, worldSpace=True))
	rMatrix = Matrix4(cmds.xform(tracker, q=True, matrix=True, worldSpace=True))
	m = tMatrix * rMatrix.inverse()
	er = tMatrix.asTransform().rotation.asEuler()
	x = math.degrees(er.x)
	y = math.degrees(er.y)
	z = math.degrees(er.z)
	cmds.setAttr(node+".restX", x)
	cmds.setAttr(node+".restY", y)
	cmds.setAttr(node+".restZ", z)

	cmds.connectAttr(node+".output", attr, force=True)

	return node

def rotationToSlider(name, attr, rotMin=-90, rotMax=90, slideMin=0, slideMax=1):
	'''	Create a rotationToSlider compound

	This node convert a rotation range in a translation

	Args:
		name (str): Name of the nodes
		attr (str): Output Attribute to connect to
		rotMin (float): The minimum rotation value in degrees
		rotMax (float): The maximum rotation value in degrees
		slideMin (float): The minimum translation value
		slideMax (float): The maximum translation value

	Returns:
		str: The RotationToSlider node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	node = cmds.createNode("RotationToSlider", name=name.format(node="RotToSld"))

	cmds.connectAttr(node+".output", attr)
	cmds.setAttr(node+".rotMin", rotMin)
	cmds.setAttr(node+".rotMax", rotMax)
	cmds.setAttr(node+".sliderMin", slideMin)
	cmds.setAttr(node+".sliderMax", slideMax)

	return node

# ----------------------------------------------------------------------------------
# NURBS and MESH CONSTRAINTS
# ----------------------------------------------------------------------------------
def curvePointCenters(name, curve, center, index):
	'''	Create a curvePointCenters compound

	This node is attaching the curve point to given transforms

	Args:
		name (str): Name of the nodes
		curve (str): Curve to drive
		center (str): Transform node to drive the position
		index (int): Index of the CV to drive
	'''

	# If that fails it might be that you don't have the matrixNodes.mll plungin installed
	dmNode = cmds.createNode("decomposeMatrix", name=name+"{i}".format(node="DcpMat", i=index))

	shape = cmds.listRelatives(curve, shapes=True)[0]

	cmds.setAttr(curve+".inheritsTransform", False)

	cmds.connectAttr(center+".worldMatrix[0]", dmNode+".inputMatrix")
	cmds.connectAttr(dmNode+".outputTranslate", shape+".controlPoints[{}]".format(index))

	for t, a in product(["translate", "rotate", "scale"], "XYZ"):
		attrName = t+a
		value = 1 if t == "scale" else 0

		cmds.setAttr(curve+"."+attrName, lock=False)
		cmds.setAttr(curve+"."+attrName, value)
		cmds.setAttr(curve+"."+attrName, lock=True)

def curveConstraints(name, slave, curve, axis="xy", parametric=True, u=.5, percentageToU=False):
	'''	Create a curveConstraints compound

	Args:
		slave (str): Node to attach to the curve
		curve (str): Curve to drive the node
		axis (str): 'xy', '-xy'...
		parametric (bool): True to use parametric attachment (Faster)
		u (float): Normalized U [0.0:1.0]
		percentageToU (bool): True to convert percentage value to U (ignored if parametric is False)

	Returns:
		str: The motionPath node
	'''
	shape = cmds.listRelatives(curve, shapes=True)[0]

	mpNode = cmds.createNode("motionPath", name=name.format(node="MoPath"))
	cmds.connectAttr(shape+".worldSpace[0]", mpNode+".geometryPath")

	# Maya doesn't compute the orientation properly at 1.0
	# So we need to make it very close to 1 but not 1
	u = min(0.999, u)

	if parametric:
		if percentageToU:
			curveMFn = cast.toMFn(shape)
			length = cmds.arclen(curve)
			u = curveMFn.findParamFromLength(length*u)
		else:
			spans = cmds.getAttr(curve+".spans")
			u *= spans

	inverseFront = axis[0] == "-"
	inverseUp = axis[-2] == "-"
	axis = axis.replace("-", "")
	cmds.setAttr(mpNode+".inverseFront", inverseFront)
	cmds.setAttr(mpNode+".frontAxis", "xyz".index(axis[0].lower()))
	cmds.setAttr(mpNode+".inverseUp", inverseUp)
	cmds.setAttr(mpNode+".upAxis", "xyz".index(axis[1].lower()))
	cmds.setAttr(mpNode+".fractionMode", not parametric)
	cmds.setAttr(mpNode+".uValue", u)
	cmds.setAttr(mpNode+".follow", True)

	pmmNode = cmds.createNode("pointMatrixMult", name=name.format(node="PtMatMul"))
	cmds.connectAttr(slave+".parentInverseMatrix[0]", pmmNode+".inMatrix")
	cmds.connectAttr(mpNode+".allCoordinates", pmmNode+".inPoint")
	cmds.connectAttr(pmmNode+".output", slave+".translate")

	mmNode = cmds.createNode("multMatrix", name=name.format(node="MulMat"))
	cmds.connectAttr(mpNode+".orientMatrix", mmNode+".matrixIn[0]")
	cmds.connectAttr(slave+".parentInverseMatrix[0]", mmNode+".matrixIn[1]")

	dmNode = cmds.createNode("decomposeMatrix", name=name.format(node="DcpMat"))
	cmds.connectAttr(mmNode+".matrixSum", dmNode+".inputMatrix")
	cmds.connectAttr(dmNode+".outputRotate", slave+".rotate")

	return mpNode

def surfaceAttach(name, slave, surface, u=None, v=None):
	'''	Create a surfaceAttach compound
	
	# TODO This can't possibly work, the variable position isn't defined

	Args:
		slave (str): Node to attach to the Surface
		surface (str): Surface to drive the node
		u (float||None): U position, if None closest U is computed 
		v (float||None): V position, if None closest V is computed 

	Returns:
		str: The SurfaceMultiAttach node
	'''
	if u is None or v is None:
		u, v = self._getClosestUV(surface, position, globalSpace=True)

	return compounds.surfaceMultiAttach(name, [[slave]], surface, 0, [u], [v])

def surfaceMultiAttach(name, slaves, surface, attach=0, uParams=None, vParams=None, evenly=False):
	'''	Create a surfaceMultiAttach compound

	Args:
		slaves (list of str): Nodes to attach to the Surface 
		surface (str): Surface to drive the node
		attach (int): 0 Parametric, 1 Percentage, 2 Fixed Length
		uParams (list of double|None): None for linear distribution. double must be between 0.0 and 1.0
		vParams (list of double|None): None for linear distribution. double must be between 0.0 and 1.0

	Returns:
		str: The SurfaceMultiAttach node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	shape = cmds.listRelatives(surface, shapes=True, path=True)[0]

	vCount = len(slaves)
	uCount = len(slaves[0])

	if uParams is not None and len(uParams) != uCount:
		raise RuntimeError("Number of uParams doesn't match u count")
	if vParams is not None and len(vParams) != vCount:
		raise RuntimeError("Number of vParams doesn't match u count")

	
	# This is a custom command part of the Harbie Plugin
	length = cmds.surfaceInfo(surface, length=True)

	cmaNode = cmds.createNode("SurfaceMultiAttach", name=name.format(node="SrfMAttch"))

	cmds.connectAttr(shape+".local", cmaNode+".surface")
	cmds.connectAttr(surface+".worldMatrix[0]", cmaNode+".surfaceMatrix")
	cmds.connectAttr(slaves[0][0]+".parentInverseMatrix[0]", cmaNode+".parentInverse")
	cmds.setAttr(cmaNode+".attach", attach)
	cmds.setAttr(cmaNode+".length", length)

	# V
	if vParams is None:
		if vCount == 1:
			vParams = [0.5]
		else:
			vParams = [j/float(vCount-1) for j in range(vCount)]
	
	# U
	if uParams is None:
		uParams = []
		if uCount == 1:
			uParams = [0.5]
		else:
			isClosed = cmds.getAttr(shape+".formU") != 0 
			count = float(uCount) if isClosed else float(uCount-1)
			for i in range(uCount):
				step = i/count
				if attach==0 and evenly:
					# This is a custom command part of the Harbie Plugin
					uParams.append(cmds.surfaceInfo(surface, pfp=step))
				else:
					uParams.append(step)

			
	for j, v in enumerate(vParams):
		cmds.setAttr(cmaNode+".v[%s]"%j, v)
	for i, u in enumerate(uParams):
		cmds.setAttr(cmaNode+".u[%s]"%i, u)


	for j in range(vCount):
		for i in range(uCount):
			index = j*uCount+i
			slave = slaves[j][i]
			cmds.connectAttr(cmaNode+".output[%s].translate"%index, slave+".translate")
			cmds.connectAttr(cmaNode+".output[%s].rotate"%index, slave+".rotate")


def meshMultiAttach(name, slave, mesh, attach=0, index=-1, orient=False):
	'''	Create a meshMultiAttach compound

	Args:
		slaves (str): Node to attach to the Surface 
		mesh (str): Mesh to drive the node
		attach (int): 0 Vertex, 1 Edge, 2 Polygon
		index (int): -1 to auto detect closest index
		orient (bool): True to compute orientation from component normal/tangent (slower)

	Returns:
		str: The MeshMultiAttach node
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	shape = cmds.listRelatives(mesh, shapes=True, path=True)[0]

	if index == -1:
		pos = cmds.xform(slave, q=True, translation=True, worldSpace=True)
		index = _closestComponentIndex(shape, pos, attach)

	# We're not creating a new node if there is already one available using the correct attach method
	mmaNode = _getMeshMultiAttachNode(shape, attach)
	if mmaNode is None:
		mmaNode = cmds.createNode("MeshMultiAttach", name=name.format(node="MshMAttch"))
	attrIndex = _getNextAvailableIndex(mmaNode)

	cmds.connectAttr(shape+".outMesh", mmaNode+".mesh", force=True)
	cmds.connectAttr(mesh+".worldMatrix[0]", mmaNode+".meshMatrix", force=True)
	cmds.setAttr(mmaNode+".attach", attach)

	cmds.connectAttr(slave+".parentInverseMatrix[0]", mmaNode+".component[%s].parentInverse"%attrIndex)
	cmds.setAttr(mmaNode+".component[%s].index"%attrIndex, index)
	cmds.setAttr(mmaNode+".component[%s].orient"%attrIndex, orient)

	cmds.connectAttr(mmaNode+".output[%s].translate"%attrIndex, slave+".translate")
	if orient:
		cmds.connectAttr(mmaNode+".output[%s].rotate"%attrIndex, slave+".rotate")

# ----------------------------------------------------------------------------------
# MISC
# ----------------------------------------------------------------------------------
def _getMeshMultiAttachNode(shape, attach):
	'''	Find existing MeshMultiAttachNode if any

	Args:
		shape (str): Mesh to drive the node
		attach (int): 0 Vertex, 1 Edge, 2 Polygon

	Returns:
		str||None: The MeshMultiAttach node if any
	'''
	nodes = cmds.listConnections(shape, type="MeshMultiAttach")
	if nodes:
		for node in nodes:
			if cmds.getAttr(node+".attach") == attach:
				return node

def _getNextAvailableIndex(node):
	'''	Get the next port available to attach to

	Args:
		node (str): MeshMultiAttach Node

	Returns:
		int: MNext available port
	'''
	indices = cmds.getAttr(node+".component", mi=True)
	if indices:
		return max(indices) + 1
	else:
		return 0

def _closestComponentIndex(shape, position, componentType):
	'''	Get the closest component Index to given position

	Args:
		shape (str):
		position (triplet of float): 
		componentType (int): 0 Vertex, 1 Edge, 2 Polygon

	Return:
		int
	'''
	point = om.MPoint(*position)
	shape = cast.toMFn(shape)

	util = om.MScriptUtil()
	util.createFromInt(0)
	idPointer = util.asIntPtr()

	shape.getClosestPoint(point, om.MPoint(), om.MSpace.kObject, idPointer)
	faceId = om.MScriptUtil(idPointer).asInt()
	if componentType == 2: #Face
		return faceId

	elif componentType == 1: # Edge
		faceIter = om.MItMeshPolygon(shape.object())
		faceIter.setIndex(faceId, idPointer)
		array = om.MIntArray()
		faceIter.getEdges(array)

		edgeIter = om.MItMeshEdge(shape.object())

		length = 99999999999.999
		edgeId = None
		for i, currentEdgeId in enumerate(array):
			edgeIter.setIndex(currentEdgeId, idPointer)
			edgePoint = edgeIter.center(om.MSpace.kObject)
			currentLenght = point.distanceTo(edgePoint)
			if currentLenght < length:
				length = currentLenght
				edgeId = currentEdgeId
		return edgeId

	elif componentType == 0: # Vertex
		faceIter = om.MItMeshPolygon(shape.object())
		faceIter.setIndex(faceId, idPointer)
		array = om.MIntArray()
		faceIter.getVertices(array)
		length = 99999999999.999
		vertexId = None
		for i, currentVertexId in enumerate(array):
			vertexPoint = om.MPoint()
			shape.getPoint(currentVertexId, vertexPoint, om.MSpace.kObject)
			currentLenght = point.distanceTo(vertexPoint)
			if currentLenght < length:
				length = currentLenght
				vertexId = currentVertexId
		return vertexId

def _getClosestUV(surface, point, globalSpace=True):
	'''Returns the Closest UV values on a NurbsSurface to 'point'

	Args:
		surface (MDagPath): dagPath to the nurbsSurface shapeNode
		point (MPoint): get the closest UV to this point
		globalSpace( bool): globalSpace?
	Returns:
		list of float: float UV values
	'''
	if globalSpace:
		space = om.MSpace.kWorld
	else:
		space = om.MSpace.kObject

	point = om.MPoint(*point)

	shape = cmds.listRelatives(surface, shapes=True, path=True)[0]
	fnSurface = cast.toMFn(shape)

	utilA = om.MScriptUtil()
	utilB = om.MScriptUtil()

	closestPointU = utilA.asDoublePtr()
	closestPointV = utilB.asDoublePtr()

	fnSurface.closestPoint(point, closestPointU, closestPointV, False, 1e-4, space)

	closestPointU = utilA.getDouble(closestPointU)
	closestPointV = utilB.getDouble(closestPointV)
	return [closestPointU, closestPointV]
