# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:08
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-14 18:57:41

import pymel.core as pm , maya.mel as mel
import pymel.core.datatypes as datatypes
import re
import Faith
from . import aboutAdd,aboutCurve
from maya import OpenMaya as om


icon_path = Faith.__path__[0].replace('\\', '/') + "/Control/Controls.ma"

def ImportIconsFile(iconFilePath):
    """
    Import controller file to create temp control
    Args:
        iconFilePath: file path

    Returns:

    """
    iconGrp = "iconsGroup"
    
    if not pm.objExists("iconsGroup"):
        iconGrp = pm.createNode("transform" , n = "iconsGroup")
        iconGrp.v.set(0)
        
    beforeObj = pm.ls(assemblies=True, l=True)
    fromBefore = []
    readLine = 0

    # read file
    fileId = open(iconFilePath, "r")
    nextLine = fileId.readline()
    previousLine = ""

    while len(nextLine) > 0:
        if not readLine:
            if pm.mel.gmatch(nextLine, \
                "\t*"):
                previousLine += nextLine
                nextLine = fileId.readline()
                continue

        if pm.mel.gmatch(nextLine, "createNode nurbsCurve*"):
            readLine = 1
            mel.eval(previousLine)
            previousLine = nextLine
            nextLine = fileId.readline()
            continue

        if readLine:
            if pm.mel.gmatch(nextLine, "\t*"):
                previousLine += nextLine
                nextLine = fileId.readline()
                continue

            else:
                readLine = 0
                mel.eval(previousLine)

        previousLine = nextLine
        nextLine = fileId.readline()

    fileId.close()
    afterObj = pm.ls(assemblies=True, l=True)

    for i in range(len(afterObj)):
        for y in range(len(beforeObj)):
            if afterObj[i] == beforeObj[y]:
                fromBefore.append(afterObj[i])
    if fromBefore:
        for Del in fromBefore:
            afterObj.remove(Del)


    for obj in afterObj:
        pm.parent(obj, iconGrp)

    pm.select(clear=True)
    print("--------> Import controls success !")

def SetDrawOverride(node , color):
    """

    Args:
        node:
        color:

    Returns:

    """
    aboutCurve.set_color(node , color)

def AddControl(parent , offset , posParent ,
               type , name , m , pr , sec , scale = 1.0):
    """

    Args:
        parent:
        offset:
        posParent:
        type:
        name:
        m:
        pr:
        sec:
        scale:

    Returns:

    """
    iconsGrp = "iconsGrp"
    if not pm.objExists("iconsGrp"):
        iconsGrp = pm.createNode("transform" , n = "iconsGrp")
        iconsGrp.v.set(0)
        ImportIconsFile(icon_path)

    control = pm.duplicate("{0}_icon".format(type) ,
                           n = name)[0]
    control.setMatrix(m)
    pm.parent(control , parent)
    scal = GetScale()
    control.setScale((scale*scal , scale*scal , scale*scal) , space = "world")
    pm.makeIdentity(control , apply = True , t = True , r = True , s = True)

    pm.select(clear=True)
    tempJoint = pm.joint(n = "AxisJnt")
    pm.delete(pm.pointConstraint(posParent, tempJoint))
    fixObjAxis(tempJoint, pr, sec)
    pm.delete(pm.orientConstraint(tempJoint, offset))
    FixCtrlAxis(tempJoint, [control], pr, sec)
    pm.delete(tempJoint)

    return  control

def fixObjAxis(obj , prAxis , secAxis):
    """
    Fix World Orient Axis
    Args:
        obj: modify axis object
        prAxis: mod primary axis
        secAxis:mod secondary axis

    Returns:

    """
    tempLoc = pm.spaceLocator(n = "tempLoc")
    pm.delete(pm.pointConstraint(obj , tempLoc))
    pm.move(0 , 1 , 0 , tempLoc , r = True , os = True)
    praxis = GetVectFromAxis(prAxis)
    secaxis = GetVectFromAxis(secAxis)
    pm.delete(pm.aimConstraint(tempLoc , obj , upVector=secaxis, worldUpType="vector",
                     aimVector=praxis, worldUpVector=(0, 0, 1)))
    pm.makeIdentity(obj , apply = True , r = True)
    pm.delete(tempLoc)

def GetVectFromAxis(axis):
    """

    Args:
        axis:

    Returns:

    """
    vec = datatypes.Vector()
    if re.search("X" , axis) : vec = datatypes.Vector(1 , 0 , 0)
    if re.search("Y" , axis) : vec = datatypes.Vector(0, 1, 0)
    if re.search("Z" , axis) : vec = datatypes.Vector(0, 0, 1)
    if re.search("-" , axis):
        vec *= -1
    return vec

def FixCtrlAxis(joint , ctrlList , primary , secondary):
    """

    Args:
        joint:
        ctrlList:
        primary:
        secondary:

    Returns:

    """
    pm.select(d = True)

    jointPos = joint.getTranslation(space = "world")
    for ctrl in ctrlList:
        pm.select("{0}.cv[0:99]".format(ctrl.getShape()) , add = True)

    tempclus = pm.cluster(envelope = 1 , n = "TempCluster")
    pm.xform(tempclus[1].rotatePivot , ws = True , t = jointPos)
    tempXform = pm.createNode("transform", n="tempXform")
    orient = pm.orientConstraint(tempXform , tempclus[1])

    ModifyControllerAxis(orient , primary , secondary)
    pm.delete(ctrlList , ch = True)
    pm.delete(tempclus[1] , tempXform)

def ModifyControllerAxis(constraint, primary, secondary):
    """

    Args:
        constraint:
        primary:
        secondary:

    Returns:

    """
    NegPriMult = 1
    NegPriYAdd = 0
    NegSecXAdd = 0
    if re.search("-", primary):
        NegPriMult = -1
        NegPriYAdd = 180
    if re.search("-", secondary):
        NegSecXAdd = 180
    if re.search("X", primary) and re.search("Y", secondary):
        constraint.offset.set(NegSecXAdd, NegPriYAdd, 0, type="float3")
    if re.search("X", primary) and re.search("Z", secondary):
        constraint.offset.set((NegSecXAdd + (180 * NegPriMult)), NegPriYAdd, 0, type="float3")
    if re.search("Y", primary) and re.search("Z", secondary):
        constraint.offset.set((NegSecXAdd + (90 * NegPriMult)), NegPriYAdd, 90, type="float3")
    if re.search("Y", primary) and re.search("X", secondary):
        constraint.offset.set((NegSecXAdd + (180 * NegPriMult)), NegPriYAdd - 90, 90, type="float3")
    if re.search("Z", primary) and re.search("X", secondary):
        constraint.offset.set((NegSecXAdd + (-90 * NegPriMult)), NegPriYAdd - 90, 0, type="float3")
    if re.search("Z", primary) and re.search("Y", secondary):
        constraint.offset.set(NegSecXAdd, NegPriYAdd, 90, type="float3")

def GetScale():
    scale = 1.0
    maxY = 0

    if not pm.objExists("Proxy_Guide"):
        return scale

    objects = pm.listRelatives("Proxy_Guide" , f = True , ad = True , type = "transform")

    for j in objects:
        pos = j.getTranslation(space = "world")
        posY = float('{:.16f}'.format(pos[1]))
        if posY > maxY:
            maxY = posY

    if maxY > 0:
        scale = maxY / 17.176163

    return scale

def CreateRootControl(parent , name , m):
    root = pm.duplicate("COG_icon" , n = name)[0]
    root.setMatrix(m)

    pm.makeIdentity(root , apply = True , t = True , r = True , s = True)
    pm.parent(root , parent)

    return root

def CreateControl(parent , typ , name , m, **kwargs):
    """

    Args:
        parent:
        typ:
        name:
        m:

    Returns:

    """
    if "w" not in kwargs.keys():
        kwargs["w"] = 1
    if "h" not in kwargs.keys():
        kwargs["h"] = 1
    if "d" not in kwargs.keys():
        kwargs["d"] = 1
    if "po" not in kwargs.keys():
        kwargs["po"] = None
    if "ro" not in kwargs.keys():
        kwargs["ro"] = None

    control = pm.duplicate("{0}_icon".format(typ), n = name)[0]
    control.setMatrix(m)
    control.setScale((kwargs["w"]*1.5, kwargs["h"]*1.5, kwargs["d"]*1.5), space = "object")
    pm.makeIdentity(control, apply=True, t=True, r=True, s=True)
    pm.parent(control, parent)

    return control

def getPointArrayWithOffset(point_pos, pos_offset=None, rot_offset=None):
    """获取具有偏移量的Point数组

    将向量列表转换为浮点数列表并添加位置和旋转偏移

    Arguments:
        point_pos (list of vector): 点的位置
        pos_offset (vector):  位置偏移
        rot_offset (vector): 旋转偏移

    Returns:
        list of vector: 新的点的位置

    """
    points = []
    for v in point_pos:
        if rot_offset:
            mv = om.MVector(v.x , v.y , v.z)
            mv = mv.rotateBy(om.MEulerRotation(rot_offset.x,
                                               rot_offset.y,
                                               rot_offset.z))
            v = datatypes.Vector(mv.x , mv.y , mv.z)
        if pos_offset:
            v += pos_offset

        points.append(v)
    return points

def axis(parent=None,
         name="axis",
         width=1,
         color=[0, 0, 0],
         m=datatypes.Matrix(),
         pos_offset=None,
         rot_offset=None):
    """创建带有AXIS形状的曲线

    Arguments:
        parent (dagNode): 新创建曲线的父对象
        name (str): 曲线的名称
        width (float): 曲线的宽度
        color (int or list of float): RGB颜色序列
        m (matrix): 曲线的transform矩阵
        pos_offset (vector): 曲线的xyz位置偏移 
        rot_offset (vector): 曲线的xyz旋转偏移 

    Returns:
        dagNode: 新创建的曲线

    """
    dlen = width * 0.5

    v0 = datatypes.Vector(0, 0, 0)
    v1 = datatypes.Vector(dlen, 0, 0)
    v2 = datatypes.Vector(0, dlen, 0)
    v3 = datatypes.Vector(0, 0, dlen)

    points = getPointArrayWithOffset([v0, v1], pos_offset, rot_offset)
    node = aboutCurve.addCurve(parent, name, points, False, 1, m)
    SetDrawOverride(node, 4)

    points = getPointArrayWithOffset([v0, v2], pos_offset, rot_offset)
    crv_0 = aboutCurve.addCurve(parent, name, points, False, 1, m)
    SetDrawOverride(crv_0, 14)

    points = getPointArrayWithOffset([v0, v3], pos_offset, rot_offset)
    crv_1 = aboutCurve.addCurve(parent, name, points, False, 1, m)
    SetDrawOverride(crv_1, 6)

    for crv in [crv_0, crv_1]:
        for shp in crv.listRelatives(shapes=True):
            node.addChild(shp, add=True, shape=True)
        pm.delete(crv)

    return node

def sphere(parent=None,
           name="sphere",
           width=1,
           color=[0, 0, 0],
           m=datatypes.Matrix(),
           pos_offset=None,
           rot_offset=None,
           degree=3):
    """Create a curve with a SPHERE shape.

    Arguments:
        parent (dagNode): The parent object of the newly created curve.
        name (str): Name of the curve.
        width (float): Width of the shape.
        color (int or list of float): The color in index base or RGB.
        m (matrix): The global transformation of the curve.
        pos_offset (vector): The xyz position offset of the curve from
            its center.
        rot_offset (vector): The xyz rotation offset of the curve from
            its center. xyz in radians

    Returns:
        dagNode: The newly created icon.

    """
    dlen = width * .5

    v0 = datatypes.Vector(0, 0, -dlen * 1.108)
    v1 = datatypes.Vector(dlen * .78, 0, -dlen * .78)
    v2 = datatypes.Vector(dlen * 1.108, 0, 0)
    v3 = datatypes.Vector(dlen * .78, 0, dlen * .78)
    v4 = datatypes.Vector(0, 0, dlen * 1.108)
    v5 = datatypes.Vector(-dlen * .78, 0, dlen * .78)
    v6 = datatypes.Vector(-dlen * 1.108, 0, 0)
    v7 = datatypes.Vector(-dlen * .78, 0, -dlen * .78)

    ro = datatypes.Vector([1.5708, 0, 0])

    points = getPointArrayWithOffset(
        [v0, v1, v2, v3, v4, v5, v6, v7], pos_offset, rot_offset)
    node = aboutCurve.addCurve(parent, name, points, True, degree, m)

    if rot_offset:
        rot_offset += ro
    else:
        rot_offset = ro
    points = getPointArrayWithOffset(
        [v0, v1, v2, v3, v4, v5, v6, v7], pos_offset, rot_offset)
    crv_0 = aboutCurve.addCurve(parent, node + "_0crv", points, True, degree, m)

    ro = datatypes.Vector([1.5708, 0, 1.5708])
    if rot_offset:
        rot_offset += ro
    else:
        rot_offset = ro
    points = getPointArrayWithOffset(
        [v0, v1, v2, v3, v4, v5, v6, v7], pos_offset, rot_offset + ro + ro)

    crv_1 = aboutCurve.addCurve(parent, node + "_1crv", points, True, degree, m)

    for crv in [crv_0, crv_1]:
        for shp in crv.listRelatives(shapes=True):
            node.addChild(shp, add=True, shape=True)
        pm.delete(crv)

    SetDrawOverride(node, color)

    return node


















