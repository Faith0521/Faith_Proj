# -*- coding: utf-8 -*-
# @Author: 46314
# @Date:   2022-09-19 20:33:56
# @Last Modified by:   46314
# @Last Modified time: 2022-09-19 20:34:02

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import re
from . import object_utils

# Create exception class
class UserInputError(Exception): pass


def isDeformer(deformer):
    '''
    Test if node is a valid deformer
    @param deformer: Name of deformer to query
    @type deformer: str
    '''
    # Check deformer exists
    if not cmds.objExists(deformer): return False
    # Check deformer type
    nodeType = cmds.nodeType(deformer,i=1)
    if not nodeType.count('geometryFilter'): return False
    # Return result
    return True


def getDeformerFn(deformer):
    '''
    Initialize and return an MFnWeightGeometryFilter function set attached to the specified deformer
    @param deformer: Name of deformer to create function set for
    @type deformer: str
    '''
    # Checks
    if not cmds.objExists(deformer):
        raise UserInputError('Deformer ' + deformer + ' does not exist!')

    # Get MFnWeightGeometryFilter
    deformerObj = object_utils.get_m_obj(deformer)
    deformerFn = OpenMayaAnim.MFnWeightGeometryFilter(deformerObj)

    # Return result
    return deformerFn


def getGeomIndex(geometry, deformer):
    '''
    Returns the geometry index of a shape to a specified deformer.
    @param geometry: Name of shape or parent transform to query
    @type geometry: str
    @param deformer: Name of deformer to query
    @type deformer: str
    '''
    # Verify input
    if not isDeformer(deformer):
        raise UserInputError('Object "' + deformer + '" is not a valid deformer!')

    # Check geometry
    geo = geometry
    if cmds.objectType(geometry) == 'transform':
        try:
            geometry = cmds.listRelatives(geometry, s=True, ni=True, pa=True)[0]
        except:
            raise UserInputError('Object "' + geo + '" is not a valid geometry!')
    geomObj = object_utils.get_m_obj(geometry)

    # Get geometry index
    deformerObj = object_utils.get_m_obj(deformer)
    deformerFn = OpenMayaAnim.MFnGeometryFilter(deformerObj)
    try:
        geomIndex = deformerFn.indexForOutputShape(geomObj)
    except:
        raise UserInputError('Object "' + geometry + '" is not affected by deformer "' + deformer + '"!')

    # Retrun result
    return geomIndex






