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
from pymel.core import datatypes
from pymel.core.datatypes import Vector
from Faith.modules import library
from Faith.maya_utils import guide_path_utils as util, rigging_utils
from Faith.maya_utils import rigging_utils as rig
from Faith.maya_utils import transform_utils as transform
reload(util)
reload(transform)
reload(library)
reload(rig)

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
        self.positions = []
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

        self.changeJointNumber(5)
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
            self.changeJointNumber(5)

    def addPrivateAttrs(self):
        """

        :return:
        """
        # return
        self.joints_num = self.addAttr("joint_num", "double", 1)
        self.autoBend = self.addAttr("auto_bend", "double", False)
        self.centralTangent = self.addAttr("central_tangent", "double", False)
        self.axis = self.addAttr("joint_axis", "string", "xy")
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
                t = datatypes.TransformationMatrix()
                prefix = side+self.guideModuleName + "_0" + self.userGuideName[-1]
                
                self.base = side+self.userGuideName+'Base'

                self.jointsNum = int(mc.getAttr(self.base + '.joint_num'))

                self.guide = pm.PyNode(side+self.userGuideName+"_JointLoc1")
                self.cvEndJoint = pm.PyNode(side+self.userGuideName+"_JointLoc" + str(self.jointsNum))

                self.RigGrp = mc.group(name=prefix + "_Grp", empty=True)
                self.ControlGrp = mc.createNode("transform", name=prefix + "_Control_Grp", p=self.RigGrp)
                self.jntGrp = mc.createNode("transform", name=prefix + "_Jnt_Grp", p=self.RigGrp)
                util.addData(objName=self.ControlGrp, dataType='ctrlData')
                util.addData(objName=self.jntGrp, dataType='scalableData')
                util.addData(objName=self.RigGrp, dataType='staticData')
                
                # add rig scale attr
                mc.addAttr(self.ControlGrp, longName="globalScaleX", at="double", dv=1.0)
                mc.addAttr(self.ControlGrp, longName="globalScaleY", at="double", dv=1.0)
                mc.addAttr(self.ControlGrp, longName="globalScaleZ", at="double", dv=1.0)

                # add rigGrp attr
                mc.addAttr(self.RigGrp, longName="guide_name", dataType="string")
                mc.addAttr(self.RigGrp, longName="guide_type", dataType="string")
                mc.setAttr(self.RigGrp+".guide_name", self.userGuideName, type="string")
                mc.setAttr(self.RigGrp+".guide_type", CLASS, type="string")
                # add module type counter value
                mc.addAttr(self.RigGrp, longName='module_count', attributeType='long', keyable=False)
                
                mc.setAttr(self.RigGrp+'.module_count', count)
                
                auto_bend = mc.getAttr(side + self.userGuideName + 'Base.auto_bend')
                centralTangent = mc.getAttr(side + self.userGuideName + 'Base.central_tangent')
                axis = mc.getAttr(side + self.userGuideName + 'Base.joint_axis')

                self.guidePos = self.guide.getTranslation(space="world")
                self.endPos = self.cvEndJoint.getTranslation(space="world")
                if auto_bend:
                    self.autoBendChain = rig.add2DChain(pm.PyNode(self.ControlGrp),
                                                        prefix + "_autoBend%s_jnt",
                                                        [self.guidePos, self.endPos],
                                                        Vector(0, 0, 1),
                                                        axis,
                                                        False,
                                                        True)
                    for j in self.autoBendChain:
                        j.drawStyle.set(2)
                
                pm.select(clear=True)

                self.TempChain = rig.add2DChain(pm.PyNode(self.ControlGrp),
                                                prefix + "_Temp%s_jnt",
                                                [self.guidePos, self.endPos],
                                                Vector(0, 0, 1),
                                                axis,
                                                False,
                                                True)

                self.ik_off = pm.createNode("transform", name=prefix + "_ik_off", p=self.ControlGrp)

                self.radius = pm.getAttr("%s.shape_size"%self.base)
                self.ik0_ctrl = self.ctrl.createCtrl("circle", prefix + "_ik0_ctrl", r=self.radius*2.0,color="yellow", addAttr=True)
                self.ik0_con = pm.PyNode(util.zeroGrp([self.ik0_ctrl], True)[0])
                pm.parent(self.ik0_con, self.ik_off)

                self.hip_lvl = pm.createNode("transform", name=prefix + "_hip_lvl", p=self.ik0_ctrl)

                pm.delete(pm.parentConstraint(self.TempChain[0], self.ik_off))
                self.positions.append(self.TempChain[0].getTranslation(space="world"))
                self.positions.append(self.TempChain[1].getTranslation(space="world"))
                if auto_bend:
                    self.autoBend_con = pm.createNode("transform", name=prefix + "_torsoPosition_con")
                    self.autoBend_ctrl = pm.PyNode(self.ctrl.createCtrl("square", prefix + "_autoBend_ctrl", r=self.radius*4.0,color="yellow", addAttr=True))
                    pm.parent(self.autoBend_ctrl, self.autoBend_con)
                    pm.delete(pm.parentConstraint(self.TempChain[-1], self.autoBend_con))
                    pm.parent(self.autoBend_con, self.ControlGrp)

                    self.ik1_con = pm.createNode("transform", name=prefix + "_ik1_con")
                    self.ik1autoRot = pm.createNode("transform", name=prefix + "_ik1autoRot", p=self.ik1_con)
                    self.ik1_ctl = self.ctrl.createCtrl("circle", prefix + "_ik1_ctl", r=self.radius*2.0,color="yellow", addAttr=True)
                    transform.addTransformLoc(self.ik1_ctl)
                    pm.parent(self.ik1_ctl, self.ik1autoRot)
                    pm.parent(self.ik1_con, self.autoBendChain[0])
                    pm.delete(pm.parentConstraint(self.TempChain[-1], self.ik1_con))
                else:
                    self.ik1_ctl = self.ctrl.createCtrl("circle", prefix + "_ik1_ctl", r=self.radius*2.0,color="yellow", addAttr=True)
                    self.ik1_con = pm.PyNode(util.zeroGrp([self.ik1_ctl], True)[0])
                    pm.parent(self.ik1_con, self.ControlGrp)
                    pm.delete(pm.parentConstraint(self.TempChain[-1], self.ik1_con))

                # get tan ctrl position(will be delete at last)
                self.tempCrvPos = [pm.PyNode(side+self.userGuideName+"_JointLoc"+str(n)).getTranslation(space="world")
                                   for n in range(1,self.jointsNum+1)]
                self.tempTanCrv = pm.curve(d=1, p=self.tempCrvPos, n=side+"tempTanCrv")
                self.tempTanCrv = pm.rebuildCurve(self.tempTanCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s=5, d=1, tol=0.01)[0]
                self.tan0Pos = self.tempTanCrv.getPointAtParam(0.333,space="world")
                self.tan1Pos = self.tempTanCrv.getPointAtParam(0.667,space="world")
                pm.delete(self.tempTanCrv)

                if centralTangent:
                    pass
                
                else:
                    # tan0
                    self.tan0Ctrl = self.ctrl.createCtrl("cube", prefix + "_tan0_ctl", r=self.radius,color="red", addAttr=True)
                    self.tan0Grp = pm.PyNode(util.zeroGrp([self.tan0Ctrl], True)[0])
                    t = transform.setMatrixPosition(t, self.tan0Pos)
                    self.tan0Grp.setTransformation(t)
                    pm.parent(self.tan0Grp, self.ik0_ctrl)

                    #tan1
                    self.tan1Ctrl = self.ctrl.createCtrl("cube", prefix + "_tan1_ctl", r=self.radius,color="red", addAttr=True)
                    self.tan1Grp = pm.PyNode(util.zeroGrp([self.tan1Ctrl], True)[0])
                    t = transform.setMatrixPosition(t, self.tan1Pos)
                    self.tan1Grp.setTransformation(t)
                    pm.parent(self.tan1Grp, self.ik1_ctl)
                
                crvCtlList = [self.ik0_ctrl+"_RevLoc", self.tan0Ctrl+"_RevLoc", self.tan1Ctrl+"_RevLoc", self.ik1_ctl+"_RevLoc"]
                self.mst_crv = rigging_utils.addCnsCurve(
                                                pm.PyNode(self.ControlGrp),
                                                side + self.guideModuleName + "_mst_crv",
                                                [pm.PyNode(loc) for loc in crvCtlList],
                                                3)
                self.slv_crv = rigging_utils.addCurve(
                                                pm.PyNode(self.ControlGrp), side + self.guideModuleName + "_slv_crv",
                                                [datatypes.Vector()] * 10,
                                                False,
                                                3)
                self.mst_crv.setAttr("visibility", False)
                self.slv_crv.setAttr("visibility", False)

                t = transform.getTransformLookingAt(
                        self.positions[0],
                        self.positions[-1],
                        Vector(0,0,1),
                        axis,
                        False)
                print(t)
                pm.delete(self.TempChain)

                mc.delete(side + self.guideModuleName + "_0" + self.userGuideName[-1] +'_'+self.mirrorGrp)
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