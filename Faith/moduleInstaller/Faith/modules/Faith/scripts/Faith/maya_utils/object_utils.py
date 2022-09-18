# -*- coding: utf-8 -*-
# @Author: 46314
# @Date:   2022-09-18 17:11:59
# @Last Modified by:   46314
# @Last Modified time: 2022-09-18 17:12:22

import re,collections

from maya import cmds
from maya import OpenMaya as om
from maya import OpenMayaAnim as aom
# from Faith.maya_utils import attribute_utils
from Faith.Core.aboutPy import PY2

if PY2:
    STR = basestring
    UNICODE = unicode
else:
    STR = str
    UNICODE = str

# 定义局部变量
node_types = {
    'nurbsCurve':           om.MFn.kNurbsCurve,
    'locator':              om.MFn.kLocator,
    'mesh':                 om.MFn.kMesh,
    'nurbsSurface':         om.MFn.kNurbsSurface,
    'unitConversion':       om.MFn.kUnitConversion,
    'blendWeighted':        om.MFn.kBlendWeighted,
    'transform':            om.MFn.kTransform,
    'follicle':             om.MFn.kFollicle,
    'dag':                  om.MFn.kDagNode,
    'joint':                om.MFn.kJoint,
    'ikHandle':             om.MFn.kIkHandle,
    'effector':             om.MFn.kIkEffector,
    'component':            om.MFn.kComponent,
    'lattice':              om.MFn.kLattice,
    'blendShape':           om.MFn.kBlendShape,
    'animCurve':            om.MFn.kAnimCurve,
    'set':                  om.MFn.kSet,
    'camera':               om.MFn.kCamera,
    'skin':                 om.MFn.kSkin,
    'skinCluster':          om.MFn.kSkinClusterFilter,
    'tweak':                om.MFn.kTweak,
    'bend':                 om.MFn.kDeformBend,
    'squash':               om.MFn.kDeformSquash,
    'cluster':              om.MFn.kCluster,
    'deltaMush':            om.MFn.kDeltaMush,
    'wire':                 om.MFn.kWire,
    'sculpt':               om.MFn.kSculpt,
    'wrap':                 om.MFn.kWrapFilter,
    'shrinkWrap':           om.MFn.kShrinkWrapFilter,
}

# 定义私有变量
__verbosity__ = 0


def vprint(*args):
    """
    print only if verbosity is > 0.
    :param args: array items.
    :return: <None>
    """
    if __verbosity__:
        print(args)


def flatten(array):
    """
    展开列表生成器
    :param array:
    :return:
    """
    for el in array:
        if isinstance(el, collections.Iterable) and not isinstance(el,STR):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def select_object(object_name):
    """
    选择物体
    :param object_name:
    :return:
    """
    return cmds.select(object_name)


def selection_order(func):
    """
    选择顺序的装饰器
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        set_pref = 0
        select_pref = cmds.selectPref(trackSelectionOrder=1, q=1)
        if not select_pref:
            set_pref = 1
            cmds.selectPref(trackSelectionOrder=1)
        # run func
        answer = func(*args, **kwargs)
        if set_pref:
            cmds.selectPref(trackSelectionOrder=select_pref)
        return answer
    return wrapper


def compare_array_length(array_1, array_2):
    """
    比较两个列表的长度是否相等
    :param array_1:
    :param array_2:
    :return:
    """
    return len(array_1) == len(array_2)


def get_dag(object_name="", shape=False):
    """
    returns a dag path object.
    :param object_name:
    :param shape:
    :return:
    """
    m_sel = om.MSelectionList()
    if not shape:
        m_sel.add(object_name)
    elif shape:
        shapes_len = get_shapes_len(get_m_obj(object_name))
        if shapes_len > 0:
            for i in range(shapes_len):
                m_sel.add(get_shape_name(object_name)[i])
        elif not shapes_len and not hasFn(get_shape_name(object_name), 'transform'):
                m_sel.add(object_name)
    m_dag = om.MDagPath()
    m_sel.getDagPath(0, m_dag)
    return m_dag


def get_shape_name(object_name="", shape_type=""):
    """
    :return: the shape name.
    """
    if not object_name:
        object_name = get_selected_node()
    return get_m_shape(get_m_obj(object_name), shape_type=shape_type, as_strings=True)


@selection_order
def get_selected_node(single=True):
    """
    grabs the current name of the selected object.
    :param single: <bool> if False, get selection array.
    :return: <str> selected object. <str> empty list for failure.
    """
    if single:
        try:
            return cmds.ls(os=1, fl=1)[0]
        except IndexError:
            return ''
    return tuple(cmds.ls(os=1, fl=1))


def get_m_shape(m_object=None, shape_type="", as_strings=False):
    """
    get the MObject children object(s).
    :param m_object: <OpenMaya.MObject> the MObject to get children frOpenMaya.
    :param shape_type: <str> get only shapes of this type.
    :param as_strings: <bool> return as string name array.
    :return: <tuple> array of shape objects.
    """
    return_items = ()
    fn_item = om.MFnDagNode(m_object)
    ch_count = fn_item.childCount()
    if ch_count:
        for i in range(ch_count):
            ch_item = fn_item.child(i)
            if shape_type and not hasFn(ch_item, shape_type):
                continue
            if hasFn(ch_item, 'transform'):
                continue
            if as_strings:
                return_items += om.MFnDependencyNode(ch_item).name(),
            elif not as_strings:
                return_items += ch_item,
    elif not ch_count:
        if hasFn(m_object, shape_type):
            return_items += m_object,
    return return_items


def hasFn(item_name, shape_type):
    """
    check if the MObject provided has this type.
    :param item_name:
    :param shape_type:
    :return:
    """
    if isinstance(item_name, STR) or isinstance(item_name, UNICODE):
        item_name = get_m_obj(item_name)
    if isinstance(shape_type, str):
        if shape_type not in node_types:
            return False
        return item_name.hasFn(node_types[shape_type])
    if isinstance(shape_type, int):
        return item_name.hasFn(shape_type)

def get_m_obj(object_str):
    """
    get MDagPath from MObject.
    :param object_str: <str> get the MObject from this parameter given.
    :return: <OpenMaya.MObject> the maya object.
    """
    if isinstance(object_str, STR) or isinstance(object_str, UNICODE):
        try:
            om_sel = om.MSelectionList()
            om_sel.add(object_str)
            node = om.MObject()
            om_sel.getDependNode(0, node)
            return node
        except:
            raise RuntimeError('[Get MObject] :: failed on {}'.format(object_str))
    return object_str


def get_shapes_len(m_object=None):
    """
    获取shape节点的长度
    :param m_object:
    :return:
    """
    fn_item = om.MFnDagNode(m_object)
    ch_shapes = []
    ch_count = fn_item.childCount()
    if ch_count:
        for i in range(ch_count):
            ch_item = fn_item.child(i)
            if hasFn(ch_item, 'transform'):
                continue
            ch_shapes .append(i)
    return len(ch_shapes)























