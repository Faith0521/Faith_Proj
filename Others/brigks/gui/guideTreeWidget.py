
from Qt import QtCompat
from Qt.QtWidgets import QTreeWidget, QHeaderView, QShortcut
from Qt.QtGui import QKeySequence
from Qt.QtCore import Qt, QPoint

from brigks.gui.guideTreeWidgetItems import GuideTreeWidgetItem, LayerTreeWidgetItem, SystemTreeWidgetItem, SubSystemTreeWidgetItem
from brigks.gui.guideActionsMenu import GuideActionsMenu
from brigks.systems import getSystemGuideClass

from brigks.gui import actions

class GuideTreeWidget(QTreeWidget):

	def __init__(self, guide=None):
		super(GuideTreeWidget, self).__init__()

		self.setColumnCount(2)
		self.setIndentation(10)
		self.setSelectionMode(self.ExtendedSelection)
		self.setDragDropMode(self.NoDragDrop)
		self.setHeaderHidden(True)

		header = self.header()
		header.setStretchLastSection(False)
		header.setMinimumSectionSize(60)
		QtCompat.QHeaderView.setSectionResizeMode(header, 0, QHeaderView.Stretch)
		QtCompat.QHeaderView.setSectionResizeMode(header, 1, QHeaderView.ResizeToContents)

		self.itemExpanded.connect(self.saveExpandedItem)
		self.itemCollapsed.connect(self.saveExpandedItem)

		self._guide = None
		self._menu = self.createRightClickMenu()

		if guide:
			self.setGuide(guide)

	def setGuide(self, guide, selection=[]):
		self.clear()
		self._guide = guide
		if guide is None:
			return

		item = GuideTreeWidgetItem(self, guide)
		item.setExpanded(True)

		if selection:
			self.selectObjectsItems(item, selection)


	def selectObjectsItems(self, item, selection):
		isInSelection = item.object() in selection
		item.setSelected(isInSelection)
		if isInSelection:
			item.parent().setExpanded(True)

		for i in range(item.childCount()):
			child = item.child(i)
			self.selectObjectsItems(child, selection)

	def guide(self):
		return self._guide

	#------------------------------------------------------
	# SELECTED ITEMS
	#------------------------------------------------------
	def saveExpandedItem(self, item):
		if isinstance(item, LayerTreeWidgetItem):
			item.object().settings()["expanded"] = item.isExpanded()

		self._guide.commit()

	#------------------------------------------------------
	# SELECTED ITEMS
	#------------------------------------------------------
	def selectedLayers(self):
		layers = []
		for item in self.selectedItems():
			if isinstance(item, LayerTreeWidgetItem):
				layers.append(item.object())
		return layers

	def selectedSystems(self):
		systems = []
		for item in self.selectedItems():
			if isinstance(item, LayerTreeWidgetItem):
				systems.extend(item.systems())
			elif isinstance(item, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
				systems.append(item.object())

		systems = list(set(systems))
		return systems

	#------------------------------------------------------
	# MENU
	#------------------------------------------------------
	def createRightClickMenu(self):
		menu = GuideActionsMenu(self)
		menu.uiAddLayerACT.triggered.connect(self.addLayer)
		menu.uiAddSystemACT.triggered.connect(self.addSystem)
		menu.uiToggleGdeACT.triggered.connect(lambda:self.toggleVisibility(gde=True))
		menu.uiToggleRigACT.triggered.connect(lambda:self.toggleVisibility(rig=True))
		menu.uiToggleJntACT.triggered.connect(lambda:self.toggleVisibility(jnt=True))
		menu.uiToggleCtlACT.triggered.connect(lambda:self.toggleVisibility(ctl=True))
		menu.uiBuildACT.triggered.connect(self.build)
		menu.uiDuplicateACT.triggered.connect(self.duplicate)
		menu.uiMirrorACT.triggered.connect(self.mirror)
		menu.uiMirrorL2RACT.triggered.connect(self.mirrorL2R)
		# menu.uiMirrorR2LACT.triggered.connect(self.MirrorR2L)
		# menu.uiSnapACT.triggered.connect(self.snapSystem)
		menu.uiDeleteACT.triggered.connect(self.delete)
		menu.uiToSceneACT.triggered.connect(self.toScene)
		menu.uiFromSceneACT.triggered.connect(self.fromScene)

		QShortcut(QKeySequence(Qt.CTRL|Qt.SHIFT|Qt.Key_N), self, self.addLayer)
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_N), self, self.addSystem)
		QShortcut(QKeySequence(Qt.Key_H), self, lambda:self.toggleVisibility(gde=True))
		QShortcut(QKeySequence(Qt.Key_R), self, lambda:self.toggleVisibility(rig=True))
		QShortcut(QKeySequence(Qt.Key_J), self, lambda:self.toggleVisibility(jnt=True))
		QShortcut(QKeySequence(Qt.Key_C), self, lambda:self.toggleVisibility(ctl=True))
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_B), self, self.build)
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_D), self, self.duplicate)
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_M), self, self.mirror)
		QShortcut(QKeySequence(Qt.CTRL|Qt.SHIFT|Qt.Key_M), self, self.mirrorL2R)
		QShortcut(QKeySequence.Delete, self, self.delete)
		QShortcut(QKeySequence(Qt.Key_F), self, self.toScene)
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_F), self, self.fromScene)

		return menu

	def mousePressEvent(self, event):
		super(GuideTreeWidget, self).mousePressEvent(event)

		if event.button() == Qt.RightButton:
			# We add a little offset, otherwise we might click the first action accidentally
			pos = self.mapToGlobal(event.pos()+QPoint(-25,15))
			self._menu.filterActions()
			self._menu.exec_(pos)
				
		event.accept()

	#-------------------------------------------------------------------------------
	# ACTIONS
	#-------------------------------------------------------------------------------
	def addLayer(self):
		layers = self.selectedLayers()
		parent = layers[0] if layers else self._guide
		layer = actions.addLayer(parent)
		self.setGuide(self._guide, [layer])

	def addSystem(self):
		layers = self.selectedLayers()
		if not layers:
			return
		system = actions.addSystem(layers[0])
		self.setGuide(self._guide, [system])
			
	def toggleVisibility(self, gde=False, rig=False, jnt=False, ctl=False):
		systemGuides = self.selectedSystems()
		if not systemGuides:
			return 
		actions.toggleVisibility(systemGuides, gde, rig, jnt, ctl)

	def build(self):
		self._guide.build(self.selectedSystems())
		self.setGuide(self._guide)

	def duplicate(self):
		systems = actions.duplicate(self._guide, self.selectedSystems())
		self.setGuide(self._guide, systems)

	def mirror(self):
		actions.mirror(self._guide, self.selectedSystems())
		self.setGuide(self._guide)

	def mirrorL2R(self):
		actions.mirrorL2R(self._guide, self.selectedSystems())
		self.setGuide(self._guide)

	def delete(self):
		actions.delete(self._guide, 
			self.selectedLayers(), 
			self.selectedSystems(), 
			self)
		self.setGuide(self._guide)

	def toScene(self):
		actions.toScene(self.selectedSystems())

	def fromScene(self):
		print "fromScene"

		

