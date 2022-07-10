# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-07-06 21:53:24
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-08 19:55:28

import pymel.core as pm,maya.cmds as mc,maya.mel as mel
import json,time,re
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as aom

class SkinNode(object):

    def _MDagPath(self, obj, mObj=None):
        activList = om.MSelectionList()
        pathDg = om.MDagPath()
        if mObj:
            pathDg = pathDg.getAPathTo(mObj)
        activList.add(obj.nodeName())
        pathDg = activList.getDagPath(0)
        return pathDg

    def _MFnDagNode(self, obj, mobj=None, toShapeNode=False):
        dgPath = self._MDagPath(obj,mobj)
        return om.MFnDagNode(dgPath)

    def getChildren(self, object, type, childImplied=True, **kwargs):
        allChildren = mc.listRelatives(str(object), c = True, pa = True, **kwargs)
        if childImplied:
            impliedChild = object.getChildren()
            if impliedChild:
                if not allChildren:
                    allChildren = []




