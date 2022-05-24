from maya import cmds

from math3d.transformation import Transformation

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import create
from brigks import config

class CameraSystemBuilder(SystemBuilder):


	def createObjects(self):
		# TRANSFORMATION
		tfm = Transformation.lookAt(self.translations("Root"), self.directions("Root", "y"), self.directions("Root", "z"), "y"+self.sign()+"z", False)
		
		# GET SETTINGS
		camera = self.markers("Root").name()
		shape = cmds.listRelatives(camera, shapes=True)[0]
		options = {}
		for attr in ["focalLength", 
				"cameraScale", 
				"nearClipPlane", 
				"farClipPlane", 
				"horizontalFilmAperture", 
				"verticalFilmAperture", 
				"lensSqueezeRatio", 
				"filmFit", 
				"filmFitOffset", 
				"horizontalFilmOffset", 
				"verticalFilmOffset"]:
			options[attr] = cmds.getAttr(shape+"."+attr)

		# OBJECTS
		bfr = self.addBfr(None, "Camera", tfm) 
		camera = self.addCamera(bfr, "Camera", tfm=tfm, **options)


	def createConnections(self):
		if "Root" in self.connections():
			root = self.getObject(config.USE_BFR, "Camera")
			self.connections("Root").connect(root)
