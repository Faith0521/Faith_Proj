import os.path
import logging

import maya.OpenMayaUI as mui
from maya import cmds

from Qt import QtCompat
from Qt.QtWidgets import QWidget, QInputDialog, QPushButton
from Qt.QtGui import QColor, QPalette

from brigks.gui.scriptWidget import ScriptWidget
from brigks.gui.pickColorDialog import PickColorDialog
from brigks.gui.guideVisibilityWidget import GuideVisibilityWidget

STEPS = ["Pre Script",
		"Create Objects",
		"Create Attributes",
		"Create Operators",
		"Connect System",
		"Post Script"]

class GuideSettingsWidget(QWidget):

	def __init__(self, guide):
		super(GuideSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "guideSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._blocked = False
		self._selectEventJobID = None

		self.uiGroupVisibilityWDG = GuideVisibilityWidget(None)
		self.uiVisibilityGRP.layout().addWidget(self.uiGroupVisibilityWDG)

		self.uiPreScriptWDG = ScriptWidget("pre")
		self.uiScriptsTAB.layout().addWidget(self.uiPreScriptWDG)
		self.uiPostScriptWDG = ScriptWidget("post")
		self.uiScriptsTAB.layout().addWidget(self.uiPostScriptWDG)

		self.setGuide(guide)
		self.connectWidgets()

	def setGuide(self, guide):
		self._guide = guide
		if self._guide is None:
			return

		self.settings = self._guide.settings
		self._blocked = True
		self._visButtons = []

		# Load Settings
		for x in ["RFk", "RIk", "MFk", "MIk", "LFk", "LIk"]:
			btn = self.__dict__["uiColor"+x]
			value = self.settings("color"+x)
			self.setButtonColor(btn, value)

		self.uiStopAfter.clear()
		self.uiStopAfter.addItems(STEPS)
		self.uiStopAfter.setCurrentIndex(STEPS.index(self.settings("stopAfter")))
		self.uiHideRig.setChecked(self.settings("hideRig"))
		self.uiHideJoints.setChecked(self.settings("hideJoints"))

		# TODO : This is slowing down the loading of the ui.
		self.uiGroupVisibilityWDG.setGuide(self._guide)

		self.loadGroups()
		self.uiPreScriptWDG.setObject(self._guide)
		self.uiPostScriptWDG.setObject(self._guide)
		self._blocked = False

	def connectWidgets(self):
		self._blocked = True

		# Colors
		self.uiColorRFk.clicked.connect(lambda:self.pickColor(self.uiColorRFk, "colorRFk"))
		self.uiColorRIk.clicked.connect(lambda:self.pickColor(self.uiColorRIk, "colorRIk"))
		self.uiColorMFk.clicked.connect(lambda:self.pickColor(self.uiColorMFk, "colorMFk"))
		self.uiColorMIk.clicked.connect(lambda:self.pickColor(self.uiColorMIk, "colorMIk"))
		self.uiColorLFk.clicked.connect(lambda:self.pickColor(self.uiColorLFk, "colorLFk"))
		self.uiColorLIk.clicked.connect(lambda:self.pickColor(self.uiColorLIk, "colorLIk"))

		# Debug 
		self.uiStopAfter.currentIndexChanged.connect(self.saveDebugSettings)
		self.uiHideRig.clicked.connect(self.saveDebugSettings)
		self.uiHideJoints.clicked.connect(self.saveDebugSettings)

		# Groups
		self.uiAddGroupBTN.clicked.connect(self.addGroup)
		self.uiRenameGroupBTN.clicked.connect(self.renameGroup)
		self.uiRemoveGroupBTN.clicked.connect(self.removeGroup)
		self.uiAddMembersBTN.clicked.connect(lambda:self.addRemoveMembers(add=True))
		self.uiRemoveMembersBTN.clicked.connect(lambda:self.addRemoveMembers(add=False))
		self.uiGroupsLIST.itemSelectionChanged.connect(self.loadMembers)
		self.uiMembersLIST.itemSelectionChanged.connect(self.selectScene)
		self.uiMainTAB.currentChanged.connect(self.connectSelection)

		# Script
		self.uiPreScriptWDG.updated.connect(self.scriptUpdated)
		self.uiPostScriptWDG.updated.connect(self.scriptUpdated)


		self._blocked = False

	def connectSelection(self, index):
		if self.uiMainTAB.tabText(index) == "Groups":
			# Connection to Maya Select Event
			self._selectEventJobID = cmds.scriptJob(e=["SelectionChanged", self.selectMembers], protected=True)
		elif self._selectEventJobID:
			cmds.scriptJob(kill=self._selectEventJobID, force=True)
	
	def closeEvent(self, event):
		if self._selectEventJobID:
			cmds.scriptJob(kill=self._selectEventJobID, force=True)
		super(GuideSettingsWidget, self).closeEvent(event)

	def commit(self):
		if self._blocked:
			return
		self._guide.commit()

	# ----------------------------------------------------------------------------------
	# FIRST TAB
	# ----------------------------------------------------------------------------------
	def pickColor(self, button, setting):
		color = self.settings(setting)
		
		dialog = PickColorDialog(self, color)
		dialog.exec_()
		if not dialog.result():
			return

		self.setButtonColor(button, dialog.color)
		self._guide.setSettings(**{setting:dialog.color})
		self.commit()

	def setButtonColor(self, button, color):
		qcolor = QColor()
		qcolor.setRgbF(color[0], color[1], color[2])
		
		palette = QPalette()
		palette.setColor(QPalette.Button, qcolor)
		button.setPalette(palette)

	def saveDebugSettings(self):
		self._guide.setSettings(
			stopAfter=self.uiStopAfter.currentText(),
			hideRig=self.uiHideRig.isChecked(),
			hideJoints=self.uiHideJoints.isChecked()
			)
		self.commit()


	# ----------------------------------------------------------------------------------
	# GROUPS
	# ----------------------------------------------------------------------------------
	def loadGroups(self):
		self.uiGroupsLIST.clear()
		for groupName in self._guide.groups().keys():
			self.uiGroupsLIST.addItem(groupName)

		if self.uiGroupsLIST.count():
			self.uiGroupsLIST.setCurrentRow(0)

	def loadMembers(self):
		groupItem = self.uiGroupsLIST.currentItem()

		self.uiMembersLIST.clear()
		groupName = groupItem.text()
		members = [m.split("|")[-1] for m in self._guide.groups(groupName)]
		self.uiMembersLIST.addItems(members)
		self.uiMembersLIST.sortItems()

	def addGroup(self):
		groupName, rtn = QInputDialog.getText(self, "Group Name", "", text="GroupName")
		if not rtn or not groupName:
			return

		self.uiGroupsLIST.addItem(groupName)
		self._guide.addGroup(groupName)
		self.commit()

	def renameGroup(self):
		groupItem = self.uiGroupsLIST.currentItem()
		groupName = groupItem.text()

		newName, rtn = QInputDialog.getText(self, "Group Name", "", text=groupName)
		if not rtn or not newName:
			return

		groupItem.setText(newName)
		self._guide.renameGroup(groupName, newName)
		self.commit()

	def removeGroup(self):
		index = self.uiGroupsLIST.currentRow()
		groupItem = self.uiGroupsLIST.takeItem(index)
		self._guide.removeGroup(groupItem.text())
		self.commit()

	def addRemoveMembers(self, add=True):
		groupItem = self.uiGroupsLIST.currentItem()
		groupName = groupItem.text()
		selection = cmds.ls(selection=True, type="transform", long=True)
		selection = [x for x in selection if x.startswith("|"+self._guide.setup())]

		if add:
			self._guide.addMembers(groupName, selection)
		else:
			self._guide.removeMembers(groupName, selection)

		self.loadMembers()
		self.selectMembers(selection)
		self.commit()

	def selectMembers(self, selection=None):
		if selection is None:
			try:
				selection = cmds.ls(selection=True, type="transform", long=True)
			except AttributeError:
				pass
			selection = [x.split("|")[-1] for x in selection if x.startswith("|"+self._guide.setup())]
		selection = [x.split("|")[-1] for x in selection]
		for i in range(self.uiMembersLIST.count()):
			item = self.uiMembersLIST.item(i)
			item.setSelected(item.text() in selection)

	def selectScene(self):
		selection = []
		for item in self.uiMembersLIST.selectedItems():
			selection += cmds.ls(item.text(), type="transform", long=True)
		selection = [x for x in selection if x.startswith("|"+self._guide.setup())]
		cmds.select(selection)

	# ----------------------------------------------------------------------------------
	# SCRIPTS
	# ----------------------------------------------------------------------------------
	def scriptUpdated(self, settings):
		self._guide.setSettings(**settings)
		self.commit()