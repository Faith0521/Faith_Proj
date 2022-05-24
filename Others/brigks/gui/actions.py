
from Qt.QtWidgets import QMessageBox

from maya import cmds

from brigks import Guide
from brigks.systems import getSystemGuideClass
from brigks.utils import gui
from brigks.gui.newSystemDialog import NewSystemDialog

def findGuides():
	guides = []
	for guideAttr in cmds.ls("*.guide", long=True):
		guide, attr = guideAttr.split(".")
		guides.append(Guide(model=guide))
	return guides

def addLayer(parent):
	layer = parent.addLayer("NewLayer")
	guide = parent if isinstance(parent, Guide) else parent.guide()
	guide.commit()
	return layer

def addSystem(layer, parent=None):
	guide = layer.guide()
	if parent is None:
		parent = gui.getMayaWindow()
	dialog = NewSystemDialog(parent, guide, layer)
	if not dialog.exec_():
		return

	systemType = dialog.systemType()
	layer = dialog.layer()

	matrices = {}
	if dialog.pickPositions():
		SystemClass = getSystemGuideClass(systemType)
		if SystemClass.markerPicked:
			matrices = SystemClass.pickMarkerPositions()
			if not matrices:
				return

	system = layer.addSystem(systemType, "M", "NewSystem", matrices, version=None)
	guide.commit()
	return system
		
def toggleVisibility(systemGuides, gde=False, rig=False, jnt=False, ctl=False):
	visible = not systemGuides[0].isVisible(gde, rig, jnt, ctl)
	for systemGuide in systemGuides:
		systemGuide.setVisible(visible, gde, rig, jnt, ctl)

def duplicate(guide, systemGuides):
	dups = []
	for systemGuide in systemGuides:
		dups.append(systemGuide.duplicate(mirror=False))
	guide.commit()
	toScene(dups)
	return dups

def mirror(guide, systemGuides):
	for systemGuide in systemGuides:
		systemGuide.mirror(duplicate=True)
	guide.commit()

def mirrorL2R(guide, systemGuides):
	systems = [s for s in systemGuides if s.settings("location") == "L"]
	for system in systems:
		system.mirror()
	guide.commit()

def delete(guide, layers, systemGuides, parent=None):
	if parent is None:
		parent = gui.getMayaWindow()
	msgBox = QMessageBox(QMessageBox.Question, "Delete", "Are you sure you want to delte those systems?", QMessageBox.Cancel, parent)
	rigBTN = msgBox.addButton("Delete Rig", QMessageBox.ActionRole)
	GuideBTN = msgBox.addButton("Delete Rig and Guide", QMessageBox.ActionRole)
	rtn = msgBox.exec_()
	if rtn == QMessageBox.Cancel:
		return

	for systemGuide in systemGuides:
		systemGuide.delete(deleteGuide=(rtn==1))
	for layer in layers:
		layer.delete(deleteGuide=(rtn==1))

	guide.commit()

def toScene(systemGuides):
	objects = []
	for system in systemGuides:
		objects += system.getObjects(gde=True, rig=False, jnt=False, ctl=False)
	cmds.select(objects)

def fromScene():
	print "fromScene"
