# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-18 20:48:28
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-18 20:48:49

from functools import partial

from importlib import reload

from maya import cmds as mc
from pymel import core as pm
# import module

class guideBase(object):
    def __init__(self, userGuideName):

        self.guideModuleName = "TYPE"
        self.name = "NAME"
        self.description = "DESCRIPTION"
        self.userGuideName = userGuideName
        self.rigType = "TYPE"
        self.root = ""

    def addRoot(self):
        self.root = mc.joint(n = self.root)














