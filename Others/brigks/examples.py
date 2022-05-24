import os.path
from datetime import datetime as dt
import logging

from guide import Guide
from brigks.gui import showWindow

from math3d.transformation import Transformation
from math3d.vectorN import Vector3


def exampleA(mirror=False, showWindow=False):
	'''Built a basic and a chain system. Set the basic to be dynamic and connect the chain to it.
	
	Args:
		mirror (bool): True to duplicate the systems on the right side
		showWindow (bool): True to popup Brigks Main Window
	'''
	# Building Matrix for guide positions
	basicMatrices = dict(
		Part1=Transformation.fromParts(translation=Vector3([2,2,0])),
		Part2=Transformation.fromParts(translation=Vector3([4,2,0])),
		)
	chainMatrices = dict(
		Part1=Transformation.fromParts(translation=Vector3([2,3,0])),
		Part2=Transformation.fromParts(translation=Vector3([4,4,0])),
		Part3=Transformation.fromParts(translation=Vector3([6,3,0])),
		)

	# Create Guide, add a layer and a couple Systems
	guide = Guide()
	guide.setSettings(hideRig=False)
	guide.setSettings(hideJoints=False)

	layer = guide.addLayer("MyFirstLayer")
	basic = layer.addSystem("basic", "L", "Basic", basicMatrices)
	chain = layer.addSystem("chain", "L", "Chain", chainMatrices)

	# System Settings
	basic.setSettings(dynamic=True, dynamicAnimatable=True, strap=True)

	# Connections
	chain.addConnection("Root", "slotParent", 
			key=basic.key(),
			slot="Part1")

	if mirror:
		for system in layer.systems().values():
			system.duplicate(mirror=True)

	# Save edit
	guide.commit()

	# Build all rig
	guide.build()

	if showWindow:
		showWindow()

	return guide



def exampleB(template="harbie_biped", build=True):
	start = dt.now()
	path = os.path.join(os.path.dirname(__file__), "templates", template+".xml")
	guide = Guide.fromXml(path)
	print "Create Rig from Template", dt.now() - start
	
	if build:
		start = dt.now()
		guide.build()
		print "Build Rig", dt.now() - start

	return guide