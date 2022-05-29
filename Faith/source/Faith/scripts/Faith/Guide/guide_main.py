import os,sys,traceback
from functools import partial

import pymel.core as pm

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from Faith.Core.Qt import QtCore, QtWidgets, QtGui
from Faith import Guide
from Faith.Guide import rig_manager
from Faith.Guide import guide_main_ui as mui
from Faith.Core import aboutUI
import importlib

PY2 = sys.version_info[0] == 2

class MainGuideUI(QtWidgets.QDialog, mui.Ui_Form):

    def __init__(self, parent=None):
        super(MainGuideUI, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setupUi(self)
        self.component_listView.setAcceptDrops(False)
        self.component_listView.setDragEnabled(True)
        self.component_listView.setDropIndicatorShown(False)
        self.installEventFilter(self)

    def keyPressEvent(self, event):
        if not event.key() == QtCore.Qt.Key_Escape:
            super(MainGuideUI, self).keyPressEvent(event)


class DockableMainUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        self.uiName = "ComponentManager"
        super(DockableMainUI, self).__init__(parent=parent)

        self.mainUI = MainGuideUI()
        self.mainUI.component_listView.setAction(self.drag_component)
        self.mainUI.component_listView.installEventFilter(self)

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
        self.setWindowTitle("Faith Module Rigging")
        self.resize(280, 600)

    def create_layout(self):

        self.gmc_layout = QtWidgets.QVBoxLayout()
        self.gmc_layout.addWidget(self.mainUI)
        self.gmc_layout.setContentsMargins(3, 3, 3, 3)

        self.setLayout(self.gmc_layout)

    def create_connections(self):
        self.mainUI.options_btn.clicked.connect(
            rig_manager.initial_settings
            )

    def refreshList(self):
        pass

    def drag_component(self, pGuide):
        if pGuide:
            if pGuide and isinstance(pGuide, list):
                pGuide = pGuide[0]
            parent = pm.PyNode(pGuide)
            self.draw_guide(parent)
        else:
            pm.displayWarning("Object is not a valid guide module.")

    def draw_guide(self, parent = None):
        for x in self.mainUI.component_listView.selectedIndexes():
            rig_manager.draw_comp(x.data(), parent)

def show_guide_component_manager(*args):
    aboutUI.showDialog(DockableMainUI, dockable=True)

if __name__ == "__main__":

    show_guide_component_manager()






































