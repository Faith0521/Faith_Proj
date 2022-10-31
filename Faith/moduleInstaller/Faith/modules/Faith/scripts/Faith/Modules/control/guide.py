# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-15 18:33:10
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-15 18:40:33

from ctypes import util
from imp import reload
from functools import partial
from maya import cmds as mc
from pymel import core as pm

from Faith.modules import library
from Faith.maya_utils import guide_path_utils as util
reload(util)
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

        self.jntLoc = self.ctrl.cvJntLoc(self.root, r=0.5)

        self.jointGuide1 = mc.joint(name=self.guideName + "_GuideJointEnd", radius=0.5)
        mc.setAttr(self.jointGuide1 + ".template", 1)

        mc.parent([self.jntLoc, self.jointGuide1], self.root)
        mc.parentConstraint(self.jntLoc, self.jointGuide1, maintainOffset=False, name=self.jointGuide1+"_PC")

    def addPrivateAttrs(self):
        """

        :return:
        """
        # self.joints_num = self.addAttr("joint_num", "double", 1)
        self.primary = self.addAttr("primary_axis", "string", "+x")
        self.secondary = self.addAttr("secondary_axis", "string", "+y")
        self.filp = self.addAttr("flip", "bool", 0)

    def rigModule(self, *args):
        """

        :return:
        """
        if mc.objExists(self.root):
            sideList = [""]
            self.mirrorAxis = mc.getAttr("%s.mirror_axis"%self.root)
            if self.mirrorAxis != "off":
                self.mirrorNames = mc.getAttr("%s.mirror_name"%self.root)
                sideList = [ self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_' ]

                for s,side in enumerate(sideList):
                    duplicated = mc.duplicate(self.root, name=side + self.userGuideName + 'Base')[0]
                    allGuideList = mc.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        mc.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = mc.group(name="Guide_Base_Grp", empty=True)
                    mc.parent(side+self.userGuideName+'Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    mc.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        if mc.getAttr(self.root+".flip") == 0:
                            for axis in self.mirrorAxis:
                                gotValue = mc.getAttr(side+self.userGuideName+"Base.translate"+axis)
                                flipedValue = gotValue*(-2)
                                mc.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                        else:
                            for axis in self.mirrorAxis:
                                mc.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else:
                duplicated = mc.duplicate(self.root, name=self.userGuideName+'Base')[0]
                allGuideList = mc.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    mc.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = mc.group(self.userGuideName+'Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                mc.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            
            count = util.findModuleLastNumber(CLASS, "guide_type") + 1
            for s, side in enumerate(sideList):
                self.base = side+self.userGuideName+'Base'
                mc.select(clear=True)
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = mc.joint(name=side+self.userGuideName+"_Jnt", scaleCompensate=False)
                mc.addAttr(self.jnt, longName='rig_joint', attributeType='float', keyable=False)