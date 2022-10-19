# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-15 18:33:10
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-15 18:40:33

from importlib import reload
from functools import partial
from maya import cmds as mc
from pymel import core as pm

from Faith.modules import library
reload(library)

TYPE = "control"
NAME = "control"
GUIDE_POSITION = {
    "root": [0.0, 0.0, 0.0]
}
DESCRIPTION = "Simple controler with space switch and Rot order selection. \n"

class guide(library.guideBase):
    def __init__(self, userGuideName):
       self.guideModuleName = TYPE
       self.name = NAME
       self.description = DESCRIPTION
       self.userGuideName = userGuideName
       self.rigType = TYPE

    def createGuide(self):
        self.guideNamespace = self.guideModuleName + "__" + self.userGuideName

        mc.namespace(setNamespace=":")
        self.namespaceExists = mc.namespace(exists=self.guideNamespace)

        self.guideName = self.guideNamespace + ":"
        self.root = self.guideName + "Base"

        if not self.namespaceExists:
            mc.namespace(add=self.guideNamespace)
        self.addRoot()
