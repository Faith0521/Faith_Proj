# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-06-23 14:46:53
# @Last Modified by:   yinyufei
# @Last Modified time: 2022-06-23 14:49:20

# from Faith.Core.Qt import QtWidgets, QtCore
from PySide2 import QtWidgets, QtCore

class FaithWindow(QtWidgets.QWidget):
    closed = QtCore.Signal()
    beginClosing = QtCore.Signal()
    minimized = QtCore.Signal()
    # helpUrl = ""

    def __init__(self, name="", title="", parent=None, resizable=True,
                 width=None, height=None, modal=False, alwaysShowAllTitle=False,
                 minButton=False, maxButton=False, onTop=False, saveWindowPref=True,
                 titleBar=None, overlay=True, minimizeEnabled=True, show=True,
                 initPos=None):
        """

        :param name:
        :param title:
        :param parent:
        :param resizable:
        :param width:
        :param height:
        :param modal:
        :param alwaysShowAllTitle:
        :param minButton:
        :param maxButton:
        :param onTop:
        :param saveWindowPref:
        :param titleBar:
        :param overlay:
        :param minimizeEnabled:
        :param show:
        :param initPos:
        """
        self.showOnInit = show
        super(FaithWindow, self).__init__(parent=None)
        self._initPos = initPos
        self._minimized = False
        if titleBar is not None:  # todo: Maybe can do better?
            self.titleBar = titleBar(self, alwaysShowAll=alwaysShowAllTitle)
        else:
            self.titleBar = TitleBar(self, alwaysShowAll=alwaysShowAllTitle)






























