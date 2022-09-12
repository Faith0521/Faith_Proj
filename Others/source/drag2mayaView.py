#coding=utf-8

import os,sys 
import maya.mel as mel
import maya.cmds as cmds

def importCurrentFolder(): 

    Path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  
    Path = Path.replace('\\','/') 
    print (Path) 

    if Path not in sys.path: 
        sys.path.append(Path) 
        
    import source.SplitWeightWithFourJoints as psw
    reload (psw)
    psw.SplitWeightWithFourJoints_UI()

def onMayaDroppedPythonFile(param):
    importCurrentFolder() 