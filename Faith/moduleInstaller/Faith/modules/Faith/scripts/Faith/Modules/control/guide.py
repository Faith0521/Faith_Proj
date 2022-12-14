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
        library.guideBase.__init__(self, *args, **kwargs)\
        
        self.jntList = []
        self.aStaticGrpList = []
        self.aCtrlGrpList = []

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
                    mc.rename(self.mirrorGrp, side+self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        if mc.getAttr(self.root+".flip") == 0:
                            for axis in self.mirrorAxis:
                                gotValue = mc.getAttr(side+self.userGuideName+"Base.translate"+axis)
                                flipedValue = gotValue*(-2)
                                mc.setAttr(side+self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                        else:
                            for axis in self.mirrorAxis:
                                mc.setAttr(side+self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp+'.scale'+axis, -1)

            else:
                duplicated = mc.duplicate(self.root, name=self.userGuideName+'Base')[0]
                allGuideList = mc.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    mc.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = mc.group(self.userGuideName+'Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                mc.rename(self.mirrorGrp, self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp)
            
            count = util.findModuleLastNumber(CLASS, "module_type") + 1
            for s, side in enumerate(sideList):
                self.base = side+self.userGuideName+'Base'
                mc.select(clear=True)
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                # create a joint:
                self.jnt = mc.joint(name=side+self.guideModuleName + "_0" + self.userGuideName[-1]+"_Jnt", scaleCompensate=False)
                mc.addAttr(self.jnt, longName='rig_joint', attributeType='float', keyable=False)

                self.radius = mc.getAttr("%s.shape_size"%self.base)
                self.controlCtrl = self.ctrl.createCtrl("cube", name=side+self.guideModuleName + "_0" + self.userGuideName[-1]+"_Ctrl", r=self.radius*2.0, color="yellow", addAttr=True)
                
                mc.delete(mc.parentConstraint(self.base, self.jnt))
                mc.delete(mc.parentConstraint(self.base, self.controlCtrl))
                
                self.controlGrp = util.zeroGrp([self.controlCtrl])[0]

                mc.setAttr(self.controlCtrl+'.visibility', keyable=False)
                # fixing flip mirror:
                if s == 1:
                    if mc.getAttr(self.root+".flip") == 1:
                        mc.setAttr(self.controlGrp+".scaleX", -1)
                        mc.setAttr(self.controlGrp+".scaleY", -1)
                        mc.setAttr(self.controlGrp+".scaleZ", -1)

                mc.parentConstraint(self.controlCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PC")
                mc.scaleConstraint(self.controlCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_SC")

                self.jntList.append(self.jnt)

                self.toCtrlDataGrp = mc.group(self.controlGrp, name=side+self.guideModuleName + "_0" + self.userGuideName[-1]+"_Control_Grp")
                self.toScalableDataGrp = mc.group(self.jnt, name=side+self.guideModuleName + "_0" + self.userGuideName[-1]+"_Joint_Grp")
                self.toStaticDataGrp   = mc.group(self.toCtrlDataGrp, self.toScalableDataGrp, name=side+self.guideModuleName + "_0" + self.userGuideName[-1]+"_Grp")

                loc = mc.spaceLocator(name=side+self.guideModuleName + "_0" + self.userGuideName[-1]+"_Static_Loc")[0]
                mc.parent(loc, self.toStaticDataGrp, absolute=True)
                mc.setAttr(loc+".visibility", 0)
                self.ctrl.LockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

                util.addData(objName=self.toCtrlDataGrp, dataType='ctrlData')
                util.addData(objName=self.toScalableDataGrp, dataType='scalableData')
                util.addData(objName=self.toStaticDataGrp, dataType='staticData')

                mc.addAttr(self.toStaticDataGrp, longName="guide_name", dataType="string")
                mc.addAttr(self.toStaticDataGrp, longName="module_type", dataType="string")
                mc.setAttr(self.toStaticDataGrp+".guide_name", self.userGuideName, type="string")
                mc.setAttr(self.toStaticDataGrp+".module_type", CLASS, type="string")
                self.aStaticGrpList.append(self.toStaticDataGrp)
                self.aCtrlGrpList.append(self.toCtrlDataGrp)
                # add module type counter value
                mc.addAttr(self.toStaticDataGrp, longName='module_count', attributeType='long', keyable=False)
                mc.setAttr(self.toStaticDataGrp+'.module_count', count)
                # mc.setAttr(self.toScalableHookGrp+".visibility", 0)
                # delete duplicated group for side (mirror):
                mc.delete(side + self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp)

            # finalize this rig:
            self.confirmInfo()
            mc.select(clear=True)

    def confirmInfo(self):
        library.guideBase.confirmInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.guideActionsDic = {
                                    "module": {
                                                "jntList"   : self.jntList,
                                                "staticGrpList" : self.aStaticGrpList,
                                                "ctrlGrpList"   : self.aCtrlGrpList,
                                              }
                                    }