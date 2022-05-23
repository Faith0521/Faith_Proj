# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:09
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-08 10:01:00
#################################################################
#################Component Rigging Basic Class###################
#################################################################

# pymel
from pymel import core as pm
from pymel.core import datatypes
from pymel import versions

# Base
import Faith
from Faith.Core import aboutAdd, aboutAttribute, aboutLog, aboutTransform, \
aboutNode, aboutPy, aboutIcon, aboutVector

from Faith.Guide import naming


class Rigging(object):
    """ Main component rigging class """

    steps = ["AddObjects", "AddProperties", "AddOperators",
             "AddConnectors", "AddJoints", "Finally"]
    
    local_attrs = ("tx", "ty", "tz", "rx", "ry", "rz", "ro", "sx", "sy", "sz")
    t_attrs = ("tx", "ty", "tz")
    r_attrs = ("rx", "ry", "rz")
    s_attrs = ("sx", "sy", "sz")
    tr_attrs = ("tx", "ty", "tz", "rx", "ry", "rz", "ro")
    rs_attrs = ("rx", "ry", "rz", "ro", "sx", "sy", "sz")
    x_axis = datatypes.Vector(1, 0, 0)
    y_axis = datatypes.Vector(0, 1, 0)
    z_axis = datatypes.Vector(0, 0, 1)

    def __init__(self, rig, guide):
        
        # init objects===============================
        self.rig = rig
        self.guide = guide
        
        self.options = self.rig.options
        self.model = self.rig.model
        self.settings = self.guide.values
        self.setUpWS = self.rig.setUpWS

        self.name = self.settings["guide_name"]
        self.side = self.settings["guide_side"]
        self.index = self.settings["guide_index"]

        self.size = self.guide.size
        self.negate = self.side == "R"
        if self.negate:
            self.n_sign = "-"
            self.n_factor = -1
        else:
            self.n_sign = ""
            self.n_factor = 1

        # --------------------------------------------------
        # Builder init
        self.groups = {}  # 存放groups的字典
        self.subGroups = {}  # 存放subgroups的字典
        self.controlers = []  # 存放controllers的列表

        # --------------------------------------------------
        # 初始化连接
        self.connections = {}
        self.connections["standard"] = self.connect_standard

        self.relatives = {}
        self.jointRelatives = {}  
        self.controlRelatives = {}
        self.aliasRelatives = {}

        # --------------------------------------------------
        # 初始化骨骼位置
        self.jnt_pos = []
        self.jointList = []

        # self.transform2Lock = []

        # Data collector
        self.build_data = {}

        # --------------------------------------------------
        # Step
        self.stepMethods = [eval("self.step0{}".format(str(i)),
                                 {"self": self})
                            for i in range(len(self.steps))]


    def step00(self):
        """

        :return:
        """
        self.preScript
        self.initialHierarchy
        self.initialCtlTag
        self.addObjects
        self.setRelation
        return

    def step01(self):
        """

        :return:
        """
        self.getHost
        self.validateProxyChannels
        self.addFullAttr
        self.addParams
        return

    def step02(self):
        """

        :return:
        """
        self.addOperators
        return

    def step03(self):
        """

        :return:
        """
        self.initConnectors
        self.addConnections
        self.connect
        self.doConnect
        return

    def step04(self):
        """

        :return:
        """
        self.jointFunc
        return

    def step05(self):
        """

        :return:
        """
        return
    
    @property
    def addObjects(self):
        """

        :return:
        """
        return

    @property
    def addOperators(self):
        """

        :return:
        """
        return

    @property
    def addConnections(self):
        """

        :return:
        """
        return

    @property
    def initialCtlTag(self):
        """

        :return:
        """
        self.parentCtlTag = None
        if versions.current() >= 201650:
            parentName = "none"
            if self.guide.parentComponent is not None:
                parentName = self.guide.parentComponent.getName(
                    self.guide.parentLocalName
                )
            self.parentCtlTag = self.rig.findControlRelative(parentName)

    @property
    def preScript(self):
        """

        :return:
        """
        return

    @property
    def initConnectors(self):
        """

        :return:
        """
        parent_name = "none"
        if self.guide.parentComponent is not None:
            parent_name = self.guide.parentComponent.getName(
                self.guide.parentLocalName
            )
        self.parent = self.rig.findRelative(parent_name)
        self.parent_comp = self.rig.findComponent(parent_name)
        print("parent is : " + self.parent)

    @property
    def connect(self):
        """

        :return:
        """
        if self.settings["connector"] not in self.connections.keys():
            aboutLog.Logger.exception("{0} connector can not found"
                                      .format(self.settings["connector"]))
            self.settings["connector"] = "standard"
        try:
            self.connections[self.settings["connector"]]()
            return True
        except AttributeError:
            return False

    @property
    def doConnect(self):
        """

        :return:
        """
        return

    @property
    def initialHierarchy(self):
        """

        :return:
        """
        self.root = aboutAdd.addTransformFromPos(
            self.model, self.getName("root"), self.guide.posDict["root"]
        )

        # attrs

        aboutAttribute.addAttribute(
            self.root, "guideType", "string", self.guide.GUIDETYPE
        )
        aboutAttribute.addAttribute(
            self.root, "guideName", "string", self.guide.GUIDENAME
        )
        # aboutAttribute.addAttribute(
        #     self.root, "guideVersion", "string", self.guide.version
        # )
        aboutAttribute.addAttribute(
            self.root, "guideAuthor", "string", self.guide.author
        )

        # joint--------------------------------------------------------
        if self.options["joint_rig"]:
            self.component_jnt_org = aboutAdd.addTransform(
                self.rig.jnt_org, self.getName("skeleton_jnts_org")
            )
            self.active_jnt = self.component_jnt_org
            self.parent_relative_jnt = self.component_jnt_org

        return

    @property
    def jointFunc(self):
        """

        :return:
        """
        if self.settings["useIndex"]:
            try:
                self.active_jnt = self.parent_comp.jointList[
                    self.settings["parentJointIndex"]
                ]
            except Exception:
                pm.warning("Parent guide for : {0} don't have joints with this index : {1} !"
                           .format(self.fullName, str(self.settings["parentJointIndex"])))
        else:
            parent_name = "none"
            if self.guide.parentComponent is not None:
                parent_name = self.guide.parentComponent.getName(
                    self.guide.parentLocalName
                )
            relative_name = self.rig.getRelativeName(parent_name)
            oParent_comp = self.parent_comp
            while oParent_comp:
                try:
                    self.active_jnt = oParent_comp.jointList[
                        oParent_comp.jointRelatives[relative_name]
                    ]
                    self.parent_relative_jnt = self.active_jnt
                    break
                except Exception:
                    if oParent_comp.parent_comp:
                        pgpc = oParent_comp.guide.parentComponent
                        parent_name = pgpc.getName(
                            oParent_comp.guide.parentLocalName)
                        relative_name = oParent_comp.rig.getRelativeName(
                            parent_name)
                    else:
                        pm.displayInfo(
                            "The parent components for: %s don't have joint " %
                            self.fullName)

                    oParent_comp = oParent_comp.parent_comp

        for jpo in  self.jnt_pos:
            if len(jpo) >= 3 and self.options["joint_rig"]:
                if jpo[2] == "component_jnt_org":
                    newActiveJnt = self.component_jnt_org
                elif jpo[2] == "parent_relative_jnt":
                    newActiveJnt = self.parent_relative_jnt
                else:
                    try:
                        newActiveJnt = self.jointList[
                            self.jointRelatives[jpo[2]]
                        ]

                    except Exception:
                        if jpo[2]:
                            pm.displayWarning("This object : %s can nnot be found."%jpo[2])

                        newActiveJnt = None
            else:
                newActiveJnt = None
            if len(jpo) >= 4 and self.options["joint_rig"]:
                uniScale = jpo[4]
            else:
                uniScale = False

            if len(jpo) >= 5 and self.options["joint_rig"]:
                gearMulMatrix = jpo[4]
            else:
                gearMulMatrix = False
            
            # self.jointList.append(self.asd)

    @property
    def setRelation(self):
        """

        Returns:

        """
        for name in self.guide.objectNames:
            self.relatives[name] = self.root
            self.controlRelatives[name] = self.global_ctrl

    @property
    def getFullName(self):
        """

        Returns:

        """
        return self.guide.fullName
    
    @property
    def getType(self):
        """return the type of the component
        """
        return self.guide.type
    
    @property
    def validateProxyChannels(self):
        """

        :return:
        """
        if versions.current() >= 201650 and self.options["proxyChannels"]:
            self.validProxyChannels = True
        else:
            self.validProxyChannels = False

    @property
    def addFullAttr(self):
        if self.options["channelName"]:
            attr = self. addEnumChannelAttr(
               self.getName(), "_________", 0, [self.getName()]
           )
        else:
           if self.options["attrPrefixName"]:
                name = self.name
           else:
                name = self.guide.GUIDENAME
                attr = self.addEnumChannelAttr(
                name, "_________", 0, [name]
            )
        return attr

    @property
    def connect_orientCns(self):
        self.parent.addChild(self.root)

    @property
    def addParams(self):
        """

        :return:
        """
        return

    @property
    def getHost(self):
        self.uihost = self.rig.findRelative(self.settings["host"])

        return self.uihost

    def connect_standard(self):
        """

        :return:
        """
        self.parent.addChild(self.root)

    def getName(self, name="",
                side=None,
                rule=None,
                ext=None,
                letter_case=0,
                short_name=False):
        """
        获取物体的fullName
        Args:
            name: 物体命名
            side: 左/右/中
            rule: 命名规则
            ext: 物体类型
            letter_case: letter_case
            short_name: 短名称

        Returns:

        """

        if side is None:
            side = self.side

        name = str(name)

        if rule and ext:
            # get side
            if ext == "jnt":
                if side == "L":
                    side = self.options["left_joint_specificate"]
                elif side == "R":
                    side = self.options["right_joint_specificate"]
                elif side == "C":
                    side = self.options["center_joint_specificate"]
            elif ext == "ctrl":
                if side == "L":
                    side = self.options["left_specificate"]
                elif side == "R":
                    side = self.options["right_specificate"]
                elif side == "C":
                    side = self.options["center_specificate"]

            # get extension
            if ext == "jnt":
                ext = self.options["joint_ext"]
                padding = self.options["joint_index"]
            elif ext == "ctrl":
                ext = self.options["ctrl_ext"]
                padding = self.options["ctrl_index"]

            # description letter case
            name = naming.letter_case_solve(name, letter_case)
            values = {
                "guide": self.name,
                "side": side,
                "index": str(self.index),
                "padding": padding,
                "description": name,
                "extension": ext
            }
            return naming.name_solve(rule, values)
        else:
            if name:
                if short_name:
                    return "_".join([self.name, name])
                else:
                    return "_".join([self.name, side + str(self.index), name])
            else:
                return self.fullName

    def addChannelAttr(self, longName, niceName, attType, value, minValue=None,
                     maxValue=None, keyable=True, readable=True, storable=True,
                     writable=True, uihost=None):
        """

        :param longName:
        :param niceName:
        :param attType:
        :param value:
        :param minValue:
        :param maxValue:
        :param keyable:
        :param readable:
        :param storable:
        :param writable:
        :param uihost:
        :return:
        """
        
        if not uihost:
            uihost = self.uihost

        if self.options["channelName"]:
            attr = aboutAttribute.addAttribute(
                uihost, self.getName(longName), attType, value,
                niceName, None, minValue=minValue, maxValue=maxValue,
                keyable=keyable, readable=readable, storable=storable, writable=writable
            )
        else:
            if uihost.hasAttr(self.getAttrName(longName)):
                attr = uihost.attr(self.getAttrName(longName))
            else:
                attr = aboutAttribute.addAttribute(uihost,
                                                   self.getAttrName(longName),
                                                   attType, value, niceName, None,
                                                   minValue=minValue,
                                                   maxValue=maxValue,
                                                   keyable=keyable,
                                                   readable=readable)

        return attr

    def addEnumChannelAttr(self,
                           longName,
                           niceName,
                           value,
                           enum = [],
                           keyable = True,
                           readable = True,
                           storable = True,
                           writable = True,
                           uihost = None):
        """

        :param longName:
        :param niceName:
        :param value:
        :param enum:
        :param keyable:
        :param readable:
        :param storable:
        :param writable:
        :param uihost:
        :return:
        """
        if not uihost:
            uihost = self.uihost

        if self.options["channelName"]:
            attr = aboutAttribute.addEnumAttribute(uihost,
                                                   self.getName(longName),
                                                   value, enum, niceName, None,
                                                   keyable=keyable,
                                                   readable=readable,
                                                   storable=storable,
                                                   writable=writable)
        else:
            if uihost.hasAttr(self.getAttrName(longName)):
                attr = uihost.attr(self.getAttrName(longName))
            else:
                attr = aboutAttribute.addEnumAttribute(uihost,
                                                       self.getName(longName),
                                                       value, enum, niceName, None,
                                                       keyable=keyable,
                                                       readable=readable,
                                                       storable=storable,
                                                       writable=writable)

        return attr

    def addJoint(self,
                 obj,
                 name,
                 newActiveJnt=None,
                 UniScale=False,
                 segComp=False,
                 gearMulMatrix=False,
                 rot_off=None,
                 vanilla_nodes=False):
        
        if vanilla_nodes:
            return self.addJoint_vanilla(obj,
                                         name,
                                         newActiveJnt=newActiveJnt,
                                         UniScale=UniScale,
                                         segComp=segComp,
                                         gearMulMatrix=gearMulMatrix)
        else:
            return self._addJoint(obj,
                                  name,
                                  newActiveJnt=newActiveJnt,
                                  UniScale=UniScale,
                                  segComp=segComp,
                                  rot_off=rot_off)

    def _addJoint(self,
                  obj,
                  name,
                  newActiveJnt=None,
                  UniScale=False,
                  segComp=False,
                  rot_off=None):
        return

    def addJoint_vanilla(self,
                         obj,
                         name,
                         newActiveJnt=None,
                         UniScale=False,
                         segComp=False,
                         gearMulMatrix=False):
        return

    def getRelation(self, name):
        """

        :param name:
        :return:
        """
        if name not in self.relatives.keys():
            # mgear.log("Can't find reference for object : "
            #           + self.fullName + "." + name, mgear.sev_error)
            return False
        return self.relatives[name]
    
    def getJointName(self, jointIndex):
        names = self.guide.values["joint_names"]
        if len(names) > jointIndex:
            return names[jointIndex].strip()
        return ""

    def addCtrl(self,
                parent,
                name,
                m,
                iconType,
                tp = None,
                lp = None,
                mirrorConf=[0, 0, 0, 0, 0, 0, 0, 0, 0],
                guide_loc_ref=None,
                ** kwargs):
        """

        Args:
            parent:
            name:
            m: 
            iconType:
            tp:
            lp:
            mirrorConf:
            guide_loc_ref:
            **kwargs:

        Returns:

        """
        if name.endswith("_ctrl"):
            name = name[:-5]
        
        if name.endswith("ctrl"):
            name = name[:-4]

        rule = self.options["ctrl_specificate"]
        if not name:
            if rule == naming.DEFAULT_NAMING_SPECIFICATE:
                rule = r"{guide}_{side}{index}_{extension}"
            else:
                name = "control"
        # print("name is : "+ name)
        fullName = self.getName(
            name, rule=rule, ext="ctrl",letter_case=self.options["ctrl_description"]
        )
        
        # # bufferName = fullName + "_ctrlBuffer"
        ctrl = aboutIcon.CreateControl(
            parent, iconType, fullName, m, **kwargs
        )

        aboutAttribute.addAttribute(ctrl, "isCtrl", "bool", keyable=False)
        aboutAttribute.addAttribute(ctrl, "host", "string", keyable=False)
        ctrl.addAttr("host_cn", at = "message", multi=False)
        aboutAttribute.addAttribute(ctrl, "ctl_role", "string", keyable=False,value=name)

        aboutAttribute.addAttribute(ctrl, "ctl_name", "string", 
                                    keyable=False,value=self.getName(name) + "_ctrl")
        aboutAttribute.addAttribute(
            ctrl, "side", "string", keyable=False,value=self.side
        )
        aboutAttribute.addAttribute(
            ctrl, "L_side_name", "string", keyable=False, value=self.options["left_specificate"]
        )
        aboutAttribute.addAttribute(
            ctrl, "R_side_name", "string", keyable=False, value=self.options["right_specificate"]
        )
        aboutAttribute.addAttribute(
            ctrl, "C_side_name", "string", keyable=False, value=self.options["center_specificate"]
        )

        aboutAttribute.add_mirror_config_channels(ctrl, mirrorConf)

        if self.settings["ctrlGrp"]:
            ctrlGrp = self.settings["ctrlGrp"]
            self.addToGroup(ctrl, ctrlGrp, "controllers")
        else:
            ctrlGrp = "controllers"
            self.addToGroup(ctrl, ctrlGrp)
        
        if parent not in self.groups[ctrlGrp] and lp:
            self.transform2Lock.append(parent)

        # Set the control shapes isHistoricallyInteresting
        for oShape in ctrl.getShapes():
            oShape.isHistoricallyInteresting.set(False)
            # connecting the always draw shapes on top to global attribute
            if versions.current() >= 20220000:
                pm.connectAttr(self.rig.ctrlXray,
                               oShape.attr("alwaysDrawOnTop"))

        # set controller tag
        if versions.current() >= 201650:
            try:
                oldTag = pm.PyNode(ctrl.name() + "_tag")
                if not oldTag.controllerObject.connections():
                    pm.delete(oldTag)

            except TypeError:
                pass

            self.add_controller_tag(ctrl, tp)
        self.controlers.append(ctrl)
        return ctrl

    def add_controller_tag(self, ctl, tagParent):
        self.rig.add_controller_tag(ctl, tagParent)

    def addToGroup(self, objects, names=["hidden"], parentGrp=None):
        if not isinstance(names, list):
            names = [names]

        if not isinstance(objects, list):
            objects = [objects]
        
        for name in names:
            if name not in self.groups.keys():
                self.groups[name] = []
            
            self.groups[name].extend(objects)

            if parentGrp:
                if parentGrp not in self.subGroups.keys():
                    self.subGroups[parentGrp] = []
                if name not in self.subGroups[parentGrp]:
                    self.subGroups[parentGrp].append(name)

    def getControlRelation(self, name):
        """Return the relational object from guide to rig.

        Args:
            name (str): Local name of the guide object.

        Returns:
            dagNode: The relational object.

        """
        if name not in self.controlRelatives.keys():
            aboutLog.Logger.exception("Can't find reference for "
                      " object : " + self.fullName + "." + name)
            return False

        return self.controlRelatives[name]
    
    def getAttrName(self, longName):
        if self.options["attrPrefixName"]:
            return self.getName(longName, short_name=True)
        else:
            return self.getName(longName)

    fullName = getFullName
    type = getType
    
    
        


