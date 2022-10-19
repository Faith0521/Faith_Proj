# -*- coding: utf-8 -*-
# @Author: 46314
# @Date:   2022-08-26 19:15:51
# @Last Modified by:   46314
# @Last Modified time: 2022-08-26 19:17:42
import math
from maya import cmds as mc
from pymel import core as pm
from maya import mel as mel

def createRBFNode(driverNode,
                  poseMode=1):
    """
    create one new weightDriver node
    @param driverNode:
    @param twistAxis:
    @param poseMode:
    @return:
    """
    driverShape = mc.createNode("weightDriver")
    driver = mc.listRelatives(driverShape, p=True)
    mc.setAttr("%s.v" % driver[0], 0, l=True)

    mc.delete(mc.pointConstraint(driverNode, driver[0]))
    driver_grp = driverNode + "_driverGrp"
    if not mc.objExists(driverNode + "_driverGrp"):
        mc.createNode("transform", name = driverNode + "_driverGrp")
    driver = mc.rename(driver[0], driverNode + "_WD")
    driverShape = mc.listRelatives(driver, s=True)[0]
    mc.parent(driver, driver_grp)

    dirValues,offsetNode = getPrimaryAxis(driverNode, 0)

    size = abs(dirValues[2]) * 0.6
    if size > 0:
        mc.setAttr(driverShape + ".iconSize", size)

    mc.setAttr(driverShape + ".type", 1)
    mc.setAttr(driverShape + ".twistAxis",dirValues[0])
    mc.setAttr("%s.driverList[0].pose[0].poseMode"%driverShape, poseMode)

    # make the connections
    mc.connectAttr("%s.worldMatrix[0]"%driverNode, "%s.driverList[0].driverInput"%driverShape)

    wm_ma = pm.getAttr("%s.worldMatrix[0]"%driverNode)
    pm.setAttr("%s.driverList[0].pose[0].poseMatrix"%driverShape, wm_ma)

    pa_ma = pm.getAttr("%s.parentMatrix[0]"%driverNode)
    pm.setAttr("%s.driverList[0].pose[0].poseParentMatrix"%driverShape, pa_ma)

    mc.refresh()

    # set pose
    attrs = mc.listAttr(driverNode, k=1, w=1, u=1, s=1)
    if not attrs:
        msg = "No keyable attributes found on the given node."
        mc.warning(msg)

        attrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]

    valueList = []
    attrList = []
    for attr in attrs:
        if not mc.getAttr("%s.%s"%(driverNode, attr), l=1):
            value = mc.getAttr("%s.%s"%(driverNode, attr))
            attrList.append(attr)
            valueList.append(value)

    mel.eval("setAttr " + driverShape + ".driverList[0].pose[0].cpa -type \"stringArray\" " + str(len(attrList)) + " " + " ".join(attrList))
    mel.eval("setAttr " + driverShape + ".driverList[0].pose[0].cpv -type \"doubleArray\" " + str(len(valueList)-1) + " " + floatArrayToString(valueList[1:], " "))
    mc.setAttr("%s.driverList[0].pose[0].cpro"%driverShape, mc.getAttr(driverNode + ".rotateOrder"))

    return driver


def createRbfPose(rbfNode, driverNode):
    """

    @param rbfNode:
    @param driverNode:
    @return:
    """
    item = findEmptyMultiIndex("%s.driverList[0].pose"%rbfNode)
    mc.setAttr("%s.driverList[0].pose[%d].poseMode" % (rbfNode, item), 1)

    # make the connections
    wm_ma = pm.getAttr("%s.worldMatrix[0]" % driverNode)
    pm.setAttr("%s.driverList[0].pose[%d].poseMatrix" % (rbfNode, item), wm_ma)

    pa_ma = pm.getAttr("%s.parentMatrix[0]" % driverNode)
    pm.setAttr("%s.driverList[0].pose[%d].poseParentMatrix" % (rbfNode, item), pa_ma)

    mc.refresh()

    # set pose
    attrs = mc.listAttr(driverNode, k=1, w=1, u=1, s=1)
    if not attrs:
        msg = "No keyable attributes found on the given node."
        mc.warning(msg)

        attrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]

    valueList = []
    attrList = []
    for attr in attrs:
        if not mc.getAttr("%s.%s" % (driverNode, attr), l=1):
            value = mc.getAttr("%s.%s" % (driverNode, attr))
            attrList.append(attr)
            valueList.append(value)
    # print(attrs)
    # print(floatArrayToString(valueList, " "))
    mel.eval("setAttr " + rbfNode + ".driverList[0].pose[" + str(item) + "].cpa -type \"stringArray\" " + str(
        len(attrList)) + " " + " ".join(attrList))
    mel.eval("setAttr " + rbfNode + ".driverList[0].pose[" + str(item) + "].cpv -type \"doubleArray\" " + str(
        len(valueList) - 1) + " " + floatArrayToString(valueList[1:], " "))
    mc.setAttr("%s.driverList[0].pose[%d].cpro" % (rbfNode, item), mc.getAttr(driverNode + ".rotateOrder"))

def floatArrayToString(array, separator):
    """

    @param array:
    @param separator:
    @return:
    """
    result = ""
    for i in array:
        if result == "":
            result = str(i)
        else:
            result += separator + str(i)
    return result


def findEmptyMultiIndex(attr):
    """

    @param rbfNode:
    @return:
    """
    index = -1
    ids = mc.getAttr(attr, mi=1)
    for i in range(len(ids)):
        if i != ids[i] and index == -1:
            index = i
            break
    if index == -1:
        index = len(ids)

    return index

def getPrimaryAxis(node, setOption):
    """

    @param node:
    @param setOption:
    @param values:
    @return:
    """
    offsetNode = getJointTranslation(node)
    if offsetNode != "":
        pos = mc.getAttr(offsetNode + ".t")[0]
    else:
        pos = mc.getAttr(node + ".t")[0]
        offsetNode = node

    axis = 1
    dir = 1
    offset = 0
    if ((abs(pos[0]) > abs(pos[1])) and (abs(pos[0]) > abs(pos[2]))):
        axis = 1
        if pos[0] < 0:
            dir = -1
        offset = pos[0]
    elif (abs(pos[1]) > abs(pos[2])):
        axis = 2
        if pos[1] < 0:
            dir = -1
        offset = pos[1]
    else:
        axis = 3
        if pos[2] < 0:
            dir = -1
        offset = pos[2]

    if ((abs(pos[0]) == abs(pos[1])) and (abs(pos[0]) == abs(pos[2]))):
        axis = 1

    values = [axis - 1, dir, offset]

    return [values, offsetNode]

def getJointTranslation(node):
    """

    @param node:
    @return:
    """
    rel = mc.listRelatives(node, c=True, type="transform")
    endOfChain = 0
    result = ""

    while endOfChain == 0:
        if rel:
            for r in rel:
                pos = mc.getAttr(r + ".t")[0]
                posSum = math.floor((pos[0] + pos[1] + pos[2]) * 1000) / 1000
                if abs(posSum) > 0.1:
                    return r
                result = getJointTranslation(r)
            endOfChain = 1
        else:
            endOfChain = 1

    if result == "":
        return node

    return result

def getRbfDriverIndices(driver):
    """

    :param driver:
    :return:
    """
    allIds = mc.getAttr("%s.driverList"%driver, mi=True)
    ids = []
    for id in allIds:
        conn = mc.listConnections("%s.driverList[%d].driverInput"%(driver, id), s=True,d=False)
        if conn:
            ids.append(id)
    return ids

def shapesDriver_getWeightDriverDriver(driver):
    """

    :param driver:
    :param ids:
    :return:
    """
    nodes = []
    ids = getRbfDriverIndices(driver)
    for id in ids:
        tmp = mc.listConnections("%s.driverList[%d].driverInput"%(driver, id), p=1)
        tmp = pm.mel.stringToStringArray(tmp[0], ".")
        nodes.append(tmp[0])
    return nodes

def mirrorRbfNode(solver):
    """

    @param solver:
    @return:
    """
    return