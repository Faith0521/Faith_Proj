# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-07-25 8:58
# Description:

import pymel.core as pm


def pin_to_surface(oNurbs, sourceObj=None, uPos=0.5, vPos=0.5):
    """
    This function replaces what I used to use follicles for.
    It pins an object to a surface's UV coordinates.
    In rare circumstances follicles can flip and jitter. This seems to solve that.
    @param oNurbs:
    @param sourceObj:
    @param uPos:
    @param vPos:
    @return:
    """
    # Parse whether it is a nurbsSurface shape or transform
    if type(oNurbs) == str and pm.objExists(oNurbs):
        oNurbs = pm.PyNode(oNurbs)
    if type(oNurbs) == pm.nodetypes.Transform:
        pass
    elif type(oNurbs) == pm.nodetypes.NurbsSurface:
        oNurbs = oNurbs.getTransform()
    elif type(oNurbs) == list:
        pm.warning('Specify a NurbsSurface, not a list.')
        return False
    else:
        pm.warning('Invalid surface object specified.')
        return False

    pointOnSurface = pm.createNode('pointOnSurfaceInfo')
    oNurbs.getShape().worldSpace.connect(pointOnSurface.inputSurface)
    # follicles remap from 0-1, but closestPointOnSurface must take minMaxRangeV into account
    paramLengthU = oNurbs.getShape().minMaxRangeU.get()
    paramLengthV = oNurbs.getShape().minMaxRangeV.get()

    if sourceObj:
        # Place the follicle at the position of the sourceObj
        # Otherwise use the UV coordinates passed in the function
        if isinstance(sourceObj, str) and pm.objExists(sourceObj):
            sourceObj = pm.PyNode(sourceObj)
        if isinstance(sourceObj, pm.nodetypes.Transform):
            pass
        elif isinstance(sourceObj, pm.nodetypes.Shape):
            sourceObj = sourceObj.getTransform()
        elif type(sourceObj) == list:
            pm.warning('sourceObj should be a transform, not a list.')
            return False
        else:
            pm.warning('Invalid sourceObj specified.')
            return False
        oNode = pm.createNode('closestPointOnSurface', n='ZZZTEMP')
        oNurbs.worldSpace.connect(oNode.inputSurface, force=True)
        oNode.inPosition.set(sourceObj.getTranslation(space='world'))
        uPos = oNode.parameterU.get()
        vPos = oNode.parameterV.get()
        pm.delete(oNode)

    pName = '{}_foll#'.format(oNurbs.name())
    result = pm.spaceLocator(n=pName).getShape()
    result.addAttr('parameterU', at='double', keyable=True, dv=uPos)
    result.addAttr('parameterV', at='double', keyable=True, dv=vPos)
    # set min and max ranges for the follicle along the UV limits.
    result.parameterU.setMin(paramLengthU[0])
    result.parameterV.setMin(paramLengthV[0])
    result.parameterU.setMax(paramLengthU[1])
    result.parameterV.setMax(paramLengthV[1])
    result.parameterU.connect(pointOnSurface.parameterU)
    result.parameterV.connect(pointOnSurface.parameterV)

    # Compose a 4x4 matrix
    mtx = pm.createNode('fourByFourMatrix')
    outMatrix = pm.createNode('decomposeMatrix')
    mtx.output.connect(outMatrix.inputMatrix)
    outMatrix.outputTranslate.connect(result.getTransform().translate)
    outMatrix.outputRotate.connect(result.getTransform().rotate)

    '''
    # Normalize these vectors
    [tanu.x, tanu.y, tanu.z, 0]
    [norm.x, norm.y, norm.z, 0]
    [tanv.x, tanv.y, tanv.z, 0]
    # World space position
    [pos.x, pos.y, pos.z, 1]
    '''

    pointOnSurface.normalizedTangentUX.connect(mtx.in00)
    pointOnSurface.normalizedTangentUY.connect(mtx.in01)
    pointOnSurface.normalizedTangentUZ.connect(mtx.in02)
    mtx.in03.set(0)

    pointOnSurface.normalizedNormalX.connect(mtx.in10)
    pointOnSurface.normalizedNormalY.connect(mtx.in11)
    pointOnSurface.normalizedNormalZ.connect(mtx.in12)
    mtx.in13.set(0)

    pointOnSurface.normalizedTangentVX.connect(mtx.in20)
    pointOnSurface.normalizedTangentVY.connect(mtx.in21)
    pointOnSurface.normalizedTangentVZ.connect(mtx.in22)
    mtx.in23.set(0)

    pointOnSurface.positionX.connect(mtx.in30)
    pointOnSurface.positionY.connect(mtx.in31)
    pointOnSurface.positionZ.connect(mtx.in32)
    mtx.in33.set(1)

    return result


def snapToSurfaceAverage(oNurbs, numberOfFollicles=10, uPos=0.5, vPos=0.5):
    follicleShapeList = []
    if isinstance(oNurbs, str):
        oNurbs = pm.PyNode(oNurbs)

    # To place a range of "follicles", just loop over U or V or both.
    # Make sure to multiply by the U or V range of your surface. UV does not always go 0 to 1.
    paramLengthU = oNurbs.getShape().minMaxRangeU.get()

    for i in range(numberOfFollicles):
        uPosR = (i/float(numberOfFollicles-1)) * paramLengthU[1]
        shape = pin_to_surface(oNurbs, uPos=uPosR, vPos=vPos)
        follicleShapeList.append(shape)

    return follicleShapeList
