# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-16 20:24:14
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-16 20:24:49

"""
Collections of weights functions
"""

from logging import exception
import re,json,time,sys
if sys.version_info < (3, 0):
    import cPickle
else:
    import _pickle as cPickle
import pymel.core as pm,maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as aom

# FAITH
from Faith.Core import utils

def getMeshPointsV01(node, ifPrint = False):
    """
    api2.0 获取模型所有的点的坐标
    :param node:
    :return:
    """
    selection = om.MSelectionList()
    try:
        selection.add(node)
    except TypeError:
        om.MGlobal.displayError(
            "Dagnode type must be string !"
        )
    dag_path = selection.getDagPath(0)
    if dag_path.extendToShape().apiType() != om.MFn.kMesh:
        return
    mesh_fn = om.MFnMesh(dag_path)
    pointsArray = mesh_fn.getPoints(om.MSpace.kWorld)
    points = [
        (pointsArray[i].x , pointsArray[i].y, pointsArray[i].z) for i in range(len(pointsArray))
    ]
    if ifPrint:
        print(points)

    return points

def getSkinInfluence(SkinNode):
    """
    获取蒙皮骨骼
    :param fnSkin: string name
    :return: (list) skin joint list
    """
    selection = om.MSelectionList()
    selection.add(SkinNode)
    skin_node = selection.getDependNode(0)
    skin = aom.MFnSkinCluster()

    jointList = []
    path_array = om.MDagPathArray()
    try:
        skin = aom.MFnSkinCluster(skin_node)
        path_array = skin.influenceObjects()
    except TypeError:
        om.MGlobal.displayError("API Type Erro !")

    for i in range(len(path_array)):
        dependency_node = om.MFnDependencyNode(path_array[i].node())
        jointList.append(dependency_node.name())

    return jointList

def getSkinData():
    """

    :return: 
    """
    selection = om.MGlobal.getActiveSelectionList()
    path, component = selection.getComponent(0)
    shapePath = path.extendToShape()
    try:
        dgIt = om.MItDependencyGraph(path.node(), om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
    except Exception:
        om.MGlobal.displayError("Selected obj does not have any skinClusters, Please check.")
        return
    skinFn = aom.MFnSkinCluster(dgIt.currentNode())
    indices = om.MIntArray()
    influences = skinFn.influenceObjects()
    jointList = []
    for i in range(len(influences)):
        joint = om.MFnDependencyNode(influences[i].node()).name()
        jointList.append(joint)
        indices.append(i)
        
    return path, component, indices, skinFn, jointList

@utils.timeFunc
def writeSkinCluster(fileName):

    # get skin data
    path, component, indices, skinFn, jointList = getSkinData()

    # get mesh skin weights of MDoubleArray
    weights = skinFn.getWeights(path,component,indices)

    skinClusterNode = skinFn.name()
    skin_shape = om.MFnDependencyNode(path.node()).name()

    # dict of data
    weightData = {}
    weightData["skin_node"] = skinClusterNode
    weightData["skin_shape"] = skin_shape
    weightData["jointList"] = jointList
    weightData["indices"] = [indices[i] for i in range(len(indices))]
    weightData["weights"] = [(weights[i]) for i in range(len(weights))]

    # output file
    try:
        with open(fileName, 'wb') as fp:
            fp.write(cPickle.dumps(weightData))
    except:
        om.MGlobal.displayError("Open file : %s failed ." % fileName)
    
    return True






































