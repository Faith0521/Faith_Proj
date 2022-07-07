# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-07-07 11:26
# Description:
from imp import reload
import subprocess, xml.etree.ElementTree, time, maya.cmds as cmds, maya.mel as mel, webbrowser as web, Faith.Tools.Skinning.hsNode as hsN
reload(hsN)
from Faith.Tools.Skinning.hsNode import *
from uuid import getnode
import shutil
if int(str(cmds.about(v=1))[0:4]) < 2022:
    from maya.OpenMaya import *
    import maya.OpenMaya as om
else:
    from maya.api.OpenMaya import *
    import maya.api.OpenMaya as om
import sys, os, math, re, pprint, socket
from maya.cmds import *
from maya.mel import *
import datetime as dt, maya.cmds as mc, random as rand, pymel.core as pm
from pymel.all import *
from pymel.core import *

class Skin(object):

    def __init__(self):
        pass

    def findSkinMesh(self, skinMesh=None):
        """

        :param skinMesh:
        :return:
        """
        if not skinMesh:
            if selected():
                skinMesh = selected()[0]
            else:
                self.confirmAction("Skinned Mesh needs to be provided.")
        else:
            skinMesh = skinMesh

        asSkinMesh = hsNode(skinMesh)
        skinClust = listHistory(skinMesh, type = "skinCluster")
        if not skinClust:
            self.error("{0} is not a skinned mesh.".format(skinMesh))
        reObj = re.compile(asSkinMesh.shortName() + '_\\d+_SC')
        if self.extractNum(skinClust[0]) and reObj.match(str(skinClust[0])):
            pass
        else:
            if mc.objExists("Skin_Grp"):
                ahssGrp = hsNode('Skin_Grp')
                numGrps = ahssGrp.numChildren()
            else:
                numGrps = 0
            skinClustName = asSkinMesh.shortName() + '_' + '%d' % (numGrps + 1) + '_SC'
            if not objExists(skinClustName):
                rename(skinClust[0], skinClustName)
            else:
                for num in range(numGrps, 200):
                    try:
                        select(asSkinMesh.shortName() + '_' + '%d' % num + '_SC', r=1)
                    except:
                        rename(skinClust[0], asSkinMesh.shortName() + '_' + '%d' % num + '_SC')
                        break
        skinClust = listHistory(skinMesh, type = "skinCluster")
        return [skinMesh, skinClust[0]]

    def confirmAction(self, action, raiseErr=False, trueVal="Yes", falseVal="No",
                      ex1Btn=None, ex1Action=None, **shortArgs):
        """

        :param action:
        :param trueVal:
        :param falseVal:
        :param ex1Btn:
        :param ex1Action:
        :param shortArgs:
        :return:
        """
        if shortArgs:
            action = shortArgs['a'] if 'a' in shortArgs else action
            raiseErr = shortArgs['e'] if 'e' in shortArgs else raiseErr
            trueVal = shortArgs['tv'] if 'tv' in shortArgs else trueVal
            falseVal = shortArgs['fv'] if 'fv' in shortArgs else falseVal
            ex1Btn = shortArgs['eb1'] if 'eb1' in shortArgs else ex1Btn
            ex1Action = shortArgs['ea1'] if 'ea1' in shortArgs else ex1Action
        if raiseErr:
            confirmDialog(title='Warning..', bgc=(0.5, 0.5, 0.5), message=action, button=[trueVal], defaultButton=trueVal)
            raise RuntimeError(action)
        if not ex1Btn:
            confirm = confirmDialog(title='Confirm Action', message=action, button=[trueVal, falseVal],
                                    defaultButton=trueVal, cancelButton=falseVal, dismissString=falseVal)
        else:
            confirm = confirmDialog(title='Confirm Action', message=action, button=[trueVal, falseVal, ex1Btn],
                                    defaultButton=trueVal, cancelButton=falseVal, dismissString=falseVal)
        if confirm == trueVal:
            return True
        else:
            if confirm == falseVal:
                return False
            if confirm == ex1Btn:
                if ex1Btn:
                    ex1Action()
                    return ex1Btn
                else:
                    return

            return

    def extractNum(self, objName, fromEnd=True, skipCount=0):
        """

        :param objName:
        :param fromEnd:
        :param skipCount:
        :return:
        """
        objName = str(objName)
        numList = re.findall('\\d+', objName)
        if numList:
            if fromEnd:
                numStr = numList[(-1 * (skipCount + 1))]
                num = int(numStr)
                return [num, str(num)]
            else:
                numStr = numList[skipCount]
                num = int(numStr)
                return [num, str(num)]

        else:
            return
        return

    def error(self, errorMsg):
        """

        :param errorMsg:
        :return:
        """
        confirmDialog(title='Error..', bgc=(1, 0.5, 0), message=errorMsg, button=['Yes'], defaultButton='Yes')
        raise RuntimeError(errorMsg)

    def createSkinPlane(self, L_Prfx="L_",
                        R_Prfx="R_",
                        skinSide="LT",
                        extractGCMs=False,
                        noDiscSkin=True):
        __showProgressTime = 0
        __displayTotalTime = 0
        __freeVersion = 0
        blendVal = 0.0
        refCount = 1

        prefixOrSuffix = 'Prefix'
        usingJntAxis = False
        excludeJntName = 'Fan'
        jntsGiven = False
        allJntList = []

        if selected():
            selObj = hsNode(selected()[0])
            if selObj.isSkinMesh():
                self.text = selObj
            elif selObj.isJnt():
                jntsGiven = True
                jnt_List = [hsNode(jnt) for jnt in selected()]
                jntList = [jnt for jnt in jnt_List if jnt.nodeType() == 'joint']
                allJntList = [jnt for jnt in jntList]
            else:
                self.error("Selected is not a mesh or skined mesh.")

        if not noDiscSkin:
            if not objExists("Skin_GCM_Shd"):
                GCMShader = shadingNode("lambert", asShader=1, n='Skin_GCM_Shd')
                setAttr(GCMShader + '.color', 0.0, 0.5, 0.8, type="double3")
            else:
                GCMShader = "Skin_GCM_Shd"

        skinMesh, skinClust = self.findSkinMesh()
        existedGCMs = None

        select(cl = True)
        if not jntsGiven:
            jnt_List = [hsNode(jnt) for jnt in skinCluster(skinClust, inf=1, q=1)]
            jntList = [jnt for jnt in jnt_List if jnt.nodeType() == 'joint']
            allJntList = [jnt for jnt in jntList]
            # print(allJntList)
        skinMesh.select()
        latList = lattice(divisions=(2, 5, 2), ldv=(2, 2, 2), objectCentered=True)
        asLat = hsNode(latList[1])
        asLatShp = latList[0]
        ffdNode = asLat.getOutputs('ffd')
        if ffdNode:
            mc.setAttr(ffdNode + '.envelope', 0)
        asLat.hide()
        asLat.scaleBy([1.1, 1.1, 1.1])
        asLat.show()
        reduceList = []
        AllJntListRemove = allJntList.remove
        JntListRemove = jntList.remove
        ReduceListAppend = reduceList.append

        for jnt in allJntList:
            splitLocList = jnt.jntSplit(4, nameSufx='_PosLoc', getPos=1, getEnds=1)
            containsLoc = False
            for splitLoc in splitLocList:
                if not containsLoc:
                    if asLat.contains(splitLoc):
                        containsLoc = True
            if not containsLoc:
                ReduceListAppend(jnt)

        if reduceList:
            if len(reduceList) > 5:
                if self.confirmAction(('No Of Unwanted Skinned Joints Are More Than {}\nIgnore Unwanted Joints?').format(len(reduceList))):
                    for jnt in reduceList:
                        AllJntListRemove(jnt)
                        JntListRemove(jnt)











































