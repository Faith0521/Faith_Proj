# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-06-19 16:49:53
# @Last Modified by:   yinyufei
# @Last Modified time: 2022-08-29 17:55:07

from Faith.Core import aboutPy, utils
import json
if aboutPy.PY2:
    import cPickle
else:
    import _pickle
import pprint,re
import pymel.core as pm,maya.mel as mel,maya.cmds as mc

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
                    attribute = "%s.%s"%(node, eachAttr),expType=expType)
                if expType == "front":
                    retrievedSDKNodes.extend(getMultSDKs("%s.%s"%(node, eachAttr)))
                if expType == "front":
                    for animPlug, targetPlug in retrievedSDKNodes:
                        allSDKInfo_dict[animPlug.nodeName()] = getSDKInfo(animPlug.node())
                else:
                    for targetPlug, animPlug in retrievedSDKNodes:
                        allSDKInfo_dict[animPlug.nodeName()] = getSDKInfo(animPlug.node())
    return allSDKInfo_dict


def getSDKInfoFromAttr(attr, expType="after"):
    allSDKInfo_dict = {}
    testConnections = pm.listConnections(attr, plugs = True)
    if testConnections:
        retrievedSDKNodes = getConnectedSDKs(
                    attribute = attr, expType=expType)
        if expType == "front":
                    retrievedSDKNodes.extend(getMultSDKs(attr))
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
    if "blendWeighted" in pm.nodeType(sourceDriverAttr):
        sourceDriverAttr_new = pm.listConnections(sourceDriverAttr.replace('output','input'),
                                          source=True,
                                          plugs=True,
                                          scn=True)[0]
        driverNode, driverAttr = sourceDriverAttr_new.split(".")
    else:
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
            while 'unitConversion' in pm.nodeType(attrTargets[i]) or 'blendWeighted' in pm.nodeType(attrTargets[i]):
                targets = pm.connectionInfo(attrTargets[i][:attrTargets[i].index('.')] + '.output', dfs=1)
                if not targets:
                    pm.error("Please clear not used 'unitConversion' or 'blendWeighted' nodes.")
                    break
                else:
                    attrTargets[i] = targets[0]
        else:
            attrTargets[i] = 'None'
        drivenNodes.append(attrTargets[i].split(".")[0])
        drivenAttrs.append(attrTargets[i].split(".")[1])

    return drivenNodes, drivenAttrs

def getConnectedSDKs(attribute = "",
                     expType="after",
                     curvesOfType=[]):
    """

    :param driverAttr:
    :return:
    """
    retrievedSDKNodes = []
    animCurveNodes = []
    if not curvesOfType:
        curvesOfType = SDK_ANIMCURVES_TYPE
    for animCurve in curvesOfType:
        if expType == "after":
            attrTargets = pm.connectionInfo(attribute, dfs=1)
            for i, attr in enumerate(attrTargets):
                if attr != '':
                    if 'unitConversion' in pm.nodeType(attrTargets[i]) or 'blendWeighted' in pm.nodeType(attrTargets[i]):
                        animCurveNodes = pm.listConnections(attrTargets[i][:attrTargets[i].index('.')] + '.output', 
                                                            source = False,
                                                            destination = True,
                                                            type = animCurve,
                                                            exactType = True,
                                                            plugs = True,
                                                            connections = True,
                                                            sourceFirst = True,
                                                            scn = True) or []
                    else:
                        animCurveNodes = pm.listConnections(attribute,
                                                source = False,
                                                destination = True,
                                                type = animCurve,
                                                exactType = True,
                                                plugs = True,
                                                connections = True,
                                                sourceFirst = True,
                                                scn = True) or []

        else:
            animCurveNodes = pm.listConnections(attribute,
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


def mirrorSDKs(nodes, attributes=[], destination="front"):
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
                        mirrorKeys("%s.%s"%(node, eachAttr),destination=destination)
        else:
            for eachAttr in attributes:
                if pm.objExists("%s.%s"%(node, eachAttr)):
                    testConnections = pm.listConnections("%s.%s"%(node, eachAttr),
                                                         plugs = True)
                    if testConnections:
                        mirrorKeys("%s.%s"%(node, eachAttr),destination=destination)


def mirrorKeys(attr, destination="front"):
    """

    :param node:
    :param attributes:
    :param invertDriver:
    :param invertDriven:
    :return:
    """

    sourceSDKInfo = getConnectedSDKs(attr,destination)
    sourceSDKInfo.extend(getMultSDKs(attr))
    # print(sourceSDKInfo)
    for source, dest in sourceSDKInfo:
        info = {}
        if destination == "front":
            info[source.nodeName()] = getSDKInfo(source.node())
        else:
            info[source.nodeName()] = getSDKInfo(dest.node())
        # print(info)
        invertKeyValues(info)


def invertKeyValues(sdkInfo):

    LeftKey = ['L_','l_','lf_','Lf_','_L','_l','_lf','_Lf','Left_','_Left']
    RightKey = ['R_','r_','rt_','Rt_','_R','_r','_rt','_Rt','Right_','_Right']
    for animNode,infoDict in sdkInfo.items():
        animKeys = infoDict["keys"]
        driverNode = infoDict['driverNode']
        driverAttr = infoDict['driverAttr']

        drivenNodes = infoDict['drivenNodes']
        drivenAttrs = infoDict['drivenAttrs']

        for j in range(len(drivenNodes)):
            for index in range(0, len(animKeys)):
                frameValue = animKeys[index]

                connectionObj = pm.connectionInfo(drivenNodes[j] + '.' + drivenAttrs[j], sfd=1)
                
                if connectionObj != '' and 'animCurve' in pm.nodeType(connectionObj):
                    pass

                checkResult = checkSymAttrIfMirror(driverNode + "." + driverAttr, drivenNodes[j] + "." + drivenAttrs[j])

                driverattr = checkResult[0]
                drivenattr = checkResult[1]

                if '-' in driverattr and '-' not in drivenattr:
                    pm.setDrivenKeyframe(drivenattr.split('.')[0], at=drivenattr.split('.')[1], cd=driverattr[:-1],
                                         dv=float(frameValue[0]) * -1, v=float(frameValue[1]))
                elif '-' not in driverattr and '-' in drivenattr:
                    pm.setDrivenKeyframe(drivenattr.split('.')[0], at=drivenattr.split('.')[1][:-1], cd=driverattr,
                                         dv=float(frameValue[0]), v=float(frameValue[1]) * (-1))
                elif '-' in driverattr and '-' in drivenattr:
                    pm.setDrivenKeyframe(drivenattr.split('.')[0], at=drivenattr.split('.')[1][:-1],
                                         cd=driverattr[:-1], dv=float(frameValue[0]) * -1, v=float(frameValue[1]) * (-1))
                elif '-' not in driverattr and '-' not in drivenattr:
                    pm.setDrivenKeyframe(drivenattr.split('.')[0], at=drivenattr.split('.')[1], cd=driverattr,
                                         dv=float(frameValue[0]), v=float(frameValue[1]))

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
            drivenAttr = removeEXnodes(x, 'output', 'dfs')
            if drivenAttr:
                if drivenAttr[0] == setdrivenAttr:
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

def checkSymAttrIfMirror(baseDriverAttr, baseDrivenAttr):
    """

    @param baseDriverAttr:
    @param baseDrivenAttr:
    @return:
    """
    PrefixKey = ['L_', 'lf_', '_L', 'facial_L_', 'left_', 'Left_', 'R_', 'rt_', '_R', 'facial_R_', 'right_', 'Right_']
    keyNum = len(PrefixKey)
    symAttr = []
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # check driver attribute
    i = 0
    while i < keyNum:
        if PrefixKey[i] in baseDriverAttr:
            driverAttr = (checkSymObj(orgObj=[baseDriverAttr], searchFor=PrefixKey[i],
                                           replaceWith=PrefixKey[(i + keyNum / 2) % keyNum]))

            if len(driverAttr) == 0:
                driverAttr = baseDriverAttr
                break

            elif len(driverAttr) != 0:
                symDriver = driverAttr.split('.')[0]
                if 'translate' in baseDriverAttr or 'rotate' in baseDriverAttr and 'order' not in baseDriverAttr and 'Order' not in baseDriverAttr:
                    mirrorAxis = checkSymAxis(baseDriverAttr.split('.')[0], symDriver)
                    driverAttr = mirrorAxis[baseDriverAttr]
            break
        else:
            i = i + 1
            if i == keyNum:
                driverAttr = baseDriverAttr
                break
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # check driven attribute
    j = 0
    while j < keyNum:
        if PrefixKey[j] in baseDrivenAttr:
            drivenAttr = (checkSymObj(orgObj=[baseDrivenAttr], searchFor=PrefixKey[j],
                                           replaceWith=PrefixKey[(j + keyNum / 2) % keyNum]))

            if len(drivenAttr) == 0:
                drivenAttr = baseDrivenAttr
                driverAttr = baseDriverAttr
                break

            elif len(drivenAttr) != 0:
                symDriven = drivenAttr.split('.')[0]
                if 'translate' in baseDrivenAttr or 'rotate' in baseDrivenAttr and 'order' not in baseDrivenAttr and 'Order' not in baseDrivenAttr:
                    mirrorAxis = checkSymAxis(baseDrivenAttr.split('.')[0], symDriven)
                    drivenAttr = mirrorAxis[baseDrivenAttr]

            break
        else:
            j = j + 1
            if j == keyNum:
                if 'translate' in baseDrivenAttr or 'rotate' in baseDrivenAttr and 'order' not in baseDrivenAttr and 'Order' not in baseDrivenAttr:
                    mirrorAxis = checkSymAxis(baseDrivenAttr.split('.')[0], baseDrivenAttr.split('.')[0])
                    drivenAttr = mirrorAxis[baseDrivenAttr]
                else:
                    drivenAttr = baseDrivenAttr
                break

    symAttr.append(driverAttr)
    symAttr.append(drivenAttr)
    return symAttr

def checkSymObj(orgObj=[], searchFor='L_', replaceWith='R_'):
    """

    @param orgObj:
    @param searchFor:
    @param replaceWith:
    @return:
    """
    symObj = []
    keyword = [searchFor]
    # ------------------------------
    if orgObj == []:
        selobjs = mc.ls(sl=1)
    else:
        selobjs = orgObj

    for x in selobjs:
        for n in keyword:
            if n not in x:
                symObj.append(x)
            else:
                theOtherSideobj = x.replace(searchFor, replaceWith)
                if mc.objExists(theOtherSideobj):
                    symObj.append(theOtherSideobj)
                else:
                    mc.warning('can not find the sysmmetry : %s' % (theOtherSideobj))

        symObj = sorted(set(symObj), key=symObj.index)

    if len(symObj) == 1:
        return symObj[0]
    else:
        return symObj

def checkSymAxis(orgobj, symobj):
    """

    @param orgobj:
    @param symobj:
    @return:
    """
    symAxis = []

    orghelploc = mc.spaceLocator(
        p=(0, 0, 0), name=str(orgobj) + '_help_loc')[0]
    symhelploc = mc.spaceLocator(
        p=(0, 0, 0), name=str(symobj) + '_help_loc')[0]

    # self.fromAtoB(orghelploc , orgobj , 1)
    # self.fromAtoB(symhelploc , symobj , 1)

    orghelplocGrp = makeObjZero('group', 'zero', 'On', orghelploc)
    symhelplocGrp = makeObjZero('group', 'zero', 'On', symhelploc)

    # update date 2017/03/16 >>
    # set zero value in object space
    mc.parent(orghelplocGrp, orgobj)
    mc.parent(symhelplocGrp, symobj)

    defaultAttr = ['.tx', '.ty', '.tz', '.rx',
                   '.ry', '.rz', '.sx', '.sy', '.sz']
    for attr in defaultAttr:
        if 's' in attr:
            mc.setAttr(orghelplocGrp + attr, 1)
            mc.setAttr(symhelplocGrp + attr, 1)
        else:
            mc.setAttr(orghelplocGrp + attr, 0)
            mc.setAttr(symhelplocGrp + attr, 0)

    # set zero value in world space
    mc.parent(orghelplocGrp, w=1)
    mc.parent(symhelplocGrp, w=1)

    zeroValue = ['.tx', '.ty', '.tz']
    for x in zeroValue:
        mc.setAttr(orghelplocGrp + x, 0)
        mc.setAttr(symhelplocGrp + x, 0)

    orgaxisValue = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    axisKey = ['X', 'Y', 'Z', 'X-', 'Y-', 'Z-']
    symaxisValue = [(1, 0, 0), (0, 1, 0), (0, 0, 1),
                    (-1, 0, 0), (0, -1, 0), (0, 0, -1)]

    i = 0
    while i < len(orgaxisValue):
        j = 0

        mc.setAttr(orghelploc + '.tx', orgaxisValue[i][0])
        mc.setAttr(orghelploc + '.ty', orgaxisValue[i][1])
        mc.setAttr(orghelploc + '.tz', orgaxisValue[i][2])

        orgcurrentPos = mc.xform(orghelploc, q=1, t=1, ws=1)

        orgcurrentPos[0] = round(orgcurrentPos[0], 1)
        orgcurrentPos[1] = round(orgcurrentPos[1], 1)
        orgcurrentPos[2] = round(orgcurrentPos[2], 1)

        mc.setAttr(orghelploc + '.tx', 0)
        mc.setAttr(orghelploc + '.ty', 0)
        mc.setAttr(orghelploc + '.tz', 0)

        while j < len(symaxisValue):

            mc.setAttr(symhelploc + '.tx', symaxisValue[j][0])
            mc.setAttr(symhelploc + '.ty', symaxisValue[j][1])
            mc.setAttr(symhelploc + '.tz', symaxisValue[j][2])

            symcurrentPos = mc.xform(symhelploc, q=1, t=1, ws=1)

            symcurrentPos[0] = round(symcurrentPos[0], 1)
            symcurrentPos[1] = round(symcurrentPos[1], 1)
            symcurrentPos[2] = round(symcurrentPos[2], 1)

            mc.setAttr(symhelploc + '.tx', 0)
            mc.setAttr(symhelploc + '.ty', 0)
            mc.setAttr(symhelploc + '.tz', 0)

            if symcurrentPos[0] * -1 == orgcurrentPos[0] and symcurrentPos[1] == orgcurrentPos[1] and symcurrentPos[
                2] == orgcurrentPos[2]:

                symAxis.append(orgobj + '.translate' + axisKey[i])
                symAxis.append(symobj + '.translate' + axisKey[j])

                # check rotate
                # create rotate help locator
                orgRollLoc = mc.spaceLocator(
                    p=(0, 0, 0), name=str(orgobj) + '_roll_loc')[0]
                symRollLoc = mc.spaceLocator(
                    p=(0, 0, 0), name=str(symobj) + '_roll_loc')[0]

                # sym help loc
                mc.setAttr(orgRollLoc + '.tx', 1)
                mc.setAttr(symRollLoc + '.tx', -1)
                mc.setAttr(orgRollLoc + '.ty', 1)
                mc.setAttr(symRollLoc + '.ty', 1)

                mc.parentConstraint(orghelploc, orgRollLoc, mo=True)
                mc.parentConstraint(symhelploc, symRollLoc, mo=True)

                # give help loc rotate
                mc.setAttr(orghelploc + '.rotate' + axisKey[i], 10)

                # check rotate at two type
                if '-' in axisKey[j]:
                    mc.setAttr(symhelploc + '.rotate' +
                               axisKey[j][:-1], -10)
                    orgRollLocPos = mc.xform(orgRollLoc, q=1, t=1, ws=1)
                    symRollLocPos = mc.xform(symRollLoc, q=1, t=1, ws=1)

                    orgRollLocPos[0] = round(orgRollLocPos[0], 1)
                    orgRollLocPos[1] = round(orgRollLocPos[1], 1)
                    orgRollLocPos[2] = round(orgRollLocPos[2], 1)

                    symRollLocPos[0] = round(symRollLocPos[0], 1)
                    symRollLocPos[1] = round(symRollLocPos[1], 1)
                    symRollLocPos[2] = round(symRollLocPos[2], 1)

                    if symRollLocPos[0] * -1 == orgRollLocPos[0] and symRollLocPos[1] == orgRollLocPos[1] and \
                            symRollLocPos[2] == orgRollLocPos[2]:
                        symAxis.append(orgobj + '.rotate' + axisKey[i])
                        symAxis.append(symobj + '.rotate' + axisKey[j])
                    else:
                        # print 'test'
                        symAxis.append(orgobj + '.rotate' + axisKey[i])
                        symAxis.append(
                            symobj + '.rotate' + axisKey[j][:-1])

                elif '-' not in axisKey[j]:
                    mc.setAttr(symhelploc + '.rotate' + axisKey[j], 10)
                    orgRollLocPos = mc.xform(orgRollLoc, q=1, t=1, ws=1)
                    symRollLocPos = mc.xform(symRollLoc, q=1, t=1, ws=1)

                    orgRollLocPos[0] = round(orgRollLocPos[0], 1)
                    orgRollLocPos[1] = round(orgRollLocPos[1], 1)
                    orgRollLocPos[2] = round(orgRollLocPos[2], 1)

                    symRollLocPos[0] = round(symRollLocPos[0], 1)
                    symRollLocPos[1] = round(symRollLocPos[1], 1)
                    symRollLocPos[2] = round(symRollLocPos[2], 1)

                    if symRollLocPos[0] * -1 == orgRollLocPos[0] and symRollLocPos[1] == orgRollLocPos[1] and \
                            symRollLocPos[2] == orgRollLocPos[2]:
                        symAxis.append(orgobj + '.rotate' + axisKey[i])
                        symAxis.append(symobj + '.rotate' + axisKey[j])
                    else:
                        symAxis.append(orgobj + '.rotate' + axisKey[i])
                        symAxis.append(
                            symobj + '.rotate' + axisKey[j] + '-')

                # clean
                mc.delete(orgRollLoc)
                mc.delete(symRollLoc)
            j += 1
        i += 1

    mc.delete(orghelplocGrp, symhelplocGrp)
    axisNote = {}
    for i in range(0, len(symAxis), 2):
        axisNote[symAxis[i]] = symAxis[i + 1]
    return axisNote

def makeObjZero(type, suffix, rotation, *obj):
    '''
    #--------------------------------------------------------------------------------
    #This Function can make object zero
    #Note: if you want create control type is joint or you wang create sdk group on objects , you can use this script.
    #FN: makeObjZero(sel,type,rotation)
    #--------------------------------------------------------------------------------
    '''

    if len(obj) == 0:

        mc.error(
            '------------------------->>>You must select one or more object !<<<----------------------------')

    else:

        # this type is joint .

        if type == 'joint':

            objNum = len(obj)

            for i in range(0, objNum, 1):

                if rotation == 'On':
                    mc.makeIdentity(obj[i], apply=True, t=1, r=1, s=1, n=0)
                    mc.duplicate(obj[i], name='%s_%s' % (obj[i], suffix))
                    childObj = mc.listRelatives('%s_%s' % (obj[i], suffix))

                    if childObj == None:
                        mc.parent(obj[i], '%s_%s' % (obj[i], suffix))
                    else:
                        childNum = len(childObj)
                        mc.delete('%s_%s|%s' %
                                  (obj[i], suffix, childObj[0]))
                        mc.parent(obj[i], '%s_%s' % (obj[i], suffix))

                elif rotation == 'Off':

                    mc.makeIdentity(obj[i], apply=True, t=1, r=1, s=1, n=0)
                    mc.duplicate(obj[i], name='%s_%s' % (obj[i], suffix))
                    mc.makeIdentity(obj[i], apply=True, t=1, r=1, s=1, n=0)
                    mc.setAttr('%s_%s.rotateX' % (obj[i], suffix), 0)
                    mc.setAttr('%s_%s.rotateY' % (obj[i], suffix), 0)
                    mc.setAttr('%s_%s.rotateZ' % (obj[i], suffix), 0)
                    childObj = mc.listRelatives('%s_%s' % (obj[i], suffix))

                    if childObj == None:
                        mc.parent(obj[i], '%s_%s' % (obj[i], suffix))
                    else:
                        childNum = len(childObj)
                        mc.delete('%s_%s|%s' %
                                  (obj[i], suffix, childObj[0]))
                        mc.parent(obj[i], '%s_%s' % (obj[i], suffix))

        # type is group ,it is have flag rotateOn / rotateOff ,you can use
        # it for ik controls  con sdk zero and so on.

        elif type == 'group':

            objNum = len(obj)

            for i in range(0, objNum, 1):

                grp = mc.createNode(
                    'transform', name='%s_%s' % (obj[i], suffix))
                parentObj = mc.listRelatives(obj[i], p=True)

                if rotation == 'On':
                    mc.delete(mc.pointConstraint(obj[i], grp, mo=False))
                    mc.delete(mc.orientConstraint(obj[i], grp, mo=False))

                    if parentObj == None:
                        mc.parent(obj[i], grp)
                    else:
                        mc.parent(grp, parentObj[0])
                        mc.parent(obj[i], grp)

                    mc.select(grp)
                    return grp

                elif rotation == 'Off':

                    mc.pointConstraint(obj[i], grp, mo=False)
                    mc.delete('%s_pointConstraint1' % (grp))

                    if parentObj == None:
                        mc.parent(obj[i], grp)
                    else:

                        mc.parent(grp, parentObj[0])
                        mc.parent(obj[i], grp)

                    mc.select(grp)
                    return grp

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
















































