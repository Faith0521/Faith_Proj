from maya import cmds
from pymel import mayautils

def menu_load():
    import Faith
    Faith.install()

    import Faith.Guide.menu
    Faith.Guide.menu.install()

if not cmds.about(batch = True):
    mayautils.executeDeferred(menu_load)
