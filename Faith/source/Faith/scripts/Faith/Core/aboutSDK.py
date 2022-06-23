# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-06-19 16:49:53
# @Last Modified by:   yinyufei
# @Last Modified time: 2022-06-23 13:56:50

from Faith.Core import aboutPy, utils
import json
if aboutPy.PY2:
    import cPickle
else:
    import _pickle
import pprint
import pymel.core as pm

SDK_UTILITY_TYPE = ("blendWeighted",)
SDK_ANIMCURVES_TYPE = ("animCurveUA", "animCurveUL", "animCurveUU")

# ==============================================================================
# Data export
# ==============================================================================
def _importData(filePath):
    """Return the contents of a json file. Expecting, but not limited to,
    a dictionary.

    Args:
        filePath (string): path to file

    Returns:
        dict: contents of json file, expected dict
    """
    try:
        with open(filePath, "r") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(e)


def _exportData(data, filePath):
    """export data, dict, to filepath provided

    Args:
        data (dict): expected dict, not limited to
        filePath (string): path to output json file
    """
    try:
        with open(filePath, "w") as f:
            json.dump(data, f, sort_keys=False, indent=4)
    except Exception as e:
        print(e)


# ==============================================================================
# pymel Convenience
# ==============================================================================

def getPynodes(nodes):
    """Conevenience function to allow uses to pass in strings, but convert to
    pynodes if not already.

    Args:
        nodes (list): string names

    Returns:
        list: of pynodes
    """
    pynodes = []
    for node in nodes:
        if isinstance(node, str):
            node = pm.PyNode(node)
        pynodes.append(node)
    return pynodes

def getSDKInfoFromNode(node, expType="after"):
    """
    export sdk information of type 'after'
    :param node: node to export
    :return:
    """
    allSDKInfo_dict = {}
    if pm.nodeType(node) == "blendShape":
        AllAlias = pm.aliasAttr(node, q = True)
        AttrsList = [AllAlias[i] for i in range(
            0, len(AllAlias), 2
        )]
    else:
        AttrsList = pm.listAttr(node, k = True)
    for eachAttr in AttrsList:
        if pm.objExists("%s.%s"%(node, eachAttr)):
            testConnections = pm.listConnections("%s.%s"%(node, eachAttr),
                                                 plugs = True)
            if testConnections:
                retrievedSDKNodes = getConnectedSDKs(
                    attr = "%s.%s"%(node, eachAttr),expType=expType)
                if expType == "front":
                    retrievedSDKNodes.extend(getMultSDKs("%s.%s"%(node, eachAttr)))
                if expType == "front":
                    for animPlug, targetPlug in retrievedSDKNodes:
                        allSDKInfo_dict[animPlug.nodeName()] = getSDKInfo(animPlug.node())
                else:
                    for targetPlug, animPlug in retrievedSDKNodes:
                        allSDKInfo_dict[animPlug.nodeName()] = getSDKInfo(animPlug.node())
    return allSDKInfo_dict

def getMultSDKs(attr):
    """

    :param attr:
    :return:
    """
    sdkDrivers = []
    for sdkUtility in SDK_UTILITY_TYPE:
        blend_NodePair = pm.listConnections(attr,
                                            source=True,
                                            type=sdkUtility,
                                            exactType=True,
                                            plugs=True,
                                            connections=True,
                                            sourceFirst=True,
                                            scn=True) or []

        if not blend_NodePair:
            continue
        for pairs in blend_NodePair:
            blw_inAttr = pairs[0].replace("output","input")
            sdkPairs = getConnectedSDKs(blw_inAttr, expType="front")
            for sPair in sdkPairs:
                sdkDrivers.append([sPair[0], pairs[1]])
    return sdkDrivers

def createSDKFromDict(sdkInfo_dict, name):
    """

    :param sdkInfo_dict:
    :return:
    """
    sdkNode = pm.createNode(sdkInfo_dict["type"], name=name, ss=True)
    pm.connectAttr("{0}.{1}".format(sdkInfo_dict["driverNode"],
                                    sdkInfo_dict["driverAttr"]),
                   "{0}.input".format(sdkNode), f=True)

    drivenAttrPlug = "{0}.{1}".format(sdkInfo_dict["drivenNode"],
                                      sdkInfo_dict["drivenAttr"])

    if pm.listConnections(drivenAttrPlug):
        targetAttrPlug = getBlendNodes(drivenAttrPlug)
    else:
        targetAttrPlug = drivenAttrPlug

    pm.connectAttr(sdkNode.output, targetAttrPlug, f=True)

    animKeys = sdkInfo_dict["keys"]
    for index in range(0, len(animKeys)):
        frameValue = animKeys[index]
        pm.setKeyframe(sdkNode,
                       float=frameValue[0],
                       value=frameValue[1],
                       itt=frameValue[2],
                       ott=frameValue[3])

    sdkNode.setAttr("preInfinity", sdkInfo_dict["preInfinity"])
    sdkNode.setAttr("postInfinity", sdkInfo_dict["postInfinity"])
    pm.keyTangent(sdkNode)
    sdkNode.setWeighted(sdkInfo_dict["weightedTangents"])

    return sdkNode

def getBlendNodes(attrPlug):
    """

    :param attrPlug:
    :return:
    """
    blendNode = pm.listConnections(attrPlug, scn = True)
    if pm.nodeType(blendNode[0]) in SDK_ANIMCURVES_TYPE:
        existingAnimNode = blendNode[0]
        blendNodeName = "{0}_blw".format(attrPlug.replace(".","_"))
        blendNode = [pm.createNode("blendWeighted", n = blendNodeName)]
        pm.connectAttr(blendNode[0].attr("output"), attrPlug, f = True)
        destPlug = "{0}.input[0]".format(blendNode[0].name())
        pm.connectAttr(existingAnimNode.attr("output"), destPlug, f = True)
    if pm.nodeType(blendNode[0]) in SDK_UTILITY_TYPE:
        blendNode = blendNode[0]
    if type(blendNode) == list:
        blendNode = blendNode[0]
    numOfInputs = len(blendNode.getAttr("input"))
    destPlug = "{0}.input[{1}]".format(blendNode.name(), numOfInputs)
    return destPlug

def getSDKInfo(animNode):
    """
    get all the information from an sdk/animCurve in a dictioanry
    for exporting.

    :param animNode (pynode): name of node, pynode
    :return: dict: dictionary of all the attrs to be exported
    """
    sdkInfo_dict = {}
    sdkKey_Info = []
    numberOfKeys = len(pm.listAttr("{0}.ktv".format(animNode), multi=True)) / 3
    itt_list = pm.keyTangent(animNode, itt=True, q=True)
    ott_list = pm.keyTangent(animNode, ott=True, q=True)
    # maya doesnt return value if there is only one key frame set.
    if itt_list == None:
        itt_list = ["linear"]
    if ott_list == None:
        ott_list = ["linear"]

    for index in range(int(numberOfKeys)):
        value = pm.getAttr("{0}.keyTimeValue[{1}]".format(animNode, index))
        absoluteValue = pm.keyframe(animNode,
                                    q=True,
                                    valueChange=True,
                                    index=index)[0]
        keyData = [value[0], absoluteValue, itt_list[index], ott_list[index]]
        sdkKey_Info.append(keyData)
    sdkInfo_dict["keys"] = sdkKey_Info
    sdkInfo_dict["type"] = animNode.type()
    sdkInfo_dict["preInfinity"] = animNode.getAttr("preInfinity")
    sdkInfo_dict["postInfinity"] = animNode.getAttr("postInfinity")
    sdkInfo_dict["weightedTangents"] = animNode.getAttr("weightedTangents")

    animNodeInputPlug = "{0}.input".format(animNode.nodeName())
    sourceDriverAttr = pm.listConnections(animNodeInputPlug,
                                          source=True,
                                          plugs=True,
                                          scn=True)[0]
    driverNode, driverAttr = sourceDriverAttr.split(".")
    sdkInfo_dict["driverNode"] = driverNode
    sdkInfo_dict["driverAttr"] = driverAttr

    animNodeOutputPlug = "{0}.output".format(animNode.nodeName())
    drivenNode, drivenAttr = getSDKDestination(animNodeOutputPlug)
    sdkInfo_dict["drivenNode"] = drivenNode
    sdkInfo_dict["drivenAttr"] = drivenAttr

    return sdkInfo_dict

def getSDKDestination(animNodeOutputPlug):
    """Get the final destination of the sdk node, skips blendweighted
    and conversion node to get the transform node.
    TODO: Open this up to provided type destination

    Args:
        animNodeOutputPlug (string): animationNode.output

    Returns:
        list: name of the node, and attr
    """
    connectionTypes = [SDK_UTILITY_TYPE[0], "transform", "blendShape"]
    targetDrivenAttr = pm.listConnections(animNodeOutputPlug,
                                          source=False,
                                          destination=True,
                                          plugs=True,
                                          type=connectionTypes,
                                          scn=True)

    if pm.nodeType(targetDrivenAttr[0]) == "blendWeighted":
        blendNodeOutAttr = targetDrivenAttr[0].node().attr("output")
        targetDrivenAttr = pm.listConnections(blendNodeOutAttr,
                                              destination=True,
                                              plugs=True,
                                              scn=True)

    if pm.nodeType(targetDrivenAttr[0]) == "blendShape":
        drivenNode = targetDrivenAttr[0].split('.')[0]
        drivenAttr = pm.aliasAttr(targetDrivenAttr[0].node(), q = True)[0]

    else:
        drivenNode, drivenAttr = targetDrivenAttr[0].split(".")

    return drivenNode, drivenAttr

def getConnectedSDKs(attr = "",
                     expType="after",
                     curvesOfType=[]):
    """

    :param driverAttr:
    :return:
    """
    retrievedSDKNodes = []
    if not curvesOfType:
        curvesOfType = SDK_ANIMCURVES_TYPE
    for animCurve in curvesOfType:
        if expType == "after":
            animCurveNodes = pm.listConnections(attr,
                                                source = False,
                                                destination = True,
                                                type = animCurve,
                                                exactType = True,
                                                plugs = True,
                                                connections = True,
                                                sourceFirst = True,
                                                scn = True) or []
        else:
            animCurveNodes = pm.listConnections(attr,
                                                source = True,
                                                destination = False,
                                                type = animCurve,
                                                exactType = True,
                                                plugs = True,
                                                connections = True,
                                                sourceFirst = True,
                                                scn = True) or []

        retrievedSDKNodes.extend(animCurveNodes)

    return retrievedSDKNodes

def mirrorSDKs(nodes, expType="front", attributes=[], invertDriver=True, invertDriven=True):
    """

    :param nodes:
    :param expType:
    :return:
    """
    for node in nodes:
        node = getPynodes([node])[0]
        if pm.nodeType(node) == "blendShape":
            AllAlias = pm.aliasAttr(node, q = True)
            AttrsList = [AllAlias[i] for i in range(
                0, len(AllAlias), 2
            )]
        else:
            AttrsList = pm.listAttr(node, k = True)
        for eachAttr in AttrsList:
            if pm.objExists("%s.%s"%(node, eachAttr)):
                testConnections = pm.listConnections("%s.%s"%(node, eachAttr),
                                                     plugs = True)
                if testConnections:
                    mirrorKeys("%s.%s"%(node, eachAttr), attributes=attributes, invertDriver=invertDriver, invertDriven=invertDriven)

def mirrorKeys(attr, attributes=[], invertDriver=True, invertDriven=True):
    """

    :param node:
    :param attributes:
    :param invertDriver:
    :param invertDriven:
    :return:
    """
    
    sourceSDKInfo = getConnectedSDKs(attr,"front")
    sourceSDKInfo.extend(getMultSDKs(attr))
    if not attributes:
        attributes = pm.listAttr(attr, connectable=True)
    for source, dest in sourceSDKInfo:
        if dest.plugAttr(longName=True) not in attributes:
            continue

        try:
            invertKeyValues(source.node(),
                            invertDriver=invertDriver,
                            invertDriven=invertDriven)

        except:
            return


def invertKeyValues(KeyNode, invertDriver=True, invertDriven=True):

    LeftKey = ['left_', '_left', 'Left_', '_Left', 'lt_', '_lt', 'Lt_', '_Lt', 'lft_', '_lft', 
    'Lft_', '_Lft', 'Lf_', '_Lf', 'lf_', '_lf', 'l_', '_l', 'L_', '_L']
    RightKey = ['right_', '_right', 'Right_', '_Right', 'rt_', '_rt', 
    'Rt_', '_Rt', 'rgt_', '_rgt', 'Rgt_', '_Rgt', 'Rg_', '_Rg', 'rg_', '_rg', 'r_', '_r', 'R_', '_R']

    sdkInfo_dict = getSDKInfo(KeyNode)
    # stripKeys(KeyNode)
    animKeys = sdkInfo_dict["keys"]
    driverNode = sdkInfo_dict['driverNode']
    driverAttr = sdkInfo_dict['driverAttr']

    drivenNode = sdkInfo_dict['drivenNode']
    drivenAttr = sdkInfo_dict['drivenAttr']

    # rightKeyNode = KeyNode

    for i in range(len(LeftKey)):
        if LeftKey[i] in driverNode:
            driverNode = driverNode.replace(LeftKey[i],RightKey[i])
        if LeftKey[i] in drivenNode:
            drivenNode = drivenNode.replace(LeftKey[i],RightKey[i])
    #     if LeftKey[i] in KeyNode.name():
    #         rightKeyNode = KeyNode.name().replace(LeftKey[i],RightKey[i])

    # if pm.objExists(rightKeyNode):
    #     return
    # newAnimNode = pm.createNode(sdkInfo_dict['type'],name=rightKeyNode)
    for index in range(0, len(animKeys)):
        frameValue = animKeys[index]
        if invertDriver and invertDriven:
            timeValue = frameValue[0] * -1
            value = frameValue[1] * -1
        elif invertDriver and not invertDriven:
            timeValue = frameValue[0] * -1
            value = frameValue[1]
        elif not invertDriver and invertDriven:
            timeValue = frameValue[0]
            value = frameValue[1] * -1
        else:
            timeValue = frameValue[0]
            value = frameValue[1]

        print(timeValue)
        pm.setDrivenKeyframe(drivenNode, at=drivenAttr, cd=driverNode+'.'+driverAttr, dv=timeValue,
                             itt=frameValue[2], ott=frameValue[3], value=value)
        
        # pm.setKeyframe(newAnimNode,
        #                float=timeValue,
        #                value=value,
        #                itt=frameValue[2],
        #                ott=frameValue[3])
        # pm.connectAttr(source, destination)

    return newAnimNode


def stripKeys(animNode):
    """remove animation keys from the provided sdk node

    Args:
        animNode (pynode): sdk/anim node
    """
    numKeys = len(pm.listAttr(animNode + ".ktv", multi=True)) / 3
    for x in range(0, numKeys):
        animNode.remove(0)

def exportSDKs(nodes, filePath, expType="front"):
    """exports the sdk information based on the provided nodes to a json file

    Args:
        nodes (list): of nodes to export
        filePath (string): full filepath to export jsons to
    """
    sdksToExport_dict = {}

    for node in nodes:
        node = getPynodes([node])[0]
        sdksToExport_dict.update(getSDKInfoFromNode(node, expType=expType))
    _exportData(sdksToExport_dict, filePath)
    print("Export Successfully!")
    return sdksToExport_dict


@utils.one_undo
def importSDKs(filePath):
    """create sdk nodes from json file, connected to drivers and driven

    Args:
        filePath (string): path to json file
    """
    allSDKInfo_dict = _importData(filePath)
    createdNodes = []
    failedNodes = []
    for sdkName, sdkInfo_dict in allSDKInfo_dict.items():
        if pm.objExists(sdkName):
            pm.delete(sdkName)
        try:
            createdNodes.append(createSDKFromDict(sdkInfo_dict, sdkName))
        except Exception as e:
            failedNodes.append(sdkName)
            print("{0}:{1}".format(sdkName, e))
    print("Nodes created ---------------------------------")
    pprint.pprint(createdNodes)

    print("Nodes failed  ---------------------------------")
    pprint.pprint(failedNodes)













































