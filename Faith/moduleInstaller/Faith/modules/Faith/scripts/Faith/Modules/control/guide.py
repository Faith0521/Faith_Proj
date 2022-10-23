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

CLASS = "control"
NAME = "control"
GUIDE_POSITION = {
    "root": [0.0, 0.0, 0.0]
}
DESCRIPTION = "Simple controler with space switch and Rot order selection. \n"

class guide(library.guideBase):

    def __init__(self, *args, **kwargs):
        kwargs["CLASS"] = CLASS
        kwargs["NAME"] = NAME
        kwargs["DESCRIPTION"] = DESCRIPTION
        library.guideBase.__init__(self, *args, **kwargs)

    def createGuide(self):
        self.root = self.addRoot()

        mc.select(d = True)
        self.jointList = []
        for joint,pos in GUIDE_POSITION.items():
            jnt = mc.joint(n = self.guideName + joint)
            mc.xform(jnt, t=pos, ws = True)
            self.jointList.append(jnt)

        mc.parent(self.jointList, self.root)

    def addPrivateAttrs(self):
        """

        :return:
        """
        # self.joints_num = self.addAttr("joint_num", "double", 1)
        self.primary = self.addAttr("primary_axis", "string", "+x")
        self.secondary = self.addAttr("secondary_axis", "string", "+y")

    def rigModule(self, *args):
        """

        :return:
        """
        print("rigging.................")