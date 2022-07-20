# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-06-19 16:49:53
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-05 21:41:54

from Faith.Core import aboutPy, utils
import json
if aboutPy.PY2:
    import cPickle
else:
    import _pickle
import pprint,re
import pymel.core as pm,maya.mel as mel

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
    animKeys = sdkInfo_dict["keys"]
    driverNode = sdkInfo_dict['driverNode']
    driverAttr = sdkInfo_dict['driverAttr']

    drivenNodes = sdkInfo_dict['drivenNodes']
    drivenAttrs = sdkInfo_dict['drivenAttrs']
    sdkNodes = []
    for j in range(len(drivenNodes)):
        for index in range(0, len(animKeys)):
            frameValue = animKeys[index]
            timeValue = frameValue[0]
            value = frameValue[1]

            pm.setDrivenKeyframe(drivenNodes[j], at=drivenAttrs[j], cd=driverNode + '.' + driverAttr, dv=timeValue,
                                 value=value)

        for index in range(0, len(animKeys)):
            frameValue = animKeys[index]
            animCurrentCrv = getAnimCurve(
                driverNode + '.' + driverAttr, drivenNodes[j] + '.' + drivenAttrs[j]
            )
            if animCurrentCrv:
                mel.eval('keyTangent -index %s -e -itt %s -ott %s %s' % (index, frameValue[2],
                                                                         frameValue[3], animCurrentCrv[0]))
                mel.eval('keyTangent -index %s -e -ia %s -oa %s %s' % (
                    index, frameValue[4], frameValue[5], animCurrentCrv[0]
                ))

                animCurrentCrv[0].preInfinity.set(sdkInfo_dict['preInfinity'])
                animCurrentCrv[0].postInfinity.set(sdkInfo_dict['postInfinity'])



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
    ia_list = pm.keyTangent(animNode, ia=True, q=True)
    oa_list = pm.keyTangent(animNode, oa=True, q=True)
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
        keyData = [value[0], absoluteValue, itt_list[index], ott_list[index], ia_list[index], oa_list[index]]
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
    drivenNodes, drivenAttrs = getSDKDestination(animNodeOutputPlug)
    sdkInfo_dict["drivenNodes"] = drivenNodes
    sdkInfo_dict["drivenAttrs"] = drivenAttrs

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
    attrTargets = pm.connectionInfo(animNodeOutputPlug, dfs=1)
    drivenNodes = []
    drivenAttrs = []
    for i, attr in enumerate(attrTargets):
        if attr != '':
            while 'unitConversion' in attrTargets[i] or 'blendWeighted' in attrTargets[i]:
                attrTargets[i] = \
                    pm.connectionInfo(attrTargets[i][:attrTargets[i].index('.')] + '.output', dfs=1)[0]
        else:
            attrTargets[i] = 'None'
        drivenNodes.append(attrTargets[i].split(".")[0])
        drivenAttrs.append(attrTargets[i].split(".")[1])

    return drivenNodes, drivenAttrs

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


def mirrorSDKs(nodes, attributes=[], invertDriver=True, invertDriven=True):
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

        if not attributes:
            for eachAttr in AttrsList:
                if pm.objExists("%s.%s"%(node, eachAttr)):
                    testConnections = pm.listConnections("%s.%s"%(node, eachAttr),
                                                         plugs = True)
                    if testConnections:
                        mirrorKeys("%s.%s"%(node, eachAttr), invertDriver=invertDriver, invertDriven=invertDriven)
        else:
            for eachAttr in attributes:
                if pm.objExists("%s.%s"%(node, eachAttr)):
                    testConnections = pm.listConnections("%s.%s"%(node, eachAttr),
                                                         plugs = True)
                    if testConnections:
                        mirrorKeys("%s.%s"%(node, eachAttr), invertDriver=invertDriver, invertDriven=invertDriven)


def mirrorKeys(attr, invertDriver=True, invertDriven=True):
    """

    :param node:
    :param attributes:
    :param invertDriver:
    :param invertDriven:
    :return:
    """

    sourceSDKInfo = getConnectedSDKs(attr,"front")
    sourceSDKInfo.extend(getMultSDKs(attr))
    for source, dest in sourceSDKInfo:
        info = {}
        info[source.nodeName()] = getSDKInfo(source.node())
        invertKeyValues(info,
                        invertDriver=invertDriver,
                        invertDriven=invertDriven)


def invertKeyValues(sdkInfo, invertDriver=True, invertDriven=True):

    LeftKey = ['L_','l_','lf_','Lf_','_L','_l','_lf','_Lf']
    RightKey = ['R_','r_','rt_','Rt_','_R','_r','_rt','_Rt']
    for animNode,infoDict in sdkInfo.items():
        animKeys = infoDict["keys"]
        driverNode = infoDict['driverNode']
        driverAttr = infoDict['driverAttr']

        drivenNodes = infoDict['drivenNodes']
        drivenAttrs = infoDict['drivenAttrs']

        for i in range(len(LeftKey)):
            if re.search('^'+ LeftKey[i], driverNode) or re.search(LeftKey[i]+'$', driverNode):
                driverNode = driverNode.replace(LeftKey[i],RightKey[i])
            if re.search('^'+ LeftKey[i], driverAttr) or re.search(LeftKey[i]+'$', driverAttr):
                driverAttr = driverAttr.replace(LeftKey[i],RightKey[i])
            for j in range(len(drivenNodes)):
                if re.search('^'+ LeftKey[i], drivenNodes[j]) or re.search(LeftKey[i]+'$', drivenNodes[j]):
                    drivenNodes[j] = drivenNodes[j].replace(LeftKey[i],RightKey[i])
                if re.search('^' + LeftKey[i], drivenAttrs[j]) or re.search(LeftKey[i] + '$', drivenAttrs[j]):
                    drivenAttrs[j] = drivenAttrs[j].replace(LeftKey[i], RightKey[i])

        for j in range(len(drivenNodes)):
            for index in range(0, len(animKeys)):
                frameValue = animKeys[index]
                if invertDriver and invertDriven:
                    timeValue = frameValue[0] * -1
                    value = frameValue[1] * -1
                if invertDriver and not invertDriven:
                    timeValue = frameValue[0]
                    value = frameValue[1] * -1
                if not invertDriver and invertDriven:
                    timeValue = frameValue[0]
                    value = frameValue[1] * -1
                else:
                    timeValue = frameValue[0]
                    value = frameValue[1]

                pm.setDrivenKeyframe(drivenNodes[j], at=drivenAttrs[j], cd=driverNode+'.'+driverAttr, dv=timeValue,
                                     value=value)

            for index in range(0, len(animKeys)):
                frameValue = animKeys[index]
                animCurrentCrv = getAnimCurve(
                    driverNode+'.'+driverAttr, drivenNodes[j]+'.'+drivenAttrs[j]
                )
                if animCurrentCrv:
                    mel.eval('keyTangent -index %s -e -itt %s -ott %s %s' % (index, frameValue[2],
                        frameValue[3], animCurrentCrv[0]))
                    mel.eval('keyTangent -index %s -e -ia %s -oa %s %s' % (
                        index, frameValue[4], frameValue[5], animCurrentCrv[0]
                    ))

                    animCurrentCrv[0].preInfinity.set(infoDict['preInfinity'])
                    animCurrentCrv[0].postInfinity.set(infoDict['postInfinity'])

def getAnimCurve(driverAttr, setdrivenAttr=None):
    """

    @param driverAttr:
    @param setdrivenAttr:
    @return:
    """
    setdrivenCrv = []
    # ------------------------------

    animCList = pm.listConnections(driverAttr, type='animCurve', s=False, d=True, scn=True)

    if animCList == None:
        return None
    elif animCList != None and setdrivenAttr == None:
        return animCList
    elif animCList != None and setdrivenAttr != None:
        for x in animCList:
            drivenAttr = removeEXnodes(x, 'output', 'dfs')[0]
            if drivenAttr == setdrivenAttr:
                setdrivenCrv.append(x)
        return setdrivenCrv

def removeEXnodes(nodeName, nodeAttr, direction):
    """

    @param nodeName:
    @param nodeAttr:
    @param direction:
    @return:
    """
    if direction == 'sfd':
        attrSource = pm.connectionInfo(nodeName + '.' + nodeAttr, sfd=1)

        while 'unitConversion' in attrSource:
            attrSource = pm.connectionInfo(attrSource.replace('output', 'input'), sfd=1)
        if attrSource == '':
            attrSource = 'None'
        return attrSource

    elif direction == 'dfs':
        attrTargets = pm.connectionInfo(nodeName + '.' + nodeAttr, dfs=1)

        for i, attr in enumerate(attrTargets):
            if attr != '':
                while 'unitConversion' in attrTargets[i] or 'blendWeighted' in attrTargets[i]:
                    attrTargets[i] = \
                        pm.connectionInfo(attrTargets[i][:attrTargets[i].index('.')] + '.output', dfs=1)[0]
            else:
                attrTargets[i] = 'None'
        return attrTargets

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
    createdNodes = {}
    failedNodes = []
    for sdkName, sdkInfo_dict in allSDKInfo_dict.items():
        if pm.objExists(sdkName):
            pm.delete(sdkName)
        try:
            createSDKFromDict(sdkInfo_dict, sdkName)

        except Exception as e:
            failedNodes.append(sdkName)
            print("{0}:{1}".format(sdkName, e))

    print("Nodes successfully created ---------------------------------")
















































