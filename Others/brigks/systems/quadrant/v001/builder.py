from maya import cmds

from math3d.transformation import Transformation
from math3d.vectorN import Vector3

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import create, attributes
from brigks import config

class QuadrantSystemBuilder(SystemBuilder):

	_connections = []

	def preDeleteObjects(self):
		# Store controllers output connections
		searchString = self.getObjectName(config.USE_CTL, "*")
		controllers = cmds.ls(searchString, type="transform", long=True)
		controllers = [c for c in controllers if c.startswith("|"+self.setup())]
		exclude = ["message", "instObjGroups", "xxxxxxxxxxxx"]
		for ctl in controllers:
			x = cmds.listConnections(ctl, connections=True, plugs=True)
			xit = iter(x)
			for source, destination in zip(xit,xit):
				if [True for x in exclude if source.endswith(x)] or cmds.addAttr(source, query=True, proxy=True):
					continue
				if destination == "Ctrl_X_NULL_Part1.Scaling":
					continue
						
				cmds.disconnectAttr(source, destination)
				self._connections.append((source, destination))

			self._connections += [(s,d) for s,d in zip(xit,xit) if not [s for x in exclude if s.endswith(x)]]

	def createObjects(self):
		north = self.settings("north")
		south = self.settings("south")
		east = self.settings("east")
		west = self.settings("west")

		# TRANSFORMATION
		tfm = Transformation.lookAt(self.translations("Root"), self.directions("Root", "y"), self.directions("Root", "z"), 
									 axis="y"+self.sign()+"z", negativeSide=False)
		tfm.scale *= .5
		if north != south and False in [east,west] or east != west and False in [north,south]:
			tfm.scale *= 2

		# Label
		if not north and not south:
			dirn = .20
			dirs = -.20
		else:
			dirn = int(north)
			dirs = -int(south)
		if not east and not west:
			dire = .20
			dirw = -.20
		else:
			dire = int(east)
			dirw = -int(west)

		if self.settings("labelPosition") == "North":
			labelTfm = Transformation.fromParts(translation=Vector3([(dire+dirw)*.5,dirn+.1,0]))
			align = "center"
		elif self.settings("labelPosition") == "South":
			labelTfm = Transformation.fromParts(translation=Vector3([(dire+dirw)*.5,dirs-.5,0]))
			align = "center"
		elif self.settings("labelPosition") == "East":
			labelTfm = Transformation.fromParts(translation=Vector3([dire+.1,-.15,0]))
			align = "left"
		elif self.settings("labelPosition") == "West":
			labelTfm = Transformation.fromParts(translation=Vector3([dirw-.1,-.15,0]))
			align = "right"

		labelTfm *= tfm

		# CREATE OBJECTS
		# Frame
		scly = 1 * (north + south) if (north or south) else 0
		sclx = 1 * (east + west) if (east or west) else 0
		offy = .5 * (north - south)
		offx = .5 * (east - west)
		frame = self.addRig(None, "Frame", tfm, "cube", size=1, po=(offx,offy,0), so=(sclx,scly,0))

		# Controller
		self.ctl = self.addCtl(frame, "1", tfm, "cube", size=1, so=(.5,.5,0), color=self.colorFk())
		attributes.setKeyables(self.ctl, ["posx", "posy"])  # Faceware doesn't like if the posx is not keyable, so we make it keyable all the time...

		# Label
		labelText = self.settings("label") if (self.settings("customLabel") and self.settings("label") != "") else self.settings("name")
		label = create.text(self.getObjectName(config.USE_RIG, "Label"), frame, labelTfm, labelText, size=.2, align=align)


		# RECONNECT 
		for source, destination in self._connections:
			cmds.connectAttr(source, destination)

	#------------------------------------------------------------------
	def createOperators(self):
		# Set controller limits
		attributes.setLimits(self.ctl, ["TransX"], 
			minimum=-int(self.settings("west"))*self.settings("push"), 
			maximum=int(self.settings("east"))*self.settings("push"))

		attributes.setLimits(self.ctl, ["TransY"], 
			minimum=-int(self.settings("south"))*self.settings("push"), 
			maximum=int(self.settings("north"))*self.settings("push"))

	#------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Root" in self.connections():
			root = self.getObject(config.USE_RIG, "Frame")
			self.connections("Root").connect(root)
