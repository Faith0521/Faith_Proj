
import shiboken2
import os.path
import math

from Qt.QtWidgets import QWidget, QFileDialog, QMainWindow

import maya.OpenMayaUI as mui
import maya.OpenMaya as om
from maya import cmds

def getMayaWindow():
	'''Returns the Maya main Window for UI parenting 

	Returns:
		QWidget
	'''
	ptr = mui.MQtUtil.mainWindow()
	return shiboken2.wrapInstance(long(ptr), QMainWindow)

def get3dViews():
	views = []
	widgets = []
	viewCount = mui.M3dView.numberOf3dViews()
	
	for v in xrange(viewCount):
		view, widget = wrapViewWidget(v)
		views.append(view)
		widgets.append(widget)

	return views, widgets

def wrapViewWidget(viewIndex):
	view = mui.M3dView()
	mui.M3dView.get3dView(viewIndex, view)
	widget = shiboken2.wrapInstance(long(view.widget()), QWidget)

	return view, widget

def viewToWorld(x, y, view=None):
	'''Convert the 2D location on the viewport to a 3D position

	Args:
		x (int): X Position
		y (int): Y Position
		view ():

	Returns:
		triplet of float: 3D Space position
	'''
	view = mui.M3dView.active3dView() if view is None else view
	height = view.portHeight()
	y = height - y

	# Picked Position
	position = om.MPoint()
	direction = om.MVector()
	view.viewToWorld(x, y, position, direction)

	# Get Camera
	camDag = om.MDagPath()
	view.getCamera(camDag)
	fnCam = om.MFnCamera(camDag)
	fnDagNode = om.MFnDagNode(camDag)

	# Get Camera and Interest Position
	camTfm = fnDagNode.parent(0)
	fn = om.MFnTransform(om.MDagPath.getAPathTo(camTfm))
	cameraPosition = om.MPoint(fn.getTranslation(om.MSpace.kWorld))
	interestPosition = fnCam.centerOfInterestPoint(om.MSpace.kWorld)

	if fnCam.isOrtho():
		origin = position
		distance = (cameraPosition - interestPosition).length()
	else:
		origin = cameraPosition
		interestDirection = (interestPosition - cameraPosition)
		direction = position - cameraPosition
		ab = interestDirection.angle(direction)
		distance = interestDirection.length() / math.cos(ab)
		
		direction.normalize()

	position = origin + (direction * distance)

	return (position.x, position.y, position.z)

def addScriptWidget(tempWindowName):
	'''Create a native Maya Script Widget

	Args:
		tempWindowName (str): 

	Returns:
		QWidget
	'''
	if not cmds.window(tempWindowName, q=True, ex=True):
	    cmds.window(tempWindowName)
	    cmds.formLayout("qtLayoutObjects")

	ptr = mui.MQtUtil.mainWindow()
	mayaWindow = shiboken2.wrapInstance(long(ptr), QWidget)
	for ind, el in enumerate(mayaWindow.children()):
	    try:
	        title = el.windowTitle()
	        if title == tempWindowName:
	            break
	    except:
	        continue

	cmds.setParent(tempWindowName+"|qtLayoutObjects")
	cmdsScriptEditor = cmds.cmdScrollFieldExecuter(sourceType="python", tabsForIndent=False, showTooltipHelp=False)#, modificationChangedCommand=self.codeModified)
	widget = el.children()[-1]
	widget.show()

	return widget


def fileDialog(parent, title, initPath, filters, save=True):
	'''Create a file dialog 

	Args:
		parent (QWidget): Parent Widget
		title (str): Dialog title
		initPath (str): Initial Path
		filters (list of str): List of valid extension ie:["ma", "mb"]
		save (bool): Open dialog in save mode

	Returns:
		str
	'''
	filters = ";;".join(["%s (*.%s)"%(filter,filter) for filter in filters] + ["All files (*.*)"])
	fileDialog = QFileDialog(parent, title, initPath, filters)
	
	if save:
		fileDialog.setAcceptMode(QFileDialog.AcceptSave)
	else:
		fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
		
	fileDialog.exec_()
	if not fileDialog.result():
		return 
	
	path = str(fileDialog.selectedFiles()[0])
	if not save and not os.path.exists(path):
		return
		
	return path