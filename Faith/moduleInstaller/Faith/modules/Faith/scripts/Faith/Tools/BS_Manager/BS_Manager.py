import sys
from functools import partial

import pymel.core as pm,maya.mel as mel,maya.cmds as mc,maya.cmds as cmds

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.Tools.BS_Manager.UI import BS_List as listui
from Faith.Tools.BS_Manager.UI import widget_item as itemui
from Faith.Tools.BS_Manager.UI import MainWin as mainWin
from Faith.Core import aboutUI
from dayu_widgets.line_tab_widget import MLineTabWidget
from dayu_widgets.message import MMessage
from dayu_widgets.toast import MToast
from dayu_widgets.qt import MIcon

class BS_ListUI(QtWidgets.QWidget, listui.Ui_BS_ListMain):
    def __init__(self, parent=None):
        super(BS_ListUI, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setupUi(self)
        self.installEventFilter(self)

class BS_itemUI(QtWidgets.QWidget, itemui.Ui_item_main):
    def __init__(self, parent=None):
        super(BS_itemUI, self).__init__(parent)
        self.setupUi(self)

class BS_MainUI(QtWidgets.QMainWindow, mainWin.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BS_MainUI, self).__init__(parent)
        self.setupUi(self)

class BS_Manager(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        self.uiName = "BS_Manager"
        super(BS_Manager, self).__init__(parent=parent)
        self.start_dir = cmds.workspace(q=True, rootDirectory=True)
        self.mainUI = BS_MainUI()
        self.listUI = BS_ListUI()
        self.init_UI()
        self.create_window()
        self.create_connections()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    def init_UI(self):
        self.main_lay = QtWidgets.QVBoxLayout()
        tab_center = MLineTabWidget()
        tab_center.add_tab(self.listUI,
                           {'text': u'BS Editer', 'svg': 'user_line.svg'})
        tab_center.tool_button_group.set_dayu_checked(0)
        self.main_lay.addWidget(self.mainUI)
        self.main_lay.addWidget(tab_center)
        self.main_lay.addSpacing(20)
        self.main_lay.addStretch()
        self.setLayout(self.main_lay)

    def create_window(self):
        self.setObjectName(self.uiName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("BS Manager v0.0.1")
        self.listUI.target_lb.setPixmap(QtGui.QPixmap("SHAPES_btn_mesh_150.png"))
        self.listUI.load_btn.setIcon(MIcon("SHAPES_btn_mesh_150.png"))
        self.listUI.edit_btn.setIcon(MIcon("SHAPES_regionColor4Paint_150.png"))
        self.listUI.delete_btn.setIcon(MIcon("SHAPES_trash_150.png"))
        self.listUI.cancel_btn.setIcon(MIcon("SHAPES_dismiss_150.png"))

    def create_connections(self):
        self.listUI.load_btn.clicked.connect(self.refresh)
        self.listUI.target_list.itemSelectionChanged.connect(self.refreshList)
        self.listUI.target_list.itemDoubleClicked.connect(self.EnableLine)
        self.listUI.edit_btn.clicked.connect(self.sculptMesh)

    def EnableLine(self):
        """

        @return:
        """

        current_widget = self.listUI.target_list.itemWidget(self.listUI.target_list.currentItem())
        current_widget.targtName_le.setEnabled(True)
        current_widget.targtName_le.returnPressed.connect(self.renameTarget)

    def renameTarget(self):
        """

        @return:
        """
        self.targetBlendShape = cmds.listAttr(self.BlendNode + '.weight', multi=True)
        for i in range(self.listUI.target_list.count()):
            widget = self.listUI.target_list.itemWidget(self.listUI.target_list.item(i))
            if self.targetBlendShape:
                if widget.targtName_le.text() != self.targetBlendShape[i]:
                    cmds.aliasAttr(widget.targtName_le.text(), self.BlendNode + '.' + self.targetBlendShape[i])

    def sculptMesh(self):
        """

        @return:
        """
        self.BlendNode = self.listUI.load_le.text()
        if not cmds.objExists(self.BlendNode):
            return False
        currentMode = cmds.getAttr(self.BlendNode + ".editMode")
        if currentMode == "Default":
            cmds.setAttr(self.BlendNode + ".editMode", "Edit", type="string")
            self.listUI.edit_btn.setIcon(MIcon("SHAPES_regionColor1Paint_200.png", self))
        if currentMode == "Edit":
            cmds.setAttr(self.BlendNode + ".editMode", "Default", type="string")
            self.listUI.edit_btn.setIcon(MIcon("SHAPES_regionColor4Paint_150.png", self))

    def refreshList(self):
        """

        :return:s
        """
        try:
            self.renameTarget()
        except:
            RuntimeError()

        current_widget = self.listUI.target_list.itemWidget(self.listUI.target_list.currentItem())
        for i in range(self.listUI.target_list.count()):
            widget = self.listUI.target_list.itemWidget(self.listUI.target_list.item(i))
            if widget.targtName_le.text() != current_widget.targtName_le.text():
                widget.targtName_le.setEnabled(False)

        targetName = current_widget.targtName_le.text()
        if not cmds.objExists(self.BlendNode + ".CurrentItemName"):
            cmds.addAttr(self.BlendNode, ln="CurrentItemName", dt="string")
            cmds.setAttr(self.BlendNode + ".CurrentItemName", targetName, type="string")
        else:
            cmds.setAttr(self.BlendNode + ".CurrentItemName", targetName, type="string")


    def refresh(self):
        """

        :return:
        """
        self.loadMesh(self.getMesh())
        MeshNode = self.listUI.load_le.text()
        BlendShapeNode = []
        try:
            meshHistory = cmds.listHistory(MeshNode, pdo=True)
            BlendShapeNode = cmds.ls(meshHistory, type='blendShape')
        except:
            pass

        if BlendShapeNode.__len__() != 0:
            self.BlendNode = BlendShapeNode[0]
        else:
            self.BlendNode = ""
        indexIntS = []

        if self.BlendNode != "":
            self.targetBlendShape = cmds.listAttr(self.BlendNode + '.weight', multi=True)
            targetInt = cmds.blendShape(self.BlendNode, query=True, wc=True)
            if not cmds.objExists(self.BlendNode + ".editMode"):
                cmds.addAttr(self.BlendNode, ln="editMode", dt="string")
            cmds.setAttr(self.BlendNode + ".editMode", "Default", type="string")

            if targetInt > 0:
                for i,target in enumerate(self.targetBlendShape):
                    listItemUI = BS_itemUI()
                    myQListWidgetItem = QtWidgets.QListWidgetItem(self.listUI.target_list)
                    myQListWidgetItem.setSizeHint(listItemUI.sizeHint())

                    listItemUI.targtName_le.setText(target)
                    targetValue = float(cmds.getAttr(self.BlendNode + '.' + target))
                    listItemUI.val_lb.setText(str(round(targetValue,3)))
                    listItemUI.connect_btn.setToolTip("Select or delete driver")
                    listItemUI.combo_btn.setToolTip("Create combo")
                    # QtWidgets.QPushButton.setToolTip()
                    targetConnect = cmds.listConnections(self.BlendNode + '.' + target, s=True, d=False)

                    if targetValue < 0.0001:
                        targetValue = 0
                    if targetConnect == None and targetValue >= 0.001:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor1_200.png", self))
                    elif targetConnect == None and targetValue == 0:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor1_200.png", self))
                    else:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor4_200.png", self))

                    self.listUI.target_list.addItem(myQListWidgetItem)
                    self.listUI.target_list.setItemWidget(myQListWidgetItem, listItemUI)


    def getMesh(self):
        sel = cmds.ls(sl=1)
        ret = 'Please Loading Mesh.'
        mesh = []
        for i in sel:
            if cmds.nodeType(i) == 'transform':
                mesh = i

        if len(mesh):
            BaseRelatives = cmds.listRelatives(mesh, f=1)[0]
            if cmds.nodeType(BaseRelatives) == 'mesh':
                ret = mesh
            else:
                ret = 'Please Loading Mesh.'
        return ret

    def meshExists(self, mesh):
        """

        :param mesh:
        :return:
        """
        try:
            listMesh = cmds.listRelatives(mesh, s=True, f=1)
            if cmds.nodeType(listMesh[0]) == 'mesh':
                return True
            return False
        except TypeError:
            pass

    def loadMesh(self, sel):
        if len(sel) > 0 and self.meshExists(sel):
            self.listUI.load_le.setText(sel)
            self.listUI.load_le.setEnabled(False)

def show(*args):
    aboutUI.showDialog(BS_Manager, dockable=True)

























