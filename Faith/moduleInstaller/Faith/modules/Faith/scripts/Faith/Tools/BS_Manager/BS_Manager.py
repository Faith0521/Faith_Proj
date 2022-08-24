import sys
from functools import partial

import pymel.core as pm,maya.mel as mel

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
from Faith.Tools.BS_Manager.UI import BS_List as listui
from Faith.Tools.BS_Manager.UI import widget_item as itemui
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
        pass

    def create_connections(self):
        self.listUI.load_btn.clicked.connect(self.refresh)

    def refresh(self):
        """

        :return:
        """

        for i in range(5):
            # self.listItemUI.connect_btn.setText(str(i))
            self.listItemUI = BS_itemUI()
            myQListWidgetItem = QtWidgets.QListWidgetItem(self.listUI.target_list)
            myQListWidgetItem.setSizeHint(self.listItemUI.sizeHint())
            self.listUI.target_list.addItem(myQListWidgetItem)
            self.listUI.target_list.setItemWidget(myQListWidgetItem, self.listItemUI)
        # for i in range(8):
        # widget = QtWidgets.QWidget()
        # main_lay = QtWidgets.QHBoxLayout(widget)
        # btn = QtWidgets.QPushButton("aaaa")
        # main_lay.addWidget(btn)
        # self.listUI.target_list.setItemWidget(item, widget)

def show(*args):
    aboutUI.showDialog(BS_Manager, dockable=True)

























