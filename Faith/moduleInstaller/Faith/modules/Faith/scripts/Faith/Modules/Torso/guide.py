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

CLASS = "torso"
NAME = "torso"

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

    def createGuide(self, *args):
        self.root = self.addRoot()
        # print()
        self.jntLoc = self.ctrl.cvJntLoc(self.guideName+"JointLoc1", r=0.5)
        self.cvEndJoint = self.ctrl.cvLocator(self.guideName + "JointEnd", r=0.2)
        mc.parent(self.cvEndJoint, self.jntLoc)
        mc.setAttr(self.cvEndJoint + '.ty', 1.3)
        mc.transformLimits(self.cvEndJoint, ty=(0.01, 1), ety=(True, False))
        self.ctrl.LockHide([self.cvEndJoint], ['tx', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        mc.parent(self.jntLoc, self.root)

        self.changeJointNumber(3)
        mc.select(d = True)

    def changeJointNumber(self, count, *args):

        self.enteredNJoints = count
        if self.enteredNJoints >= 3:
            # get the number of joints existing:
            self.currentNJoints = int(mc.getAttr(self.root+".joint_num"))
            # start analisys the difference between values:
            if self.enteredNJoints != self.currentNJoints:
                self.cvEndJoint = self.guideName+"JointEnd"
                if self.currentNJoints > 1:
                    # delete current point constraints:
                    for n in range(2, self.currentNJoints):
                        mc.delete(self.guideName+"_PC"+str(n))
                # verify if the nJoints is greather or less than the current
                if self.enteredNJoints > self.currentNJoints:
                    # add the new cvLocators:
                    for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                        # create another N cvLocator:
                        self.cvLocator = self.ctrl.cvLocator(self.guideName+"JointLoc"+str(n), r=0.3)
                        # set its nJoint value as n:
                        mc.setAttr(self.cvLocator+".joint_num", n)
                        # parent its group to the first cvJointLocator:
                        self.cvLocGrp = mc.group(self.cvLocator, name=self.cvLocator+"_Grp")
                        mc.parent(self.cvLocGrp, self.guideName+"JointLoc"+str(n-1), relative=True)
                        mc.setAttr(self.cvLocGrp+".translateY", 2)
                        if n > 2:
                            mc.parent(self.cvLocGrp, self.guideName+"JointLoc1", absolute=True)
                elif self.enteredNJoints < self.currentNJoints:
                    # re-parent cvEndJoint:
                    self.cvLocator = self.guideName+"_JointLoc" + str(self.enteredNJoints)
                    mc.parent(self.cvEndJoint, world=True)
                    # delete difference of nJoints:
                    for n in range(self.enteredNJoints, self.currentNJoints):
                        # re-parent the children guides:
                        childrenGuideBellowList = util.getGuideChildrenList(self.guideName+"JointLoc"+str(n+1)+"_Grp")
                        if childrenGuideBellowList:
                            for childGuide in childrenGuideBellowList:
                                mc.parent(childGuide, self.cvLocator)
                        mc.delete(self.guideName+"JointLoc"+str(n+1)+"_Grp")
                # re-parent cvEndJoint:
                mc.parent(self.cvEndJoint, self.cvLocator)
                mc.setAttr(self.cvEndJoint+".ty", 1.3)
                mc.setAttr(self.cvEndJoint+".visibility", 0)
                # re-create parentConstraints:
                if self.enteredNJoints > 1:
                    for n in range(2, self.enteredNJoints):
                        self.parentConst = mc.parentConstraint(self.guideName+"JointLoc1", self.cvEndJoint, self.guideName+"JointLoc"+str(n)+"_Grp", name=self.guideName+"_PC"+str(n), maintainOffset=True)[0]
                        nParentValue = (n-1) / float(self.enteredNJoints-1)
                        mc.setAttr(self.parentConst+".JointLoc1W0", 1-nParentValue)
                        mc.setAttr(self.parentConst+".JointEndW1", nParentValue)
                        self.ctrl.LockHide([self.guideName+"JointLoc"+ str(n)], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                # actualise the nJoints in the moduleGrp:
                mc.setAttr(self.root+".joint_num", self.enteredNJoints)
                self.currentNJoints = self.enteredNJoints
                # re-build the preview mirror:
                # dpLayoutClass.LayoutClass.createPreviewMirror(self)
            mc.select(self.root)
        else:
            self.changeJointNumber(3)

    def addPrivateAttrs(self):
        """

        :return:
        """
        # return
        self.joints_num = self.addAttr("joint_num", "double", 1)
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
            self.up_axis = mc.upAxis(q=True, axis=True)
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

            else:
                duplicated = mc.duplicate(self.root, name=self.userGuideName+'Base')[0]
                allGuideList = mc.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    mc.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = mc.group(self.userGuideName+'Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                mc.rename(self.mirrorGrp, self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp)
            
            count = util.findModuleLastNumber(CLASS, "guide_type") + 1
            for s, side in enumerate(sideList):
                pass
        self.confirmInfo()

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