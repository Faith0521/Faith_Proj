import pymel.core as pm
import Faith
from Faith import Guide
from Faith.Core import aboutUI

def draw_comp(comp_type, parent=None):
    """

    :param comp_type:
    :param parent:
    :return:
    """
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

def initial_settings(tabIndex = 0, *args):
    selection = pm.selected()
    if selection:
        root = selection[0]
    else:
        pm.displayWarning("Please select a module guide component.")
        return

    comp_type = False
    guide_root = False
    while root:
        if pm.attributeQuery("guide_type", node = root, ex = True):
            comp_type = root.attr("guide_type").get()
            break
        elif pm.attributeQuery("isHighest", node = root, ex = True):
            guide_root = root
            break
        root = root.getParent()
        pm.select(root)

    if comp_type:
        guide = Guide.importComponentGuide(comp_type)
        wind = aboutUI.showDialog(guide.)
        # wind.tabs






























