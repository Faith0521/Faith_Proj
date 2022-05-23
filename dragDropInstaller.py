import os,sys,shutil,re,datetime

try:
    from maya.app.startup import basic
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
    import maya.OpenMayaUI as OpenMayaUI
    import maya.cmds as cmds
    import maya.api.OpenMaya as om
    is_maya = True

except ImportError():
    is_maya = False

TITLE = "Install Faith"
VERSION = 0.0.1
FAITH_MOD_PATH = "FAITH_MODULE_PATH"
MAYA_MOD_PATH = "MAYA_MODULE_PATH"

