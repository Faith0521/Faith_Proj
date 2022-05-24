import math
from itertools import izip

from maya import cmds
from maya import OpenMaya as om
import pymel.core as pm
import pymel.core.datatypes as dt

from math3d.transformation import TransformationArray, Transformation
from math3d.vectorN import Vector3
from math3d.matrixN import Matrix4

from brigks.utils import attributes, compounds, cast, skin

ICONS = ["arrow", "bone", "circle", "compass", "cross", "crossarrow", "cube", "cubewithpeak",
	"cylinder", "diamond", "flower", "jaw", "null", "pyramid", "sphere", "spine", "square",
	 "lookat", "bendedarrow", "rotatearrow", "gear", "lung"]

def transform(name, parent=None, matrix=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
	'''	Create a Transform node

	Args:
		name (str): Name of the node
		parent (str): Parent node
		matrix (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
		icon (str): Type of nurbscurve shape 
		size (float): Size of the shape
		po (triplet of float): Position offset of the shape
		ro (triplet of float): Rotation offset of the shape
		so (triplet of float): Scale offset of the shape
		color (triplet of float): Color of the shape

	Returns:
		str
	'''
	node = cmds.createNode("transform", name=name)
	if parent:
		node = cmds.parent(node, parent)[0]

	attributes.setColor(node, color)

	# Transform
	if matrix is not None:
		attributes.setMatrix(node, matrix, worldSpace=True)

	return node

def joint(name, parent=None, matrix=None, color=None, radius=1, useJointOrient=False):
	'''	Create a Joint node

	Args:
		name (str): Name of the node
		parent (str): Parent node
		matrix (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
		color (triplet of float): Color of the shape
		radius (float): Size of the shape
		useJointOrient (bool): Use the jointOrient Attribute to set the rotation

	Returns:
		str
	'''
	jnt = cmds.createNode("joint", name=name)
	cmds.setAttr(jnt+".radius", radius)
	if parent:
		# Maya has a tendency to add an inbetween parent when parenting joint in absolute.
		m = cmds.xform(jnt, q=True, matrix=True, worldSpace=True)
		jnt = cmds.parent(jnt, parent, relative=True)[0]
		m = cmds.xform(jnt, matrix=m, worldSpace=True)

	attributes.setColor(jnt, color)

	# Transform
	if matrix is not None:
		attributes.setMatrix(jnt, matrix, worldSpace=True)
	
	if useJointOrient:
		# Because Joints are fun, you actually want the orientation  
		# to be on the JointOrientation and not the Rotation
		# It only really matters when you use a ikhandle, but better safe than sorry
		rot = cmds.getAttr(jnt+".rotate")[0]
		ori = cmds.getAttr(jnt+".jointOrient")[0]
		eRot = om.MEulerRotation(math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]), om.MEulerRotation.kXYZ)
		eOri = om.MEulerRotation(math.radians(ori[0]), math.radians(ori[1]), math.radians(ori[2]), om.MEulerRotation.kXYZ)
		qRot = eRot.asQuaternion()
		qOri = eOri.asQuaternion()
		q =  qRot * qOri
		e = q.asEulerRotation()
		e = (math.degrees(e.x), math.degrees(e.y), math.degrees(e.z))
		try:
			# The joint might be locked or connected, int that case we don't do anything.
			cmds.setAttr(jnt+".rotate", 0,0,0)
			cmds.setAttr(jnt+".jointOrient", *e)
		except:
			pass

	return jnt

def camera(name, parent=None, matrix=None, color=None, **kwargs):
	'''Creates a Transform Node with a camera shape node.

	Args:
		name (str): Name of the node
		parent (str): Parent node
		matrix (math3d.Transformation||math3d.Matrix4||list of float): The world transformation
		color (int|float triplet): color as index or rgb(0-1)
		kwargs (dictionary): extra camera attributes
			centerOfInterest
			focalLength
			lensSqueezeRatio
			cameraScale
			horizontalFilmAperture
			horizontalFilmOffset
			verticalFilmAperture
			verticalFilmOffset
			filmFit
			overscan
			motionBlur
			shutterAngle
			nearClipPlane
			farClipPlane
			orthographic
			orthographicWidth
			panZoomEnabled
			horizontalPan
			verticalPan
			zoom

	Returns:
		str
	'''
	options=dict(
		centerOfInterest=5.0, 
		focalLength=35.0, 
		lensSqueezeRatio=1.0, 
		cameraScale=1.0, 
		horizontalFilmAperture=1.41732, 
		horizontalFilmOffset=0.0, 
		verticalFilmAperture=0.94488, 
		verticalFilmOffset=0.0, 
		filmFit="Fill", 
		overscan=1.0, 
		motionBlur=False, 
		shutterAngle=144.0, 
		nearClipPlane=0.1, 
		farClipPlane=10000.0, 
		orthographic=False, 
		orthographicWidth=30.0, 
		panZoomEnabled=False, 
		horizontalPan=0.0, 
		verticalPan=0.0, 
		zoom=1.0
		)
	options.update(kwargs)

	camera = cmds.camera(name=name, **options)[0]
	# For some reason the name is not set properly with the command
	camera = cmds.rename(camera, name)

	if parent:
		camera = cmds.parent(camera, parent)[0]
		
	# Setting the global/world Transformation 
	if matrix is not None:
		attributes.setMatrix(camera, matrix, worldSpace=True)

	attributes.setColor(camera, color)

	return camera

def icon(icon, parent=None, size=1, po=None, ro=None, so=None, showCenter=False, showOrientation=False, centerScale=1.0):
	'''Add a Nurbscurve shape to the given node

	Args:
		icon (str): Type of nurbscurve shape 
		parent (str): Parent node
		size (float): Size of the shape
		po (triplet of float): Position offset of the shape
		ro (triplet of float): Rotation offset of the shape
		so (triplet of float): Scale offset of the shape
		showCenter (float): Show the center helper
		showOrientation (float): Show the orientation helper
		centerScale (float): Size of the center shape

	Returns:
		str
	'''
	if not cmds.pluginInfo("harbieLocator.mll", q=True, loaded=True): 
		cmds.loadPlugin("harbieLocator.mll")

	shape = cmds.createNode("nurbsCurve", name=parent+"Shape", parent=parent, skipSelect=True)
	mhc = cmds.createNode("makeHarbieCurve", name=parent+"MHC", skipSelect=True)
	cmds.connectAttr (mhc+".outputCurve", shape+".create")

	# Icon
	cmds.setAttr(mhc+".display", ICONS.index(icon.lower()))
	cmds.setAttr(mhc+".size", size)

	# Icon Offset Transform
	if po:
		for value, s in zip(po, "XYZ"):
			cmds.setAttr(mhc+".localPosition%s"%s, value)
	if ro:
		for value, s in zip(ro, "XYZ"):
			cmds.setAttr(mhc+".localRotate%s"%s, value)
	if so:
		for value, s in zip(so, "XYZ"):
			cmds.setAttr(mhc+".localScale%s"%s, value)

	cmds.setAttr(mhc+".ShowCenter", showCenter)
	cmds.setAttr(mhc+".ShowOrientation", showOrientation)
	cmds.setAttr(mhc+".CenterScale", centerScale)

	return shape

def text(name="curve", parent=None, matrix=None, text="Text", font="Arial", size=40, align="left", bold=False, italic=False, color=None):
	'''	Creates a Transform node with a Text NurbsCurve Shape.

	Args:
		name (str): Name of the newly created Node
		parent (MObject): parent of the node. None if no parent
		transform (MTransformationMatrix or MVector): Transform or position of the node
		text (str): Text to display. 
		font (str): Font to be used. Default is Arial
		size (int): size off the text. Default is 40 which is close to 1 maya unit high.
		align (left|center|right): Alignment of the Text.
		bold (bool): Make text bold
		italic (bool): Make text italic.
		color (list of float): Color of the curve.

	Returns:
		str
	'''
	wt = "wt:75" if bold else "wt:50"
	sl = "sl:i" if italic else "sl:n"
	sz = "sz:%s"%size 

	font = "|".join([font, wt, sz, sl, "st:100"])

	text = cmds.textCurves(name=name, font=font, text=text)[0]

	# Make the shape relatives to the first node pivot
	cmds.makeIdentity(text, apply=True, t=True, r=True, s=True)

	# Set the name properly
	text = cmds.rename(text, name)

	# Parent all subshapes to the first node
	for node in cmds.listRelatives(text, allDescendents=True):
		for shp in cmds.listRelatives(node, shapes=True) or []:
			cmds.parent(shp, text, shape=True, addObject=True)

	cmds.delete(cmds.listRelatives(text, allDescendents=True, type="transform"))

	if align in ["center", "right"]:
		bb = [0,0,0]
		for shp in cmds.listRelatives(text, shapes=True):
			shp = cast.toMFn(shp)
			sbb = shp.boundingBox()
			sctr = sbb.center()

			sbb = [sbb.width()*.5+sctr.x, sbb.height()*.5+sctr.y, sbb.depth()*.5+sctr.z]
			bb = [max(o, v) for o, v in izip(bb, sbb)]

		if align == "center":
			cmds.setAttr(text+".translateX", -bb[0]*.5)
		else:
			cmds.setAttr(text+".translateX", -bb[0])

		cmds.makeIdentity(text, apply=True, t=True, r=True, s=True)
		cmds.makeIdentity(text, apply=False, t=True, r=True, s=True)

	if parent:
		text = cmds.parent(text, parent)[0]

	# Transform
	if matrix is not None:
		attributes.setMatrix(text, matrix, worldSpace=True)

	return text


# ----------------------------------------------------------------------------------
#  CHAIN
# ----------------------------------------------------------------------------------
def chain(name, parent, positions, normal=None, axis="xz", negate=False, size=1, color=None):
	'''	Creates an Ik chain of joints

	Args:
		name (str): Name of the newly created Node
		parent (str): parent of the node. None if no parent
		positions (list of triplet): position of the node
		normal (triplet of float):
		axis (str):
		size (int): size off the text. Default is 40 which is close to 1 maya unit high.
		color (list of float): Color of the curve.

	Returns:
		(str, str, str): joints, effector, handle
	'''
	if normal is None:
		if len(positions) >= 3:
			normal = Vector3.planeNormal(positions, normalize=True)
		else:
			normal = Vector(0,0,-1)

	# Transform.setMirrorMethod(Transform.inversedRotation)
	transforms = TransformationArray.chain(positions, normal, axis, negate, endTransform=True)
	d = [(positions[i],positions[i+1]) for i in range(len(positions)-1)]
	lengths = [Vector3.distance(a,b) for a,b in d] + [1]

	joints = []
	jointParent = parent
	for i, tfm in enumerate(transforms, start=1):
		jnt = joint(name+"%02d"%i, jointParent, tfm, color, useJointOrient=True)

		jointParent = jnt
		joints.append(jnt)

	handle, effector = cmds.ikHandle(startJoint=joints[0], endEffector=joints[-1])

	if negate:
		upv = Vector3([0,-1,0]) * transforms[0].asMatrix()
		tfm = Transformation.fromParts(translation=transforms[0].translation)
		upv = upv * tfm.asMatrix().inverse()

		cmds.setAttr(handle+".poleVectorX", upv.x)
		cmds.setAttr(handle+".poleVectorY", upv.y)
		cmds.setAttr(handle+".poleVectorZ", upv.z)

	effector = cmds.rename(effector, name+"Eff")
	handle = cmds.rename(handle, name+"Hdl")
	if parent:
		handle = cmds.parent(handle, parent, absolute=True)[0]

	cmds.delete(joints.pop(-1))

	return joints, effector, handle

# ----------------------------------------------------------------------------------
#  NURBS
# ----------------------------------------------------------------------------------
def curve(name, points, closed=False, degree=3, parent=None, color=None):
	'''Creates a Transform node with a NurbsCurve Shape. 

	This method uses pymel for convenience.
	I wasn't able to make it work using OM. 
	The commented code below works for kOpen, kClosed but not kPeriodic
	The issue is related to the knots. 

	knot count muyst be #CVs + degree - 1

	Args:
		name (str): Name of the newly created Node
		points (list of float3): Control points positions
		closed (bool): Close the curve
		degree (1 or 3): degree of the curve
		parent (str): parent of the node. None if no parent. Automatically casted when possible. 
		color (int|list of float): color as index or rbg

	Returns:
		str
	'''
	if len(points) < 2:
		raise ValueError("You need at least 2 points")
	elif len(points) == 2:
		degree = 1
	elif len(points) == 3 and degree == 3:
		points.append(points[-1])

	if degree not in [1,3]:
		raise ValueError("Give degree must be 1 or 3")

	# Process
	if bool(closed):
		points.extend(points[:degree])
		knots = range(len(points)+degree-1)
		points = [dt.Vector(p) for p in points]
		# As much as I want to avoid pyMel, this is easier here
		pmNode = pm.curve(n=name, d=degree, p=points, per=True, k=knots)
		curve = str(pmNode)
	else:
		points = [(p[0],p[1],p[2]) for p in points]
		curve = cmds.curve(n=name, d=degree, p=points)

	if color:
		attributes.setColor(curve, color)
	
	if parent:
		curve = cmds.parent(curve, parent)[0]

	return curve

def bezier(name, parent=None, points=None, matrix=None, color=None):
	'''Creates a Transform node with a NurbsCurve Bezier Shape. 

	Args:
		name (str): Name of the newly created Node
		parent (str): parent of the node. None if no parent. Automatically casted when possible. 
		matrix (): Transform or position of the node
		points (list of MVector): Control points positions
		color (int|list of float): color as index or rbg

	Returns:
		str
	'''
	if len(points) < 4:
		raise ValueError("Need at least 4 points")

	pointCount = (len(points)+2)/3
	knots = []
	for i in xrange(pointCount):
		knots += [i,i,i]


	crv = cmds.curve(name=name, bezier=True, degree=3, point=points, knot=knots)

	if color:
		attributes.setColor(crv, color)
	
	if parent:
		crv = cmds.parent(crv, parent)[0]

	if matrix:
		if isinstance(matrix, Transformation):
			matrix = matrix.asMatrix().flattened()
		elif isinstance(matrix, Matrix4):
			matrix = matrix.flattened()

		cmds.xform(crv, matrix=matrix, worldSpace=True)

	return crv

def cnsCurve(name="curve", centers=[], closed=False, degree=3, color=None):
	'''Creates a Transform node with a NurbsCurve Shape with each point constrained to a given center. 

	Args:
		name (str): Name of the newly created Node
		centers (list of str): 
		closed (bool): Close the curve
		degree (1 or 3): degree of the curve
		color (int|list of float): color as index or rbg

	Returns:
		str
	'''
	if len(centers) < 2:
		raise ValueError("You need at least 2 centers")
	elif len(centers) == 2:
		degree = 1
	elif len(centers) == 3 and degree == 3:
		centers.append(centers[-1])

	if degree not in [1,3]:
		raise ValueError("Give degree must be 1 or 3")

	points = [cmds.xform(center, q=1, worldSpace=True, translation=True) for center in centers]
	crv = curve(name, points, closed, degree, centers[0], color)

	for i, center in enumerate(centers):
		compounds.curvePointCenters(name, crv, center, i)

	return crv

def cnsSurface(name="cnsSurface", parent=None, centers=[], closed=False, degree=3, width=1.0, 
																axis="z", tangent=.5, color=None):
	'''Creates a Transform node with a NurbsSurface Shape with each point constrained to a given center. 

	Args:
		name (str): Name of the newly created Node
		centers (list of path): Automatically casted when possible.
		closed (bool): Close the curve
		degree (1 or 3): degree of the curve
		width (float): Width of the surface
		axis (x, y or z): axis to align the surface to
		tangent (None or float 0-1): if not None, length of the tangents in 0-1 blend between first and next point
		color (int|list of float): color as index or rbg

	Returns:
		str
	'''

	if axis == "x":
		p = Vector3([width*.5, 0, 0])
		n = Vector3([-width*.5, 0, 0])
	elif axis == "y":
		p = Vector3([0, width*.5, 0])
		n = Vector3([0, -width*.5, 0])
	else:
		p = Vector3([0, 0, width*.5])
		n = Vector3([0, 0, -width*.5])
	
	ps = []
	ns = []
	for center in centers:
		matrix = cmds.xform(center, q=True, matrix=True, worldSpace=True)
		tfm = Matrix4(matrix).asTransform()

		p2 = p * tfm.rotation
		p2 += tfm.translation
		n2 = n * tfm.rotation
		n2 += tfm.translation

		ps.append(p2)
		ns.append(n2)
		
	if tangent is not None and tangent > 0:
		ps.insert(1, ps[0].lerp(ps[1], tangent))
		ps.insert(-1, ps[-2].lerp(ps[-1], 1-tangent))

		ns.insert(1, ns[0].lerp(ns[1], tangent))
		ns.insert(-1, ns[-2].lerp(ns[-1], 1-tangent))

	pcrv = curve("DELETEME_pos_crv", points=ps, closed=closed, degree=degree)
	ncrv = curve("DELETEME_neg_crv", points=ns, closed=closed, degree=degree)

	surface = cmds.loft(pcrv, ncrv, constructionHistory=False, degree=degree, name=name, 
				reverseSurfaceNormals=True, polygon=0, range=False, uniform=True)[0] 

	cmds.delete(pcrv, ncrv)
	if parent:
		surface = cmds.parent(surface, parent)[0]

	# cmds is not create to bind to transform, so we bind to temp joints
	tmpJnts = []
	for center in centers:	
		matrix = cmds.xform(center, q=True, matrix=True, worldSpace=True)
		tmpJnt = joint(center+"_TEMPJNT", center, matrix)
		tmpJnts.append(tmpJnt)
	skinCluster = cmds.skinCluster(tmpJnts, surface, maximumInfluences=1, toSelectedBones=True, bindMethod=0)[0]
	for center, tmpJnt in izip(centers, tmpJnts):
		attributes.create(center, "lockInfluenceWeights", 'bool', value=False)
		cnx = cmds.listConnections(tmpJnt, type="skinCluster", plugs=True, connections=True)
		cnx = [(cnx[i*2].split(".")[-1], cnx[i*2+1].split(".")[-1]) for i in range(len(cnx)/2)]
		for src, dst in cnx:
			cmds.connectAttr(center+"."+src, skinCluster+"."+dst, force=True)
	cmds.delete(tmpJnts)

	return surface

