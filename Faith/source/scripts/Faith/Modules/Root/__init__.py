# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:09
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-14 19:56:54

""" Root Control Rig Class """
from Faith.Guide import Component

from Faith.Core import aboutAttribute, aboutTransform, aboutAdd

###############################################################
###############################################################

class Rigging(Component.Rigging):
    
    @property
    def addObjects(self):
        
        if self.settings["NeutralRotation"]:
            t = aboutTransform.getTransformFromPos(self.guide.posDict["root"])
        else:
            t = self.guide.traDict["root"]
            if self.settings["mirrorBehavior"] and self.negate:
                scale = [1, 1, -1]
            else:
                scale = [1, 1, 1]
            t = aboutTransform.setMatrixScale(t, scale)
        
        self.ik_cons = aboutAdd.addTransform(
            self.root, self.getName("ik_cons"), t
        )

        self.ctrl = self.addCtrl(
            parent=self.ik_cons, name="ctrl", m=t,
            iconType="IK", tp=self.parentCtlTag,
            w = self.settings["ctrlSize"] * self.size * 10,
            h = self.settings["ctrlSize"] * self.size * 10,
            d = self.settings["ctrlSize"] * self.size * 10
        )

        if self.settings["k_ro"]:
            rotOderList = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
            aboutAttribute.setRotOrder(
                self.ctrl, rotOderList[self.settings["rotOrder"]]
            )

        params = [s for s in 
                 ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]
                 if self.settings["k_" + s]]
        aboutAttribute.setKeyableAttributes(self.ctrl, params)

        if self.settings["joint"]:
            self.jnt_pos.append(
                [self.ctrl, self.name, None, self.settings["unitSca"]]
            )

    @property
    def setRelation(self):
        """

        :return:
        """
        self.relatives["root"] = self.ctrl
        self.controlRelatives["root"] = self.ctrl
        if self.settings["joint"]:
            self.jointRelatives["root"] = 0

        self.aliasRelatives["root"] = "ctrl"

    @property
    def addParams(self):
        return

    @property
    def addOperators(self):
        return
    
    @property
    def addConnections(self):
        self.connections["standard"] = self.connect_standard
        self.connections["orientation"] = self.connect_orientation
    
    def connect_orientation(self):
        self.connect_orientCns

















