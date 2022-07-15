# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:08
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-14 18:56:58

"""创建物体对象的函数(非几何体)"""

import pymel.core as pm
import pymel.core.datatypes as datatypes

from . import aboutTransform

#############################################
# ADD CUSTOM OBJECTS
#############################################

# ==================================================
# TRANSFORM

def addTransform(parent, name, m=datatypes.Matrix()):
    """创建一个transform节点

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 节点的名字
        m (matrix): 位置变换矩阵

    Returns:
        dagNode: 创建的节点对象

    """
    node = pm.PyNode(pm.createNode("transform", n=name))
    node.setTransformation(m)

    if parent is not None:
        parent.addChild(node)

    return node


def addTransformFromPos(parent, name, pos=datatypes.Vector(0, 0, 0)):
    """根据给定的position创建transform节点

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        pos (vector): 给定的物体位置

    Returns:
        dagNode: 创建的节点对象

    """
    node = pm.PyNode(pm.createNode("transform", n=name))
    node.setTranslation(pos, space="world")

    if parent is not None:
        parent.addChild(node)

    return node

# ===========================================
# LOCATOR


def addLocator(parent, name, m=datatypes.Matrix(), size=1):
    """创建一个Locator对象

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        m (matrix): 位置变换矩阵
        size (float): 定位器大小

    Returns:
        dagNode: 创建的物体对象

    """
    node = pm.PyNode(pm.createNode("locator")).getParent()
    node.rename(name)
    node.setTransformation(m)
    node.setAttr("localScale", size, size, size)

    if parent is not None:
        parent.addChild(node)

    return node


def addLocatorFromPos(parent, name, pos=datatypes.Vector(0, 0, 0), size=1):
    """根据给定的position创建一个Locator对象

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        pos (vector): 给定的物体位置
        size (float): 定位器大小

    Returns:
        dagNode: 创建的物体对象

    """
    node = pm.PyNode(pm.createNode("locator")).getParent()
    node.rename(name)
    node.setTranslation(pos, space="world")
    node.setAttr("localScale", size, size, size)

    if parent is not None:
        parent.addChild(node)

    return node

# ===========================================
# JOINT


def addJoint(parent, name, m=datatypes.Matrix(), vis=True):
    """创建骨骼对象

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        m (matrix): 位置变换矩阵
        vis (bool): 设置骨骼显示隐藏

    Returns:
        dagNode: 创建的物体对象

    """
    node = pm.PyNode(pm.createNode("joint", n=name))
    node.setTransformation(m)
    node.setAttr("visibility", vis)

    if parent is not None:
        parent.addChild(node)

    return node


def addJointFromPos(parent, name, pos=datatypes.Vector(0, 0, 0)):
    """创建骨骼对象

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        pos (vector): 给定的物体位置
        vis (bool): 设置骨骼显示隐藏

    Returns:
        dagNode: 创建的物体对象

    """
    node = pm.PyNode(pm.createNode("joint", n=name))
    node.setTranslation(pos, space="world")

    if parent is not None:
        parent.addChild(node)

    return node


def add2DChain2(parent, name, positions, normal, negate=False, vis=True):
    """创建一个2段式骨骼链

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        positions(list of vectors): 给定的物体位置
        normal (vector): 指定骨骼链的法线方向
        negate (bool): If True 将反转骨骼方向

    Returns;
        list of dagNodes: 创建一个列表包含创建的所有骨骼



    >> self.chain3bones = pri.add2DChain2(
        self.setup,
        self.getName("chain3bones%s_jnt"),
        self.guide.apos[0:4],
        self.normal,
        False)

    """
    if "%s" not in name:
        name += "%s"

    transforms = aboutTransform.getChainTransform(positions, normal, negate)
    t = aboutTransform.setMatrixPosition(transforms[-1], positions[-1])
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
        elif i == len(chain) - 1:
            jnt.setAttr("jointOrient", 0, 0, 0)
        else:
            # This will fail if chain is not always oriented the same
            # way (like Z chain)
            v0 = positions[i] - positions[i - 1]
            v1 = positions[i + 1] - positions[i]
            angle = datatypes.degrees(v0.angle(v1))

            jnt.setAttr("jointOrient", 0, 0, angle)

        jnt.setAttr("rotate", 0, 0, 0)
        jnt.setAttr("radius", 1.5)

    return chain


def add2DChain(parent, name, positions, normal, negate=False, vis=True):
    """创建一个2段式骨骼链

    Arguments:
        parent (dagNode): 物体的父级
        name (str): 物体的名称
        positions(list of vectors): 给定的物体位置
        normal (vector): 指定骨骼链的法线方向
        negate (bool): If True 将反转骨骼方向

    Returns;
        list of dagNodes: 创建一个列表包含创建的所有骨骼

    >>> self.rollRef = pri.add2DChain(
        self.root,
        self.getName("rollChain"),
        self.guide.apos[:2],
        self.normal,
        self.negate)

    """
    if "%s" not in name:
        name += "%s"

    transforms = aboutTransform.getChainTransform(positions, normal, negate)
    t = aboutTransform.setMatrixPosition(transforms[-1], positions[-1])
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
            if ([round(elem, 4) for elem in aboutTransform.getTranslation(jnt)]
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


def addIkHandle(parent, name, chn, solver="ikRPsolver", poleV=None):
    """创建IKHandle

    Arguments:
        parent (dagNode): The parent for the IKhandle.
        name (str): The node name.
        chn (list): List of joints.
        solver (str): the solver to be use for the ikHandel. Default
            value is "ikRPsolver"
        poleV (dagNode): Pole vector for the IKHandle

    Returns:
        dagNode: The IKHandle

    >>> self.ikHandleUpvRef = pri.addIkHandle(
        self.root,
        self.getName("ikHandleLegChainUpvRef"),
        self.legChainUpvRef,
        "ikSCsolver")

    """
    # creating a crazy name to avoid name clashing before convert to pyNode.
    node = pm.ikHandle(n=name + "kjfjfklsdf049r58420582y829h3jnf",
                       sj=chn[0],
                       ee=chn[-1],
                       solver=solver)[0]
    node = pm.PyNode(node)
    pm.rename(node, name)
    node.attr("visibility").set(False)

    if parent:
        parent.addChild(node)

    if poleV:
        pm.poleVectorConstraint(poleV, node)

    return node
