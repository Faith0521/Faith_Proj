import sys
from functools import partial

import pymel.core as pm,maya.mel as mel,maya.cmds as mc,maya.cmds as cmds

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.Tools.BS_Manager.UI import BS_List as listui
from Faith.Tools.BS_Manager.UI import widget_item as itemui
reload(itemui)
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
        super(BS_Manager, self).__init__(parent=parent)
        self.uiName = "BS_Manager"
        self.mainUI = BS_MainUI()
        self.listUI = BS_ListUI()
        self.init_UI()
        self.create_window()
        self.create_connections()

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
        self.listUI.edit_btn.setStyleSheet("QPushButton{border-image:'SHAPES_regionColor4Paint_150.png';}")
        self.listUI.load_btn.setIcon(MIcon("SHAPES_btn_mesh_150.png"))
        # self.listUI.edit_btn.setIcon(MIcon("SHAPES_regionColor4Paint_150.png"))
        self.listUI.delete_btn.setIcon(MIcon("SHAPES_trash_150.png"))
        self.listUI.cancel_btn.setIcon(MIcon("SHAPES_dismiss_150.png"))

    def create_connections(self):
        self.listUI.load_btn.clicked.connect(self.refresh)
        self.listUI.target_list.itemSelectionChanged.connect(self.refreshBtList)

    def refreshBtList(self):
        """

        :return:s
        """
        current_widget = self.listUI.target_list.itemWidget(self.listUI.target_list.currentItem())
        current_widget.connect_btn.clicked.connect(lambda : self.refresh_cnBtn(current_widget.connect_btn))
        print(current_widget.targtName_le.text())

    def refresh_cnBtn(self, btn):
        """

        :return:
        """
        # btn.setIcon(MIcon("SHAPES_confirm_150.png", self))
        return

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
            BlendNode = BlendShapeNode[0]
        else:
            BlendNode = ""
        indexIntS = []

        if BlendNode != "":
            targetBlendShape = cmds.listAttr(BlendNode + '.weight', multi=True)
            targetInt = cmds.blendShape(BlendNode, query=True, wc=True)
            # print(targetBlendShape, targetInt)
            if targetInt > 0:
                for i,target in enumerate(targetBlendShape):
                    listItemUI = BS_itemUI()
                    myQListWidgetItem = QtWidgets.QListWidgetItem(self.listUI.target_list)
                    myQListWidgetItem.setSizeHint(listItemUI.sizeHint())

                    listItemUI.targtName_le.setText(target)
                    targetValue = cmds.getAttr(BlendNode + '.' + target)
                    listItemUI.val_lb.setText(str(round(targetValue,3)))

                    connections = pm.listConnections(BlendNode + '.' + target, s=True, d=False)
                    if connections and targetValue == 0:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor4_200.png", self))
                    elif not connections and targetValue > 0:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor1_200.png", self))
                    else:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor2_200.png", self))

                    self.listUI.target_list.addItem(myQListWidgetItem)
                    self.listUI.target_list.setItemWidget(myQListWidgetItem, listItemUI)
        # selected_node = pm.selected()
        # if not selected_node:
        #     return
        #
        # mesh = pm.listRelatives(selected_node, s=1, type="mesh")
        # if not mesh:
        #
        #     return False
        #
        #
        #
        # shape = ""
        # if self.listUI.load_le.text() != "":
        #     shape = self.listUI.load_le.text()
        #
        # shapeNode = pm.PyNode(shape)
        # bsNodes = shapeNode.history(type = "blendShape")
        # if len(bsNodes) >= 1:
        #     MMessage.error("Have too many bs nodes!", self)
        #
        # bs_node = bsNodes[0]
        # if not mc.nodeType(selected_node)
        # self.listUI.load_le
        # for i in range(5):
            # self.listItemUI.connect_btn.setText(str(i))

        # for i in range(8):
        # widget = QtWidgets.QWidget()
        # main_lay = QtWidgets.QHBoxLayout(widget)
        # btn = QtWidgets.QPushButton("aaaa")
        # main_lay.addWidget(btn)
        # self.listUI.target_list.setItemWidget(item, widget)

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

























