import sys
from functools import partial

import pymel.core as pm

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.Tools.SDK_Manager.UI import UI as mui
from Faith.Core import aboutUI

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
        self.__proxyModel = QtCore.QSortFilterProxyModel(self)
        self.mainUI.component_listView.setModel(self.__proxyModel)

        self.create_window()
        self.create_layout()
        self.create_connections()
        self.refreshList()

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

    def refreshList(self):
        pass

    def loadObj(self):
        """

        :return:
        """
        pass

def show_guide_component_manager(*args):
    aboutUI.showDialog(DockableMainUI, dockable=True)

if __name__ == "__main__":

    show_guide_component_manager()