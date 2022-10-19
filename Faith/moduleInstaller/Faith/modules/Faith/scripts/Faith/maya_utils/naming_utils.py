# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-16 16:23:45
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-16 16:23:53
import string
import re
import maya.cmds as mc

# default fields/tokens
NAMING_RULE_TOKENS = ["side",
                      "component",
                      "index",
                      "extension"]
DEFAULT_NAMING_RULE = r"{side}_{guide}{index}_{extension}"
DEFAULT_SIDE_L_NAME = "L"
DEFAULT_SIDE_R_NAME = "R"
DEFAULT_SIDE_C_NAME = "C"
DEFAULT_JOINT_SIDE_L_NAME = "L"
DEFAULT_JOINT_SIDE_R_NAME = "R"
DEFAULT_JOINT_SIDE_C_NAME = "C"
DEFAULT_CTL_EXT_NAME = "ctrl"
DEFAULT_JOINT_EXT_NAME = "jnt"