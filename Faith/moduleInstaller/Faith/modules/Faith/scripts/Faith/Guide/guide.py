# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-26 19:34:55
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-01 21:28:21

import datetime,getpass,imp,inspect,\
json,re,sys,os,shutil,subprocess,traceback
from functools import partial
from imp import reload

# pymel
from pymel import core as pm
from pymel.core import datatypes as datatypes

# faith
import Faith
from Faith.Core import aboutAttribute,aboutIcon,utils,\
    aboutCurve,aboutDag,aboutLog,aboutVector,aboutString
from . import naming

if sys.version_info[0] == 2:
    string_types = (basestring, )
else:
    string_types = (str,)

class MainGuide(object):


    def __init__(self):
        self.attrNames = []
        self.attrDefs = {}
        self.values = {}
        self.valid = True

    def addPropertyAttributes(self, parent):
        """

        :param parent:
        :return:

        """

        for guidetName in self.attrNames:
            attrDef = self.attrDefs[guidetName]
            attrDef.create(parent)

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

        attrDef = aboutAttribute.AttrDef2(attrName, valueType, value, niceName,
                                       shortName, minimum, maximum, keyable,
                                       readable, storable, writable)
        self.attrDefs[attrName] = attrDef
        self.values[attrName] = value
        self.attrNames.append(attrName)

        return attrDef

    def addEnumAttr(self, attrName, enum, value = False):
        """

        :param attrName:
        :param enum:
        :param value:
        :return:
        """
        attrDef = aboutAttribute.enumParamDef(attrName, enum, value)
        self.attrDefs[attrName] = attrDef
        self.values[attrName] = value
        self.attrNames.append(attrName)

        return attrDef

    def setAttrDefValue(self, attrName, value):
        """
        给attribute函数设置匹配的value
        :param attrName: 添加的属性名称
        :param value: 新的value数据
        :return: False (如果属性找不到)
        """

        if attrName not in self.attrDefs.keys():
            return False

        self.attrDefs[attrName].value = value
        self.values[attrName] = value

        return True

    def setAttrDefValuesFromProperty(self, node):
        """

        :param node:
        :return:
        """

        for attrName,attrDef in self.attrDefs.items():
            if not pm.attributeQuery(attrName, node = node, exists = True):
                aboutLog.Logger.warning("Can not find attribute '%s' in %s" %
                    attrName, node)
                self.valid = False
            else:
                connection = pm.listConnections("%s.%s"%(node, attrName),
                                                destination=False, source=True)
                if isinstance(attrDef, aboutAttribute.FCurveAttrDef):
                    attrDef.value = aboutCurve.getFCurveValues(
                        connection[0], self.get_divisions()
                    )
                    self.values[attrName] = attrDef.value

                if connection:
                    attrDef.value = None
                    self.values[attrName] = connection[0]
                else:
                    attrDef.value = pm.getAttr("%s.%s"%(node, attrName))
                    self.values[attrName] = pm.getAttr("%s.%s"%(node, attrName))

##########################################################
# DRAW GUIDE
##########################################################
class ComponentDraw(MainGuide):

    def __init__(self):

        self.attrNames = []
        self.attrDefs = {}
        self.values = {}
        self.valid = True

        self.controllers = {}
        self.components = {}
        self.componentsIndex = []
        self.parents = []

        self.guide_template_dict = {}

        self.addAttrs()

    def addAttrs(self):
        """

        :return:
        """
        # --------------------------------------------------
        # Main Tab
        self.RigName = self.addAttr("rig_name", "string", "Rig")
        # self.Mode = self.addEnumParam("mode", ["Final", "WIP"], 0)
        self.Step = self.addEnumAttr(
            "step",
            ["all_steps", "add_objects", "add_defs",
                "add_operators", "add_connector", "add_joints", "final"],
            6)
        self.isHighest = self.addAttr("isHighest" , "bool" , True)
        self.channelNames = self.addAttr("channelName" , "bool" , False)
        self.proxyChannels = self.addAttr("proxyChannels", "bool", False)
        self.attrPrefix = self.addAttr("attrPrefixName", "bool", False)

        self.globalCtl = self.addAttr("globalCtl", "bool", False)
        self.globalCtlName = self.addAttr("globalCtl_Name", "string", "global_ctrl")

        # =======================================================================
        # skin
        self.skin = self.addAttr("skin", "bool", False)
        self.importSkin = self.addAttr("import_skin", "bool", False)

        self.jointRig = self.addAttr("joint_rig", "bool", True)
        self.jointRig = self.addAttr("joint_uniSca", "bool", True)
        self.jointConnect = self.addAttr("joint_connection", "bool", True)

        self.userPath = self.addAttr("user_path", "string", getpass.getuser())
        self.date = self.addAttr("now_time", "string", str(datetime.datetime.now()))
        self.version = self.addAttr("version", "string",
                                    str(pm.mel.getApplicationVersionAsFloat()))

        # Naming rules
        self.ctrl_name_style = self.addAttr("ctrl_specificate", "string",
                                            naming.DEFAULT_NAMING_SPECIFICATE)
        self.joint_name_style = self.addAttr("joint_specificate", "string",
                                            naming.DEFAULT_NAMING_SPECIFICATE)
        self.left_name_style = self.addAttr("left_specificate", "string",
                                             naming.DEFAULT_SIDE_L_NAME)
        self.right_name_style = self.addAttr("right_specificate", "string",
                                            naming.DEFAULT_SIDE_R_NAME)
        self.center_name_style = self.addAttr("center_specificate", "string",
                                            naming.DEFAULT_SIDE_C_NAME)

        self.left_joint_style = self.addAttr("left_joint_specificate", "string",
                                            naming.DEFAULT_JOINT_SIDE_L_NAME)
        self.right_joint_style = self.addAttr("right_joint_specificate", "string",
                                             naming.DEFAULT_JOINT_SIDE_R_NAME)
        self.center_joint_style = self.addAttr("center_joint_specificate", "string",
                                             naming.DEFAULT_JOINT_SIDE_C_NAME)
        self.ctrl_ext = self.addAttr("ctrl_ext", "string",
                                     naming.DEFAULT_CTL_EXT_NAME)
        self.joint_ext = self.addAttr("joint_ext", "string",
                                     naming.DEFAULT_JOINT_EXT_NAME)

        self.ctrl_des = self.addEnumAttr(
            "ctrl_description",
            ["Default", "Upper Case", "Lower Case", "Capitalization"],
            0
        )

        self.joint_des = self.addEnumAttr(
            "joint_description",
            ["Default", "Upper Case", "Lower Case", "Capitalization"],
            0
        )

        self.ctrl_index = self.addAttr(
            "ctrl_index", "long", 0, 0, 99
        )
        self.joint_index = self.addAttr(
            "joint_index", "long", 0, 0, 99
        )

    def getComponentGuide(self, guide_type):
        """
        获取guide的文件路径
        :param guide_type:
        :return:
        """

        # Import module and get class
        from Faith import Guide as guide
        module = guide.importComponentGuide(guide_type)

        ComponentGuide = getattr(module, "Guide")

        return ComponentGuide()

    def initialHierarchy(self):
        """
        =============Init=============
        :return:
        """
        aboutIcon.ImportIconsFile(aboutIcon.icon_path)

        self.model = pm.createNode("transform" , n = "Proxy_guide")

        # Options
        self.options = self.addPropertyAttributes(self.model)

        self.controllers_org = pm.createNode(
            "transform",
            n = "controllers_org",
            p = self.model)
        self.controllers_org.attr('visibility').set(0)

    def drawNewComponent(self, parent, guideType):
        """

        :param parent:
        :param guideType:
        :return:
        """
        comp_guide = self.getComponentGuide(guideType)
        if not comp_guide:
            return
        if parent is None:
            self.initialHierarchy()
            parent = self.model
        else:
            parent_root = parent
            while True:
                if parent_root.hasAttr("ismodel"):
                    break

                if parent_root.hasAttr("guide_type"):
                    parent_type = parent_root.attr("guide_type").get()
                    parent_side = parent_root.attr("guide_side").get()
                    parent_ctlGrp = parent_root.attr("ctlrGrp").get()
    
                    if parent_type in comp_guide.connectors:
                        comp_guide.setParamDefValue("connector", parent_type)
    
                    comp_guide.setParamDefValue("guide_side", parent_side)
                    comp_guide.setParamDefValue("ctlrGrp", parent_ctlGrp)
    
                    break
    
                parent_root = parent_root.getParent()

        comp_guide.drawGuide(parent)

    def setDict(self, dict):
        """

        :param dict:
        :return:
        """
        return

    def set_hierarchy(self, node, children = True):
        """

        :param node:
        :param children:
        :return:
        """

        startTime = datetime.datetime.now()
        aboutLog.Logger.info("Prepare Components")

        self.model = node.getParent(generations = -1)
        while True:
            if node.hasAttr("guide_type") or self.model == node:
                break
            node = node.getParent()
            aboutLog.Logger.info(node)

        aboutLog.Logger.info("Load settings")
        self.setAttrDefValuesFromProperty(self.model)

        aboutLog.Logger.info("Load Controllers")
        self.controllers_org = aboutDag.findChild(self.model, "controllers_org")
        if self.controllers_org:
            for child in self.controllers_org.getChildren():
                self.controllers[child.name().split("|")[-1]] = child
        # ============================================================================
        aboutLog.Logger.info("Load Components")
        self.findComponentRecursive(node, children)
        endTime = datetime.datetime.now()
        finalTime = endTime - startTime
        aboutLog.Logger.info("Load in [" + str(finalTime) + "]")

        if self.valid:
            for name in self.componentsIndex:
                aboutLog.Logger.info("Get {0} parent----->".format(name))

                try:
                    compParent = self.components[name].root.getParent()
                    if compParent and compParent.hasAttr("isGuide"):
                        names = naming.get_component_and_relative_name(
                            compParent.name(long = None)
                        )
                        pName = names[0]
                        pLocal = names[1]
                        pComp = self.components[pName]
                        self.components[name].parentComponent = pComp
                        self.components[name].parentLocalName = pLocal
                except KeyError:
                    compParent = self.components[name]

                    for localName, element in compParent.getObjects3(
                            self.model).items():
                        for name in self.componentsIndex:
                            compChild = self.components[name]
                            compChild_parent = compChild.root.getParent()
                            if (element is not None and
                                    element == compChild_parent):
                                compChild.parentComponent = compParent
                                compChild.parentLocalName = localName

            self.addOptionsValues()

        if not self.valid:
            aboutLog.Logger.exception("Update Error!")

        endTime = datetime.datetime.now()
        finalTime = endTime - startTime
        aboutLog.Logger.info("Guide loaded in  [ " + str(finalTime) + " ]")                

    def findComponents(self, node, children = True):
        """

        :param node:
        :param children:
        :return:
        """
        if node.hasAttr("guide_type"):
            guide_type = node.getAttr("guide_type")
            guide = self.getComponentGuide(guide_type)

            if guide:
                guide.set_hierarchy(node)

    def findComponentRecursive(self, node, children = True):
        """

        :param node:
        :param children:
        :return:
        """
        if node.hasAttr("guide_type"):
            comp_type = node.getAttr("guide_type")
            comp_guide = self.getComponentGuide(comp_type)

            if comp_guide:
                comp_guide.set_hierarchy(node)
                aboutLog.Logger.info("{0} ({1})".format(comp_guide.fullName, comp_type))
                if not comp_guide.valid:
                    self.valid = False
                
                self.componentsIndex.append(comp_guide.fullName)
                self.components[comp_guide.fullName] = comp_guide
        if children:
            for child in node.getChildren(type="transform"):
                self.findComponentRecursive(child)

    def addOptionsValues(self):
        """

        :return:
        """
        maximum = 1
        v = datatypes.Vector()
        for comp in self.components.values():
            for pos in comp.posList:
                d = aboutVector.getDistance(v, pos)
                maximum = max(d, maximum)

        self.values["size"] = max(maximum * .05, .1)

    def set_selection(self):
        """

        :return:
        """
        selection = pm.ls(selection = True)
        if not selection:
            aboutLog.Logger.warning("Please select one or more guide components!")
            self.valid = False
            return False

        for node in selection:
            self.set_hierarchy(node, node.hasAttr("isHighest"))

        return True

    @utils.timeFunc
    def draw_Components(self , partial = None , Inparent = None):
        """

        :param partial:
        :param Inparent:
        :return:
        """
        partial_components = None
        partial_components_id = []
        parent = None

        if partial:
            if not isinstance(partial, list):
                partial = [partial]

            partial_components = list(partial)

        if Inparent:
            if Inparent and Inparent.getParent(-1).hasAttr("isHighest"):
                self.model = Inparent.getParent(-1)
            else:
                pm.warning("Current parent is not a valid object !")

                return
        else:
            self.initialHierarchy()

        # Draw components
        # Show progressWindow
        pm.progressWindow(title = "Draw Module Components" , 
                          progress = 0,
                          max = len(self.components))

        for name in self.componentsIndex:
            pm.progressWindow()

class SinalSlots(object):

    def updateCheck(self, targetWidget, sourceAttr, *args):
        """

        :param targetWidget:
        :param sourceAttr:
        :param args:
        :return:
        """
        self.root.attr(targetWidget).set(sourceAttr.isChecked)

    def updateSpinBox(self, sourceWidget, targetAttr, *args):
        """

        :param sourceWidget:
        :param targetAttr:
        :param args:
        :return:
        """
        self.root.attr(targetAttr).set(sourceWidget.value())
        return True

    def updateSlider(self, sourceWidget, targetAttr, *args):
        """

        :param sourceWidget:
        :param targetAttr:
        :param args:
        :return:
        """
        self.root.attr(targetAttr).set(float(sourceWidget.value()) / 100)

    def updateComboBox(self, sourceWidget, targetAttr, *args):
        """

        :param sourceWidget:
        :param targetAttr:
        :param args:
        :return:
        """
        self.root.attr(targetAttr).set(sourceWidget.currentIndex())












