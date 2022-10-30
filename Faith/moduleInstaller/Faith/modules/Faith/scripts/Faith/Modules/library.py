# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-18 20:48:28
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-18 20:48:49

from functools import partial

from imp import reload

from maya import cmds as mc
from pymel import core as pm
# import module
from Faith.guide import guide_base
from Faith.guide import rig_base
from Faith.maya_utils import guide_path_utils as util
reload(guide_base)
reload(util)
reload(rig_base)

VERSION = "0.0.1"


class guideBase(guide_base.guideSetup):

    def __init__(self, userGuideName, rigType, CLASS, NAME, DESCRIPTION, *args):

        self.attr_names = []
        self.attr_defs = {}
        self.values = {}

        self.userGuideName = userGuideName
        self.rigType = rigType
        self.guideModuleName = CLASS
        self.name = NAME
        self.description = DESCRIPTION

        self.initializeAttrs()

        self.addPrivateAttrs()

        self.guideNamespace = self.guideModuleName + "__" + self.userGuideName

        mc.namespace(setNamespace=":")
        self.namespaceExists = mc.namespace(exists=self.guideNamespace)

        self.guideName = self.guideNamespace + ":"
        self.root = self.guideName + "Base"

        self.ctrl = guide_base.controlBase(self.root)

        if not self.namespaceExists:
            mc.namespace(add=self.guideNamespace)
            self.createGuide()

    def createGuide(self):
        return

    def initializeAttrs(self):
        """

        :return:
        """
        self.guide_base = self.addAttr("guide_base", "bool", True)
        self.guide_type = self.addAttr("guide_type", "string", self.rigType)
        self.module_name = self.addAttr("module_name", "string", self.guideModuleName)
        self.user_name = self.addAttr("user_name", "string", self.userGuideName)
        self.prefix_name = self.addAttr("prefix_name", "string", "")
        self.mirror_on = self.addAttr("mirror_on", "bool", False)
        self.mirror_axis = self.addAttr("mirror_axis", "string", "off")
        self.mirror_name = self.addAttr("mirror_name", "string", "L-->R")
        self.shape_size = self.addAttr("shape_size", "double", 1.0)
        self.version = self.addAttr("version", "string", VERSION)

    def addRoot(self):
        
        self.root = self.ctrl.cvBase(self.root, 4)

        for name in self.attr_names:
            attrDef = self.attr_defs[name]
            attrDef.add(self.root)

        return self.root

    def confirmModules(self):
        """

        :param args:
        :return:
        """
        if mc.objExists(self.root):
            if mc.objExists(self.root + '.guide_base'):
                if mc.getAttr(self.root + '.guide_base') == 1:
                    return True
                else:
                    try:
                        self.deleteModule()
                    except:
                        pass
                    return False
        return False

    def checkParentMirror(self, *args):
        if self.confirmModules():
            miiroredParentGuide = util.getMirroredParentGuide(self.root)


    def deleteModule(self, *args):
        """

        :param args:
        :return:
        """
        try:
            mc.delete(self.root[:self.root.find(":")] + "_MirrorGrp")
        except:
            pass
        util.clearNodeGrp(nodeGrpName=self.moduleGrp, attrFind='guideBase', unparent=True)
        # clear default 'dpAR_GuideMirror_Grp':
        util.clearNodeGrp()
        # remove the namespaces:
        allNamespaceList = mc.namespaceInfo(listOnlyNamespaces=True)
        if self.guideNamespace in allNamespaceList:
            mc.namespace(moveNamespace=(self.guideNamespace, ':'), force=True)
            mc.namespace(removeNamespace=self.guideNamespace, force=True)


    def addPrivateAttrs(self):
        """

        :return:
        """
        return

    def rigModule(self, *args):
        return




        





























