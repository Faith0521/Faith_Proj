
from Qt.QtCore import Qt, QObject, Signal, QEvent, QEventLoop
from Qt.QtWidgets import QApplication

import maya.OpenMaya as om 
import maya.OpenMayaUI as mui
from maya import cmds

from brigks.utils import gui, create

class PickPositions(QObject):

	pickSessionEnded = Signal(list)

	def __init__(self, min=1, max=-1, show=False, delete=True, messages=[], returnAsMatrix=False):
		self._mainWindow = gui.getMayaWindow()
		super(PickPositions, self).__init__(self._mainWindow)

		self._min, self._max = min, max
		self._clickFilter = ClickFilter(self)
		self._keyFilter = KeyFilter(self)
		x, self._viewWidgets = gui.get3dViews()
		self._fnFreePoint = mui.MFnFreePointTriadManip()
		self._fnDependNode = om.MFnDependencyNode()
		self._positions = []
		self._show = show
		self._delete = delete
		self._messages = messages or [""]
		self._messageCount = 0
		self._returnAsMatrix = returnAsMatrix
		self._guides = []
		self._manipulators = []

	# Attributes ----------------------
	def positions(self):
		if self._returnAsMatrix:
			return [self._asMatrix(p) for p in self._positions]
		else:
			return self._positions

	# Methods -------------------------
	def start(self):
		self._loop = QEventLoop()
		self.pickSessionEnded.connect(lambda:self._loop.quit())
		self._showMessage()
		self._createEventFilters()
		self._setCursor(Qt.CrossCursor)
		self._loop.exec_()

	def finish(self, completed=True):
		count = len(self._positions)
		self._removeEventFilters()
		if self._delete:
			self._removeGuides()
		self._setCursor()
		if count < self._min or (self._max > 0 and not count <= self._max) or not completed:
			self._positions = []
		self.pickSessionEnded.emit(self._positions)

	def appendPosition(self, position):
		self._positions.append(position)
		if self._show:
			self._createGuide(position)
		if self._max > 0 and len(self._positions) >= self._max:
			self.finish(completed=True)
		else:
			self._showMessage()

	# Private -------------------
	def _createEventFilters(self):
		for v in self._viewWidgets:
			v.installEventFilter(self._clickFilter)
		self._mainWindow.installEventFilter(self._keyFilter)	

	def _removeEventFilters(self):   
		for v in self._viewWidgets:
			v.removeEventFilter(self._clickFilter)
		self._mainWindow.removeEventFilter(self._keyFilter)

	def _setCursor(self, cursor=Qt.ArrowCursor):   
		for v in self._viewWidgets:
			v.setCursor(cursor)

	def _showMessage(self):
		index = self._messageCount if self._messageCount < len(self._messages) else -1
		message = "Pick {} Position (Right Click to End)".format(self._messages[index])
		cmds.inViewMessage(statusMessage=message, position="topRight", backColor=0x00000000, fade=True)
		self._messageCount += 1

	def _createGuide(self, position):  
		matrix = self._asMatrix(position)
		guide = create.transform("PickSessionGuide", parent=None, matrix=matrix)
		create.icon("sphere", parent=guide, size=3, showCenter=True)

		self._guides.append(guide)
		cmds.setAttr(guide+".overrideEnabled", True)
		cmds.setAttr(guide+".overrideColor", 28)

		# I'm not using Manipulators because it's crashing when deleting them :(
		# manip = self._fnFreePoint.create()
		# self._manipulators.append(manip)
    
		# self._fnFreePoint.setDrawAxes(False)
		# self._fnFreePoint.connectToPointPlug(self._fnDependNode.findPlug("translate"))
		# self._fnFreePoint.setPoint(om.MPoint(position)) 

	def _removeGuides(self):
		if self._guides:
			cmds.delete(self._guides)
		self._guides = []

		# for manip in self._manipulators:
		# 	try: self._fnFreePoint.deleteManipulator(manip)
		# 	except: pass
		# self._manipulators = []

	def guides(self):
		return self._guides

	def _asMatrix(self, position):
		return [1,0,0,0, 0,1,0,0, 0,0,1,0,
				position[0], position[1], position[2], 1] 


#-------------------------------------------------------------------------------
# EVENT FILTERS
#-------------------------------------------------------------------------------
class ClickFilter(QObject):

	def __init__(self, parent):
		super(ClickFilter, self).__init__()
		self.parent = parent

	def eventFilter(self, obj, event):
		eventType = event.type()
		keyMod = QApplication.keyboardModifiers()
		
		# CANCEL FOR NAVIGATION
		if keyMod == Qt.AltModifier:
			pass

		# MOUSE CLICK
		elif eventType == QEvent.MouseButtonRelease:
			if event.button() == Qt.LeftButton:
				position = gui.viewToWorld(event.pos().x(), event.pos().y())
				self.parent.appendPosition(position)
			elif event.button() == Qt.RightButton:
				self.parent.finish(completed=True)

		return super(ClickFilter, self).eventFilter(obj, event)


class KeyFilter(QObject):

	def __init__(self, parent):
		super(KeyFilter, self).__init__()
		self.parent = parent

	def eventFilter(self, obj, event):
		eventType = event.type()
		keyMod = QApplication.keyboardModifiers()

		# KEY PRESSED
		if eventType == QEvent.KeyPress:
			key = event.key()

			if key == Qt.Key_Escape:
				self.parent.finish(completed=False)

			elif key == Qt.Key_Return or key == Qt.Key_Enter:
				self.parent.finish(completed=True)

		return super(KeyFilter, self).eventFilter(obj, event)
