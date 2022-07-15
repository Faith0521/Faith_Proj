# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-27 08:55:58
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-28 17:12:48

"""
Component guide class.
"""

from functools import partial
from imp import reload
import maya.cmds as cmds
# pyMel
import pymel.core as pm
from pymel.core import datatypes

# Faith
import Faith
from Faith.Core import aboutAttribute,aboutTransform,aboutIcon,\
aboutDag,aboutNode,aboutLog,aboutString,aboutVector
from .. import guide

##########################################################
# COMPONENT GUIDE
##########################################################

class ComponentGuide(guide.MainGuide):

    GUIDETYPE = "TYPE"  # 模板类型
    GUIDENAME = "NAME"  # 模板名称
    GUIDESIDE = "M"
    GUIDEINDEX = 0  # 模板序号

    DESCRIPTION = ""  # 模板的描述

    CONNECTORS = []
    COMPATIBLE = []
    CTL_GRP = ""

    # ====================================================
    # Init method.
    def __init__(self):
        # 所有属性名称, 函数定义和数值
        # 添加的属性列表
        self.attrNames = []
        # 装Attributes函数的字典
        self.attrDefs = {}
        # 存放属性一系列数值的字典
        self.values = {}

        self.valid = True

        self.root = None
        self.id = None

        # 父组件模板
        self.parentComponent = None
        self.parentLocalName = None

        # 子组件
        self.child_components = []

        # 创建组件时使用的列表和字典
        self.traDict = {}  # transform字典
        self.traList = []  # transform列表
        self.posDict = {}  # postion字典
        self.posList = []  # position列表
        self.addObjDict = {}  # dictionary of primitive
        self.blades = {}
        self.size = 0.1

        # 用于定义数据的列表和字典
        # 将保存此列表中对象名称的transform信息
        self.save_transform = []
        # 将保存此列表中原始的对象名称
        self.save_primitive = []
        # 对象的法线信息将被保存
        self.save_blade = []
        # 为多位置对象定义最小和最大对象
        self.minmax = {}
        self.minmax_blade = {}

        # 初始化模块组件
        self.postInit()
        self.initialHierarchy()
        self.addAttributes()

    def postInit(self):
        """

        Returns:

        """
        self.save_transform = ["root"]
        return

    def initialHierarchy(self):
        """初始化


        """
        # 添加Rig属性到字典中 --------------------------------------
        self.guideType = self.addAttr("guide_type", "string", self.GUIDETYPE)
        self.guideName = self.addAttr("guide_name", "string", self.GUIDENAME)
        self.guideSide = self.addAttr("guide_side", "string", self.GUIDESIDE)
        self.guideIndex = self.addAttr("guide_index", "long", self.GUIDEINDEX, 0)
        self.Connector = self.addAttr("connector", "string", "standard")
        self.CtlGroup = self.addAttr("ctrlGrp", "string", "")
        self.uiHost = self.addAttr("host", "string", "")
        self.JointNames = self.addAttr("joint_names", "string", "")
        self.JointRotOffX = self.addAttr(
            "joint_rot_offset_x", "double", 0.0, -360.0, 360.0)
        self.JointRotOffY = self.addAttr(
            "joint_rot_offset_y", "double", 0.0, -360.0, 360.0)
        self.JointRotOffZ = self.addAttr(
            "joint_rot_offset_z", "double", 0.0, -360.0, 360.0)

        self.jointPrimaryAxis = self.addAttr("primary" , "string" , "Y")
        self.jointSecondaryAxis = self.addAttr("secondary", "string", "Z")

        # Items============================================================
        typeItems = [self.guideType , self.guideType]
        for type in self.COMPATIBLE:
            typeItems.append(type)
            typeItems.append(type)

        connectorItems = ["standard", "standard"]
        for item in self.CONNECTORS:
            connectorItems.append(item)
            connectorItems.append(item)

    def addObjects(self):
        """

        Args:

        Returns:

        """
        self.root = self.addRoot

    def addAttributes(self):
        """

        Returns:

        """
        return

    def addLoc(self, name, parent, position=None):
        """
        给组件添加一个loc对象
        Args:
            name: 名称
            parent: 父组件
            position: 默认的位置

        Returns: loc object

        """
        if name not in self.traDict.keys():
            self.traDict[name] = aboutTransform.getTransformFromPos(position)
        if name in self.addObjDict.keys():
            loc = self.addObjDict[name].create(
                parent , self.getName(name) , self.traDict[name] , color = 17
            )
        else:
            loc = aboutIcon.CreateControl(
                parent , "Locator" , self.getName(name) , m = self.traDict[name])

        return loc

    def postDraw(self):
        """Add anything to the guide after drawing it.

        Note:
            REIMPLEMENT. This method should be reimplemented in each component.

        """
        return

    @property
    def addRoot(self):
        """添加root组件

        此方法可以初始化对象或绘制组件

        Returns:
            dagNode: The root

        """
        if "root" not in self.traDict.keys():
            self.traDict["root"] = aboutTransform.getTransformFromPos(
                datatypes.Vector(0 , 0 , 0))

        self.root = aboutIcon.CreateRootControl(self.parent , self.getName("root") , self.traDict["root"])
        for attrName in self.attrNames:
            attrDefs = self.attrDefs[attrName]
            attrDefs.create(self.root)

        return self.root

    def draw(self , parent):
        """

        Args:
            parent:

        Returns:

        """
        self.parent = parent
        self.setIndex(self.parent)
        self.addObjects()
        self.postDraw()
        pm.select(self.root)

    def drawGuide(self, parent):
        """Draw the guide in the scene from the UI command.

        Args:
            parent (dagNode): the parent of the component.

        """
        # if not self.isGuidePos():
        #     return False
            
        self.draw(parent)
        aboutTransform.resetTransform(self.root, r = False, s = False)

        # reset size
        self.root.scale.set(1, 1, 1)

        return True

    def isGuidePos(self):
        self.sections_number = None
        self.dir_axis = None
        self.spacing = None

        # for name in self.save_transform:

        #     if "#" in name:
        #         init_window = 

    def get_divisions(self):
        """

        Returns:

        """
        return

    def add_ref_Axis(self , loc , vis = True , invert = False , w = 0.5):
        """
        添加轴的曲线
        Args:
            loc: locator或者root组件
            vis: vis属性开关
            invert:
            w: 宽度

        Returns:

        """
        axis = aboutIcon.axis(loc , self.getName("axis") ,
                              width = w , m = loc.getMatrix(worldSpace = True))
        pm.parent(axis , w = True)
        pm.makeIdentity(axis , apply = True , t = False , r = False , s = True , n = 0)
        if vis and invert:
            vis_node = aboutNode.createReverseNode(vis, loc + "_AxisReverse")
            vis = vis_node.outputX

        for shape in axis.getShapes():
            if vis:
                pm.connectAttr(vis , shape.attr("visibility"))
            shape.isHistoricallyInteresting.set(False)
            shape.lineWidth.set(3)
            loc.addChild(shape, add=True, shape=True)
        pm.delete(axis)

    def add_ref_joint(self, loc, vis_attr=None, width=.5):
        """Add a visual reference joint to a locator or root of the guide

        Args:
            loc (dagNode): locator or guide root
            vis_attr (attr list, optional): attribute to activate or deactivate
                the visual ref. Should be a list [attr1, attr2]
            width (float, optional): icon width
        """
        add_ref_joint = aboutIcon.sphere(loc,
                                    self.getName("joint"),
                                    width=width,
                                    color=[0, 1, 0],
                                    m=loc.getMatrix(worldSpace=True))
        pm.parent(add_ref_joint, world=True)
        pm.makeIdentity(add_ref_joint, apply=True,
                        t=False, r=False, s=True, n=0)

        for shp in add_ref_joint.getShapes():
            if vis_attr:
                multNode = aboutNode.createMulNode(vis_attr[0],
                                   vis_attr[1],
                                   shp.attr("visibility")
                                    )
                pm.rename(multNode, shp + "_Mult")
            shp.isHistoricallyInteresting.set(False)

            loc.addChild(shp, add=True, shape=True)
        pm.delete(add_ref_joint)

    def setIndex(self, model):
        """更新组件index以获取下一个有效的index

        Args:
            model (dagNode): 组件的父级组件

        """
        self.model = model.getParent(generations=-1)

        # Find next index available
        while True:
            obj = aboutDag.findChild(self.model, self.getName("root"))
            if not obj or (self.root and obj == self.root):
                break
            self.setAttrDefValue("guide_index", self.values["guide_index"] + 1)

    def set_hierarchy(self, node):
        """
        
        Args:
            node:

        Returns:

        """
        self.root = node
        self.model = self.root.getParent(generations=-1)

        # ==============================================
        # set settings
        if not self.root.hasAttr("guide_type"):
            aboutLog.Logger.exception("Current selection is not \
                a root or highest guide !")
            self.valid = False
            return
        self.setAttrDefValuesFromProperty(self.root)

        # ==============================================
        # get objects
        for name in self.save_transform:
            if "#" in name:
                i = 0
                while not self.minmax[name].max > 0 or \
                    i < self.minmax[name].max:
                    localName = aboutString.replaceSharpWithPadding(name, i)

                    nod = aboutDag.findChild(self.model, self.getName(localName))
                    if not nod:
                        break

                    self.traDict[localName] = nod.getMatrix(worldSpace = True)
                    self.traList.append(nod.getMatrix(worldSpace = True))
                    self.posDict[localName] = nod.getTranslation(space="world")
                    self.posList.append(nod.getTranslation(space="world"))

                    i += 1
                if i < self.minmax[name].min:
                    aboutLog.Logger.exception("Minimum of object requiered for "
                              + name + " hasn't been reached!!")
                    self.valid = False
                    continue
            else:
                nod = aboutDag.findChild(self.model, self.getName(name))
                if not nod:
                    aboutLog.Logger.exception("Can not find object : %s" % self.getName(name))
                    self.valid = False
                    continue

                self.traDict[name] = nod.getMatrix(worldSpace = True)
                self.traList.append(nod.getMatrix(worldSpace = True))
                self.posDict[name] = nod.getTranslation(space = "world")
                self.posList.append(nod.getTranslation(space = "world"))

        for name in self.save_blade:
            if "#" in name:
                i = 0
                while not self.minmax_blade[name].max > 0 or \
                    i < self.minmax_blade[name].max:
                    localName = aboutString.replaceSharpWithPadding(name, i)

                    nod = aboutDag.findChild(self.model, self.getName(localName))
                    if not nod:
                        break
                    self.blades[localName] = aboutVector.Blade(
                        nod.getMatrix(worldSpace = True))
                    i += 1
                if i < self.minmax_blade[name].min:
                    aboutLog.Logger.exception("Minimum of object requiered for "
                              + name + " hasn't been reached!!")
                    self.valid = False
                    continue
            else:
                nod = aboutDag.findChild(self.model, self.getName(name))
                if not nod:
                    aboutLog.Logger.exception("Can not find object : %s" % self.getName(name))
                    self.valid = False
                    continue

                self.blades[name] = aboutVector.Blade(
                    nod.getMatrix(worldSpace=True)
                )
        self.size = self.getSize

    @property
    def getSize(self):
        """

        Returns:

        """
        size = 0.1
        for pos in self.posList:
            dist = aboutVector.getDistance(self.posDict["root"], pos)
            size = max(size, dist)
        size = max(size, 0.1)

        return size
    
    def getName(self , name):
        """获得物体的全部名称

                Args:
                    name (str): Localname of the element.

                Returns:
                    str: Element fullname.
                """
        return self.fullName + "_" + name
    
    @property
    def getType(self):

        return self.GUIDETYPE

    @property
    def getObjectsNames(self):

        names = set()
        names.update(self.save_transform)
        names.update(self.save_primitive)
        names.update(self.save_blade)

        return names

    @property
    def getFullName(self):
        """Return the fullname of the component.

        Returns:
            str: Component fullname.

        """
        return self.values["guide_name"] + "_" + self.values["guide_side"] + \
            str(self.values["guide_index"])

    fullName = getFullName
    type = getType
    objectNames = getObjectsNames





