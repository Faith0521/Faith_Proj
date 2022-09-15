# -*- coding: utf-8 -*-
import sys
from functools import partial

import pymel.core as pm,maya.mel as mel,maya.cmds as mc,maya.cmds as cmds
# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
# from imp import reload
from Faith.Tools.BS_Manager.UI import BS_List as listui
from Faith.Tools.BS_Manager.UI import list_item as itemui
from Faith.Tools.BS_Manager.UI import item_widget as co_widget
from Faith.Tools.BS_Manager.UI import BS_clone as cloneui
from Faith.Tools.BS_Manager.UI import between_item as betweenui
from Faith.Tools.BS_Manager.UI import driver as drvui
from Faith.Tools.BS_Manager.UI import MainWin as mainWin
from Faith.Tools.BS_Manager import corrective
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


class BS_drvUI(QtWidgets.QWidget, drvui.Ui_Form):
    def __init__(self, parent=None):
        super(BS_drvUI, self).__init__(parent)
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
        self.drvUI = BS_drvUI()

        self.widgetInfo = {}
        self.deleteGrp = []

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
        tab_center.add_tab(self.drvUI,
                           {'text': u'BS 驱动', 'svg': 'SHAPES_editAddNode_200.png'})
        tab_center.setStyleSheet(QSS)
        self.mainUI.verticalLayout_2.addWidget(tab_center)

        main_layout.addWidget(self.mainUI)

    def create_connections(self):
        self.listUI.load_btn.clicked.connect(self.loadList)
        self.listUI.target_list.itemSelectionChanged.connect(self.refreshList)
        self.listUI.target_list.itemDoubleClicked.connect(self.EnableLine)
        self.listUI.edit_btn.clicked.connect(
            lambda: self.changeBtnMode(
                self.listUI.load_le.text(), self.BlendNode, self.widgetInfo["widgetInfo"][1]
            )
        )
        self.collapse_item.mirror_btn.clicked.connect(self.mirrorBlendShape)
        # self.listUI.edit_btn.clicked.connect(self.sculptMesh)

    def refreshChannels(self):
        """
        刷新通道栏ui
        :return:
        """
        if "widgetInfo" not in self.widgetInfo:
            return False

        self.collapsible_wdg_b.add_widget(self.betweenUI)
        self.betweenUI.val_dspin.valueChanged.connect(self.SpinValueChange)
        self.betweenUI.val_slider.valueChanged.connect(self.SliderValueChange)
        self.betweenUI.delete_btn.clicked.connect(self.deleteTarget)
        value = cmds.getAttr("%s.%s" % (self.BlendNode, self.widgetInfo["widgetInfo"][1]))
        self.betweenUI.val_dspin.setValue(value)

    def deleteTarget(self):
        """

        :return:
        """
        return

    def SpinValueChange(self):
        """
        spinBox槽函数
        @return:
        """
        self.betweenUI.val_slider.setValue(self.betweenUI.val_dspin.value() * 1000)
        cmds.setAttr("%s.%s"%(self.BlendNode, self.widgetInfo["widgetInfo"][1]), self.betweenUI.val_dspin.value())

    def SliderValueChange(self):
        """
        slider槽函数
        @return:
        """
        self.betweenUI.val_dspin.setValue(self.betweenUI.val_slider.value() / 1000.0)

    def EnableLine(self):
        """
        设置target lineEdit是否可编辑
        @return:
        """

        current_widget = self.widgetInfo["widgetInfo"][0]
        current_widget.targtName_le.setEnabled(True)
        current_widget.targtName_le.returnPressed.connect(self.renameTarget)

    def renameTarget(self):
        """
        重命名 target
        @return:
        """
        self.targetBlendShape = cmds.listAttr(self.BlendNode + '.weight', multi=True)
        for i in range(self.listUI.target_list.count()):
            widget = self.listUI.target_list.itemWidget(self.listUI.target_list.item(i))
            if self.targetBlendShape:
                if widget.targtName_le.text() != self.targetBlendShape[i]:
                    cmds.aliasAttr(widget.targtName_le.text(), self.BlendNode + '.' + self.targetBlendShape[i])

    @QtCore.Slot()
    def changeBtnMode(self, mesh, bsName, editTargetName):
        """
        编辑按钮槽函数
        :param mesh:
        :param bsName:
        :param editTargetName:
        :return:
        """
        if self.listUI.edit_btn.text() == u"编辑":
            self.correctivePose(mesh, bsName, editTargetName)
        elif self.listUI.edit_btn.text() == u"退出":
            self.correctiveExit()
        print(self.edit, editTargetName)

    def correctiveExit(self):
        """
        退出编辑模式
        :return:
        """
        self.listUI.edit_btn.setText(u"编辑")
        if self.deleteGrp:
            try:
                pm.delete(self.deleteGrp)
            except Exception as msg:
                RuntimeError(msg)
        cmds.setAttr(self.listUI.load_le.text() + ".v", 1)
        self.listUI.edit_btn.setStyleSheet("")
        # self.edit = 0

    def refreshList(self):
        """
        列表item切换槽函数
        :return:
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

    def loadList(self):
        """
        加载按钮槽函数
        :return:
        """
        currentHeight = self.listUI.target_list.height()
        self.listUI.target_list.setMinimumSize(QtCore.QSize(0, currentHeight+100))
        self.loadMesh(self.getMesh())
        self.MeshNode = self.listUI.load_le.text()
        BlendShapeNode = []
        try:
            meshHistory = cmds.listHistory(self.MeshNode, pdo=True)
            BlendShapeNode = cmds.ls(meshHistory, type='blendShape')
        except:
            pass

        if BlendShapeNode.__len__() != 0:
            self.BlendNode = BlendShapeNode[0]
        else:
            self.BlendNode = ""
        # indexIntS = []

        if self.BlendNode != "":
            self.listUI.bs_cb.setItemText(0, self.BlendNode)
            self.targetBlendShape = cmds.listAttr(self.BlendNode + '.weight', multi=True)
            targetInt = cmds.blendShape(self.BlendNode, query=True, wc=True)
            if not cmds.objExists(self.BlendNode + ".editMode"):
                cmds.addAttr(self.BlendNode, ln="editMode", dt="string")
            cmds.setAttr(self.BlendNode + ".editMode", "Default", type="string")

            if targetInt > 0:
                for i,target in enumerate(self.targetBlendShape):
                    self.refreshItem(self.listUI.bs_cb.currentText(), target)

    def refreshItem(self, bsName, targetName):
        """
        刷新item
        :param bsName:
        :param targetName:
        :return:
        """
        listItemUI = BS_itemUI()
        myQListWidgetItem = QtWidgets.QListWidgetItem(self.listUI.target_list)
        myQListWidgetItem.setSizeHint(listItemUI.sizeHint())

        listItemUI.targtName_le.setText(targetName)
        targetValue = float(cmds.getAttr(bsName + '.' + targetName))
        listItemUI.connect_btn.setToolTip("Select or delete driver")
        listItemUI.combo_btn.setToolTip("Create combo")

        targetConnect = cmds.listConnections(bsName + '.' + targetName, s=True, d=False)

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

    def correctivePose(self, mesh, bsName, editTargetName):
        """

        :param mesh:
        :param bsName:
        :param editTargetName:
        :return:
        """
        self.betweenUI.val_dspin.setValue(1.0)
        self.listUI.edit_btn.setText(u"退出")
        self.listUI.edit_btn.setStyleSheet("background-color:red;")
        if isinstance(bsName, unicode) or isinstance(bsName, str):
            bsName = pm.PyNode(bsName)
        targetIndex = bsName.attr(editTargetName).index()
        inputTarget = bsName.it[0].itg[targetIndex].iti[6000].igt.listConnections(d=False)
        if inputTarget:
            orgGeo = bsName.getInputGeometry()
            orgGeo[0].outMesh >> pm.PyNode(inputTarget[0]).inMesh
        else:
            # rebuild target
            inputTarget = corrective.rebuildTarget('%s.%s' % (bsName.name(), editTargetName))
            inputTarget = [pm.PyNode(inputTarget[0])]
        # beZero
        orgGeo = bsName.getInputGeometry()
        orgGeo[0].outMesh >> pm.PyNode(inputTarget[0]).inMesh
        pm.refresh(f=True)
        orgGeo[0].outMesh // pm.PyNode(inputTarget[0]).inMesh
        # CCS
        pm.select(mesh)
        ccsReturn = corrective.invert(base=mesh, name=None, targetName=editTargetName, invert=inputTarget[0].name())
        # ccsShape = cmds.listHistory(ccsReturn[1], pdo=True)

        cmds.select(ccsReturn[0])
        self.deleteGrp.append(ccsReturn[0])
        self.deleteGrp.append(ccsReturn[2])

    def mirrorBlendShape(self):
        xyz = 1
        if self.collapse_item.x_rb.isChecked():
            xyz = 1
        elif self.collapse_item.y_rb.isChecked():
            xyz = 2
        elif self.collapse_item.z_rb.isChecked():
            xyz = 3

        self.sourceField = self.collapse_item.name_le.text()
        targetBlendShapeWeight = cmds.listAttr(self.BlendNode + '.weight', multi=True)

        if cmds.objExists(self.sourceField):
            standerd = len(cmds.ls('*%s*' % self.sourceField))
            nMirror = self.sourceField + '_' + str(standerd)
        else:
            nMirror = self.sourceField

        nameMirror = nMirror
        if targetBlendShapeWeight.__contains__(nameMirror):
            MToast.warning(u'属性:%s可能已经存在.'%nameMirror, self)
            return

        targetIndex = -1
        baseMesh = cmds.createNode("mesh", name="baseIn_%s"%self.MeshNode)
        cmds.sets(baseMesh, edit=True, forceElement='initialShadingGroup')
        listMeshShape_Orig = corrective.meshOrig(self.MeshNode)
        cmds.connectAttr(listMeshShape_Orig[0] + '.outMesh', baseMesh + '.inMesh')
        base = cmds.listRelatives(baseMesh, p=True, f=1)[0]


def show(*args):
    aboutUI.showDialog(BS_Manager, dockable=True)