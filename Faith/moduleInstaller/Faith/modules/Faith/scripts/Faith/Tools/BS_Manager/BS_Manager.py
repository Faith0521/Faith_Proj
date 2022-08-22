import sys
from functools import partial

import pymel.core as pm,maya.mel as mel

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.Tools.BS_Manager.UI import BS_List as listui
from Faith.Tools.BS_Manager.UI import widget_item as itemui
from Faith.Core import aboutUI
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


class BS_Manager(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        self.uiName = "BS_Manager"
        super(BS_Manager, self).__init__(parent=parent)


def show(*args):
    aboutUI.showDialog(BS_Manager, dockable=True)

























