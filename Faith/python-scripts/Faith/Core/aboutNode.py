# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:08
# @Last Modified by:   YinYuFei
# @Last Modified time: 2022-07-10 19:22:16

"""Functions to create and connect nodes."""

import pymel.core as pm, maya.cmds as mc, maya.mel as mel
import pymel.core.datatypes as datatypes
import json, inspect, re, math
from pymel import versions
from . import aboutAttribute
from .aboutPy import PY2, string_types

maya_Ver = int(str(mc.about(v=True))[0:4])

from maya import OpenMaya as om
from maya import OpenMayaAnim as aom


#############################################
# CREATE SIMPLE NODES
#############################################


def createMultMatrixNode(mA, mB, target=False, transform='srt'):
    """Create Maya multiply Matrix node.

    Note:
        This node have same functionality as the default Maya matrix
        multiplication.

    Arguments:
        mA (matrix): input matrix A.
        mB (matrix): input matrix B.
        target (dagNode): object target to apply the transformation
        transform (str): if target is True. out transform  to SRT valid
            value s r t

    Returns:
        pyNode: Newly created mGear_multMatrix node

    """
    node = pm.createNode("multMatrix")
    for m, mi in zip([mA, mB], ['matrixIn[0]', 'matrixIn[1]']):
        if isinstance(m, datatypes.Matrix):
            pm.setAttr(node.attr(mi), m)
        else:
            pm.connectAttr(m, node.attr(mi))
    if target:
        dm_node = pm.createNode("decomposeMatrix")
        pm.connectAttr(node + ".matrixSum",
                       dm_node + ".inputMatrix")
        if 't' in transform:
            pm.connectAttr(dm_node + ".outputTranslate",
                           target.attr("translate"), f=True)
        if 'r' in transform:
            pm.connectAttr(dm_node + ".outputRotate",
                           target.attr("rotate"), f=True)
        if 's' in transform:
            pm.connectAttr(dm_node + ".outputScale",
                           target.attr("scale"), f=True)

    return node


def createDecomposeMatrixNode(m, name=""):
    """
    Create and connect a decomposeMatrix node.

    Arguments:
        m(str or attr): The matrix attribute name.

    Returns:
        pyNode: the newly created node.

    >>> dm_node = nod.createDecomposeMatrixNode(mulmat_node+".output")

    """
    node = pm.createNode("decomposeMatrix", n=name + "_decomp")

    pm.connectAttr(m, node + ".inputMatrix")

    return node


def createDistNode(objA, objB, output=None):
    """Create and connect a distance node.

    Arguments:
        objA (dagNode): The dagNode A.
        objB (dagNode): The dagNode B.
        output (attr): Output attribute.

    Returns:
        pyNode: the newly created node.

    >>> distA_node = nod.createDistNode(self.tws0_loc, self.tws1_loc)

    """
    node = pm.createNode("distanceBetween")

    dm_nodeA = pm.createNode("decomposeMatrix")
    dm_nodeB = pm.createNode("decomposeMatrix")

    pm.connectAttr(objA + ".worldMatrix", dm_nodeA + ".inputMatrix")
    pm.connectAttr(objB + ".worldMatrix", dm_nodeB + ".inputMatrix")

    pm.connectAttr(dm_nodeA + ".outputTranslate", node + ".point1")
    pm.connectAttr(dm_nodeB + ".outputTranslate", node + ".point2")

    if output:
        pm.connectAttr(node + ".distance", output)

    return node


def createConditionNode(firstTerm=False,
                        secondTerm=False,
                        operator=0,
                        ifTrue=False,
                        ifFalse=False):
    """Create and connect a condition node.

    ========    ======
    operator    index
    ========    ======
    ==          0
    !=          1
    >           2
    >=          3
    <           4
    <=          5
    ========    ======

    Arguments:
        firstTerm (attr): The attribute string name for the first
            conditions.
        secondTerm (attr): The attribute string for the second
            conditions.
        operator (int): The operator to make the condition.
        ifTrue (bool or attr): If an attribute is provided will connect
            ifTrue output.
        ifFalse (bool or attr): If an attribute is provided will connect
            ifFalse output.

    Returns:
        pyNode: the newly created node.

    >>> cond1_node = nod.createConditionNode(self.soft_attr,
                                             0,
                                             2,
                                             subtract3_node+".output1D",
                                             plusTotalLength_node+".output1D")

    """
    check_list = [pm.Attribute, str]
    if PY2:
        check_list.append(unicode)
    node = pm.createNode("condition")
    pm.setAttr(node + ".operation", operator)
    if firstTerm:
        aboutAttribute.connectSet(firstTerm, node + ".firstTerm", check_list)

    if secondTerm:
        aboutAttribute.connectSet(secondTerm, node + ".secondTerm", check_list)

    if ifTrue:
        aboutAttribute.connectSet(ifTrue, node + ".colorIfTrueR", check_list)

    if ifFalse:
        aboutAttribute.connectSet(ifFalse, node + ".colorIfFalseR", check_list)

    return node


def createBlendNode(inputA, inputB, blender=.5):
    """Create and connect a createBlendNode node.

    Arguments:
        inputA (attr or list of 3 attr): The attribute input A
        inputB (attr or list of 3 attr): The attribute input B
        blender (float or attr): Float in 0 to 1 range or attribute
            string name.


    Returns:
        pyNode: the newly created node.

    >>> blend_node = nod.createBlendNode(
            [dm_node+".outputRotate%s"%s for s in "XYZ"],
            [cns+".rotate%s"%s for s in "XYZ"],
            self.lock_ori_att)

    """
    node = pm.createNode("blendColors")

    if not isinstance(inputA, list):
        inputA = [inputA]

    if not isinstance(inputB, list):
        inputB = [inputB]

    for item, s in zip(inputA, "RGB"):
        if (isinstance(item, string_types)
                or isinstance(item, pm.Attribute)):
            pm.connectAttr(item, node + ".color1" + s)
        else:
            pm.setAttr(node + ".color1" + s, item)

    for item, s in zip(inputB, "RGB"):
        if (isinstance(item, string_types)
                or isinstance(item, pm.Attribute)):
            pm.connectAttr(item, node + ".color2" + s)
        else:
            pm.setAttr(node + ".color2" + s, item)

    if (isinstance(blender, string_types)
            or isinstance(blender, pm.Attribute)):
        pm.connectAttr(blender, node + ".blender")
    else:
        pm.setAttr(node + ".blender", blender)

    return node


def createPairBlend(inputA=None,
                    inputB=None,
                    blender=.5,
                    rotInterpolation=0,
                    output=None,
                    trans=True,
                    rot=True):
    """Create and connect a PairBlend node.

    Arguments:
        inputA (dagNode): The transfomr input 1
        inputB (dagNode): The transfomr input 2
        blender (float or attr): Float in 0 to 1 range or attribute
            string name.
        rotInterpolation (int): Rotation interpolation option. 0=Euler.
            1=Quaternion.
        output (dagNode): The output node with the blend transfomr
            applied.
        trans (bool): If true connects translation.
        rot (bool): If true connects rotation.

    Returns:
        pyNode: the newly created node.

    Example:
        .. code-block:: python

            blend_node = nod.createPairBlend(self.legBonesFK[i],
                                             self.legBonesIK[i],
                                             self.blend_att,
                                             1)
            pm.connectAttr(blend_node + ".outRotate", x+".rotate")
            pm.connectAttr(blend_node + ".outTranslate", x+".translate")

    """
    node = pm.createNode("pairBlend")
    node.attr("rotInterpolation").set(rotInterpolation)

    if inputA:
        if trans:
            pm.connectAttr(inputA + ".translate", node + ".inTranslate1")
        if rot:
            pm.connectAttr(inputA + ".rotate", node + ".inRotate1")

    if inputB:
        if trans:
            pm.connectAttr(inputB + ".translate", node + ".inTranslate2")
        if rot:
            pm.connectAttr(inputB + ".rotate", node + ".inRotate2")

    if (isinstance(blender, string_types)
            or isinstance(blender, pm.Attribute)):
        pm.connectAttr(blender, node + ".weight")
    else:
        pm.setAttr(node + ".weight", blender)

    if output:
        if rot:
            pm.connectAttr(node + ".outRotate", output + ".rotate")
        if trans:
            pm.connectAttr(node + ".outTranslate", output + ".translate")

    return node


def createSetRangeNode(input,
                       oldMin,
                       oldMax,
                       newMin=0,
                       newMax=1,
                       output=None,
                       name="setRange"):
    """Create Set Range Node"""

    node = pm.createNode("setRange", n=name)

    if not isinstance(input, list):
        input = [input]

    for item, s in zip(input, "XYZ"):
        if (isinstance(item, string_types)
                or isinstance(item, pm.Attribute)):
            pm.connectAttr(item, node + ".value" + s)
        else:
            pm.setAttr(node + ".value" + s, item)

        if (isinstance(oldMin, string_types)
                or isinstance(oldMin, pm.Attribute)):
            pm.connectAttr(oldMin, node + ".oldMin" + s)
        else:
            pm.setAttr(node + ".oldMin" + s, oldMin)

        if (isinstance(oldMax, string_types)
                or isinstance(oldMax, pm.Attribute)):
            pm.connectAttr(oldMax, node + ".oldMax" + s)
        else:
            pm.setAttr(node + ".oldMax" + s, oldMax)

        if (isinstance(newMin, string_types)
                or isinstance(newMin, pm.Attribute)):
            pm.connectAttr(newMin, node + ".min" + s)
        else:
            pm.setAttr(node + ".min" + s, newMin)

        if (isinstance(newMax, string_types)
                or isinstance(newMax, pm.Attribute)):
            pm.connectAttr(newMax, node + ".max" + s)
        else:
            pm.setAttr(node + ".max" + s, newMax)

    if output:
        if not isinstance(output, list):
            output = [output]
        for out, s in zip(output, "XYZ"):
            pm.connectAttr(node + ".outValue" + s, out, f=True)

    return node


def createReverseNode(input, name, output=None):
    """Create and connect a reverse node.

    Arguments:
        input (attr or list of 3 attr): The attribute input.
        output (attr or list of 3 attr): The attribute to connect the
            output.

    Returns:
        pyNode: the newly created node.

    >>> fkvis_node = nod.createReverseNode(self.blend_att)

    """
    node = pm.createNode("reverse", n=name)

    if not isinstance(input, list):
        input = [input]

    for item, s in zip(input, "XYZ"):
        if (isinstance(item, string_types)
                or isinstance(item, pm.Attribute)):
            pm.connectAttr(item, node + ".input" + s)
        else:
            pm.setAttr(node + ".input" + s, item)

    if output:
        if not isinstance(output, list):
            output = [output]
        for out, s in zip(output, "XYZ"):
            pm.connectAttr(node + ".output" + s, out, f=True)

    return node


def createCurveInfoNode(crv):
    """Create and connect a curveInfo node.

    Arguments:
        crv (dagNode): The curve.

    Returns:
        pyNode: the newly created node.

    >>> crv_node = nod.createCurveInfoNode(self.slv_crv)

    """
    node = pm.createNode("curveInfo")

    shape = pm.listRelatives(crv, shapes=True)[0]

    pm.connectAttr(shape + ".local", node + ".inputCurve")

    return node


# TODO: update using plusMinusAverage node
def createAddNode(inputA, inputB):
    """Create and connect a addition node.

    Arguments:
        inputA (attr or float): The attribute input A
        inputB (attr or float): The attribute input B

    Returns:
        pyNode: the newly created node.

    >>> add_node = nod.createAddNode(self.roundness_att, .001)

    """
    node = pm.createNode("addDoubleLinear")

    if (isinstance(inputA, string_types)
            or isinstance(inputA, pm.Attribute)):
        pm.connectAttr(inputA, node + ".input1")
    else:
        pm.setAttr(node + ".input1", inputA)

    if (isinstance(inputB, string_types)
            or isinstance(inputB, pm.Attribute)):
        pm.connectAttr(inputB, node + ".input2")
    else:
        pm.setAttr(node + ".input2", inputB)

    return node


# TODO: update using plusMinusAverage node
def createSubNode(inputA, inputB):
    """Create and connect a subtraction node.

    Arguments:
        inputA (attr or float): The attribute input A
        inputB (attr or float): The attribute input B

    Returns:
        pyNode: the newly created node.

    >>> sub_nod = nod.createSubNode(self.roll_att, angle_outputs[i-1])

    """
    node = pm.createNode("addDoubleLinear")

    if (isinstance(inputA, string_types)
            or isinstance(inputA, pm.Attribute)):
        pm.connectAttr(inputA, node + ".input1")
    else:
        pm.setAttr(node + ".input1", inputA)

    if (isinstance(inputB, string_types)
            or isinstance(inputB, pm.Attribute)):
        neg_node = pm.createNode("multiplyDivide")
        pm.connectAttr(inputB, neg_node + ".input1X")
        pm.setAttr(neg_node + ".input2X", -1)
        pm.connectAttr(neg_node + ".outputX", node + ".input2")
    else:
        pm.setAttr(node + ".input2", -inputB)

    return node


def createPowNode(inputA, inputB, output=None):
    """Create and connect a power node.

    Arguments:
        inputA (attr, float or list of float): The attribute input A
        inputB (attr, float or list of float): The attribute input B
        output (attr or list of attr): The attribute to connect the
            output.

    Returns:
        pyNode: the newly created node.

    """
    return createMulDivNode(inputA, inputB, 3, output)


def createMulNode(inputA, inputB, output=None):
    """Create and connect a Multiply node.

    Arguments:
        inputA (attr, float or list of float): The attribute input A
        inputB (attr, float or list of float): The attribute input B
        output (attr or list of attr): The attribute to connect the
            output.

    Returns:
        pyNode: the newly created node.

    """
    return createMulDivNode(inputA, inputB, 1, output)


def createDivNode(inputA, inputB, output=None):
    """Create and connect a Divide node.

    Arguments:
        inputA (attr, float or list of float): The attribute input A
        inputB (attr, float or list of float): The attribute input B
        output (attr or list of attr): The attribute to connect the
            output.

    Returns:
        pyNode: the newly created node.

    Example:
        .. code-block:: python

            # Classic Maya style creation and connection = 4 lines
            div1_node = pm.createNode("multiplyDivide")
            div1_node.setAttr("operation", 2)
            div1_node.setAttr("input1X", 1)
            pm.connectAttr(self.rig.global_ctl+".sx",
                           div1_node+".input2X")

            # mGear style = 1 line
            div1_node = nod.createDivNode(1.0,
                                          self.rig.global_ctl+".sx")

    """
    return createMulDivNode(inputA, inputB, 2, output)


def createMulDivNode(inputA, inputB, operation=1, output=None):
    """Create and connect a Multiply or Divide node.

    Arguments:
        inputA (attr, float or list of float): The attribute input A
        inputB (attr, float or list of float): The attribute input B
        output (attr or list of attr): The attribute to connect the
            output.

    Returns:
        pyNode: the newly created node.

    """
    node = pm.createNode("multiplyDivide")
    pm.setAttr(node + ".operation", operation)

    if not isinstance(inputA, list):
        inputA = [inputA]

    if not isinstance(inputB, list):
        inputB = [inputB]

    for item, s in zip(inputA, "XYZ"):
        if (isinstance(item, string_types)
                or isinstance(item, pm.Attribute)):
            try:
                pm.connectAttr(item, node + ".input1" + s, f=True)
            except(UnicodeEncodeError, RuntimeError):
                # Maya in Japanese have an issue with unicodeEndoce
                # UnicodeEncodeError is a workaround
                pm.connectAttr(item, node + ".input1", f=True)
                break

        else:
            pm.setAttr(node + ".input1" + s, item)

    for item, s in zip(inputB, "XYZ"):
        if (isinstance(item, string_types)
                or isinstance(item, pm.Attribute)):
            try:
                pm.connectAttr(item, node + ".input2" + s, f=True)
            except(UnicodeEncodeError, RuntimeError):
                # Maya in Japanese have an issue with unicodeEndoce
                # UnicodeEncodeError is a workaround
                pm.connectAttr(item, node + ".input2", f=True)
                break
        else:
            pm.setAttr(node + ".input2" + s, item)

    if output:
        if not isinstance(output, list):
            output = [output]

        for item, s in zip(output, "XYZ"):
            pm.connectAttr(node + ".output" + s, item, f=True)

    return node


def createClampNode(input, in_min, in_max):
    """Create and connect a clamp node

    Arguments:
        input (attr, float or list): The input value to clamp
        in_min (float): The minimun value to clamp
        in_max (float): The maximun value to clamp

    Returns:
        pyNode: the newly created node.

    >>> clamp_node = nod.createClampNode(
        [self.roll_att, self.bank_att, self.bank_att],
        [0, -180, 0],
        [180,0,180])

    """
    node = pm.createNode("clamp")

    if not isinstance(input, list):
        input = [input]
    if not isinstance(in_min, list):
        in_min = [in_min]
    if not isinstance(in_max, list):
        in_max = [in_max]

    for in_item, min_item, max_item, s in zip(input, in_min, in_max, "RGB"):

        if (isinstance(in_item, string_types)
                or isinstance(in_item, pm.Attribute)):
            pm.connectAttr(in_item, node + ".input" + s)
        else:
            pm.setAttr(node + ".input" + s, in_item)

        if (isinstance(min_item, string_types)
                or isinstance(min_item, pm.Attribute)):
            pm.connectAttr(min_item, node + ".min" + s)
        else:
            pm.setAttr(node + ".min" + s, min_item)

        if (isinstance(max_item, string_types)
                or isinstance(max_item, pm.Attribute)):
            pm.connectAttr(max_item, node + ".max" + s)
        else:
            pm.setAttr(node + ".max" + s, max_item)

    return node


def createPlusMinusAverage1D(input, operation=1, output=None):
    """Create a multiple average node 1D.
    Arguments:
        input (attr, float or list): The input values.
        operation (int): Node operation. 0=None, 1=sum, 2=subtract,
            3=average
        output (attr): The attribute to connect the result.

    Returns:
        pyNode: the newly created node.

    """
    if not isinstance(input, list):
        input = [input]

    node = pm.createNode("plusMinusAverage")
    node.attr("operation").set(operation)

    for i, x in enumerate(input):
        try:
            pm.connectAttr(x, node + ".input1D[%s]" % str(i))
        except RuntimeError:
            pm.setAttr(node + ".input1D[%s]" % str(i), x)

    if output:
        pm.connectAttr(node + ".output1D", output)

    return node


def createVertexPositionNode(inShape,
                             vId=0,
                             output=None,
                             name="mgear_vertexPosition"):
    """Creates a mgear_vertexPosition node"""
    node = pm.createNode("mgear_vertexPosition", n=name)
    inShape.worldMesh.connect(node.inputShape)
    node.vertex.set(vId)
    if output:
        pm.connectAttr(output.parentInverseMatrix,
                       node.drivenParentInverseMatrix)
        pm.connectAttr(node.output, output.translate)

    return node


#############################################
# CREATE MULTI NODES
#############################################

def createNegateNodeMulti(name, inputs=[]):
    """Create and connect multiple negate nodes

    Arguments:
        name (str): The name for the new node.
        inputs (list of attr): The list of attributes to negate

    Returns:
        list: The output attributes list.

    """
    s = "XYZ"
    count = 0
    i = 0
    outputs = []
    for input in inputs:
        if count == 0:
            real_name = name + "_" + str(i)
            node_name = pm.createNode("multiplyDivide", n=real_name)
            i += 1

        pm.connectAttr(input, node_name + ".input1" + s[count], f=True)
        pm.setAttr(node_name + ".input2" + s[count], -1)

        outputs.append(node_name + ".output" + s[count])
        count = (count + 1) % 3

    return outputs


def createAddNodeMulti(inputs=[]):
    """Create and connect multiple add nodes

    Arguments:
        inputs (list of attr): The list of attributes to add

    Returns:
        list: The output attributes list.

    >>> angle_outputs = nod.createAddNodeMulti(self.angles_att)

    """
    outputs = [inputs[0]]

    for i, input in enumerate(inputs[1:]):
        node_name = pm.createNode("addDoubleLinear")

        if (isinstance(outputs[-1], string_types)
                or isinstance(outputs[-1], pm.Attribute)):
            pm.connectAttr(outputs[-1], node_name + ".input1", f=True)
        else:
            pm.setAttr(node_name + ".input1", outputs[-1])

        if (isinstance(input, string_types)
                or isinstance(input, pm.Attribute)):
            pm.connectAttr(input, node_name + ".input2", f=True)
        else:
            pm.setAttr(node_name + ".input2", input)

        outputs.append(node_name + ".output")

    return outputs


def createMulNodeMulti(name, inputs=[]):
    """Create and connect multiple multiply nodes

    Arguments:
        name (str): The name for the new node.
        inputs (list of attr): The list of attributes to multiply

    Returns:
        list: The output attributes list.

    """
    outputs = [inputs[0]]

    for i, input in enumerate(inputs[1:]):
        real_name = name + "_" + str(i)
        node_name = pm.createNode("multiplyDivide", n=real_name)
        pm.setAttr(node_name + ".operation", 1)

        if (isinstance(outputs[-1], string_types)
                or isinstance(outputs[-1], pm.Attribute)):
            pm.connectAttr(outputs[-1], node_name + ".input1X", f=True)
        else:
            pm.setAttr(node_name + ".input1X", outputs[-1])

        if (isinstance(input, string_types)
                or isinstance(input, pm.Attribute)):
            pm.connectAttr(input, node_name + ".input2X", f=True)
        else:
            pm.setAttr(node_name + ".input2X", input)

        outputs.append(node_name + ".output")

    return outputs


def createDivNodeMulti(name, inputs1=[], inputs2=[]):
    """Create and connect multiple divide nodes

    Arguments:
        name (str): The name for the new node.
        inputs1 (list of attr): The list of attributes
        inputs2 (list of attr): The list of attributes

    Returns:
        list: The output attributes list.

    """
    for i, input in enumerate(pm.inputs[1:]):
        real_name = name + "_" + str(i)
        node_name = pm.createNode("multiplyDivide", n=real_name)
        pm.setAttr(node_name + ".operation", 2)

        if (isinstance(pm.outputs[-1], string_types)
                or isinstance(pm.outputs[-1], pm.Attribute)):
            pm.connectAttr(pm.outputs[-1], node_name + ".input1X", f=True)
        else:
            pm.setAttr(node_name + ".input1X", pm.outputs[-1])

        if (isinstance(input, string_types)
                or isinstance(input, pm.Attribute)):
            pm.connectAttr(input, node_name + ".input2X", f=True)
        else:
            pm.setAttr(node_name + ".input2X", input)

        pm.outputs.append(node_name + ".output")

    return pm.outputs


def createClampNodeMulti(name, inputs=[], in_min=[], in_max=[]):
    """Create and connect multiple clamp nodes

    Arguments:
        name (str): The name for the new node.
        inputs (list of attr): The list of attributes
        in_min (list of attr): The list of attributes
        in_max (list of attr): The list of attributes

    Returns:
        list: The output attributes list.

    """
    s = "RGB"
    count = 0
    i = 0
    outputs = []
    for input, min, max in zip(inputs, in_min, in_max):
        if count == 0:
            real_name = name + "_" + str(i)
            node_name = pm.createNode("clamp", n=real_name)
            i += 1

        pm.connectAttr(input, node_name + ".input" + s[count], f=True)

        if (isinstance(min, string_types)
                or isinstance(min, pm.Attribute)):
            pm.connectAttr(min, node_name + ".min" + s[count], f=True)
        else:
            pm.setAttr(node_name + ".min" + s[count], min)

        if (isinstance(max, string_types)
                or isinstance(max, pm.Attribute)):
            pm.connectAttr(max, node_name + ".max" + s[count], f=True)
        else:
            pm.setAttr(node_name + ".max" + s[count], max)

        outputs.append(node_name + ".output" + s[count])
        count = (count + 1) % 3

    return outputs


#############################################
# Ctl tag node
#############################################


def add_controller_tag(ctl, tagParent=None):
    """Add a controller tag

    Args:
        ctl (dagNode): Controller to add the tar
        tagParent (dagNode): tag parent for the connection
    """
    if versions.current() >= 201650:
        pm.controller(ctl)
        ctt = pm.PyNode(pm.controller(ctl, q=True)[0])
        if tagParent:
            controller_tag_connect(ctt, tagParent)

        return ctt


def controller_tag_connect(ctt, tagParent):
    """Summary

    Args:
        ctt (TYPE): Teh control tag
        tagParent (TYPE): The object with the parent control tag
    """
    if pm.controller(tagParent, q=True):
        tpTagNode = pm.PyNode(pm.controller(tagParent, q=True)[0])
        tpTagNode.cycleWalkSibling.set(True)
        pm.connectAttr(tpTagNode.prepopulate, ctt.prepopulate, f=True)

        ni = aboutAttribute.get_next_available_index(tpTagNode.children)
        pm.disconnectAttr(ctt.parent)
        pm.connectAttr(ctt.parent, tpTagNode.attr(
            "children[%s]" % str(ni)))


class myNode(type):

    def __repr__(self):
        return 'asNode'


class asNode(object):
    _mayaVer = int(str(mc.about(v = True))[0:4])
    _cNum = -1
    _cType = ''
    _uvNums = 0
    _attrSup = None
    __metaclass__ = myNode

    def __new__(cls, *args, **kwargs):
        asN = super(asNode, cls).__new__(cls)
        return asN

    def __repr__(self):
        frame = inspect.currentframe()
        dictN = dict(list(frame.f_globals.items()) + list(frame.f_locals.items()))
        fGlobals = frame.f_globals
        for k, v in dictN.items():
            if isinstance(v, self.__class__):
                if hash(self) == hash(v):
                    if self._cNum >= 0 or self._uvNums:
                        fGlobals[k] = asNode(self.name)
                    else:
                        fGlobals[k] = self.asObj()
                    break
        return self.name

    def __str__(self):
        frame = inspect.currentframe()
        dictN = dict(list(frame.f_globals.items()) + list(frame.f_locals.items()))
        fGlobals = frame.f_globals
        for k, v in dictN.items():
            if isinstance(v, self.__class__):
                if hash(self) == hash(v):
                    if self._cNum >= 0 or self._uvNums:
                        fGlobals[k] = asNode(self.name)
                    else:
                        fGlobals[k] = self.asObj
                    break
        return self.name

    def __call__(self, getInfo=False, *args, **kwargs):
        pass
    #     if getInfo:
    #         argList = [arg for arg in dir(self) if not arg.startswith('_')]
    #         uArgList = [arg for arg in dir(str) if not arg.startswith('_')]
    #         for arg in uArgList:
    #             argList.remove(arg)
    #
    #         for item in argList:
    #             try:
    #                 exec('print item; print inspect.getargspec(self.' + item + ');')
    #             except:
    #                 pass
    #
    #             exec('print self.' + item + '.__doc__')
    #             print('\n')
    #
    #         print('Total Methods (Rigging Pipeline): ', len(argList) + len(uArgList))
    #         numParents = self._MDagPath().length() - 1
            # numSibs = self.selectSiblings()[(-1)] - 1
            # numChd = self.numChildren()
            # self.select()
            # return [self.name(), numParents, numSibs, numChd]

    def __init__(self, obj, attrSup=0):
        """

        @param obj:
        @param attrSup:
        """
        self._attrSup = attrSup
        __mayaVer = int(str(mc.about(v=True))[0:4])
        # if not pm.objExists(str(obj)):
        #     self._confirmAction('Maya node "%s" is not exists.'%str(obj))
        if '.' in str(obj):
            # 点
            if '.vtx[' in str(obj):
                self._cType = 'vtx'
            # 边
            elif '.e[' in str(obj):
                self._cType = 'e'
            # uv
            elif re.match('^.*\\.cv\\[(?P<uVal>\\d+)\\]\\[(?P<vVal>\\d+)\\]$', str(obj)):
                self._cType = 'uv'
            # cv点
            elif re.match('^.*\\.cv\\[(?P<uVal>\\d+)\\]$', str(obj)):
                self._cType = 'cv'
            # 面
            elif '.f[' in str(obj):
                self._cType = 'f'
            # 点的index序号
            if re.match('^.*\\.(cv|vtx|f|e)\\[(?P<uVal>\\d+)\\]$', str(obj)):
                reObj = re.search('(?<=\\[)(?P<vtxNum>[\\d]+)(?=\\])', str(obj))
                self._cNum = int(reObj.group())
            # u的值和v的值
            elif re.match('^.*\\.cv\\[(?P<uVal>\\d+)\\]\\[(?P<vVal>\\d+)\\]$', str(obj)):
                reObj = re.match('^.*\\.cv\\[(?P<uVal>\\d+)\\]\\[(?P<vVal>\\d+)\\]$', str(obj))
                self._uvNums = [int(reObj.group('uVal')), int(reObj.group('vVal'))]
            else:
                pass

            objName = str(obj).split('.')[0]
            activeList = om.MSelectionList()
            activeList.add(objName)
            pathDg = om.MDagPath()
            activeList.getDagPath(0, pathDg)

            compIt = None
            # 指定的api迭代器类型
            if self._cType == 'vtx':
                compIt = om.MItMeshVertex(pathDg)
            elif self._cType == 'e':
                compIt = om.MItMeshEdge(pathDg)
            elif self._cType == 'f':
                compIt = om.MItMeshPolygon(pathDg)
            elif self._cType == 'cv':
                compIt = om.MItCurveCV(pathDg)
            elif self._cType == 'uv':
                compIt = om.MItSurfaceCV(pathDg)
            if self._cType != 'uv':
                if compIt:
                    while not compIt.isDone():
                        if compIt.index() == self._cNum:
                            cName = compIt.currentItem()
                            break
                        compIt.next()
            else:
                if compIt:
                    while not compIt.isDone():
                        while not compIt.isRowDone():
                            utilU = om.MScriptUtil()
                            utilU.createFromInt(0)
                            uInt = utilU.asIntPtr()
                            utilV = om.MScriptUtil()
                            utilV.createFromInt(0)
                            vInt = utilV.asIntPtr()
                            compIt.getIndex(uInt, vInt)
                            uvList = [
                                om.MScriptUtil.getInt(uInt),
                                om.MScriptUtil.getInt(vInt)
                            ]
                            if uvList == self._uvNums:
                                cName = compIt.currentItem()
                                break
                            compIt.next()
                        if uvList == self._uvNums:
                            break
                        compIt.nextRow()

        self.obj = str(obj)
        self.obj = self._MDagPath()
        self.setCtrlColor = self.applyCtrlColor

    def _MObject(self):
        """

        @return:
        """
        dgPath = self._MDagPath()
        if self._cNum >= 0:
            dgPath.pop()
        return dgPath.node()

    def _MFnDagNode(self,
                    mObj=None,
                    toShapeNode=False):
        """

        @param mObj:
        @param toShapeNode:
        @return:
        """
        dgPath = self._MDagPath(mObj)
        if not toShapeNode:
            if self._cNum >= 0 or self._cType == 'uv':
                dgPath.pop()
        return om.MFnDagNode(dgPath)

    def _MBoundingBox(self):
        """

        @return:
        """
        mBB = self._MFnDagNode()
        return mBB.boundingBox()

    def _MDagPath(self, mObj=None):
        """

        @param mObj:
        @return: Instance of Maya API node : MDagPath
        """
        activeList = om.MSelectionList()
        pathDg = om.MDagPath()
        if mObj:
            pathDg.getAPathTo(mObj, pathDg)
        else:
            activeList.add(self.obj)
            activeList.getDagPath(0, pathDg)
        return pathDg

    def _MfnDependencyNode(self, mObj=None):
        """

        @param mObj:
        @return:
        """
        depFn = om.MFnDependencyNode()
        if mObj:
            depFn.setObject(mObj)
            return depFn
        else:
            dgPath = self._MDagPath()
            if self._cNum >= 0:
                dgPath.pop()
            depFn.setObject(dgPath.node())
            return depFn

    def _MFnMesh(self):
        return om.MFnMesh(self._MDagPath())

    def _nextVar(self, givenName,
                 fromEnd=True,
                 skipCount=0,
                 versionUpAll=False):
        """

        @param givenName:
        @param fromEnd:
        @param skipCount:
        @param versionUpAll:
        @return:
        """
        asN = givenName
        if not versionUpAll:
            numList = re.findall(r'\d+', asN)
            numRange = range(len(numList))
            if fromEnd:
                numStr = numList[(-1 * (skipCount + 1))]
                lenStr = len(numStr)
                nextNum = int(numStr) + 1
                nextNumStr = ('%0.' + str(lenStr) + 'd') % nextNum
                patternStr = r'[^\d+]*'
                for num in numRange:
                    patternStr += r'(\d+)'
                    patternStr += r'[^\d+]*'

                reObj = re.search(
                    patternStr, self.shortName
                )
                spanRange = reObj.span(
                    len(numList) - 1 * skipCount
                )
                nextName = asN[0:spanRange[0]] + nextNumStr + asN[spanRange[1]:]
                if mc.objExists(nextName):
                    nextName = asNode(nextName)
                return [nextName, nextNum]

            numStr = numList[skipCount]
            lenStr = len(numStr)
            nextNum = int(numStr) + 1
            nextNumStr = ('%0.' + str(lenStr) + 'd') % nextNum
            patternStr = r'[^\d+]*'
            for num in numRange:
                patternStr += r'(\d+)'
                patternStr += r'[^\d+]*'

            reObj = re.search(patternStr, self.shortName)
            spanRange = reObj.span(skipCount + 1)
            nextName = asN[0:spanRange[0]] + nextNumStr + asN[spanRange[1]:]
            if mc.objExists(nextName):
                nextName = asNode(nextName)
            return [
                nextName, nextNum]
        else:
            def repMGrp(mObj):
                numVal = int(mObj.group())
                formNum = len(mObj.group())
                formVar = '%0.' + str(formNum) + 'd'
                return str(formVar % (numVal + 1))
            nextName = re.sub('\\d+', repMGrp, self.shortName())
            if mc.objExists(nextName):
                return asNode(nextName)
            return nextName

    def _getFilePath(self, fileName=None):
        """

        :param fileName:
        :return:
        """
        if not fileName:
            scnName = mc.file(q=True, sn=True)
        else:
            scnName = fileName
        if scnName:
            filePath, fileNameFull = scnName.rsplit('/', 1)
            fileName, fileExtn = fileNameFull.rsplit('.')
            return [
                filePath, fileName, fileExtn
            ]
        else:
            return

    def parent(self, numParent=1, allParents=False,
               nType=None, prntImplied=True):
        """

        @param numParent:
        @param allParents:
        @param nType:
        @param prntImplied:
        @return:
        """
        if prntImplied:
            if allParents and numParent > 1:
                a = 1
                pCount = True
                prntList = []
                while pCount:
                    try:
                        if not prntList:
                            asParent = self.parent()
                        else:
                            asParent = prntList[-1].parent()
                        if asParent:
                            if nType:
                                if asParent.nodeType() == nType:
                                    prntList.append(asParent)
                                else:
                                    numParent += 1
                            else:
                                prntList.append(asParent)
                    except:
                        pCount = False
                    if numParent:
                        if a >= numParent:
                            break
                    a += 1
                if prntList:
                    return prntList

        if not allParents:
            dgPath = self._MDagPath()
            dgPath.pop(numParent)
            if self._cNum >= 0:
                dgPath.pop()
            dgNodeFn = om.MFnDagNode()
            dgNodeFn.setObject(dgPath)
            parentName = dgNodeFn.partialPathName()
            if mc.objExists(parentName):
                return asNode(parentName)
            return
        else:
            a = 1
            pCount = True
            prntList = []
            while pCount:
                try:
                    asParent = self.parent(a)
                    if asParent:
                        if nType:
                            if asParent.nodeType() == nType:
                                prntList.append(asParent)
                            else:
                                numParent += 1
                        else:
                            prntList.append(asParent)
                except:
                    pCount = False

                if numParent:
                    if a >= numParent:
                        break
                a += 1

            if prntList:
                return prntList
            return


    def getParent(self,numParent=1, allParents=False,
               nType=None, prntImplied=True):
        """

        @param numParent:
        @param allParents:
        @param nType:
        @param prntImplied:
        @return:
        """
        return self.parent(numParent=1, allParents=False,
               nType=None, prntImplied=True)

    def child(self, indexNum=0):
        """

        @param indexNum:
        @param childImplied:
        @return:
        """
        numChildren = self.numChildren()
        if indexNum >= numChildren:
            return
        else:
            dgPath = self._MDagPath()
            chdObj = dgPath.child(indexNum)
            if chdObj:
                dagNodeFn = self._MFnDagNode(chdObj)
                chdName = dagNodeFn.partialPathName()
                return asNode(chdName)
            return

    def getChildren(self, type=None,
                    childImplied=True,
                    **kwargs):
        """

        @param type:
        @param kwargs:
        @return:
        """
        allChildren = mc.listRelatives(
            self.name, c=1, pa=1, **kwargs
        )
        if childImplied:
            impliedChild = self.child(0)
            if impliedChild:
                if not allChildren:
                    allChildren = []
                if str(impliedChild) not in allChildren:
                    allChildren.append(impliedChild)
        asChildren = []
        if allChildren:
            for child in allChildren:
                try:
                    asChildren.append(asNode(child))
                except:
                    asChildren.append(child)
        else:
            return

        if not type:
            return asChildren
        else:
            typeChildren = []
            if type == 'constrain' or type == 'constraint':
                conList = [conType + 'Constraint' for conType in
                           ['point', 'orient', 'parent', 'scale', 'aim', 'geometry', 'normal', 'tangent']]
                for child in asChildren:
                    if str(mc.nodeType(child)) in conList:
                        typeChildren.append(child)

            else:
                for child in asChildren:
                    if mc.nodeType(child) == type:
                        typeChildren.append(child)

            return typeChildren


    def numChildren(self, type=None, **kwargs):
        """

        @param type:
        @param kwargs:
        @return:
        """
        allChildren = mc.listRelatives(self.name(),
                                       c = True,
                                       **kwargs)
        if not allChildren:
            return 0
        if not type:
            if allChildren: return len(allChildren)
            else: return 0
        else:
            typeChildren = []
            for child in allChildren:
                if mc.nodeType(child) == type:
                    typeChildren.append(child)
            if typeChildren:
                return len(typeChildren)
            return 0

    def extractNum(self,
                   fromEnd=True,
                   skipCount=0):
        """

        @param fromEnd:
        @param skipCount:
        @return:
        """
        numList = re.findall(r'\d+', self.shortName)
        if numList:
            if fromEnd:
                numStr = numList[(-1 * (skipCount + 1))]
                num = int(numStr)
                return [
                    num, numStr
                ]
            else:
                numStr = numList[skipCount]
                num = int(numStr)
                return [
                    num, numStr
                ]
        else:
            return

    def numChildren(self, type=None, **kwargs):
        """

        @param type:
        @param kwargs:
        @return:
        """
        allChildren = mc.listRelatives(self.name,
                                       c=True, **kwargs)
        if not allChildren:
            return 0
        if not type:
            if allChildren:
                return len(allChildren)
            else:
                return 0
        else:
            typeChildren = []
            for child in allChildren:
                if mc.nodeType(child) == type:
                    typeChildren.append(child)
            if typeChildren:
                return len(typeChildren)
            return 0

    def _confirmAction(self, action, raiseErr=False):
        """

        @param action:
        @param raiseErr:
        @return:
        """
        if raiseErr:
            mc.confirmDialog(title="Warning..", bgc=(0.6,0.8,1.0),
                             message=action, button=['Yes'],
                             defaultButton='Yes')
            raise RuntimeError(action)
        confirm = mc.confirmDialog(title="Confirm Action", message=action,
                                   button=['Yes', 'No'], defaultButton='Yes',
                                   cancelButton='No', dismissString='No'
                                   )
        if confirm == 'Yes':
            return True
        else:
            return False

    def applyCtrlColor(self, colorNum):
        """

        @param colorNum:
        @return:
        """
        self.setAttr()

    def setAttr(self, attr, *args, **kwargs):
        """

        @param attr:
        @param args:
        @param kwargs:
        @return:
        """
        attrList = [attr] if type(attr) != list else attr
        for attr in attrList:
            attr = str('')

    def getShape(self, multiShapes=False):
        """

        @param multiShapes:
        @return:
        """
        try:
            if not multiShapes:
                if self._cNum >= 0:
                    return asNode(mc.listRelatives(self._fullName.split('.', 1)[0],
                                                   shapes=1, f=1)[0])
                else:
                    return asNode(mc.listRelatives(self._fullName,
                                                   shapes=1, f=1)[0])
            else:
                if self._cNum >= 0:
                    return map(asNode, mc.listRelatives(
                        self._fullName.split('.', 1)[0],
                        shapes=1, f=1))
                else:
                    return map(asNode, mc.listRelatives(self._fullName,
                                                        shapes=1, f=1))
        except:
            return

    def listHistory(self, **kwargs):
        """

        @param kwargs:
        @return:
        """
        self.select()
        histNodes = []
        try:
            histNodes = mc.listHistory(**kwargs)
        except:
            if kwargs:
                if 'type' in kwargs.keys():
                    nodeList = mc.listHistory()
                    if nodeList:
                        for node in nodeList:
                            if kwargs['type'] == 'constraint':
                                try:
                                    node = asNode(node)
                                except:
                                    continue
                                if mc.nodeType(node) == 'pointConstraint'\
                                        or mc.nodeType(node) == 'orientConstraint'\
                                        or mc.nodeType(node) == 'parentConstraint'\
                                        or mc.nodeType(node) == 'scaleConstraint'\
                                        or mc.nodeType(node) == 'aimConstraint'\
                                        or mc.nodeType(node) == 'tangentConstraint'\
                                        or mc.nodeType(node) == 'normalConstraint'\
                                        or mc.nodeType(node) == 'geometryConstraint'\
                                        or mc.nodeType(node) == 'poleVectorConstraint':
                                    if self.isParentOf(node):
                                        histNodes.append(node)
                            elif 'Constraint' in kwargs['type'] \
                                and mc.nodeType(node) == kwargs['type']:
                                try:
                                    node = asNode(node)
                                except:
                                    continue
                                if self.isParentOf(node):
                                    histNodes.append(node)
                            elif mc.nodeType(node) == kwargs['type']:
                                histNodes.append(node)
            else:
                return

        if histNodes:
            return histNodes
        else:
            return

    def isParentOf(self, targetObj, prntImplied=True):
        """

        @param targetObj:
        @param prntImplied:
        @return:
        """
        asTarget = asNode(targetObj)
        nodeDg = self._MFnDagNode()
        mObj = asTarget._MObject()
        return nodeDg.isParentOf(mObj)

    def attributeQuery(self, *args, **kwargs):
        """

        @param args:
        @param kwargs:
        @return:
        """
        if 'n' not in kwargs:
            if 'node' not in kwargs:
                kwargs['node'] = self.name
        return mc.attributeQuery(*args, **kwargs)

    def select(self, *args, **kwargs):
        """

        @param args:
        @param kwargs:
        @return:
        """
        if not kwargs:
            kwargs = {'r': 1}
        try:
            mc.select(self.name, *args, **kwargs)
        except TypeError as msg:
            if args == ([],):
                for modeFlag in ('add', 'af', 'addFirst',
                                 'd', 'deselect', 'tgl', 'toggle'):
                    if kwargs.get(modeFlag, False):
                        return
                mc.select(cl=True)
            else:
                raise TypeError(msg)

    def selectHI(self, objType='jnt',
                 topSelect=True,
                 includeShapes=False,
                 childImplied=1):
        """

        @param objType:
        @param topSelect:
        @param includeShapes:
        @param childImplied:
        @return:
        """
        if objType == 'jnt' or objType == 'joint' or objType == '^jnt' or objType == '^joint':
            nType = 'joint'
        else:
            if objType == 'crv' or objType == 'curv' or objType == 'nurbsCurve' or objType == '^crv' or objType == '^curv' or objType == '^nurbsCurve':
                nType = 'nurbsCurve'
            elif objType == 'mesh' or objType == 'obj' or objType == '^mesh' or objType == '^obj':
                nType = 'mesh'
            else:
                nType = objType
            self.select(r=1)
            mc.select(hi=True)


    def nodeType(self, transformCheck=False):
        """

        @param transformCheck:
        @return:
        """
        if not transformCheck:
            if self.hasShape:
                return mc.nodeType(self.getShape())
            else:
                return mc.nodeType(self.name)
        else:
            return mc.listRelatives(self.name)

    def listRelatives(self, *args, **kwargs):
        """

        @param args:
        @param kwargs:
        @return:
        """
        if kwargs:
            if 'fullPath' not in kwargs or 'f' not in kwargs:
                kwargs['fullPath'] = 1
        else:
            kwargs['fullPath'] = 1
        relativeList = mc.listRelatives(self.name, *args, **kwargs)
        if relativeList:
            return [asNode(obj) for obj in relativeList]
        else:
            return

    def attr(self, attrList):
        """

        @param attrList:
        @return:
        """
        attrList = [attrList] if type(attrList) != list else attrList
        attributeList = []

        for attrName in attrList:
            if mc.objExists('%s.%s'%(self.name, str(attrName))):
                attrList.append('%s.%s'%(self.name, str(attrName)))
            else:
                self._confirmAction(
                    'Attrbute "{}" not exists.'.
                        format(self.name + '.' + str(attrName))
                )
        if attributeList:
            if len(attributeList) > 1:
                return attributeList
            else:
                return attributeList[0]
        else:
            return

    def hssAttrLocked(self, attr):
        """

        @param attr:
        @return:
        """
        attrType = mc.attributeQuery(attr, n=self.name, at=1)
        if attrType == 'double3':
            boolType = False
            subAttrs = mc.attributeQuery(
                attr, n=self.name, listChildren=1
            )
            # if subAttrs:
            #     for subAttr in subAttrs:
            #         if mc.getAttr()

    def getVtxList(self, get_asNode=True):
        """

        @param get_asNode:
        @return:
        """
        if self.isNodeType('nurbsCurve'):
            shapeList = self.getShape(1)
            if len(shapeList) == 1:
                curvFn = om.MFnNurbsCurve(self._MDagPath())
                numCVs = curvFn.numCVs()
                if curvFn.form() == 3:
                    numCVs = numCVs - curvFn.degree()
                cvList = [
                    asNode('%s.cv[%d]'%(self.name, num) for num in range(numCVs))
                ]
                mc.select(cvList, r=True)
                return [
                    cvList, numCVs
                ]

            cv_List = []
            for shape in shapeList:
                curvFn = om.MFnNurbsCurve(shape._MDagPath())
                numCVs = curvFn.numCVs()
                if curvFn.form() == 3:
                    numCVs = numCVs - curvFn.degree()
                cvList = [
                    asNode('%s.cv[%d]'%(self.name, num) for num in range(numCVs))
                ]
                cv_List.extend(cvList)
            mc.select(cv_List, r=True)
            return [
                cv_List, len(cv_List)
            ]
        else:
            if self.isNodeType('mesh'):
                # polyIt = sel
                return
    def getPos(self, shapePos=False):
        """

        @param shapePos:
        @return:
        """
        if '.' not in self.name:
            if not shapePos:
                transFn = om.MFnTransform()
                pathDg = self._MDagPath()
                transFn.setObject(pathDg)
                point = om.MPoint()
                point = transFn.rotatePivot(om.MSpace.kWorld)
                objPos = [round(point.x, 5), round(point.y, 5), round(point.z, 5)]
                return objPos
            if self.isNodeType('nurbsCurve'):
                cvList,numCvs = self.getVtxList()


    @property
    def asObj(self):
        """

        @return:
        """
        if self._cNum >= 0:
            return asNode(self.name.split('.', 1)[0])
        else:
            return asNode(self.name)

    @property
    def name(self):
        """

        @return:
        """
        dgPath = self._MDagPath()
        shapes = self.getShape(True)
        if self._cNum >= 0 or self._cType == 'uv':
            if shapes and len(shapes) == 1:
                dgPath.pop()
        dgNodeFn = om.MFnDagNode()
        dgNodeFn.setObject(dgPath)
        nodeName = dgNodeFn.partialPathName()
        if self._cNum >= 0:
            return '%s.%s[%d]' % (nodeName, self._cType, self._cNum)
        else:
            if self._cType == 'uv':
                return '%s.cv[%d][%d]' % (nodeName, self._uvNums[0], self._uvNums[1])
            return nodeName

    @property
    def hasUniqueName(self):
        """

        :return:
        """
        depFn = self._MfnDependencyNode()
        return depFn.hasUniqueName()

    @property
    def _fullName(self):
        """

        @return:
        """
        dgPath = self._MDagPath()
        if self._cNum >= 0:
            dgPath.pop()
        dgNodeFn = om.MFnDagNode()
        dgNodeFn.setObject(dgPath)
        if self._cNum >= 0:
            return dgNodeFn.fullPathName() + '.' + self._cType + '[' + str(self._cNum) + ']'
        else:
            return dgNodeFn.fullPathName()

    @property
    def shortName(self):
        """

        @return:
        """
        depNodeFn = self._MfnDependencyNode()
        if self._cNum >= 0:
            dgPath = self._MDagPath()
            dgPath.pop()
            dgNodeFn = om.MFnDagNode()
            dgNodeFn.setObject(dgPath)
            parentName = dgNodeFn.partialPathName()
            return '%s.%s[%d]' % (parentName, self._cType, self._cNum)
        else:
            return depNodeFn.name()

    @property
    def longName(self):
        """

        @return:
        """
        dgNodeFn = self._MFnDagNode()
        if self._cNum >= 0:
            return '%s.%s[%d]'%(
                dgNodeFn.fullPathName(), self._cType, self._cNum
            )
        else:
            return dgNodeFn.fullPathName()

    @property
    def hasShape(self):
        """

        @return:
        """
        if self._cNum >= 0:
            shapes = mc.listRelatives(
                self.name.split('.', 1)[0],
                shapes = True
            )
        else:
            shapes = mc.listRelatives(
                self.name,
                shapes = True
            )
        if shapes:
            return True
        else:
            return False

    @property
    def isMesh(self):
        """

        @return:
        """
        shpNode = self.getShape()
        if shpNode:
            if shpNode.nodeType() == 'mesh':
                return True
            else:
                return False
        else:
            if self.nodeType() == 'mesh':
                return True
            else:
                return False

    @property
    def isSkinMesh(self):
        if not self.isMesh:
            return False
        skinClust = self.listHistory(type = 'skinCluster')
        if not skinClust:
            return False
        return True

    @property
    def isTrans(self):
        """

        :return:
        """
        if self.nodeType(True) == 'transform':
            return True
        else:
            return False

    @property
    def isShape(self):
        """

        :return:
        """
        dgPath = self._MDagPath()
        dgPath.pop()
        if self._cNum >= 0:
            dgPath.pop()
        dgNodeFn = om.MFnDagNode()
        dgNodeFn.setObject(dgPath)
        parentName = dgNodeFn.partialPathName()
        if mc.objExists(parentName):
            pNode = asNode(parentName)
        else:
            pNode = None
        if pNode and not self.hasShape:
            if pNode.isTrans:
                pass
        else:
            return False
        pShapes = pNode.listRelatives(shapes=1)

        if pShapes:
            pShapes = [str(shape) for shape in pShapes]
            if str(self.name) in pShapes or str(self._fullName) in pShapes:
                return True
        else:
            return False

    @property
    def isComponent(self):
        """

        :return:
        """
        if '.' in self.shortName:
            return True
        else:
            return False

    @property
    def isCurve(self):
        """

        :return:
        """
        if self.getShape():
            if self.getShape().nodeType() == 'nurbsCurve':
                return True
            else:
                return False
        else:
            if self.nodeType() == 'nurbsCurve':
                return True
            else:
                return False

    @property
    def isEdge(self):
        """

        :return:
        """
        if '.e[' in self.name:
            return True
        else:
            return False

    @property
    def isVertex(self):
        """

        :return:
        """
        if '.vtx[' in self.name:
            return True
        else:
            return False

    @property
    def isFace(self):
        if '.f[' in self.name:
            return True
        else:
            return False

    @property
    def isJoint(self):
        """

        :return:
        """
        if mc.nodeType(self.name) == 'joint':
            return True
        else:
            return False

    @property
    def isLoc(self):
        """

        :return:
        """
        if self.getShape():
            if self.getShape().nodeType() == 'locator':
                return True
            else:
                return False
        else:
            if self.nodeType() == 'locator':
                return True
            else:
                return False

    @property
    def isRightSide(self):
        """

        @return:
        """
        return

    def isNodeType(self, objType):
        """

        @return:
        """
        if self.getShape():
            if self.getShape().nodeType() == objType:
                return True
            else:
                return False
        else:
            if self.nodeType():
                return True
            else:
                return False

    def isLastJoint(self, numFromEnd=0, childImplied=True):
        """

        @param numFromEnd:
        @param childImplied:
        @return:
        """
        jnt = self.asObj
        if mc.nodeType(jnt.name) == 'joint':
            pass
        else:
            self._confirmAction('"%s" is Not Joint..' % self.name, True)
        if numFromEnd:
            childList = jnt.getChildren()
            if not childList:
                return True









