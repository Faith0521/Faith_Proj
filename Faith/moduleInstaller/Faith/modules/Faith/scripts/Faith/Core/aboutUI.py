# -*- coding: utf-8 -*-
# @Author: 46314
# @Date:   2022-09-01 18:58:18
# @Last Modified by:   46314
# @Last Modified time: 2022-09-06 21:20:57
"""mgear qt functions"""
import os,traceback
import maya.OpenMayaUI as omui,pymel.core as pm,maya.cmds as cmds
from dayu_widgets import dayu_theme
from collections import OrderedDict
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
    dayu_theme.apply(windw)
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


def convertMayaUIToQt(uiName):
    """

    :param uiName:
    :return:
    """
    getcontrol = omui.MQtUtil.findControl(uiName)
    if PY2:
        getobjPyside = QtCompat.wrapInstance(long(getcontrol), QtWidgets.QWidget)
    else:
        getobjPyside = QtCompat.wrapInstance(int(getcontrol), QtWidgets.QWidget)
    return getobjPyside


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


class CollapsibleHeader(QtWidgets.QWidget):
    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")

    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super(CollapsibleHeader, self).__init__(parent)

        self.setAutoFillBackground(True)
        self.set_background_color(None)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.COLLAPSED_PIXMAP.width())

        self.text_label = QtWidgets.QLabel()
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)

        self.set_text(text)
        self.set_expanded(False)

    def set_text(self, text):
        self.text_label.setText(u"<b>{0}</b>".format(text))

    def set_background_color(self, color):
        if not color:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded):
        self._expanded = expanded

        if (self._expanded):
            self.icon_label.setPixmap(self.EXPANDED_PIXMAP)
        else:
            self.icon_label.setPixmap(self.COLLAPSED_PIXMAP)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()  # pylint: disable=E1101


class CollapsibleWidget(QtWidgets.QWidget):

    def __init__(self, text, parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)  # pylint: disable=E1101

        self.body_wdg = QtWidgets.QWidget()

        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.header_wdg)
        self.main_layout.addWidget(self.body_wdg)

        self.set_expanded(False)

    def add_widget(self, widget):
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        self.body_layout.addLayout(layout)

    def set_expanded(self, expanded):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)

    def set_header_background_color(self, color):
        self.header_wdg.set_background_color(color)

    def on_header_clicked(self):
        self.set_expanded(not self.header_wdg.is_expanded())


class RampPoint(object):
    class InterpType(object):
        None_ = 0
        Linear = 1
        Smooth = 2
        Spline = 3

        @classmethod
        def asDict(cls):
            return OrderedDict((("None", cls.None_),
                                ("Linear", cls.Linear),
                                ("Smooth", cls.Smooth),
                                ("Spline", cls.Spline)))

    def __init__(self, val, pos, interp):
        self.pos = float(pos)
        self.value = float(val)
        self.interp = int(interp)

    def asString(self):
        return ",".join([str(each) for each in (self.value, self.pos, self.interp)])


def createCollapsibleWidget(addWidget=None, expanded=False, text=""):
    """

    :param expanded:
    :return:
    """
    collapsible_wdg = CollapsibleWidget(text)
    collapsible_wdg.set_expanded(expanded)
    if not addWidget:
        return collapsible_wdg
    collapsible_wdg.add_widget(addWidget)
    return collapsible_wdg


def createMayaCurveEditer(interType = "Smooth",getValue=None):
    """

    :param interType:
    :return:
    """
    if cmds.window('MyCrvEditorWindow', ex=True):
        cmds.deleteUI('MyCrvEditor')
        cmds.deleteUI('MyCrvEditorWindow')
    cmds.window('MyCrvEditorWindow')
    cmds.columnLayout()
    cmds.gradientControlNoAttr('MyCrvEditor')

    cmds.optionVar(rm='falloffCurveOptionVar')
    cmds.optionVar(stringValueAppend=['falloffCurveOptionVar', '0,1,2'])
    cmds.optionVar(stringValueAppend=['falloffCurveOptionVar', '1,0,2'])
    cmds.gradientControlNoAttr('MyCrvEditor', e=True, optionVar='falloffCurveOptionVar')

    rampPoints, strVals = createCrvEditerInterType(interType=interType)

    cmds.gradientControlNoAttr('MyCrvEditor', e=True, asString=strVals)

    if getValue:
        value = cmds.gradientControlNoAttr('MyCrvEditor', q=True, valueAtPoint=getValue)
        cmds.deleteUI('MyCrvEditor')
        return value

    getobjPyside = convertMayaUIToQt('MyCrvEditor')
    return getobjPyside

def createCrvEditerInterType(interType = "Smooth"):
    """

    :param interType:
    :return:
    """
    if interType == "None":
        rampPoints = (RampPoint(0, 0, RampPoint.InterpType.None_), RampPoint(1, 1, RampPoint.InterpType.None_))
    if interType == "Linear":
        rampPoints = (RampPoint(0, 0, RampPoint.InterpType.Linear), RampPoint(1, 1, RampPoint.InterpType.Linear))
    if interType == "Smooth":
        rampPoints = (RampPoint(0, 0, RampPoint.InterpType.Smooth), RampPoint(1, 1, RampPoint.InterpType.Smooth))
    if interType == "Spline":
        rampPoints = (RampPoint(0, 0, RampPoint.InterpType.Spline), RampPoint(1, 1, RampPoint.InterpType.Spline))

    strVals = ",".join([each.asString() for each in rampPoints])
    return [rampPoints, strVals]


































