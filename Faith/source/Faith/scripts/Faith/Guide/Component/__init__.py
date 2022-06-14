# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:09
# @Last Modified by:   Admin
# @Last Modified time: 2022-06-14 19:22:02
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
aboutNode, aboutPy, aboutIcon, aboutVector, aboutRig

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

        self.transform2Lock = []

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
        self.final
        self.postScript
        self.collect_build_data
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
                uniScale = jpo[3]
            else:
                uniScale = False

            if len(jpo) >= 5 and self.options["joint_rig"]:
                MulMatrix = jpo[4]
            else:
                MulMatrix = False
            
            self.jointList.append(
                self.addJoint(jpo[0], jpo[1], newActiveJnt, uniScale,
                              MulMatrix=MulMatrix)
                )

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
        """

        :return:
        """
        self.uihost = self.rig.findRelative(self.settings["host"])

        return self.uihost

    @property
    def final(self):
        """

        :return:
        """
        for t in self.transform2Lock:
            aboutAttribute.lockAttribute()

        return

    @property
    def postScript(self):
        """

        :return:
        """
        return

    @property
    def collect_build_data(self):
        """

        :return:
        """
        self.build_data["FullName"] = self.fullName
        self.build_data["Name"] = self.name
        self.build_data["Type"] = self.guide.type
        self.build_data["Side"] = self.side
        self.build_data["Index"] = self.index
        self.build_data["DataContracts"] = []
        self.build_data["Joints"] = []
        self.build_data["Controls"] = []
        self.build_data["IK"] = []
        self.build_data["Twist"] = []

        for j in self.jointList:
            jnt_dict = {}
            jnt_dict["Name"] = j.name()
            jnt_dict.update(self.transform_info(j))
            self.build_data["Joints"].append(jnt_dict)

        for c in self.controlers:
            ctl_dict = {}
            ctl_dict["Name"] = c.name()
            # ctl_dict["Role"] = c.ctl_
            ctl_dict.update(self.transform_info(c))
            self.build_data["Controls"].append(ctl_dict)

    def transform_info(self, obj):
        """

        :param obj:
        :return:
        """
        trans_info = {}

        world_position = obj.getTranslation(space='world')
        temp_dict_position = {}
        temp_dict_position['x'] = world_position.x
        temp_dict_position['y'] = world_position.y
        temp_dict_position['z'] = world_position.z
        trans_info['WorldPosition'] = temp_dict_position

        temp_dict_rotation = {}
        world_rotation = obj.getRotation(space='world')
        temp_dict_rotation['x'] = world_rotation.x
        temp_dict_rotation['y'] = world_rotation.y
        temp_dict_rotation['z'] = world_rotation.z
        trans_info['WorldRotation'] = temp_dict_rotation

        return trans_info

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
                 MulMatrix=False,
                 rot_off=None,
                 vanilla_nodes=False):
        
        if vanilla_nodes:
            return self.addJoint_vanilla(obj,
                                         name,
                                         newActiveJnt=newActiveJnt,
                                         UniScale=UniScale,
                                         segComp=segComp,
                                         MulMatrix=MulMatrix)
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
        
        if not rot_off:
            rot_off = [
                self.settings["joint_rot_offset_x"],
                self.settings["joint_rot_offset_y"],
                self.settings["joint_rot_offset_z"]
            ]
        customName = self.getCustomName(len(self.jointList))

        if self.options["joint_rig"]:
            if newActiveJnt:
                self.active_jnt = newActiveJnt
            rule_name = self.getName(
                str(name),
                rule=self.options["joint_specificate"],
                ext="jnt",
                letter_case=self.options["joint_description"]
            )
            if rule_name[0] in "0123456789":
                pm.displayWarning("Name : {0} starts with a invalid name."
                                  .format(rule_name))
                rule_name = self.name + rule_name

            if pm.ls(customName) and self.options["joint_connection"]:
                jnt = pm.ls(customName)[0]
                keep_off = True

            elif pm.ls(rule_name) and self.options["joint_connection"]:
                jnt = pm.ls(rule_name[0])
                keep_off = True
            else:
                if isinstance(obj, datatypes.Matrix):
                    t = obj
                else:
                    t = aboutTransform.getTransform(obj)
                jnt = aboutAdd.addJoint(self.active_jnt,
                                        customName or rule_name,
                                        t)
                keep_off = False

            if not jnt.translate.listConnections(d = False):
                if isinstance(self.active_jnt, pm.nodetypes.Joint):
                    try:
                        pm.disconnectAttr(
                            self.active_jnt.scale, jnt.inverseScale
                        )
                    except RuntimeError:
                        if not isinstance(jnt, pm.nodetypes.Joint):
                            pm.ungroup(jnt.getParent())

                self.active_jnt = jnt

                if keep_off:
                    driver = aboutAdd.addTransform(
                        obj,
                        name=obj.name() + "_con_off")
                    aboutTransform.matchWorldTransform(jnt, driver)
                    rot_off = [0, 0, 0]

                else:
                    if isinstance(obj, datatypes.Matrix):
                        driver = None
                        jnt.setMatrix(obj, worldSpace=True)

                    else:
                        driver = obj
                        rot_off = rot_off

                if driver:
                    cns_m = aboutRig._matrix_cns(
                        [driver], jnt, rot_off=rot_off, name = driver)

                    # # invert negative scaling in Joints. We only inver Z axis,
                    # # so is the only axis that we are checking
                    # if jnt.scaleZ.get() < 0:
                    #     cns_m.scaleMultZ.set(-1.0)
                    #     cns_m.rotationMultX.set(-1.0)
                    #     cns_m.rotationMultY.set(-1.0)

                    # if unifor scale is False by default. It can be forced
                    # using uniScale arg or set from the ui
                    # if self.options["joint_uniSca"]:
                    #     UniScale = True
                    # if UniScale:
                    #     jnt.disconnectAttr("scale")
                    #     pm.connectAttr(cns_m.scaleZ, jnt.sx)
                    #     pm.connectAttr(cns_m.scaleZ, jnt.sy)
                    #     pm.connectAttr(cns_m.scaleZ, jnt.sz)
                else:
                    cns_m = None

                    # Segment scale compensate Off to avoid issues with the
                    # global scale
                jnt.setAttr("segmentScaleCompensate", segComp)

                if not keep_off:
                    # setting the joint orient compensation in order to
                    # have clean rotation channels
                    jnt.setAttr("jointOrient", 0, 0, 0)
                    if cns_m:
                        m = cns_m.restMatrix.get()
                    else:
                        driven_m = pm.getAttr(jnt + ".parentInverseMatrix[0]")
                        m = t * driven_m
                        jnt.attr("rotateX").set(0)
                        jnt.attr("rotateY").set(0)
                        jnt.attr("rotateZ").set(0)
                        if jnt.scaleZ.get() < 0:
                            jnt.scaleZ.set(1)
                    tm = datatypes.TransformationMatrix(m)
                    r = datatypes.degrees(tm.getRotation())
                    jnt.attr("jointOrientX").set(r[0])
                    jnt.attr("jointOrientY").set(r[1])
                    jnt.attr("jointOrientZ").set(r[2])

                # set not keyable
                aboutAttribute.setNotKeyableAttributes(jnt)

            else:
                jnt = aboutAdd.addJoint(obj,
                                         customName or self.getName(
                                             str(name) + "_jnt"),
                                         aboutTransform.getTransform(obj))
                pm.connectAttr(self.rig.jntVis, jnt.attr("visibility"))
                aboutAttribute.lockAttribute(jnt)

            self.addToGroup(jnt, "deformers")

            return jnt

    def addJoint_vanilla(self,
                         obj,
                         name,
                         newActiveJnt=None,
                         UniScale=False,
                         segComp=False,
                         MulMatrix=False):
        customName = self.getCustomName(len(self.jointList))

        if self.options["joint_rig"]:
            if newActiveJnt:
                self.active_jnt = newActiveJnt

            jnt = aboutAdd.addJoint(self.active_jnt,
                                    customName or self.getName(
                                        str(name) + "_jnt"),
                                    aboutTransform.getTransform(obj))

            # Disconnect inversScale
            if isinstance(self.active_jnt, pm.nodetypes.Joint):
                try:
                    pm.disconnectAttr(self.active_jnt.scale, jnt.inverseScale)

                except RuntimeError:
                    pm.ungroup(jnt.getParent())

            self.active_jnt = jnt

            if MulMatrix:
                mulmat_node = aboutRig.create_mulmatrix(
                    obj + ".worldMatrix", jnt + ".parentInverseMatrix",
                    name = "{0}_{1}".format(obj, jnt)
                    )
                dm_node = aboutNode.createDecomposeMatrixNode(
                    mulmat_node + ".outMatrix", name = jnt)
                m = mulmat_node.attr('outMatrix').get()
            else:
                mulmat_node = aboutNode.createDecomposeMatrixNode(
                    obj + ".worldMatrix", jnt + ".parentInverseMatrix",
                    name = "{0}_{1}".format(obj, jnt)
                    )
                dm_node = aboutNode.createDecomposeMatrixNode(
                    mulmat_node + ".matrixSum", name = jnt
                    )
                m = mulmat_node.attr('matrixSum').get()
            pm.connectAttr(dm_node + ".outputTranslate", jnt + ".t")
            pm.connectAttr(dm_node + ".outputRotate", jnt + ".r")


    def getCustomName(self, jointIndex):
        names = self.guide.values["joint_names"].split(",")
        if len(names) > jointIndex:
            return names[jointIndex].strip()

        return ""

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
    
    
        


