from itertools import izip

from maya import cmds

from math3d.transformation import Transformation

from brigks.utils import attributes
from brigks.systems.systemBuilder import SystemBuilder
from brigks import config

class SliderSystemBuilder(SystemBuilder):

	def createObjects(self):
		# TRANSFORMATION
		rootTfm = self.transforms("Rail")
		posTfm = [tfm.copy(translation=pos) for tfm, pos in izip(rootTfm, self.translations("Pos"))]
		negTfm = [tfm.copy(translation=pos) for tfm, pos in izip(rootTfm, self.translations("Neg"))]
		
		# CONTROLLERS
		self._lmts = []
		self._slds = []
		self._ctls = []
		
		for i, (rtfm, ptfm, ntfm) in enumerate(izip(rootTfm, posTfm, negTfm), start=1):
			irtfm = rtfm.asMatrix().inverse()
			irtfm = irtfm.asTransform()
			p = ptfm * irtfm
			limit_max = p.translation.x
			p = ntfm * irtfm
			limit_min = p.translation.x
			
			length = limit_max - limit_min
			offset = length *.5 + limit_min
			
			self._lmts.append([limit_min, limit_max])

			rail = self.addRig(None, "Rail{}".format(i), rtfm, "cube", size=1, 
				po=(offset,0,0), so=(abs(length), .5, .5))
						
			slider = self.addRig(rail, "Slider{}".format(i), rtfm, "cube")	

			if self.settings("addControllers"):
				ctl = self.addCtl(slider, "Slider{}".format(i), rtfm, "cube", color=self.colorIk())
				self._ctls.append(ctl)

			attributes.setKeyables(slider)
			self._slds.append(slider)

	def createJoints(self):
		parents = self._ctls if self.settings("addControllers") else self._slds
		for i, slider in enumerate(parents, start=1):
			self.addJnt(slider, str(i))

	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.outrotAttr = self.addSetupAttr("OutRot", "float3", (0,0,0))

	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		rots = [(self.settings("minRot{}".format(i)), self.settings("maxRot{}".format(i))) for i in xrange(1, self.count("Rail")+1)]
		axis = ["XYZ".index(self.settings("axis{}".format(i))) for i in xrange(1, self.count("Rail")+1)]
		for slider, limits, rot, a in izip(self._slds, self._lmts, rots, axis):
			
			# TODO, Change the RotationToSlider Cpp Node to tak a float3angle as input and an enum to pick which axis is used.
			# That would match the output from RotationTracker and would be much easier to connect
			# After the compound creation you would just do 
			# cmds.setAttr(rotSld+".axis", 2)
			# Then in the connection part you would connect directly the RotationTracker output to rotationToSlider Input
			# cmds.connectAttr(cnx+".output", rotSld+".input")
			# Then you don't need the Setup Attr

			rotSld = self.addCompound("rotationToSlider", "Slider{}".format(i), slider+".tx", rotMin=rot[0], rotMax=rot[1], 
										slideMin=limits[0], slideMax=limits[1])

			cmds.connectAttr(self.outrotAttr+str(a), rotSld+".angle")

	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		for port, cnx in self.connections().iteritems():
			if port == "Tracker":
				cnx.connect(self.outrotAttr)
			else:
				child = self.getObject(config.USE_RIG, port)
				cnx.connect(child)