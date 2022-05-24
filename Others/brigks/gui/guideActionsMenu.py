
from Qt.QtWidgets import QMenu
from Qt.QtGui import QKeySequence
from Qt.QtCore import Qt

from brigks.gui.guideTreeWidgetItems import GuideTreeWidgetItem, LayerTreeWidgetItem, SystemTreeWidgetItem, SubSystemTreeWidgetItem

#-------------------------------------------------------------------------------
# RIGHT CLICK MENU
#-------------------------------------------------------------------------------
class GuideActionsMenu(QMenu):
	
	def __init__(self, tree, parent=None):
		super(GuideActionsMenu, self).__init__(parent)

		self._tree = tree
		
		# Actions
		self.uiAddLayerACT = self.addAction("Add Layer")
		self.uiAddLayerACT.setShortcut(QKeySequence(Qt.CTRL|Qt.SHIFT|Qt.Key_H))
		self.uiAddSystemACT = self.addAction("Add System")
		self.uiAddSystemACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_N))
		self.addSeparator()
		self.uiToggleGdeACT = self.addAction("Toggle Vis Gde")
		self.uiToggleGdeACT.setShortcut(QKeySequence(Qt.Key_H))
		self.uiToggleRigACT = self.addAction("Toggle Vis Rig")
		self.uiToggleRigACT.setShortcut(QKeySequence(Qt.Key_R))
		self.uiToggleJntACT = self.addAction("Toggle Vis Jnt")
		self.uiToggleJntACT.setShortcut(QKeySequence(Qt.Key_J))
		self.uiToggleCtlACT = self.addAction("Toggle Vis Ctl")
		self.uiToggleCtlACT.setShortcut(QKeySequence(Qt.Key_C))
		self.addSeparator()
		self.uiBuildACT = self.addAction("Build")
		self.uiBuildACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_B))
		self.uiDuplicateACT = self.addAction("Duplicate")
		self.uiDuplicateACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_D))
		self.uiMirrorACT = self.addAction("Mirror")
		self.uiMirrorACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_M))
		self.uiMirrorL2RACT = self.addAction("Mirror L to R")
		self.uiMirrorACT.setShortcut(QKeySequence(Qt.CTRL|Qt.SHIFT|Qt.Key_M))
		# self.uiMirrorR2LACT = self.addAction("Mirror R to L")
		# self.uiSnapACT = self.addAction("Snap")
		self.addSeparator()
		self.uiDeleteACT = self.addAction("Delete")
		self.uiDeleteACT.setShortcut(QKeySequence.Delete)
		self.addSeparator()
		self.uiToSceneACT = self.addAction("Select in Scene")
		self.uiToSceneACT.setShortcut(QKeySequence(Qt.Key_F))
		self.uiFromSceneACT = self.addAction("Select from Scene")
		self.uiFromSceneACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_F))
	
	def filterActions(self):
		guideSelected = []
		layerSelected = []
		systemSelected = []
		
		for item in self._tree.selectedItems():
			if isinstance(item, GuideTreeWidgetItem):
				guideSelected.append(item.object())
			elif isinstance(item, LayerTreeWidgetItem):
				layerSelected.append(item.object())
			elif isinstance(item, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
				systemSelected.append(item.object())
				
		# Actions Visible
		isEmpty = self._tree.guide() is None
		hasSelection = bool(guideSelected+layerSelected+systemSelected)
		isLayerOnly = bool(layerSelected and not guideSelected and not systemSelected)
		isOneLayer = bool(isLayerOnly and (len(layerSelected) == 1))
		isSystemOnly = bool(systemSelected and not guideSelected and not layerSelected)
		isSystemOrLayer = bool(not guideSelected and hasSelection)
		isGuideOrLayer = bool(not systemSelected and hasSelection)
		isOneGuideOrOneLayer = bool(isGuideOrLayer and (len(layerSelected+guideSelected) == 1))

		self.uiAddLayerACT.setVisible(isOneGuideOrOneLayer)
		self.uiAddSystemACT.setVisible(isOneLayer)

		self.uiToggleGdeACT.setVisible(isSystemOrLayer)
		self.uiToggleRigACT.setVisible(isSystemOrLayer)
		self.uiToggleJntACT.setVisible(isSystemOrLayer)
		self.uiToggleCtlACT.setVisible(isSystemOrLayer)

		self.uiBuildACT.setVisible(hasSelection)
		self.uiDuplicateACT.setVisible(isSystemOnly) 
		self.uiMirrorACT.setVisible(isSystemOnly) 
		self.uiMirrorL2RACT.setVisible(isLayerOnly)
		# self.uiMirrorR2LACT.setVisible(isLayerOnly)

		self.uiDeleteACT.setVisible(isSystemOrLayer)

		self.uiToSceneACT.setVisible(isSystemOrLayer) 
		self.uiFromSceneACT.setVisible(not isEmpty)
