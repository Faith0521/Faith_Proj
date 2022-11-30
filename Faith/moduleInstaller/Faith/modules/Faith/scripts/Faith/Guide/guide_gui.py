from Faith.Guide import guide_main
from Faith.Core import aboutUI
from Faith.Core.Qt import QtCore, QtWidgets, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

class GuideManager(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent = None):
        self.uiName = "GuideManager"
        super(GuideManager, self).__init__(parent=parent)

        self.guide_ui = guide_main.DockableMainUI()
        self.installEventFilter(self)
        self.create_window()
        self.create_layout()

    def keyPressEvent(self, event):
        if not event.key() == QtCore.Qt.Key_Escape:
            super(GuideManager, self).keyPressEvent(event)

    def create_window(self):
        self.setObjectName(self.uiName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Faith Module Manager")
        self.resize(340, 527)

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName("manager_tab")
        self.tabs.insertTab(0, self.guide_ui, "ModuleLib")

        self.main_layout.addWidget(self.tabs)
        self.setLayout(self.main_layout)

def show_ui(*args):
    aboutUI.showDialog(GuideManager, dockable=True)
















