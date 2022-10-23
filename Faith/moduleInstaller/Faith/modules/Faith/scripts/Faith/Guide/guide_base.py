# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-15 16:14:02
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-15 16:14:12

import datetime,getpass,imp,inspect,\
json,re,sys,os,shutil,subprocess,traceback
from functools import partial

from importlib import reload

from maya import cmds as mc
from pymel import core as pm
# import module
from Faith.maya_utils import guide_path_utils as util
from Faith.maya_utils import attribute_utils as attribute
from Faith.maya_utils import naming_utils as naming
reload(util)
reload(attribute)
reload(naming)
# string type in py2 and py3
if sys.version_info[0] == 2:
    string_types = (basestring, )
else:
    string_types = (str, )

class guideAttributes(object):

    def __init__(self):
        self.baseName = "GUIDE_1"
        self.attr_names = []
        self.attr_defs = {}
        self.values = {}

    def addAttributes(self, parent):
        """

        :param parent:
        :return:
        """
        for guideName in self.attr_names:
            attrDef = self.attr_defs[guideName]
            attrDef.add(parent)

        return parent


    def addAttr(self, attrName, valueType, value,
                minimum=None, maximum=None, keyable=False,
                readable=True, storable=True, writable=True,
                niceName=None, shortName=None):
        """

        :param attrName:
        :param valueType:
        :param value:
        :param minimum:
        :param maximum:
        :param keyable:
        :param readable:
        :param storable:
        :param writable:
        :param niceName:
        :param shortName:
        :return:
        """

        attrDef = attribute.attrDef_create(attrName, valueType, value, niceName,
                                          shortName, minimum, maximum, keyable,
                                          readable, storable, writable)
        self.attr_defs[attrName] = attrDef
        self.values[attrName] = value
        self.attr_names.append(attrName)

        return attrDef


    # def addEnumAttr(self, attrName, enum, value=False):
    #     """
    #
    #     :param attrName:
    #     :param enum:
    #     :param value:
    #     :return:
    #     """
    #     attrDef = attribute.enumParamDef(attrName, enum, value)
    #     self.attr_defs[attrName] = attrDef
    #     self.values[attrName] = value
    #     self.attr_names.append(attrName)
    #
    #     return attrDef


    def setAttrDefValue(self, attrName, value):
        """
        给attribute函数设置匹配的value
        :param attrName: 添加的属性名称
        :param value: 新的value数据
        :return: False (如果属性找不到)
        """

        if attrName not in self.attr_defs.keys():
            return False

        self.attr_defs[attrName].value = value
        self.values[attrName] = value

        return True


class guideSetup(guideAttributes):

    def __init__(self):
        self.instanceList = []
        self.attr_names = []
        self.attr_defs = {}
        self.values = {}
        self.index = []

        self.allGuidesList = []
        self.getMoudleInfo()
        # self.addRootTagsAttributes()

    def addRootTagsAttributes(self):
        self.pRigName = self.addAttr("rig_name", "string", "rig")

        self.isRoot = self.addAttr("is_root", "bool", False)
        self.pSkin = self.addAttr("import_skin", "bool", False)
        self.pSkinPath = self.addAttr("skin_path", "string", "")

        self.pLfkColor = self.addAttr("L_fk_color", "long", 6, 0, 31)
        self.pLikColor = self.addAttr("L_ik_color", "long", 18, 0, 31)
        self.pRfkColor = self.addAttr("R_fk_color", "long", 6, 0, 31)
        self.pRikColor = self.addAttr("R_ik_color", "long", 18, 0, 31)

        self.p_ctrl_name_rule = self.addAttr("ctrl_naming_setting", "string", naming.DEFAULT_NAMING_RULE)
        self.p_joint_name_rule = self.addAttr("joint_naming_setting", "string", naming.DEFAULT_NAMING_RULE)
        self.p_left_name_rule = self.addAttr("left_naming_setting", "string", naming.DEFAULT_SIDE_L_NAME)
        self.p_right_name_rule = self.addAttr("right_naming_setting", "string", naming.DEFAULT_SIDE_R_NAME)
        self.p_center_name_rule = self.addAttr("center_naming_setting", "string", naming.DEFAULT_SIDE_C_NAME)

        self.rigVersion = self.addAttr("version", "string", "0.0.1")

    def get_guide(self, type):
        """
        获取guide的文件路径
        :param type:
        :return:
        """
        module = util.importDefGuide(type)
        reload(module)
        module_guide_class = getattr(module, "guide")
        return module_guide_class

    def getUserName(self):
        """

        :return:
        """
        mc.namespace(setNamespace=":")
        namespaceList = mc.namespaceInfo(listOnlyNamespaces=True)

        for i in range(len(namespaceList)):
            if namespaceList[i].find("__") != -1:
                namespaceList[i] = namespaceList[i].partition("__")[2]

        newSuffix = util.findLastNumber(namespaceList, "GUIDE_") + 1
        # print(namespaceList)
        userGuideName = "GUIDE_" + str(newSuffix)
        return userGuideName

    def setup_new_guide(self, type):
        """
        创建新的guide
        :param parent: the parent guide
        :param type: type of the guide
        :return:d
        """
        guide = self.get_guide(type)
        if not guide:
            return
        userGuideName = self.getUserName()
        guideInstance = guide(userGuideName, type)
        return guideInstance
        # guide.draw(parent)

    def rig(self):
        """

        :return:
        """
        mc.refresh()
        self.modulesToBeRiggedList = util.getModulesToBeRigged(self.instanceList)

        self.rigModule = {}
        if self.modulesToBeRiggedList:
            progressAmount = 0
            mc.progressWindow(title='GuideRigSystem', progress=progressAmount,
                              status='Rigging : %0', isInterruptable=False)
            maxProcess = len(self.modulesToBeRiggedList)

            if mc.objExists('guideMirror_Grp'):
                mc.delete('guideMirror_Grp')

            for module in self.modulesToBeRiggedList:
                guideModuleCustomName = mc.getAttr(module.root + '.module_name')
                progressAmount += 1
                mc.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount,
                                    status=('Rigging : ' + repr(progressAmount) + ' ' + str(guideModuleCustomName)))

                module.rigModule()

            mc.progressWindow(endProgress=True)

    def getMoudleInfo(self):
        """
        获取场景中的namespace 存放到列表中为rig做准备
        :return:
        """
        moduleList = util.findAllModules()

        namespaceList = mc.namespaceInfo(listOnlyNamespaces=True)

        for n in namespaceList:
            divString = n.partition("__")
            if divString[1] != "":
                module = divString[0]
                userSpecName = divString[2]
                if module in moduleList:
                    index = moduleList.index(module)
                    # check if there is this module guide base in the scene:
                    curGuideName = moduleList[index] + "__" + userSpecName + ":Base"
                    if mc.objExists(curGuideName):
                        self.allGuidesList.append([moduleList[index], userSpecName, curGuideName])

        if self.allGuidesList:
            for module in self.allGuidesList:
                guide = self.get_guide(module[0])
                instance = guide(module[1], module[0])
                self.instanceList.append(instance)



















