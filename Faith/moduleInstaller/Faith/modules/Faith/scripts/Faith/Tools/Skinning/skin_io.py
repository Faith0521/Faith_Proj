# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-07-07 19:01:29
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-08 19:55:29
import subprocess, xml.etree.ElementTree, time, maya.cmds as cmds, maya.mel as mel, webbrowser as web, Faith.Core.aboutNode as asN
import json,re,shutil
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as aom
from Faith.Core.aboutNode import *
from uuid import getnode
from maya.cmds import *
from maya.mel import *
from pymel.all import *
from pymel.core import *


class Skin(object):

    def __init__(self):
        mc.softSelect(e=1, softSelectEnabled=0)
        if mc.currentUnit(q=1, linear=1) != 'centimeter':
            mc.currentUnit(linear='centimeter')

    def createSplitPlane(self,
                         skinMesh,
                         L_Prfx = 'L_',
                         R_Prfx = 'R_',
                         skinSide = 'LT'):
        __showProgressTime = 0
        __displayTotalTime = 0
        __freeVersion = 0
        blendVal = 0.0
        refCount = 1
        prefixOrSuffix = 'Prefix'
        usingJntAxis = False
        extractGCMs = False
        noDiscSkin = True
        excludeJntName = 'Fan'
        jntsGiven = False
        allJntList = []
        self.skinMesh = skinMesh

        if selected():
            selObj = asNode(selected()[0])
            if selObj.isSkinMesh:
                self.skinMesh = selObj.strip()
            elif selObj.isJoint:
                jntsGiven = True
                jnt_List = [asNode(jnt) for jnt in selected()]
                jntList = [jnt for jnt in jnt_List if jnt.nodeType() == 'joint']
                allJntList = [jnt for jnt in jntList]
            else:
                self.error('Selected Is Not A Mesh | Skinned Mesh..!\nYou need to provide Skin_Mesh')
                



















