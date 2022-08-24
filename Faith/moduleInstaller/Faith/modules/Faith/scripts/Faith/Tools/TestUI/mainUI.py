import pymel.core as pm

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from Faith.Core import aboutUI
from PySide2 import QtCore, QtWidgets
from . import UI

class TestUI(QtWidgets.QMainWindow, UI.Ui_MainWindow):

    def __init__(self, parent=None):
        super(TestUI, self).__init__(parent)
        self.setupUi(self)


class TstMain(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        self.uiName = "SDK"
        super(TstMain, self).__init__(parent=parent)
        self.gteUIInst = TestUI()
        self.start_dir = pm.workspace(q=True, rootDirectory=True)

        self.create_window()
        self.create_layout()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.installEventFilter(self)

    def create_window(self):
        self.setObjectName(self.uiName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Test")
        self.resize(300, 330)

    def create_layout(self):
        self.gte_layout = QtWidgets.QVBoxLayout()
        self.gte_layout.addWidget(self.gteUIInst)
        self.setLayout(self.gte_layout)


def show():
    aboutUI.showDialog(TstMain,dockable=True)