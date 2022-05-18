# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-28 20:48:25
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-18 21:06:58

"""
Just a test py file
"""

import Faith
from Faith import Guide
from pymel import core as pm
from functools import partial

def draw_comp(comp_type, parent=None):
    """"""
    guide = Guide.guide.ComponentDraw()
    if not parent and pm.selected():
        parent = pm.selected()[0]

    if parent:
        if not parent.hasAttr("isGuide") and not parent.hasAttr("isHighest"):
            pm.displayWarning(
                "{}: is not valid Shifter guide elemenet".format(parent))
            return

    guide.drawNewComponent(parent, comp_type)

def build_from_selection(*args):
    """Build rig from current selection

    Args:
        *args: None
    """
    rg = Guide.Rigging()
    rg.build_from_selected()

if __name__ == "__main__":
    draw_comp("Root", None)
    build_from_selection()








































