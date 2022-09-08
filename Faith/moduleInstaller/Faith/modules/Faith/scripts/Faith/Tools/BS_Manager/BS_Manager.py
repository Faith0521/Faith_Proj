# -*- coding: utf-8 -*-
import sys
from functools import partial

import pymel.core as pm,maya.mel as mel,maya.cmds as mc,maya.cmds as cmds

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui

from Faith.Tools.BS_Manager.UI import BS_List as listui
from Faith.Tools.BS_Manager.UI import list_item as itemui
from Faith.Tools.BS_Manager.UI import item_widget as co_widget
from Faith.Tools.BS_Manager.UI import BS_clone as cloneui
from Faith.Tools.BS_Manager.UI import between_item as betweenui
from Faith.Tools.BS_Manager.UI import MainWin as mainWin
from Faith.Core import aboutUI

from dayu_widgets.line_tab_widget import MLineTabWidget
from dayu_widgets.message import MMessage
from dayu_widgets.toast import MToast
from dayu_widgets.collapse import MCollapse
from dayu_widgets.qt import MIcon

QSS = """
QWidget{
    font-size: 14px;
    font-family: 楷体;
} 
"""

class BS_ListUI(QtWidgets.QWidget, listui.Ui_BS_ListMain):
    def __init__(self, parent=None):
        super(BS_ListUI, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setupUi(self)
        self.installEventFilter(self)


class BS_itemUI(QtWidgets.QWidget, itemui.Ui_listItem_Main):
    def __init__(self, parent=None):
        super(BS_itemUI, self).__init__(parent)
        self.setupUi(self)


class BS_CoItemUI(QtWidgets.QWidget, co_widget.Ui_tab_main):
    def __init__(self, parent=None):
        super(BS_CoItemUI, self).__init__(parent)
        self.setupUi(self)


class BS_CloneUI(QtWidgets.QWidget, cloneui.Ui_Clone_Main):
    def __init__(self, parent=None):
        super(BS_CloneUI, self).__init__(parent)
        self.setupUi(self)


class BS_betweenUI(QtWidgets.QWidget, betweenui.Ui_in_item_Main):
    def __init__(self, parent=None):
        super(BS_betweenUI, self).__init__(parent)
        self.setupUi(self)


class BS_MainUI(QtWidgets.QMainWindow, mainWin.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BS_MainUI, self).__init__(parent)
        ui = self.setupUi(self)


class BS_Manager(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        self.uiName = "BS_Manager"
        super(BS_Manager, self).__init__(parent=parent)
        self.start_dir = cmds.workspace(q=True, rootDirectory=True)
        self.mainUI = BS_MainUI()
        self.listUI = BS_ListUI()
        self.collapse_item = BS_CoItemUI()
        self.cloneUI = BS_CloneUI()
        self.betweenUI = BS_betweenUI()

        self.widgetInfo = {}

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    def create_widgets(self):
        self.setObjectName(self.uiName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("BS Manager v0.0.1")

        self.listUI.load_btn.setIcon(MIcon("SHAPES_btn_mesh_200.png", self))

        self.collapsible_wdg_a = aboutUI.createCollapsibleWidget(self.listUI.list_widget, True, u"BS列表")
        self.collapsible_wdg_b = aboutUI.createCollapsibleWidget(None, False,u"通道")
        self.collapsible_wdg_c = aboutUI.createCollapsibleWidget(self.collapse_item.mirror_widget, False, u"镜像目标体")
        self.collapsible_wdg_d = aboutUI.createCollapsibleWidget(self.collapse_item.drive_widget, False, u"驱动属性")

        self.clone_collapsible_a = aboutUI.createCollapsibleWidget(self.cloneUI.load_widget, True, u"加载模型")
        self.clone_collapsible_b = aboutUI.createCollapsibleWidget(self.cloneUI.cloneList_widget, True, u"目标体列表")


    def createScrollWidget(self, widgets):
        body_wdg = QtWidgets.QWidget()

        body_layout = QtWidgets.QVBoxLayout(body_wdg)
        body_layout.setContentsMargins(4, 2, 4, 2)
        body_layout.setSpacing(3)
        body_layout.setAlignment(QtCore.Qt.AlignTop)

        for widget in widgets:
            body_layout.addWidget(widget)

        body_scroll_area = QtWidgets.QScrollArea()
        body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        body_scroll_area.setWidgetResizable(True)
        body_scroll_area.setWidget(body_wdg)

        return body_scroll_area

    def create_layouts(self):
        self.body_scroll_area = self.createScrollWidget([self.collapsible_wdg_a,self.collapsible_wdg_b,
                                                         self.collapsible_wdg_c,self.collapsible_wdg_d])
        self.clone_scroll_area = self.createScrollWidget([self.clone_collapsible_a, self.clone_collapsible_b])


        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        tab_center = MLineTabWidget()
        tab_center.add_tab(self.body_scroll_area,
                           {'text': u'BS 编辑', 'svg': 'SHAPES_drivenSet_200.png'})
        tab_center.add_tab(self.clone_scroll_area,
                           {'text': u'BS 拷贝', 'svg': 'SHAPES_editAddNode_200.png'})
        tab_center.setStyleSheet(QSS)
        self.mainUI.verticalLayout_2.addWidget(tab_center)

        main_layout.addWidget(self.mainUI)

    def create_connections(self):
        self.listUI.load_btn.clicked.connect(self.refresh)
        self.listUI.target_list.itemSelectionChanged.connect(self.refreshList)
        self.listUI.target_list.itemDoubleClicked.connect(self.EnableLine)
        # self.listUI.edit_btn.clicked.connect(self.sculptMesh)


    def refreshChannels(self):
        """

        :return:
        """
        if "widgetInfo" not in self.widgetInfo:
            return False
        self.collapsible_wdg_b.add_widget(self.betweenUI)
        self.betweenUI.val_dspin.valueChanged.connect(self.SpinValueChange)
        self.betweenUI.val_slider.valueChanged.connect(self.SliderValueChange)
        self.betweenUI.set_btn.clicked.connect(self.setTargetValue)
        value = cmds.getAttr("%s.%s" % (self.BlendNode, self.widgetInfo["widgetInfo"][1]))
        self.betweenUI.val_dspin.setValue(value)

    def SpinValueChange(self):
        """

        @return:
        """
        self.betweenUI.val_slider.setValue(self.betweenUI.val_dspin.value() * 1000)
        cmds.setAttr("%s.%s"%(self.BlendNode, self.widgetInfo["widgetInfo"][1]), self.betweenUI.val_dspin.value())

    def SliderValueChange(self):
        """

        @return:
        """
        self.betweenUI.val_dspin.setValue(self.betweenUI.val_slider.value() / 1000.0)

    def EnableLine(self):
        """

        @return:
        """

        current_widget = self.widgetInfo["widgetInfo"][0]
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

    def setTargetValue(self):
        """

        @return:
        """
        if self.listUI.load_le.text() == "":
            return False
        if not cmds.objExists(self.BlendNode):
            return False
        btnText = self.betweenUI.set_btn.text()
        if btnText == u"设置":
            self.betweenUI.set_btn.setText(u"编辑")
        if btnText == u"编辑":
            self.betweenUI.set_btn.setStyleSheet("background-color:red;")
            self.betweenUI.set_btn.setText(u"退出")
        if btnText == u"编辑":
            self.betweenUI.set_btn.setStyleSheet("")
            self.betweenUI.set_btn.setText(u"设置")
        # if currentMode == "Default":
        #     cmds.setAttr(self.BlendNode + ".editMode", "Edit", type="string")
        #     self.betweenUI.set_btn.setStyleSheet("background-color:red;")
        #     cmds.setAttr("%s.%s"%(self.BlendNode, self.widgetInfo["widgetInfo"][1]), 1.0)
        # if currentMode == "Edit":
        #     cmds.setAttr(self.BlendNode + ".editMode", "Default", type="string")
        #     self.betweenUI.set_btn.setStyleSheet("")

    def refreshList(self):
        """

        :return:s
        """
        try:
            self.renameTarget()
        except:
            RuntimeError()
        widgetInfoList = []
        current_widget = self.listUI.target_list.itemWidget(self.listUI.target_list.currentItem())
        if current_widget:
            widgetInfoList.append(current_widget)
            for i in range(self.listUI.target_list.count()):
                widget = self.listUI.target_list.itemWidget(self.listUI.target_list.item(i))
                if widget.targtName_le.text() != current_widget.targtName_le.text():
                    widget.targtName_le.setEnabled(False)

            targetName = current_widget.targtName_le.text()
            widgetInfoList.append(targetName)
            self.widgetInfo.update({"widgetInfo": widgetInfoList})
            self.refreshChannels()


    def refresh(self):
        """

        :return:
        """
        currentHeight = self.listUI.target_list.height()
        self.listUI.target_list.setMinimumSize(QtCore.QSize(0, currentHeight+100))
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
        # indexIntS = []

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
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor1.png", self))
                    elif targetConnect == None and targetValue == 0:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor1.png", self))
                    else:
                        listItemUI.connect_btn.setIcon(MIcon("SHAPES_regionColor4.png", self))

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
    # BS_Manager().show()
    aboutUI.showDialog(BS_Manager, dockable=True)