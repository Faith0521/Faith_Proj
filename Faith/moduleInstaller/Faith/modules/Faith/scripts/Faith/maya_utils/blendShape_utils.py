# -*- coding: utf-8 -*-
# @Author: 46314
# @Date:   2022-09-19 20:25:58
# @Last Modified by:   46314
# @Last Modified time: 2022-09-20 19:07:29

# import standard modules
from maya import cmds,mel
from pymel import core as pm
# import maya modules
from maya import OpenMayaAnim
from maya import OpenMaya

# import local modules
from Faith.maya_utils import object_utils

# define local variables
origin = OpenMayaAnim.MFnBlendShapeDeformer.kLocalOrigin
world_origin = OpenMayaAnim.MFnBlendShapeDeformer.kWorldOrigin
front_of_chain = OpenMayaAnim.MFnBlendShapeDeformer.kFrontOfChain
normal_chain = OpenMayaAnim.MFnBlendShapeDeformer.kNormal

STR = object_utils.STR
UNICODE = object_utils.UNICODE

def is_blendshape(object_name):
    """
    return true if the node object is of type blendShape.
    :return: <bool>
    """
    return bool(object_utils.has_fn(object_utils.get_m_obj(object_name), 'blendShape'))


def get_connected_blendshape_names(mesh_obj):
    """
    get connected blendshape from this mesh
    :param mesh_obj:
    :return:
    """
    return object_utils.get_connected_nodes(mesh_obj,
                                            find_node_type='blendShape',
                                            down_stream=False,
                                            up_stream=True,
                                            as_strings=True)


def get_connected_blendshape(mesh_obj):
    """
    get connected blendshape from this mesh
    :param mesh_obj:
    :return:
    """
    return object_utils.get_connected_nodes(mesh_obj, find_node_type='blendShape', down_stream=False, up_stream=True)


def get_connected_mesh_shape(blend_node=""):
    """
    gets the connected mesh this blend shape is acting on.
    :param blend_node:
    :return:
    """
    return object_utils.get_connected_nodes(blend_node, find_node_type='mesh', down_stream=True, up_stream=False)


def get_scene_blendshapes(as_strings=False):
    """
    returns a array of valid blendshapes in the scene.
    :return: <dict> {OpenMaya.MObject: <str> blendShape node.}
    """
    blendshapes = {}
    mesh_array = object_utils.get_scene_objects(node_type='mesh')
    for mesh_obj in mesh_array:
        obj_name = object_utils.get_m_object_name(mesh_obj)
        blend_node = get_connected_blendshape(mesh_obj)
        if blend_node:
            if as_strings:
                blendshapes[obj_name] = object_utils.get_m_object_name(blend_node[0])
            else:
                blendshapes[obj_name] = blend_node[0],
    return blendshapes


def get_deformer_fn(object_name=""):
    """
    get a blendshape deformer fn
    :param object_name: <str> object name to get get blendShapeDeformer function set from.
    :return: <OpenMaya.MFnBlendShapeDeformer> object type.
    """
    m_blend_obj = None
    if object_utils.is_transform(object_name):
        shape_obj = object_utils.get_shape_name(object_name)[0]
        m_blend_obj = get_connected_blendshape(shape_obj)[0]
    elif is_blendshape(object_name):
        m_blend_obj = object_utils.get_m_obj(object_name)
    return OpenMayaAnim.MFnBlendShapeDeformer(m_blend_obj)


def round_blend_step(step):
    """
    get the blendshape weight value
    :param step:
    :return:
    """
    return int(step * 1000) / 1000.0


def get_base_object(blend_name=""):
    """
    gets the connected base object to this blendShape node.
    :param blend_name:
    :return:
    """
    return get_connected_mesh_shape(blend_name)


def create_blendshape(mesh_objects, name=""):
    """
    creates a new blendShape from the array of mesh objects provided
    :param mesh_objects: <tuple> array of mesh shapes.
    :param name: <str> name of the blendshape.
    :return: <OpenMayaAnim.MFnBlendShapeDeformer>
    """
    blend_fn = OpenMayaAnim.MFnBlendShapeDeformer()
    if isinstance(mesh_objects, (STR, UNICODE)):
        mesh_obj = object_utils.get_m_obj(mesh_objects)
        blend_fn.create(mesh_obj, origin, normal_chain)
    elif len(mesh_objects) > 1 and isinstance(mesh_objects, (tuple, list)):
        mesh_obj_array = object_utils.get_m_obj_array(mesh_objects)
        blend_fn.create(mesh_obj_array, origin, normal_chain)
    else:
        raise ValueError("Could not create blendshape.")

    if name:
        object_utils.rename_node(blend_fn.object(), name)
    return blend_fn


def add_target(targets_array, blend_name="", weight=1.0, index=0):
    """
    adds a new target with the weight to this blend shape.
    Maya has a fail-safe to get the inputTargetItem from 6000-5000
    :param targets_array: <tuple> array of mesh shapes designated as targets.
    :param blend_name: <str> the blendShape node to add targets to.
    :param weight: <float> append this weight value to the target.
    :param index: <int> specify the index in which to add a target to the blend node.
    :return:
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    if isinstance(targets_array, (STR, UNICODE)):
        targets_array = targets_array
    targets_array = object_utils.get_m_shape_obj_array(targets_array)
    length = targets_array.length()
    if not index:
        index = get_weight_indices(blend_fn.name()).length() + 1
    # step = 1.0 / length - 1
    for i in range(0, length):
        # weight_idx = (i * step) * 1000/1000.0
        blend_fn.addTarget(base_obj, index, targets_array[i], weight)
    return True


def removeTarget(blendShape, target, baseGeometry):
    '''
    Remove the specified blendShape target
    @param blendShape: Name of blendShape to remove target from
    @type blendShape: str
    @param target: BlendShape target to remove
    @type target: str
    @param baseGeometry: BlendShape base geometry name
    @type baseGeometry: str
    '''
    # Check blendShape
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape node!')

    # Get target index
    targetIndex = getTargetIndex(blendShape, target)

    # Connect null duplicate
    cmds.setAttr(blendShape + '.envelope', 0.0)
    dup = cmds.duplicate(baseGeometry)
    cmds.setAttr(blendShape + '.envelope', 1.0)
    connectToTarget(blendShape, dup[0], target, baseGeometry, 1.0, force=True)

    # Remove target
    cmds.blendShape(blendShape, e=True, rm=True, t=[baseGeometry, targetIndex, dup[0], 1.0])

    # Delete duplicate geometry
    cmds.delete(dup)


def renameTarget(blendShape, target, newName):
    """
    Rename the specified blendShape target
    :param blendShape:
    :param target:
    :param newName:
    :return:
    """
    # Check blendShape
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape node!')

    # Check target
    if not hasTarget(blendShape, target):
        raise Exception('BlendShape "' + blendShape + '" has no target "' + target + '"!')

    # Rename target attribute
    cmds.aliasAttr(newName, blendShape + '.' + target)

    # Return Result
    return newName


def removeUnconnectedTargets(blendShape, base):
    """

    :param blendShape:
    :param base:
    :return:
    """
    # Check blendShape
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape deformer!!')

    # Get blendShape target list
    targetList = getTargetList(blendShape)

    # Check blendShape target connections
    deletedTargetList = []
    for target in targetList:
        targetConn = cmds.listConnections(blendShape + '.' + target, s=True, d=False)

        # If no incoming connnections, delete target
        if not targetConn:
            try:
                removeTarget(blendShape, target, base)
            except:
                print('Unable to delete blendShape target "' + target + '"!')
            else:
                print('Target "' + target + '" deleted!')
                deletedTargetList.append(target)

    # Return result
    return deletedTargetList


def hasTarget(blendShape, target):
    """
    Specify if the a named target exists on a blendShape node
    :param blendShape:
    :param target:
    :return:
    """
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape node!')

        # Check target
    if target in getTargetList(blendShape): return True

    # Return Result
    return False


def getTargetList(blendShape):
    """
    Return the target list for the input blendShape
    :param blendShape:
    :return:
    """
    # Check blendShape
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape node!')

    # Get attribute alias
    targetList = cmds.listAttr(blendShape + '.w', m=True)
    if not targetList: targetList = []

    # Return result
    return targetList


def connectToTarget(blendShape, geometry, target, baseGeometry, weight=1.0, force=False):
    '''
    Connect a new target geometry to a specified blendShape target
    @param blendShape: Name of blendShape to connect geometry target to
    @type blendShape: str
    @param geometry: Geometry to connect to blendShape target
    @type geometry: str
    @param target: BlendShape target name to connect geometry to
    @type target: str
    @param baseGeometry: BlendShape base geometry name
    @type baseGeometry: str
    @param weight: BlendShape target weight value to connect geometry to
    @type weight: float
    '''
    from Faith.maya_utils import deformer_utils
    # Check blendShape
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape node!')

    # Check target
    if not cmds.objExists(blendShape + '.' + target):
        raise Exception('Blendshape "' + blendShape + '" has no target "' + target + '"!')

    # Check geometry
    if not cmds.objExists(geometry):
        raise Exception('Geometry object "' + geometry + '" does not exist!')

    # Get target index
    targetIndex = getTargetIndex(blendShape, target)

    # FORCE connection
    if force:

        # Get geometry details
        geomIndex = deformer_utils.getGeomIndex(baseGeometry, blendShape)
        geomShape = cmds.listRelatives(geometry, s=True, ni=True)
        if geomShape:
            geomShape = geomShape[0]
            geomType = cmds.objectType(geomShape)
        else:
            geomShape = geometry
            geomType = 'none'

        # Get geometry type output attribute.
        # Non dict values allow specific node attributes to be connected!!
        geomDict = {'mesh': '.worldMesh[0]', 'nurbsSurface': '.worldSpace[0]', 'nurbsCurve': '.worldSpace[0]'}
        if geomType in geomDict.keys():
            geomAttr = geomDict[geomType]
        else:
            geomAttr = ''

        # Get weight index
        wtIndex = int(weight * 6000)

        # Connect geometry to target input
        cmds.connectAttr(geomShape + geomAttr,
                       blendShape + '.inputTarget[' + str(geomIndex) + '].inputTargetGroup[' + str(
                           targetIndex) + '].inputTargetItem[' + str(wtIndex) + '].inputGeomTarget', f=True)

    else:

        # Connect geometry to target input
        cmds.blendShape(blendShape, e=True, t=[baseGeometry, targetIndex, geometry, weight])


def getTargetIndex(blendShape, target):
    '''
    Get the target index of the specified blendShape and target name
    @param blendShape: Name of blendShape to get target index for
    @type blendShape: str
    @param target: BlendShape target to get the index for
    @type target: str
    '''
    # Check blendShape
    if not is_blendshape(blendShape):
        raise Exception('Object "' + blendShape + '" is not a valid blendShape node!')

    # Check target
    if not cmds.objExists(blendShape + '.' + target):
        raise Exception('Blendshape "' + blendShape + '" has no target "' + target + '"!')

    # Get attribute alias
    aliasList = cmds.aliasAttr(blendShape, q=True)
    aliasIndex = aliasList.index(target)
    aliasAttr = aliasList[aliasIndex + 1]

    # Get index
    targetIndex = int(aliasAttr.split('[')[-1].split(']')[0])

    # Return result
    return targetIndex


def get_weight_indices(blend_name=""):
    """
    get the weight indices from the blendShape name provided.
    :param blend_name: <str> the name of the blendShape node.
    :return: <OpenMaya.MIntArray>
    """
    blend_fn = get_deformer_fn(blend_name)
    int_array = OpenMaya.MIntArray()
    blend_fn.weightIndexList(int_array)
    return int_array


def get_num_weights(blend_name=""):
    """
    get the weight indices from the blendShape name provided.
    :param blend_name: <str> the name of the blendShape node.
    :return: <OpenMaya.MIntArray>
    """
    return get_deformer_fn(blend_name).numWeights()


def delete_blendshapes(mesh_obj):
    """
    deletes all connected blendshape.
    :param mesh_obj:
    :return:
    """
    shape_obj = object_utils.get_shape_name(mesh_obj)[0]
    cmds.delete(get_connected_blendshape_names(shape_obj))


def get_base_objects(blend_name=""):
    """
    return the base objects associated with this blend shape node.
    :param blend_name: <str> the name of the blendShape node.
    :return: <tuple> array of base objects
    """
    m_obj_array = OpenMaya.MObjectArray()
    blend_fn = get_deformer_fn(blend_name)
    blend_fn.getBaseObjects(m_obj_array)
    return object_utils.convert_obj_array_to_string_array(m_obj_array)


def getInbetweenWeight(blendShapeName, target):
    """

    :param blendShapeName:
    :param target:
    :return:
    """
    tragetIndexItem = getTargetIndex(blendShapeName, target)
    inputTargetItem = cmds.getAttr(
        "%s.inputTarget[0].inputTargetGroup[%d].inputTargetItem" % (blendShapeName, tragetIndexItem), mi=True
    )
    weightList = []
    for i in inputTargetItem:
        indexInt = (int(i) - 5000) / 1000.0
        weightList.append(indexInt)

    return weightList


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
        add_target([geometryNode.name()], blend_name=bsName, weight=1.0)
        # addBlendShape(targetList=newTarget, toObj=geometryNode.name())
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
