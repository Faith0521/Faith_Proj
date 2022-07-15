# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-07-07 19:01:29
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-08 19:55:29
import pymel.core as pm,maya.cmds as mc,maya.mel as mel
import json,time,re
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as aom
from Faith.Tools.Skinning import skin_core

class Skin(skin_core.SkinNode):

    def __init__(self):
        pass

    def extractNum(self, objName, fromEnd=True, skipCount=0):
        objName = str(objName)
        numList = re.findall('\\d+', objName)
        if numList:
            if fromEnd:
                numStr = numList[(-1 * (skipCount + 1))]
                num = int(numStr)
                return [
                    num, str(num)]
            else:
                numStr = numList[skipCount]
                num = int(numStr)
                return [num, str(num)]

        else:
            return

    def createSplitPlane(self, skinMesh):
        skinClust = skinMesh.history(type = "skinCluster")
        if not skinClust:
            pm.error("Mesh is not a skinned mesh.")

        skinNode = skinClust[0]
        jnt_list = [jnt for jnt in pm.skinCluster(skinNode, inf = 1, q = 1)]

        # if not pm.objExists('Skin_Grp'):
        #     skinGrp = pm.group(em = True, n = "Skin_Grp") if 1 else pm.PyNode("Skin_Grp")
        #     skinClusNum = self.extractNum(skinNode)[1]
        #     MeshGrpName = str(skinMesh) + "_MeshGrp"
        #
        #     if not pm.objExists(MeshGrpName):
        #         MeshGrp = pm.group(em = True, n = MeshGrpName, p = skinGrp) if 1 else pm.PyNode(MeshGrpName)
        #
        for jnt in jnt_list:
            chdJnt = jnt.getChildren(type="joint")
            if chdJnt:
                chdJnt = chdJnt[0]
                



















