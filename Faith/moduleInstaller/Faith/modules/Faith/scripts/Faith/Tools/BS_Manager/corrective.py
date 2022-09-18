# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-07-19 20:11:59
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-19 20:14:06
import maya.cmds as cmds,pymel.core as pm,maya.mel as mel
import maya.OpenMaya as OpenMaya
import math
from Faith.Core.aboutPy import PY2

if PY2:
    UNICODETYPE = unicode
else:
    UNICODETYPE = str

def invert(base=None, name=None, targetName=None,invert=None):
    """Inverts a shape through the deformation chain.
    @param[in] base Deformed base mesh.
    @param[in] corrective Sculpted corrective mesh.
    @param[in] name Name of the generated inverted shape.
    @return The name of the inverted shape.
    """
    if not base:
        sel = cmds.ls(sl=True)
        if not sel or len(sel) != 1:
            raise RuntimeError('Must select a mesh.')
        base = sel
    if targetName:
        corrective = cmds.duplicate(base, rr=True, n="%s_%s_Sculpt"%(base, targetName))[0]
    else:
        corrective = cmds.duplicate(base, rr=True, n="%s_Sculpt" % base)[0]
    # Get points on base mesh
    base_points = get_points(base)
    point_count = base_points.length()

    # Get points on corrective mesh
    corrective_points = get_points(corrective)
    if not invert:
        invertShape = duplicateOrigMesh(base)
    else:
        invertShape = invert
    # Get the intermediate mesh
    orig_mesh = cmds.listRelatives(invertShape, shapes=True)[0]

    # Get the component offset axes
    orig_points = get_points(orig_mesh)
    x_points = OpenMaya.MPointArray(orig_points)
    y_points = OpenMaya.MPointArray(orig_points)
    z_points = OpenMaya.MPointArray(orig_points)

    cmds.undoInfo(openChunk=True)
    for i in range(point_count):
        x_points[i].x += 1.0
        y_points[i].y += 1.0
        z_points[i].z += 1.0
    set_points(orig_mesh, x_points)
    x_points = get_points(base)
    set_points(orig_mesh, y_points)
    y_points = get_points(base)
    set_points(orig_mesh, z_points)
    z_points = get_points(base)
    set_points(orig_mesh, orig_points)

    # Create the mesh to get the inversion deformer
    if not name:
        name = corrective.replace('Sculpt', 'Target')

    if not invertShape:
        inverted_shapes = cmds.duplicate(base, name=name)[0]
    else:
        inverted_shapes = invertShape
    # Delete the unnessary shapes
    shapes = cmds.listRelatives(inverted_shapes, children=True, shapes=True, path=True)
    for s in shapes:
        if cmds.getAttr('%s.intermediateObject' % s):
            cmds.delete(s)
    set_points(inverted_shapes, orig_points)
    # Unlock the transformation attrs
    for attr in 'trs':
        for x in 'xyz':
            cmds.setAttr('%s.%s%s' % (inverted_shapes, attr, x), lock=False)
    cmds.setAttr('%s.visibility' % inverted_shapes, 1)
    deformer = cmds.deformer(inverted_shapes, type='FAITH_CorrectiveShape')[0]

    # Calculate the inversion matrices
    deformer_mobj = get_mobject(deformer)
    fn_deformer = OpenMaya.MFnDependencyNode(deformer_mobj)
    plug_matrix = fn_deformer.findPlug('inversionMatrix', False)
    fn_matrix_data = OpenMaya.MFnMatrixData()
    for i in range(point_count):
        matrix = OpenMaya.MMatrix()
        set_matrix_row(matrix, x_points[i] - base_points[i], 0)
        set_matrix_row(matrix, y_points[i] - base_points[i], 1)
        set_matrix_row(matrix, z_points[i] - base_points[i], 2)
        set_matrix_row(matrix, corrective_points[i], 3)
        matrix = matrix.inverse()
        matrix_mobj = fn_matrix_data.create(matrix)

        plug_matrixElement = plug_matrix.elementByLogicalIndex(i)
        plug_matrixElement.setMObject(matrix_mobj)

    # Store the base points.
    fn_point_data = OpenMaya.MFnPointArrayData()
    point_data_mobj = fn_point_data.create(base_points)
    plug_deformed_points = fn_deformer.findPlug('deformedPoints', False)
    plug_deformed_points.setMObject(point_data_mobj)

    cmds.connectAttr('%s.outMesh' % get_shape(corrective), '%s.correctiveMesh' % deformer)
    targetGrp = cmds.createNode("transform", n = base + "_bsTarget_Grp")
    cmds.parent(inverted_shapes, targetGrp)
    cmds.setAttr(inverted_shapes + ".v", 0)
    cmds.setAttr(base + ".v", 0)
    cmds.undoInfo(closeChunk=True)

    return [corrective, inverted_shapes, targetGrp]

def findBlendShapeInHistory(mesh):
    """

    @param mesh:
    @return:
    """
    history = cmds.listHistory(mesh)
    for h in history:
        if cmds.nodeType(h) == "blendShape":
            return h
    return None

def findSkinClusterInHistory(mesh):
    """

    @param mesh:
    @return:
    """
    history = cmds.listHistory(mesh)
    for h in history:
        if cmds.nodeType(h) == "skinCluster":
            return h
    return None

def duplicateOrigMesh(mesh):
    """

    @param mesh:
    @return:
    """
    bs = findBlendShapeInHistory(mesh)
    skin = findSkinClusterInHistory(mesh)
    if bs:
        cmds.setAttr("%s.envelope"%bs, 0)
    if skin:
        cmds.setAttr("%s.envelope"%skin, 0)
    origMesh = cmds.duplicate(mesh, rr=True, n=mesh + '_Target')[0]
    if bs:
        cmds.setAttr("%s.envelope"%bs, 1)
    if skin:
        cmds.setAttr("%s.envelope"%skin, 1)

    return origMesh

def get_shape(node, intermediate=False):
    """Returns a shape node from a given transform or shape.
    @param[in] node Name of the node.
    @param[in] intermediate True to get the intermediate mesh
    @return The associated shape node.
    """
    if cmds.nodeType(node) == 'transform':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            raise RuntimeError('%s has no shape' % node)
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject' % shape)
            if intermediate and is_intermediate and cmds.listConnections('%s.worldMesh' % shape,
                                                                         source=False):
                return shape
            elif not intermediate and not is_intermediate:
                return shape
        raise RuntimeError('Could not find shape on node {0}'.format(node))
    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        return node


def get_mobject(node):
    """Gets the dag path of a node.
    @param[in] node Name of the node.
    @return The dag path of a node.
    """
    selection_list = OpenMaya.MSelectionList()
    selection_list.add(node)
    node_mobj = OpenMaya.MObject()
    selection_list.getDependNode(0, node_mobj)
    return node_mobj


def get_dag_path(node):
    """Gets the dag path of a node.
    @param[in] node Name of the node.
    @return The dag path of a node.
    """
    selection_list = OpenMaya.MSelectionList()
    selection_list.add(node)
    path_node = OpenMaya.MDagPath()
    selection_list.getDagPath(0, path_node)
    return path_node


def get_points(path, space=OpenMaya.MSpace.kObject):
    """Get the control point positions of a geometry node.
    @param[in] path Name or dag path of a node.
    @param[in] space Space to get the points.
    @return The MPointArray of points.
    """
    if isinstance(path, UNICODETYPE):
        path = get_dag_path(get_shape(path))
    it_geo = OpenMaya.MItGeometry(path)
    points = OpenMaya.MPointArray()
    it_geo.allPositions(points, space)
    return points


def set_points(path, points, space=OpenMaya.MSpace.kObject):
    """Set the control points positions of a geometry node.
    @param[in] path Name or dag path of a node.
    @param[in] points MPointArray of points.
    @param[in] space Space to get the points.
    """
    if isinstance(path, UNICODETYPE):
        path = get_dag_path(get_shape(path))
    it_geo = OpenMaya.MItGeometry(path)
    it_geo.setAllPositions(points, space)


def set_matrix_row(matrix, new_vector, row):
    """Sets a matrix row with an MVector or MPoint.
    @param[in/out] matrix Matrix to set.
    @param[in] new_vector Vector to use.
    @param[in] row Row number.
    """
    set_matrix_cell(matrix, new_vector.x, row, 0)
    set_matrix_cell(matrix, new_vector.y, row, 1)
    set_matrix_cell(matrix, new_vector.z, row, 2)


def set_matrix_cell(matrix, value, row, column):
    """Sets a matrix cell
    @param[in/out] matrix Matrix to set.
    @param[in] value Value to set cell.
    @param[in] row Row number.
    @param[in] column Column number.
    """
    OpenMaya.MScriptUtil.setDoubleArray(matrix[row], column, value)

def rebuildTarget(attr):
    """
    输入一个bs目标体属性名类似 bsName.weightName后,会重建这个目标体
    :param attr:
    :return:
    """
    targetIndex = pm.PyNode(attr).index()
    bsName, attrName = attr.split('.')
    bsNode = pm.PyNode(bsName)
    geometryNode = bsNode.getBaseObjects()[0].getParent()
    orgShape = bsNode.getInputGeometry()[0].name()
    # createTarget
    newMeshShape = cmds.createNode('mesh', n='%sShape' % attrName)
    newTarget = cmds.listRelatives(newMeshShape, p=True)
    cmds.hide(newTarget)
    cmds.connectAttr('%s.worldMesh[0]' % orgShape, '%s.inMesh' % newMeshShape)
    cmds.refresh(f=True)
    cmds.disconnectAttr('%s.worldMesh[0]' % orgShape, '%s.inMesh' % newMeshShape)
    # move vtx
    ictValue = cmds.getAttr('%s.it[0].itg[%s].iti[6000].ict' % (bsName, targetIndex))
    if ictValue:
        vtxList = cmds.ls(['%s.%s' % (newTarget[0], vtxE) for vtxE in ictValue], fl=True)
        vtxRelativeTranslateList = cmds.getAttr('%s.it[0].itg[%s].iti[6000].ipt' % (bsName, targetIndex))
        for i in range(len(vtxList)):
            currentMoveValue = vtxRelativeTranslateList[i][:-1]
            cmds.move(currentMoveValue[0], currentMoveValue[1], currentMoveValue[2], vtxList[i], r=True, ws=True)
    # connect to blendShape
    cmds.connectAttr('%s.worldMesh[0]' % newMeshShape, '%s.it[0].itg[%s].iti[6000].igt' % (bsName, targetIndex))
    return newTarget

def mirrorTarget(attrStr='bsName.weightName',searchStr = 'lf_',searchToStr = 'rt_'):
    """
    镜像指定名称的bs目标体
    :param attrStr:
    :param searchStr:
    :param searchToStr:
    :return:
    """
    bsName,attrName = attrStr.split('.')
    bsNode = pm.PyNode(bsName)
    geometryNode = bsNode.getBaseObjects()[0].getParent()
    orgShape = bsNode.getInputGeometry()[0].name()
    toAttrName = attrName.replace(searchStr, searchToStr)
    bsWeightList = pm.listAttr(bsNode.w, m=True)
    targetIndex = pm.PyNode(attrStr).index()

    if not searchStr in attrName:
        return False
    inputTarget = cmds.listConnections('%s.it[0].itg[%s].iti[6000].igt'%(bsName,targetIndex),d=False)
    if not inputTarget:
        inputTarget = rebuildTarget(attrStr)

    if toAttrName in bsWeightList:
        toAttr_targetIndex = pm.PyNode('%s.%s' % (bsName, toAttrName)).index()
        toAttr_inputTarget = cmds.listConnections('%s.it[0].itg[%s].iti[6000].igt' % (bsName, toAttr_targetIndex),
                                                  d=False)
        if not toAttr_inputTarget:
            toAttr_inputTarget = rebuildTarget('%s.%s' % (bsName, toAttrName))
    else:
        # toTarget not exists   so   create new one
        newMeshShape = cmds.createNode('mesh', n='%sShape' % toAttrName)
        newTarget = cmds.listRelatives(newMeshShape, p=True)
        cmds.hide(newTarget)
        cmds.connectAttr('%s.worldMesh[0]' % orgShape, '%s.inMesh' % newMeshShape)
        cmds.refresh(f=True)
        cmds.disconnectAttr('%s.worldMesh[0]' % orgShape, '%s.inMesh' % newMeshShape)
        addBlendShape(targetList=newTarget, toObj=geometryNode.name())
        toAttr_inputTarget = newTarget

        # reverse WRAP
        # ---createORG
    newMeshShape = cmds.createNode('mesh', n='%sShape' % 'TEMP_ORG')
    newTarget = cmds.listRelatives(newMeshShape, p=True)
    cmds.hide(newTarget)
    cmds.connectAttr('%s.worldMesh[0]' % orgShape, '%s.inMesh' % newMeshShape)
    cmds.refresh(f=True)
    cmds.disconnectAttr('%s.worldMesh[0]' % orgShape, '%s.inMesh' % newMeshShape)
    toWrapGeo = reverseWrap([inputTarget[0], newTarget[0]], False)
    # wrapMesh connect toTargetMesh
    cmds.connectAttr('%s.worldMesh[0]' % toWrapGeo[0], '%s.inMesh' % toAttr_inputTarget[0])
    cmds.refresh(f=True)
    cmds.disconnectAttr('%s.worldMesh[0]' % toWrapGeo[0], '%s.inMesh' % toAttr_inputTarget[0])
    # setZero
    vtxAttrList = cmds.ls('%s.pnts[*]' % toAttr_inputTarget[0], fl=True)
    setDataList = len(vtxAttrList) * [0, 0, 0]
    cmds.setAttr('%s.pnts[*]' % toAttr_inputTarget[0], *setDataList)
    # clean
    cmds.delete(toWrapGeo, newTarget, inputTarget, toAttr_inputTarget)

def addBlendShape(targetList=[],toObj = ''):
    #2list
    if type(targetList) != list:
        targetList = [targetList]
    #top
    returnList = []
    bsNode = pm.listHistory(toObj,pdo=True,type='blendShape')
    if not bsNode:
        bsNode = pm.blendShape(toObj,foc=True,n='%s_correctiveBs'%toObj)
    for targetE in targetList:
        #no exists
        if not cmds.objExists(targetE):
            #create new target
            pm_toObj = pm.PyNode(toObj)
            orgShape = pm_toObj.getShapes()[-1].name()
            newMeshShape = cmds.createNode('mesh',n='%sShape'%targetE)
            newTarget = cmds.listRelatives(newMeshShape,p=True)
            cmds.hide(newTarget)
            cmds.connectAttr('%s.worldMesh[0]'%orgShape,'%s.inMesh'%newMeshShape)
            cmds.refresh(f=True)
            cmds.disconnectAttr('%s.worldMesh[0]'%orgShape,'%s.inMesh'%newMeshShape)
        #targetExists
        targetAttr = '%s.%s'%(bsNode[0],targetE)
        if cmds.objExists(targetAttr):
            continue
        #get Max+1 index
        wiList = bsNode[0].weightIndexList()
        if wiList:
            newIndex = wiList[-1]+1
        else:
            newIndex = 0
        pm.blendShape(bsNode[0],e=True,t=(toObj,newIndex,targetE,1))
        returnList.append(targetAttr)
    return returnList

def meshOrig(meshNode):
    MeshOrigList = []
    Mesh_Orig = cmds.listHistory(meshNode)
    for i in range(len(Mesh_Orig)):
        if cmds.nodeType(Mesh_Orig[i]) == 'mesh':
            if 'Orig' in Mesh_Orig[i]:
                if Mesh_Orig[i] != None:
                    if cmds.listConnections(Mesh_Orig[i] + '.worldMesh[0]', source=True):
                        MeshOrigList.append(Mesh_Orig[i])

    return MeshOrigList

def getWeightIndex(blendShapeName, target):
    """

    :param blendShapeName:
    :param target:
    :return:
    """
    aliases = cmds.aliasAttr(blendShapeName, q=True)
    a = aliases.index(target)
    weight = aliases[(a + 1)]
    index = weight.split('[')[(-1)][:-1]
    return int(index)

def getInbetweenWeight(blendShapeName, target):
    """

    :param blendShapeName:
    :param target:
    :return:
    """
    tragetIndexItem = getWeightIndex(blendShapeName, target)
    inputTargetItem = cmds.getAttr(
        "%s.inputTarget[0].inputTargetGroup[%d].inputTargetItem" % (blendShapeName, tragetIndexItem), mi=True
    )
    weightList = []
    for i in inputTargetItem:
        indexInt = (int(i) - 5000) / 1000.0
        weightList.append(indexInt)

    return weightList

def removeTarget(blendShapeName, target):
    count = cmds.getAttr('%s.inputTarget[0].inputTargetGroup'%blendShapeName, mi=True)[(-1)] + 1
    tragetIndexItem = getWeightIndex(blendShapeName, target)

def InputTargetGroup(blendShapeNode, target):
    tragetIndexItem = getWeightIndex(blendShapeNode, target)
    return tragetIndexItem

def reverseWrap(objList=[],deleteWrapGroup=True):
    """

    :param objList:
    :param deleteWrapGroup:
    :return:
    """
    if not cmds.objExists('reverseWrap_delete') and objList:  # create wrapGroup
        deleteGroup = cmds.group(em=True, n='reverseWrap_delete')
        wrapGeo = cmds.duplicate(objList[1], rr=True, name=('reverseWrap_outputGeometry'))
        newBaseGeo = cmds.duplicate(objList[1], n='reverseWrap_bsGeometry')
        cmds.parent(newBaseGeo, wrapGeo, deleteGroup)
        cmds.setAttr(newBaseGeo[0] + '.sx', -1)
        cmds.select(wrapGeo, newBaseGeo[0])
        mel.eval('doWrapArgList "7" { "1","0","1", "2", "1", "1", "1", "0" };')

    else:
        deleteGroup = ['reverseWrap_delete']
        wrapGeo = ['reverseWrap_outputGeometry']
        newBaseGeo = ['reverseWrap_bsGeometry']
    reverseGeo = []
    if objList:  # output
        bsNodeName = cmds.blendShape(objList[0], newBaseGeo[0], w=(0, 1))
        cmds.refresh(f=True)
        reverseGeo = cmds.duplicate(wrapGeo[0], n=objList[0] + '_reverseWrap')
        cmds.parent(reverseGeo, w=True)
        cmds.delete(bsNodeName)
    if deleteWrapGroup:  # delete useless
        cmds.delete(wrapGeo[0], ch=True)
        cmds.delete(deleteGroup)
    return reverseGeo

