# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-07-19 20:11:59
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-19 20:14:06
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import pymel.core as pm
from Faith.maya_utils.python_utils import PY2
from Faith.maya_utils import object_utils

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
        base = sel[0]
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
    bs = findBlendShapeInHistory(base)
    connections = {}
    if bs:
        targetList = cmds.listAttr(bs + '.w', m=True)
        
        for target in targetList:
            index = pm.PyNode(bs + "." + target).index()
            cns = cmds.listConnections('%s.inputTarget[0].inputTargetGroup[%d].inputTargetItem[6000].inputGeomTarget' % (bs, index),s=1,d=0,plugs=1)
            if cns:
                cmds.disconnectAttr(cns[0], '%s.inputTarget[0].inputTargetGroup[%d].inputTargetItem[6000].inputGeomTarget' % (bs, index))
                connections[cns[0]] = '%s.inputTarget[0].inputTargetGroup[%d].inputTargetItem[6000].inputGeomTarget' % (bs, index)
    # Get the intermediate mesh
    orig_mesh = get_shape(base, intermediate=True)

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
    deformer_mobj = object_utils.get_m_obj(deformer)
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

    if connections:
        for target,ipt in connections.items():
            cmds.connectAttr(target, ipt, force=True)

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
