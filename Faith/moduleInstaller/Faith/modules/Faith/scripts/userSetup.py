from maya import cmds
from pymel import mayautils

def menu_load():
    import Faith
    Faith.install()

    import Faith.Guide.menu
    Faith.Guide.menu.install()

    import Faith.Tools.menu
    Faith.Tools.menu.install_tool()
    Faith.Tools.menu.install_skin()


if not cmds.about(batch = True):
    mayautils.executeDeferred(menu_load)
