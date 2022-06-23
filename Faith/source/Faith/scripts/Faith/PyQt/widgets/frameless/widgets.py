# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-06-23 15:33
# Description:

from PySide2 import QtCore, QtWidgets, QtGui
from Faith.PyQt.widgets import layouts

MODIFIER = QtCore.Qt.AltModifier

class TitleBar(QtWidgets.QWidget):
    doubleClicked = QtCore.Signal()
    moving = QtCore.Signal(object, object)

    class TitleStyle:
        Default = "DEFAULT"
        Thin = "THIN"

    def __init__(self, parent=None, showTitle=True, alwaysShowAll=False):
        """
        Title bar of the frameless window.
        Click drag this widget to move the window widget
        :param parent:
        :param showTitle:
        :param alwaysShowAll:
        """
        super(TitleBar, self).__init__(parent = parent)

        self.titleBarHeight = 40
        self.pressedAt = None
        self.leftContents = QtWidgets.QFrame(self)
        self._mainLayout = layouts.hBoxLayout()

































