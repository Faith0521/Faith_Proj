# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-31 16:22:25
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-31 16:22:34
import cmd
from imp import reload
from maya import cmds as mc
from pymel import core as pm


def spineStretchSoftCmd(bridge, crv, parent, count):

    if mc.objExists(bridge):
        return False

    crv_info = mc.shadingNode("curveInfo", asUtility=True, name=crv + "_crvInfo")

















































