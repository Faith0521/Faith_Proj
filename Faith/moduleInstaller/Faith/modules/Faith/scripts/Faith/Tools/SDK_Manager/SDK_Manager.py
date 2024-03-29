import sys,time
from functools import partial

import pymel.core as pm,maya.mel as mel

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.tools.SDK_Manager.UI import UI as mui
from Faith.Core import aboutUI,aboutSDK
from dayu_widgets.message import MMessage
from dayu_widgets.toast import MToast
from dayu_widgets.qt import MIcon
from dayu_widgets.progress_bar import MProgressBar

PY2 = sys.version_info[0] == 2


class MainSDKGUI(QtWidgets.QDialog, mui.Ui_Form):


    def __init__(self, parent=None):
        super(MainSDKGUI, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setupUi(self)
        self.driver_list.setAcceptDrops(False)
        self.driver_list.setDragEnabled(True)
        self.driver_list.setDropIndicatorShown(False)
        self.driven_list.setAcceptDrops(False)
        self.driven_list.setDragEnabled(True)
        self.driven_list.setDropIndicatorShown(False)
        self.installEventFilter(self)


    def keyPressEvent(self, event):
        if not event.key() == QtCore.Qt.Key_Escape:
            super(MainSDKGUI, self).keyPressEvent(event)


class DockableMainUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        self.uiName = "SDKManager"
        super(DockableMainUI, self).__init__(parent=parent)

        self.mainUI = MainSDKGUI()
        self.start_dir = pm.workspace(q=True, rootDirectory=True)
        self.__proxyModel01 = QtCore.QSortFilterProxyModel(self)
        self.__proxyModel02 = QtCore.QSortFilterProxyModel(self)
        self.mainUI.driver_list.setModel(self.__proxyModel01)
        self.mainUI.driven_list.setModel(self.__proxyModel02)

        self.mainUI.driver_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.mainUI.driven_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.create_window()
        self.create_layout()
        self.create_connections()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)


    def create_window(self):

        self.setObjectName(self.uiName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("SDK Tool v0.0.1")
        self.resize(350, 500)
        self.mainUI.pushButton.setIcon(MIcon("cil-lightbulb.png","#ddd"))
        self.mainUI.pushButton_2.setIcon(MIcon("cil-transfer.png", "#ddd"))
        self.mainUI.load_btn.setIcon(MIcon("right_line_dark.png"))
        self.mainUI.refresh_btn.setIcon(MIcon("big_view.svg"))
        self.mainUI.mirror_btn.setIcon(MIcon("list_view.svg"))

    def create_layout(self):

        self.gmc_layout = QtWidgets.QVBoxLayout()
        self.gmc_layout.addWidget(self.mainUI)
        self.gmc_layout.setContentsMargins(3, 3, 3, 3)

        self.setLayout(self.gmc_layout)

    def create_connections(self):
        """
        ui slots connections
        :return:
        """
        self.mainUI.load_btn.clicked.connect(self.loadObj)
        self.mainUI.refresh_btn.clicked.connect(lambda : self.refreshList(self.mainUI.node_le.text()))
        self.mainUI.mirror_btn.clicked.connect(self.mirrorNode)
        self.mainUI.node_le.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainUI.node_le.customContextMenuRequested.connect(self.le_menu)
        self.mainUI.driven_list.clicked.connect(self._refreshDriver)
        self.mainUI.driver_list.clicked.connect(self._refreshDriven)
        self.mainUI.driver_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainUI.driver_list.customContextMenuRequested.connect(self._component_driver_menu)
        self.mainUI.driven_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainUI.driven_list.customContextMenuRequested.connect(self._component_driven_menu)

    def le_menu(self, QPos):
        """

        :return:
        """
        comp_widget = self.mainUI.node_le
        if self.mainUI.node_le.text() == "":
            return
        self.comp_menu = QtWidgets.QMenu()
        parentPosition = comp_widget.mapToGlobal(QtCore.QPoint(0, 0))
        menu_item_01 = self.comp_menu.addAction("Export Node")
        menu_item_01.triggered.connect(self._exportSDK)
        self.comp_menu.addSeparator()
        menu_item_02 = self.comp_menu.addAction("Import Node")
        menu_item_02.triggered.connect(self._importSDK)
        self.comp_menu.addSeparator()
        menu_item_03 = self.comp_menu.addAction("Clear Useless Nodes")
        menu_item_03.triggered.connect(self.delUselessNode)

        self.comp_menu.move(parentPosition + QPos)
        self.comp_menu.show()

    def _refreshDriver(self):
        """

        :return:
        """
        node = self.mainUI.node_le.text()
        model = QtGui.QStandardItemModel(self)
        self.allSDKInfo_dict = {}
        if self.mainUI.frnt_rbtn.isChecked():
            pm.select(node, r=True)
            item = self.mainUI.driven_list.selectedIndexes()[0].data()
            SDKInfo_dict = aboutSDK.getSDKInfoFromAttr(node + '.' + item, "front")
            driverNodes = []
            for sdk,info_dict in SDKInfo_dict.items():   
                driverNode = info_dict["driverNode"]
                driverNodes.append(driverNode)
            driverNodes = set(driverNodes)
            for node in driverNodes:
                model.appendRow(QtGui.QStandardItem(node))
                self.__proxyModel01.setSourceModel(model)
        else:
            pm.select(self.mainUI.driven_list.selectedIndexes()[0].data(),r=True)

    def loadObj(self):
        """

        :return:
        """
        selection = pm.selected()
        if len(selection) == 1:
            self.mainUI.node_le.setText(selection[0].name())
        if len(selection) > 1:
            pm.warning("You select two more objects in the scene.")
            MMessage.warning("You select two more objects in the scene.",parent=self)
        if not selection:
            self.mainUI.node_le.setText("")
            self.refreshList()

        if self.mainUI.node_le.text() != "":
            self.refreshList(selection[0].name())

    def refreshList(self, node=None):
        """

        @return:
        """
        model_01 = QtGui.QStandardItemModel(self)
        model_02 = QtGui.QStandardItemModel(self)
        self.__proxyModel02.setSourceModel(model_01)
        self.__proxyModel01.setSourceModel(model_02)

        if node:
            self.allSDKInfo_dict = {}
            driverAttrs = []
            drivenList = []
            if self.mainUI.frnt_rbtn.isChecked():
                self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "front")
                [drivenList.extend(infoDict["drivenAttrs"]) for animNode, infoDict in self.allSDKInfo_dict.items()]
                drivenList = (set(sorted(drivenList)))
                map(lambda x: model_01.appendRow(QtGui.QStandardItem(x)),drivenList)
                # [model_01.appendRow(QtGui.QStandardItem(obj)) for obj in drivenList]
                self.__proxyModel02.setSourceModel(model_01)
            if self.mainUI.after_rbtn.isChecked():
                self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "after")
                [driverAttrs.append(infoDict["driverAttr"]) for animNode, infoDict in self.allSDKInfo_dict.items()]
                driverAttrs = set(sorted(driverAttrs))
                for attr in driverAttrs:
                    model_02.appendRow(QtGui.QStandardItem(attr))
                    self.__proxyModel01.setSourceModel(model_02)

    def _refreshDriven(self):
        """

        :return:
        """
        node = self.mainUI.node_le.text()
        item = self.mainUI.driver_list.selectedIndexes()[0].data()

        model = QtGui.QStandardItemModel(self)
        self.allSDKInfo_dict = {}
        if self.mainUI.frnt_rbtn.isChecked():
            self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "front")
            pm.select(item, r=True)
        else:
            item = self.mainUI.driver_list.selectedIndexes()[0].data()
            SDKInfo_dict = aboutSDK.getSDKInfoFromAttr(node + '.' + item, "after")
            pm.select(node, r=True)
            drivenNodes = []
            for sdk,infoDict in SDKInfo_dict.items():
                drivenList = infoDict["drivenNodes"]
                drivenNodes.extend(drivenList)
            drivenNodes = set(drivenNodes)
            for node in drivenNodes:
                model.appendRow(QtGui.QStandardItem(node))
            
            self.__proxyModel02.setSourceModel(model)
        
    def _component_driven_menu(self, QPos):
        """

        :return:
        """
        comp_widget = self.mainUI.driven_list
        currentSelection = comp_widget.selectedIndexes()
        if not currentSelection:
            return
        self.comp_menu = QtWidgets.QMenu()
        parentPosition = comp_widget.mapToGlobal(QtCore.QPoint(0, 0))
        menu_item_01 = self.comp_menu.addAction("Mirror Selected")
        menu_item_01.triggered.connect(self.mirrorDrivenKeys)
        self.comp_menu.addSeparator()
        menu_item_02 = self.comp_menu.addAction("Refresh List")
        menu_item_02.triggered.connect(lambda:self.refreshList(node=self.mainUI.node_le.text()))

        self.comp_menu.move(parentPosition + QPos)
        self.comp_menu.show()

    def _component_driver_menu(self, QPos):
        """

        :return:
        """
        comp_widget = self.mainUI.driver_list
        currentSelection = comp_widget.selectedIndexes()
        if not currentSelection:
            return
        self.comp_menu = QtWidgets.QMenu()
        parentPosition = comp_widget.mapToGlobal(QtCore.QPoint(0, 0))
        menu_item_01 = self.comp_menu.addAction("Mirror Selected")
        menu_item_01.triggered.connect(self.mirrorDriverKeys)
        self.comp_menu.addSeparator()
        menu_item_02 = self.comp_menu.addAction("Refresh List")
        menu_item_02.triggered.connect(lambda: self.refreshList(node=self.mainUI.node_le.text()))
        self.comp_menu.move(parentPosition + QPos)
        self.comp_menu.show()

    def _exportSDK(self):
        """

        :return:
        """
        filepath,type = QtWidgets.QFileDialog.getSaveFileName(self,'export','/','json(*.json)')
        if not filepath:
            return
        node = self.mainUI.node_le.text()
        try:
            if self.mainUI.frnt_rbtn.isChecked():
                aboutSDK.exportSDKs([node], filepath, expType="front")
            else:
                aboutSDK.exportSDKs([node], filepath, expType="after")
            MToast.success("Export Success!", self)
        except:
            MToast.error("Export Failed!", self)

    def _importSDK(self):
        """

        :return:
        """
        filepath, type = QtWidgets.QFileDialog.getOpenFileName(self, 'import', '/', 'json(*.json)')
        if not filepath:
            return
        try:
            aboutSDK.importSDKs(filepath)
            MToast.success("Import Success!", self)
        except:
            MToast.error("Import Failed!", self)

    def mirrorDrivenKeys(self):
        node = self.mainUI.node_le.text()
        items = self.mainUI.driven_list.selectedIndexes()
        for i in items:
            attr = i.data()
            isAttr = pm.objExists(node + '.' + attr)
            if isAttr:
                aboutSDK.mirrorSDKs([node], attributes=[attr])
            else:
                MMessage.warning("Selected item {0}.{1} is not exists.".format(node, attr), parent = self)

    def mirrorDriverKeys(self):
        node = self.mainUI.node_le.text()
        items = self.mainUI.driver_list.selectedIndexes()
        for i in items:
            attr = i.data()
            isAttr = pm.objExists(node + '.' + attr)
            if isAttr:
                aboutSDK.mirrorSDKs([node], attributes=[attr])
            else:
                MMessage.warning("Selected item {0}.{1} is not exists.".format(node, attr), parent = self)

    def mirrorNode(self):
        """

        :return:
        """
        node = self.mainUI.node_le.text()
        try:
            aboutSDK.mirrorSDKs([node], attributes=[])
        except RuntimeError as msg:
            print(msg)
            return False

    def delUselessNode(self):

        '''delete all usdless node'''
        # -------------------------------------------------
        # Delete all usdless node in current sence.
        # -------------------------------------------------

        try:
            mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
        except:
            pass
        removeType = ["animCurve", "blendWeighted"]
        ani = pm.ls(type=removeType)

        if len(ani) == 0:
            pass
        else:
            pointsNum = len(ani) - 1
            progress_dialog = QtWidgets.QProgressDialog(
                "Waiting to process...", "Cancel", 0, 8, self
            )
            progress_dialog.setWindowTitle("Delete Useless Nodes")
            progress_dialog.setValue(0)
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.show()

            QtCore.QCoreApplication.processEvents()
            removeNodes = []
            for i,x in enumerate(ani):
                if progress_dialog.wasCanceled():
                    break
                if pm.objExists(x):
                    hasInput = pm.listConnections(x, s=True, d=False, scn=True)
                    hasOutput = pm.listConnections(x, s=False, d=True, scn=True)
                    if 'hyperLayout' in str(hasOutput) and len(hasOutput) == 1:
                        hasOutput = None
                    isLocked = pm.lockNode(x, q=1, l=1)[0]
                    if isLocked == True:
                        pm.lockNode(x, l=False)
                    if not hasInput or not hasOutput:
                        removeNodes.append(x)
            for i in range(0, len(removeNodes)):
                progress_dialog.setLabelText("Delete useless node %s." % (removeNodes[i]))
                progress_dialog.setValue(i)
                pm.delete(removeNodes[i])
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents()
            progress_dialog.close()
            MToast.success("Clear Success.", self)

def show_guide_component_manager(*args):
    aboutUI.showDialog(DockableMainUI, dockable=True)
