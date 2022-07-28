# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-27 21:08:00
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-28 00:39:55
"""mgear qt functions"""
import os,traceback
import maya.OpenMayaUI as omui,pymel.core as pm


from .Qt import QtCore, QtWidgets, QtGui, QtCompat, QtSvg
from pymel import versions
from .aboutPy import PY2

def maya_main_window():
    """Get Maya's main window

    Returns:
        QMainWindow: main window.

    """

    main_window_ptr = omui.MQtUtil.mainWindow()
    if PY2:
        return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return QtCompat.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def showDialog(dialog, dInst=True, dockable=False, *args):
    """
    Show the defined dialog window

    Attributes:
        dialog (QDialog): The window to show.

    """
    if dInst:
        try:
            for c in maya_main_window().children():
                if isinstance(c, dialog):
                    c.deleteLater()
        except Exception:
            pass

    # Create minimal dialog object
    windw = dialog()

    # ensure clean workspace name
    if hasattr(windw, "uiName") and dockable:
        control = windw.uiName + "WorkspaceControl"
        if pm.workspaceControl(control, q=True, exists=True):
            pm.workspaceControl(control, e=True, close=True)
            pm.deleteUI(control, control=True)
    desktop = QtWidgets.QApplication.desktop()
    screen = desktop.screen()
    screen_center = screen.rect().center()
    windw_center = windw.rect().center()
    windw.move(screen_center - windw_center)

    # Delete the UI if errors occur to avoid causing winEvent
    # and event errors (in Maya 2014)
    try:
        if dockable:
            windw.show(dockable=True)
        else:
            windw.show()
        return windw
    except Exception:
        windw.deleteLater()
        traceback.print_exc()

class DragQListView(QtWidgets.QListView):
    
    def __init__(self, parent):
        super(DragQListView, self).__init__(parent)

        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(True)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.exp = 3
        self.ignore_self = True

    def mouseMoveEvent(self, event):
        mimeData = QtCore.QMimeData()
        mimeData.setText("%d,%d" % (event.x(), event.y()))

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos())
        dropAction = drag.start(QtCore.Qt.MoveAction)
        if not dropAction == QtCore.Qt.MoveAction:
            pos = QtGui.QCursor.pos()
            widget = QtWidgets.QApplication.widgetAt(pos)
            if self.ignore_self and (
                widget is self or widget.objectName() == "qt_scrollarea_viewport"):
                return

            relpos = widget.mapFromGlobal(pos)
            invY = widget.frameSize().height() - relpos.y()
            # sel = selectFromScreenApi(relpos.x() - self.exp,
            #                           invY - self.exp,
            #                           relpos.x() + self.exp,
            #                           invY + self.exp)
            #
            # self.doAction(sel)

    def setAction(self, action):
        self.theAction = action

    def doAction(self, sel):
        self.theAction(sel)
        





























