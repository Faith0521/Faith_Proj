# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-31 16:22:25
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-31 16:22:34
import cmd
from imp import reload
from maya import cmds as mc
from pymel import core as pm
from pymel.core import datatypes
from Faith.maya_utils import transform_utils as transform
reload(transform)

def spineStretchSoftCmd(bridge, crv, prefix, count):
    
    if not pm.objExists(bridge):
        return False

    crv_info = pm.shadingNode("curveInfo", asUtility=True, name=crv + "_crvInfo")
    crv.worldSpace[0] >> crv_info.inputCurve

    # soft val
    soft_val_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_soft_val_condition")
    soft_val_condition.operation.set(0)
    bridge.softness >> soft_val_condition.firstTerm
    soft_val_condition.colorIfTrueR.set(0.001)
    bridge.softness >> soft_val_condition.colorIfFalseR

    # stretch ==================================================================================
    sl_stretch_mult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sl_stretch_mult")
    bridge.slave_length >> sl_stretch_mult.input1
    bridge.maxstretch >> sl_stretch_mult.input2

    activeLengthMinus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_activeLengthMinus")
    activeLengthMinus.operation.set(2)
    crv_info.arcLength >> activeLengthMinus.input1D[0]
    bridge.master_length >> activeLengthMinus.input1D[1]
    
    stretch = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_stretch")
    stretch.operation.set(2)
    activeLengthMinus.output1D >> stretch.input1X
    sl_stretch_mult.output >> stretch.input2X

    neg_stretch = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_neg_stretch")
    neg_stretch.input1.set(-1)
    stretch.outputX >> neg_stretch.input2

    stretch_soft_div = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_stretch_soft_div")
    stretch_soft_div.operation.set(2)
    neg_stretch.output >> stretch_soft_div.input1X
    soft_val_condition.outColorR >> stretch_soft_div.input2X

    stretch_soft_pow = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_stretch_soft_pow")
    stretch_soft_pow.operation.set(3)
    stretch_soft_pow.input1X.set(2.718)
    stretch_soft_div.outputX >> stretch_soft_pow.input2X

    expo_minus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_expo_minus")
    expo_minus.operation.set(2)
    expo_minus.input1D[0].set(1)
    stretch_soft_pow.outputX >> expo_minus.input1D[1]

    stretch_expo_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_stretch_expo_condition")
    stretch_expo_condition.operation.set(0)
    soft_val_condition.outColorR >> stretch_expo_condition.firstTerm
    expo_minus.output1D >> stretch_expo_condition.colorIfFalseR
    stretch_expo_condition.colorIfTrueR.set(1.0)

    stretch_val = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_stretch_val")
    stretch_val.operation.set(2)
    bridge.maxstretch >> stretch_val.input1D[0]
    stretch_val.input1D[1].set(1)

    sl_stretch_mult_a = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sl_stretch_mult_a")
    bridge.slave_length >> sl_stretch_mult_a.input1
    stretch_val.output1D >> sl_stretch_mult_a.input2

    sl_val_after = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sl_val_after")
    sl_stretch_mult_a.output >> sl_val_after.input1
    stretch_expo_condition.outColorR >> sl_val_after.input2

    st_ext_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_st_ext_condition")
    st_ext_condition.operation.set(4)
    sl_val_after.output >> st_ext_condition.firstTerm
    activeLengthMinus.output1D >> st_ext_condition.secondTerm
    sl_val_after.output >> st_ext_condition.colorIfTrueR
    activeLengthMinus.output1D >> st_ext_condition.colorIfFalseR

    in_sl_stretch = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_in_sl_stretch")
    st_ext_condition.outColorR >> in_sl_stretch.input1D[0]
    bridge.slave_length >> in_sl_stretch.input1D[1]

    # squash ==================================================================================
    negtiveLengthMinus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_negtiveLengthMinus")
    negtiveLengthMinus.operation.set(2)
    bridge.master_length >> negtiveLengthMinus.input1D[0]
    crv_info.arcLength >> negtiveLengthMinus.input1D[1]

    sl_squash_mult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sl_squash_mult")
    bridge.slave_length >> sl_squash_mult.input1
    bridge.maxsquash >> sl_squash_mult.input2
    
    squash = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_squash")
    squash.operation.set(2)
    negtiveLengthMinus.output1D >> squash.input1X
    sl_squash_mult.output >> squash.input2X

    neg_squash = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_neg_squash")
    neg_squash.input1.set(-1)
    squash.outputX >> neg_squash.input2

    squash_soft_div = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_squash_soft_div")
    squash_soft_div.operation.set(2)
    neg_squash.output >> squash_soft_div.input1X
    soft_val_condition.outColorR >> squash_soft_div.input2X

    squash_soft_pow = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_squash_soft_pow")
    squash_soft_pow.operation.set(3)
    squash_soft_pow.input1X.set(2.718)
    squash_soft_div.outputX >> squash_soft_pow.input2X

    expo_minus1 = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_expo_minus1")
    expo_minus1.operation.set(2)
    expo_minus1.input1D[0].set(1)
    squash_soft_pow.outputX >> expo_minus1.input1D[1]

    squash_expo_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_squash_expo_condition")
    squash_expo_condition.operation.set(0)
    squash_expo_condition.colorIfTrueR.set(1.0)
    bridge.softness >> squash_expo_condition.firstTerm
    expo_minus1.output1D >> squash_expo_condition.colorIfFalseR

    squash_val = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_squash_val")
    squash_val.operation.set(2)
    squash_val.input1D[0].set(1)
    bridge.maxsquash >> squash_val.input1D[1]

    sl_squash_mult_a = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sl_squash_mult_a")
    bridge.slave_length >> sl_squash_mult_a.input1
    squash_val.output1D >> sl_squash_mult_a.input2

    squash_sl_val_after = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_squash_sl_val_after")
    squash_expo_condition.outColorR >> squash_sl_val_after.input1
    sl_squash_mult_a.output >> squash_sl_val_after.input2

    sq_ext_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_sq_ext_condition")
    sq_ext_condition.operation.set(4)
    squash_sl_val_after.output >> sq_ext_condition.firstTerm
    negtiveLengthMinus.output1D >> sq_ext_condition.secondTerm
    negtiveLengthMinus.output1D >> sq_ext_condition.colorIfFalseR
    squash_sl_val_after.output >> sq_ext_condition.colorIfTrueR

    in_sl_squash = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_in_sl_squash")
    in_sl_squash.operation.set(2)
    bridge.slave_length >> in_sl_squash.input1D[0]
    sq_ext_condition.outColorR >> in_sl_squash.input1D[1]

    #**************************************************************************************************
    in_sl_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_in_sl_condition")
    in_sl_condition.operation.set(3)
    crv_info.arcLength >> in_sl_condition.firstTerm
    bridge.master_length >> in_sl_condition.secondTerm
    in_sl_squash.output1D >> in_sl_condition.colorIfFalseR
    in_sl_stretch.output1D >> in_sl_condition.colorIfTrueR

    size = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_size")
    size.operation.set(2)
    in_sl_condition.outColorR >> size.input1X
    crv_info.arcLength >> size.input2X

    size_plus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_size_plus")
    size_plus.operation.set(2)
    size_plus.input1D[0].set(1)
    size.outputX >> size_plus.input1D[1]

    start = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_start")
    bridge.position >> start.input1
    size_plus.output1D >> start.input2

    end = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_end")
    start.output >> end.input1D[0]
    size.outputX >> end.input1D[1]

    start_end_length = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_start_end_length")
    start_end_length.operation.set(2)
    end.output1D >> start_end_length.input1D[0]
    start.output >> start_end_length.input1D[1]

    step = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_step")
    step.operation.set(2)
    start_end_length.output1D >> step.input1X
    step.input2X.set(int(count-1))

    pciList = []
    for i in range(count):
        step_mult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_step_mult" + str(i))
        step_mult.input1.set(i)
        step.outputX >> step_mult.input2

        perc = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_per" + str(i))
        start.output >> perc.input1D[0]
        step_mult.output >> perc.input1D[1]

        perc_clamp = pm.shadingNode("clamp", asUtility=True, name=prefix+"_perc_clamp" + str(i))
        perc_clamp.maxR.set(1)
        perc.output1D >> perc_clamp.inputR

        pci = pm.createNode("pointOnCurveInfo", name=prefix + "_pci" + str(i))
        crv.worldSpace[0] >> pci.inputCurve
        perc_clamp.outputR >> pci.parameter
        pci.turnOnPercentage.set(1)
        pciList.append(pci)
    
    return pciList

def spineVolumeCmd(bridge, prefix, outObj):
    # in st----------------------------------------------------------------------------------------
    driver_ctrl_minus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_dc_minus")
    driver_ctrl_minus.operation.set(2)
    bridge.driver >> driver_ctrl_minus.input1D[0]
    bridge.driver_ctr >> driver_ctrl_minus.input1D[1]

    driver_ctrl_max = pm.shadingNode("condition", asUtility=True, name=prefix+"_dc_max")
    driver_ctrl_minus.output1D >> driver_ctrl_max.firstTerm
    driver_ctrl_max.operation.set(2)
    driver_ctrl_max.colorIfFalseR.set(0)
    driver_ctrl_minus.output1D >> driver_ctrl_max.colorIfTrueR

    max_ctrl_minus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_mc_minus")
    max_ctrl_minus.operation.set(2)
    bridge.driver_max >> max_ctrl_minus.input1D[0]
    bridge.driver_ctr >> max_ctrl_minus.input1D[1]

    max_ctrl_max = pm.shadingNode("condition", asUtility=True, name=prefix+"_mc_max")
    max_ctrl_minus.output1D >> max_ctrl_max.firstTerm
    max_ctrl_max.operation.set(2)
    max_ctrl_max.secondTerm.set(0.001)
    max_ctrl_max.colorIfFalseR.set(0.001)
    max_ctrl_minus.output1D >> max_ctrl_max.colorIfTrueR

    ctrl_max_div = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_cm_div")
    ctrl_max_div.operation.set(2)
    driver_ctrl_max.outColorR >> ctrl_max_div.input1X
    max_ctrl_max.outColorR >> ctrl_max_div.input2X

    cm_clamp = pm.shadingNode("clamp", asUtility=True, name=prefix+"_cm_clamp")
    cm_clamp.maxR.set(1)
    ctrl_max_div.outputX >> cm_clamp.inputR

    in_st = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_in_st")
    bridge.stretch >> in_st.input1
    cm_clamp.outputR >> in_st.input2

    # in sq---------------------------------------------------------------------------------------------
    ctrl_driver_minus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_cd_minus")
    ctrl_driver_minus.operation.set(2)
    bridge.driver_ctr >> ctrl_driver_minus.input1D[0]
    bridge.driver >> ctrl_driver_minus.input1D[1]

    ctrl_driver_max = pm.shadingNode("condition", asUtility=True, name=prefix+"_cd_max")
    ctrl_driver_minus.output1D >> ctrl_driver_max.firstTerm
    ctrl_driver_max.operation.set(2)
    ctrl_driver_max.colorIfFalseR.set(0.001)
    ctrl_driver_minus.output1D >> ctrl_driver_max.colorIfTrueR

    ctrl_min_minus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_cm_minus")
    ctrl_min_minus.operation.set(2)
    bridge.driver_ctr >> ctrl_min_minus.input1D[0]
    bridge.driver_min >> ctrl_min_minus.input1D[1]

    min_ctrl_max = pm.shadingNode("condition", asUtility=True, name=prefix+"_mic_max")
    ctrl_min_minus.output1D >> min_ctrl_max.firstTerm
    min_ctrl_max.operation.set(2)
    min_ctrl_max.secondTerm.set(0.001)
    min_ctrl_max.colorIfFalseR.set(0.001)
    ctrl_min_minus.output1D >> min_ctrl_max.colorIfTrueR

    ctrl_min_div = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_cmi_div")
    ctrl_min_div.operation.set(2)
    ctrl_driver_max.outColorR >> ctrl_min_div.input1X
    min_ctrl_max.outColorR >> ctrl_min_div.input2X

    cmi_clamp = pm.shadingNode("clamp", asUtility=True, name=prefix+"_cmi_clamp")
    cmi_clamp.maxR.set(1)
    ctrl_min_div.outputX >> cmi_clamp.inputR

    in_sq = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_in_sq")
    cmi_clamp.outputR >> in_sq.input1
    bridge.squash >> in_sq.input2

    qt_plus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_sqst_plus")
    qt_plus.input1D[0].set(1)
    in_st.output >> qt_plus.input1D[1]
    in_sq.output >> qt_plus.input1D[2]

    scale_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_scale_condition")
    scale_condition.operation.set(2)
    qt_plus.output1D >> scale_condition.firstTerm
    qt_plus.output1D >> scale_condition.colorIfTrueR

    sxMult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sx_mult")
    bridge.global_scaleX >> sxMult.input1
    scale_condition.outColorR >> sxMult.input2

    syMult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sy_mult")
    bridge.global_scaleY >> syMult.input1
    scale_condition.outColorR >> syMult.input2

    szMult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_sz_mult")
    bridge.global_scaleZ >> szMult.input1
    scale_condition.outColorR >> szMult.input2

    x_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_x_condition")
    x_condition.operation.set(1)
    bridge.axis >> x_condition.firstTerm
    sxMult.output >> x_condition.colorIfTrueR
    bridge.global_scaleX >> x_condition.colorIfFalseR

    y_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_y_condition")
    y_condition.operation.set(1)
    y_condition.secondTerm.set(1)
    bridge.axis >> y_condition.firstTerm
    syMult.output >> y_condition.colorIfTrueR
    bridge.global_scaleY >> y_condition.colorIfFalseR

    z_condition = pm.shadingNode("condition", asUtility=True, name=prefix+"_z_condition")
    z_condition.operation.set(1)
    z_condition.secondTerm.set(2)
    bridge.axis >> z_condition.firstTerm
    szMult.output >> z_condition.colorIfTrueR
    bridge.global_scaleY >> z_condition.colorIfFalseR

    x_blendMult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_x_blendMult")
    x_condition.outColorR >> x_blendMult.input1
    bridge.blend >> x_blendMult.input2

    y_blendMult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_y_blendMult")
    y_condition.outColorR >> y_blendMult.input1
    bridge.blend >> y_blendMult.input2

    z_blendMult = pm.shadingNode("multDoubleLinear", asUtility=True, name=prefix+"_z_blendMult")
    z_condition.outColorR >> z_blendMult.input1
    bridge.blend >> z_blendMult.input2

    blend_minus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_blend_minus")
    blend_minus.operation.set(2)
    blend_minus.input1D[0].set(1)
    bridge.blend >> blend_minus.input1D[1]

    blendScl_mult = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_blendScl_mult")
    bridge.global_scaleX >> blendScl_mult.input1X
    bridge.global_scaleY >> blendScl_mult.input1Y
    bridge.global_scaleZ >> blendScl_mult.input1Z

    blend_minus.output1D >> blendScl_mult.input2X
    blend_minus.output1D >> blendScl_mult.input2Y
    blend_minus.output1D >> blendScl_mult.input2Z

    scale_plus = pm.shadingNode("plusMinusAverage", asUtility=True, name=prefix+"_scale_plus")
    x_blendMult.output >> scale_plus.input3D[0].input3Dx
    y_blendMult.output >> scale_plus.input3D[0].input3Dy
    z_blendMult.output >> scale_plus.input3D[0].input3Dz
    blendScl_mult.outputX >> scale_plus.input3D[1].input3Dx
    blendScl_mult.outputY >> scale_plus.input3D[1].input3Dy
    blendScl_mult.outputZ >> scale_plus.input3D[1].input3Dz

    global_div = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_global_div")
    global_div.operation.set(2)
    global_div.input1X.set(1)
    global_div.input1Y.set(1)
    global_div.input1Z.set(1)
    bridge.global_scaleX >> global_div.input1X
    bridge.global_scaleY >> global_div.input1Y
    bridge.global_scaleZ >> global_div.input1Z

    scale_out = pm.shadingNode("multiplyDivide", asUtility=True, name=prefix+"_scl_out")
    scale_plus.output3D >> scale_out.input1
    global_div.output >> scale_out.input2

    scale_out.output >> outObj.scale

    scaleValue = scale_out.output.get()
    return scaleValue

def add2DChain(parent, name, positions, normal, axis, negate=False, vis=True):

    transforms = transform.getChainTransform(positions, normal, axis, negate)
    t = transform.setMatrixPosition(transforms[-1], positions[-1])
    transforms.append(t)

    chain = []
    for i, t in enumerate(transforms):
        node = addJoint(parent, name % i, t, vis)
        chain.append(node)
        parent = node

    # moving rotation value to joint orient
    for i, jnt in enumerate(chain):
        if i == 0:
            jnt.setAttr("jointOrient", jnt.getAttr("rotate"))
            jnt.setAttr("rotate", 0, 0, 0)
        elif i == len(chain) - 1:
            jnt.setAttr("jointOrient", 0, 0, 0)
            jnt.setAttr("rotate", 0, 0, 0)
        else:
            # This will fail if chain is not always oriented the same
            # way (like X chain)
            v0 = positions[i] - positions[i - 1]
            v1 = positions[i + 1] - positions[i]
            angle = datatypes.degrees(v0.angle(v1))
            jnt.setAttr("rotate", 0, 0, 0)
            jnt.setAttr("jointOrient", 0, 0, angle)

        # check if we have to negate Z angle by comparing the guide
        # position and the resulting position.
        if i >= 1:
            # round the position values to 6 decimals precission
            # TODO: test with less precision and new check after apply
            # Ik solver
            if ([round(elem, 4) for elem in transform.getTranslation(jnt)]
                    != [round(elem, 4) for elem in positions[i]]):

                jp = jnt.getParent()

                # Aviod intermediate e.g. `transform3` groups that can appear
                # between joints due to basic moving around.
                while jp.type() == "transform":
                    jp = jp.getParent()

                jp.setAttr(
                    "jointOrient", 0, 0, jp.attr("jointOrient").get()[2] * -1)

        jnt.setAttr("radius", 1.5)

    return chain

def addJointChain(parent, name, positions, normal, axis, negate=False, prefix=''):
    transforms = transform.getChainTransform(positions, normal, axis, negate)
    t = transform.setMatrixPosition(transforms[-1], positions[-1])
    transforms.append(t)
    chain = []
    # pm.select(d=1)
    for i, t in enumerate(transforms):
        node = pm.createNode("joint", name=prefix+"_%s%d_jnt"%(name, i))
        node.setMatrix(t)
        chain.append(node)

    for i, jnt in enumerate(chain):
        # if i == 0:
        jnt.setAttr("jointOrient", jnt.getAttr("rotate"))
        jnt.setAttr("rotate", 0, 0, 0)

    [pm.parent(chain[i+1], chain[i]) for i in range(len(chain)-1)]
    pm.parent(chain, parent)

    return chain

def addJoint(parent, name, m=datatypes.Matrix(), vis=True):
    """Create a joint dagNode.

    Note:
        I'm not using the joint() comand because this is parenting
        the newly created joint to current selection which might not be desired

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The node name.
        m (matrix): The matrix for the node transformation (optional).
        vis (bool): Set the visibility of the new joint.

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("joint", n=name))
    node.setTransformation(m)
    node.setAttr("visibility", vis)

    if parent is not None:
        parent.addChild(node)

    return node

def controlCrv(crv, name, inputs=[]):

    for i, item in enumerate(inputs):
        node = pm.createNode("decomposeMatrix", name=name)
        item.worldMatrix[0] >> node.inputMatrix
        node.outputTranslate >> crv.controlPoints[i]

    return node    

def addCnsCurve(parent, name, centers, degree=1):
    """Create a curve attached to given centers. One point per center

    Arguments:
        parent (dagNode): Parent object.
        name (str): Name
        centers (list of dagNode): Object that will drive the curve.
        degree (int): 1 for linear curve, 3 for Cubic.

    Returns:
        dagNode: The newly created curve.
    """
    # rebuild list to avoid input list modification
    centers = centers[:]
    if degree == 3:
        if len(centers) == 2:
            centers.insert(0, centers[0])
            centers.append(centers[-1])
        elif len(centers) == 3:
            centers.append(centers[-1])

    points = [datatypes.Vector() for center in centers]

    node = addCurve(parent, name, points, False, degree)

    for i,loc in enumerate(centers):
        loc.worldPosition[0] >> node.controlPoints[i]
    # applyop.gear_curvecns_op(node, centers)

    return node


def addCurve(parent,
             name,
             points,
             close=False,
             degree=3,
             m=datatypes.Matrix()):
    """Create a NurbsCurve with a single subcurve.

    Arguments:
        parent (dagNode): Parent object.
        name (str): Name
        positions (list of float): points of the curve in a one dimension array
            [point0X, point0Y, point0Z, 1, point1X, point1Y, point1Z, 1, ...].
        close (bool): True to close the curve.
        degree (bool): 1 for linear curve, 3 for Cubic.
        m (matrix): Global transform.

    Returns:
        dagNode: The newly created curve.
    """
    if close:
        points.extend(points[:degree])
        knots = range(len(points) + degree - 1)
        node = pm.curve(n=name, d=degree, p=points, per=close, k=knots)
    else:
        node = pm.curve(n=name, d=degree, p=points)

    if m is not None:
        node.setTransformation(m)

    if parent is not None:
        parent.addChild(node)

    return node

def follicleConvertUVPin():
    findType = ["mesh", "nurbsSurface",]
    objs = pm.ls(type=findType)
    uvDict = {}
    for obj in objs:
        uvDict[obj] = {}
        outs = pm.listConnections(obj + ".worldMatrix[0]", s=0, d=1, plugs=1)
        if outs:
            for out in outs:
                if pm.nodeType(out) == "follicle":
                    follicle = pm.PyNode(out.split('.')[0])
                    uvDict[obj][follicle.getParent()] = {"u":follicle.parameterU.get(),
                                            "v":follicle.parameterV.get()}
                    pm.delete(follicle)

    for obj,follicleInfo in uvDict.items():
        follicleShapes = []
        if follicleInfo:
            follicleShapes = follicleInfo.keys()
            pm.select(obj, follicleShapes, r=1)
            pm.UVPin(obj, follicleShapes)
        









































































