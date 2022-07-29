import sys
from functools import partial

import pymel.core as pm

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.Tools.SDK_Manager.UI import UI as mui
from Faith.Core import aboutUI,aboutSDK

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

        self.create_window()
        self.create_layout()
        self.create_connections()
        # self.refreshList()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)


    def create_window(self):

        self.setObjectName(self.uiName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("SDK Tool v0.0.1")
        self.resize(350, 500)


    def create_layout(self):

        self.gmc_layout = QtWidgets.QVBoxLayout()
        self.gmc_layout.addWidget(self.mainUI)
        self.gmc_layout.setContentsMargins(3, 3, 3, 3)

        self.setLayout(self.gmc_layout)

    def create_connections(self):
        self.mainUI.load_btn.clicked.connect(self.loadObj)
        # QtWidgets.QListView().selectedIndexes()
        self.mainUI.driven_list.clicked.connect(self._refreshDriver)
        self.mainUI.driven_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainUI.driven_list.customContextMenuRequested.connect(self._component_menu)

    def _refreshDriver(self):
        """

        :return:
        """
        node = self.mainUI.node_le.text()
        model = QtGui.QStandardItemModel(self)
        self.allSDKInfo_dict = {}
        if self.mainUI.frnt_rbtn.isChecked():
            self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "front")
        else:
            self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "after")

        driverList = []
        for sdk,infoDict in self.allSDKInfo_dict.items():
            driverNode = infoDict["driverNode"]
            drivenAttrs = infoDict["drivenAttrs"]
            item = self.mainUI.driven_list.selectedIndexes()[0].data()
            if item in drivenAttrs:
                model.appendRow(QtGui.QStandardItem(driverNode))
        self.__proxyModel01.setSourceModel(model)

    def loadObj(self):
        """

        :return:
        """
        selection = pm.selected()
        if len(selection) == 1:
            self.mainUI.node_le.setText(selection[0].name())
        if len(selection) > 1:
            pm.warning("You select two more objects in the scene.")
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
                for animNode, infoDict in self.allSDKInfo_dict.items():
                    drivenList.extend(infoDict["drivenAttrs"])
                drivenList = set(drivenList)    
                for obj in drivenList:
                    model_01.appendRow(QtGui.QStandardItem(obj))
                self.__proxyModel02.setSourceModel(model_01)
            if self.mainUI.after_rbtn.isChecked():
                self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "after")
                for animNode, infoDict in self.allSDKInfo_dict.items():
                    driverAttrs.append(infoDict["driverAttr"])
                driverAttrs = set(driverAttrs)
                for attr in driverAttrs:
                    model_02.appendRow(QtGui.QStandardItem(attr))
                    self.__proxyModel01.setSourceModel(model_02)

    def _refreshDrivenList(self, node):
        """

        :return:
        """
        model = QtGui.QStandardItemModel(self)
        self.allSDKInfo_dict = {}
        if self.mainUI.frnt_rbtn.isChecked():
            self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "front")
        else:
            self.allSDKInfo_dict = aboutSDK.getSDKInfoFromNode(node, "after")

        for animNode, infoDict in self.allSDKInfo_dict.items():
            drivenList = infoDict["drivenAttrs"]
            for obj in drivenList:
                model.appendRow(QtGui.QStandardItem(obj))
            self.__proxyModel02.setSourceModel(model)

    def _component_menu(self, QPos):
        """

        :return:
        """
        comp_widget = self.mainUI.driven_list
        currentSelection = comp_widget.selectedIndexes()
        if currentSelection is None:
            return
        self.comp_menu = QtWidgets.QMenu()
        parentPosition = comp_widget.mapToGlobal(QtCore.QPoint(0, 0))
        menu_item_01 = self.comp_menu.addAction("Mirror Selected")
        self.comp_menu.addSeparator()
        menu_item_02 = self.comp_menu.addAction("Refresh List")
        self.comp_menu.addSeparator()
        menu_item_03 = self.comp_menu.addAction("Export Node")
        self.comp_menu.addSeparator()
        menu_item_04 = self.comp_menu.addAction("Import Node")

        self.comp_menu.move(parentPosition + QPos)
        self.comp_menu.show()

def show_guide_component_manager(*args):
    aboutUI.showDialog(DockableMainUI, dockable=True)


if __name__ == "__main__":

    show_guide_component_manager()