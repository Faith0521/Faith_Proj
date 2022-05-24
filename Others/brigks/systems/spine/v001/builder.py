from itertools import izip

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, umath
from brigks import config

class SpineSystemBuilder(SystemBuilder):
	ctl_count = 5

	def createObjects(self):

		# SIZE
		size = self.translations("Root").distance(self.translations("Eff"))
		fkSize = size * .8
		ikSize = size *.75
		hipSize = size * 1.25

		# TRANSFORMATION
		normal = self.directions("Root", "z")
		
		positions = []
		transforms = []

		for i in range(self.ctl_count):
			lookat = self.translations("Eff") - self.translations("Root")
			t = Transformation.lookAt(self.translations("Root"), lookat, normal, self.settings("axis").lower(), self.negate())
			t.translation = self.translations("Root").lerp(self.translations("Eff"), i/(self.ctl_count-1.0))
			positions.append(t.translation)
			transforms.append(t)

		# OBJECTS
		self.root = self.addRig(None, "Root")

		# Curves
		points = [positions[i] for i in [0,2,2,4]]
		self.crvA = create.curve(self.getObjectName(config.USE_RIG, "CrvA"), points, closed=False, degree=3, parent=self.root)

		points = [positions[0].lerp(positions[-1], i/6.0) for i in xrange(7)]
		self.crvB = create.bezier(self.getObjectName(config.USE_RIG, "CrvB"), self.root, points)
		
		# Controllers
		self.fkCtl = []
		self.hookRig = []
		fk_parent = self.root
		self.ikBfr = []
		self.ikCtl = []
		self.hookRig = []
		for i, tfm in enumerate(transforms, start=1):
			
			# Fk Controllers
			fkCtl = self.addCtl(fk_parent, "Fk%s"%i, tfm, "sphere", size=fkSize, so=(1,0,1), color=self.colorFk())
			# self.setInversedsettings(fkCtl, ["posx", "rotz", "roty"])
			attributes.setRotOrder(fkCtl, "XYZ")
			
			fk_parent = fkCtl
			self.fkCtl.append(fkCtl)
			
			# Ik Controllers
			ikBfr = self.addBfr(self.root, "Ik%s"%i, tfm)
			self.ikBfr.append(ikBfr)
			

			# First ik ctl is a box
			if i in [1,5]:
				ikCtl = self.addCtl(ikBfr, "Ik%s"%i, tfm, "cube", size=hipSize, so=(1,.25,1), color=self.colorIk())
			else:
				ikCtl = self.addCtl(ikBfr, "Ik%s"%i, tfm, "sphere", size=ikSize, so=(1,0,1), color=self.colorIk())
			
			# if i in [2,4]:
			# 	self.addToSubControllers(ikCtl)

			# self.setInversedsettings(ikCtl, ["posx", "rotz", "roty"])
			attributes.setRotOrder(ikCtl, "YZX")

			self.ikCtl.append(ikCtl)

			# Hooks
			if i == 1:
				hookRig = None
			else:
				hookRig = self.addRig(self.root, "Hook%s"%i, tfm, "cube", size=2)
			self.hookRig.append(hookRig)

		# Tangent parents
		self.aTan0 = self.addRig(self.ikCtl[0], "ATan0", transforms[2], "pyramid", size=.5)
		self.aTan1 = self.addRig(self.ikCtl[-1], "ATan1", transforms[2], "pyramid", size=.5)

		self.bTan0 = self.addRig(self.ikCtl[0], "BTan0", transforms[1], "pyramid", size=.5)
		self.bTan1 = self.addRig(self.ikCtl[2], "BTan1", transforms[1], "pyramid", size=.5)
		self.bTan2 = self.addRig(self.ikCtl[2], "BTan2", transforms[2], "pyramid", size=.5)
		self.bTan3 = self.addRig(self.ikCtl[2], "BTan3", transforms[3], "pyramid", size=.5)
		self.bTan4 = self.addRig(self.ikCtl[4], "BTan4", transforms[3], "pyramid", size=.5)
		
		if self.settings("breathing"):
			breathBfr = self.addBfr(self.hookRig[4], "Breathing", transforms[-1])
			self.breathCtl = self.addCtl(breathBfr, "Breathing", transforms[-1], "lung", size=ikSize/2.0, po=(0,0,ikSize), color=self.colorIk())
			# self.addToSubControllers(self.breathCtl)
			# self.setInversedsettings(self.breathCtl, ["posx", "rotz", "roty"])
			attributes.setRotOrder(self.breathCtl, "YZX")

	def createJoints(self):
		self.addJnt(self.ikCtl[0], "1")
		self.addJnt(self.hookRig[2], "3")
		if self.settings("breathing"):
			self.addJnt(self.breathCtl, "5")
		else:
			self.addJnt(self.hookRig[4], "5")
	
	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend") == "IK", 0, 1)
		self.showCtrlAttr = self.addAnimAttr("showCtrl", "bool", False) 
		
	def createLayout(self): 
		pass
		
	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibilities
		fkCompare = self.addCompound("compare", "FkViz", self.blendAttr, 1, "<")
		ikCompare = self.addCompound("compare", "IkViz", self.blendAttr, 0, ">")
		
		cmds.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
		cmds.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

		for ctl in self.fkCtl:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		for ctl in self.ikCtl[1:]:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		# Cluster Centers
		self.addCompound("curvePointCenters", "CPCA0", self.crvA, self.ikCtl[0], 0)
		self.addCompound("curvePointCenters", "CPCA1", self.crvA, self.aTan0, 1)
		self.addCompound("curvePointCenters", "CPCA2", self.crvA, self.aTan1, 2)
		self.addCompound("curvePointCenters", "CPCA3", self.crvA, self.ikCtl[4], 3)

		self.addCompound("curvePointCenters", "CPCB0", self.crvB, self.ikCtl[0], 0)
		self.addCompound("curvePointCenters", "CPCB1", self.crvB, self.bTan0, 1)
		self.addCompound("curvePointCenters", "CPCB2", self.crvB, self.bTan1, 2)
		self.addCompound("curvePointCenters", "CPCB3", self.crvB, self.bTan2, 3)
		self.addCompound("curvePointCenters", "CPCB4", self.crvB, self.bTan3, 4)
		self.addCompound("curvePointCenters", "CPCB5", self.crvB, self.bTan4, 5)
		self.addCompound("curvePointCenters", "CPCB6", self.crvB, self.ikCtl[4], 6)

		# Hooks
		for hookRig, fkCtl, ikCtl in izip(self.hookRig, self.fkCtl, self.ikCtl):
			if hookRig is None:
				continue

			cns = self.addCompound("blendMatrix", "Hook", hookRig, [fkCtl, ikCtl])
			cmds.connectAttr(self.blendAttr, cns+".target[1].weight")
		
		# Mid Ik Controller
		axis = self.settings("axis").lower()
		axis = axis[0] + "-"+ axis[-1]
		cns = self.addCompound("curveConstraints", "Ik0", self.ikBfr[2], self.crvA, axis=axis, parametric=True, u=.5)
		self.addCompound("spinePointAt", "SPA0", cns, self.ikCtl[0], self.ikCtl[4], blend=.5, solver=1) 

		cns = self.addCompound("curveConstraints", "Ik1", self.ikBfr[1], self.crvB, axis=axis, parametric=False, u=.25)
		self.addCompound("spinePointAt", "SPA1", cns, self.ikCtl[0], self.ikCtl[2], blend=.5, solver=1) 

		cns = self.addCompound("curveConstraints", "Ik2", self.ikBfr[3], self.crvB, axis=axis, parametric=False, u=.75)
		self.addCompound("spinePointAt", "SPA2", cns, self.ikCtl[2], self.ikCtl[4], blend=.5, solver=1) 

	
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		root = self.getObject("Root")
		self.connect_parenting(root, "Root")
		
		