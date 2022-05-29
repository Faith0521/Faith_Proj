# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-27 08:55:58
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-28 17:27:40

"""Guide base root module"""

from functools import partial
import pymel.core as pm
import Faith
from Faith.Guide.Component import guide
from Faith.Core import aboutTransform, aboutAttribute

# ui import
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget


# guide info
AUTHOR = "Yin Yu Fei(Copyright by mgear)"
EMAIL = "463146085@qq.com"
VERSION = [0, 0, 1]
TYPE = "Root"
NAME = "Root"
DESCRIPTION = "Simple controler with space switch and Rot order selection. \n"

##########################################################
# CLASS
##########################################################


class Guide(guide.ComponentGuide):
    """Component Guide Class"""

    GUIDETYPE = TYPE
    GUIDENAME = NAME
    DESCRIPTION = DESCRIPTION

    author = AUTHOR
    email = EMAIL
    version = VERSION

    CONNECTORS = ["orientation"]

    def postInit(self):
        self.save_transform = ["root" , "sizeReset"]

    # 向对象定义列表中添加对象
    def addObjects(self):
        self.root = self.addRoot
        vTemp = aboutTransform.getOffsetPosition(self.root, [0, 0, 1])
        self.sizeRef = self.addLoc("sizeReset" , self.root, vTemp)
        pm.delete(self.sizeRef.getShapes())
        aboutAttribute.lockAttribute(self.sizeRef)

    def addAttributes(self):
        self.icon = self.addAttr("icon" , "string" , "COG")
        # self.ikRefArray = self.addAttr("ikRefArray" , "string" , "")
        self.joint = self.addAttr("joint" , "bool" , False)
        self.leafJoint = self.addAttr("leafJoint" , "bool" , False)
        self.joint = self.addAttr("unitSca", "bool", False)

        for s in ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]:
            self.addAttr("k_" + s, "bool", True)

        self.rotOrder = self.addAttr("rotOrder" , "long" , 0 , 0 , 5)
        self.NeutralRotation = self.addAttr("NeutralRotation" , "bool" , True)
        self.mirrorBehavior = self.addAttr("mirrorBehavior" , "bool" , False)
        self.ctrlSize = self.addAttr("ctrlSize" , "double" , 1 , None , None)
        self.UseIndex = self.addAttr("useIndex", "bool", False)
        self.ParentJointIndex = self.addAttr(
            "parentJointIndex", "long", -1, None, None)

        return

    def postDraw(self):
        """

        Returns:

        """
        size = pm.xform(self.root , q = True , ws = True , scale = True)[0]
        self.add_ref_Axis(self.root,
                          self.root.NeutralRotation,
                          invert = True,
                          w = 0.5/ size)
        self.add_ref_joint(self.root,
                           [self.root.leafJoint, self.root.joint],
                           width = 0.1 / size)

class GuideSettings(object):
    """docstring for GuideSettings"""
    def __init__(self, arg):
        super(GuideSettings, self).__init__()
        self.arg = arg
        

































