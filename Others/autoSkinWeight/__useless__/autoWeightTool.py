import sys,re
import maya.cmds as mc
import maya.OpenMayaUI as OpenMayaUI
import shiboken2
import autoSkinWeight_ui
from PySide2 import QtCore, QtGui, QtWidgets

def get_maya_window():
    '''
    return maya window by Qt object..
    '''
    maya_window = OpenMayaUI.MQtUtil.mainWindow()
    if maya_window:
        return shiboken2.wrapInstance(long(maya_window), QtWidgets.QMainWindow)
        
class autoWeightTool(QtWidgets.QMainWindow):
    
    def __init__( self, parent=get_maya_window() ):
        
        super(autoWeightTool, self).__init__(parent)
        # UI size init
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        # load UI
        self.ui = autoSkinWeight_ui.Ui_autoSkinWeight_Window()
        self.ui.setupUi(self)
 
        self.ui.geometryVtx_pushButton.clicked.connect(self.test)

    def test(self):
        testVal = 'fuck'
        self.ui.geometryVtx_lineEdit.setText(testVal) 
        
        
win=autoWeightTool()
win.show()


# &"C:\Program Files\Autodesk\Maya2018\bin\mayapy.exe" "C:\Program Files\Autodesk\Maya2018\bin\pyside2-uic" -o .\autoSkinWeight_ui.py .\autoSkinWeight.ui