import pymel.core as pm
import Faith

menuName = "Faith"

def create(menuName = menuName):
    """

    :param menuName:
    :return:
    """
    if pm.menu(menuName, exists = True):
        pm.deleteUI(menuName)

    pm.menu(menuName,
            parent = "MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuName
            )
    return menuName

def install(label, commands, parent=menuName, image=""):
    """Installer Function for sub menus

    Args:
        label (str): Name of the sub menu
        commands (list): List of commands to install
        parent (str, optional): Parent menu for the submenu
    """

    try:
        m = pm.menuItem(parent=parent,
                        subMenu=True,
                        tearOff=True,
                        label=label,
                        image = image)
        for conf in commands:
            if len(conf) == 3:
                in_label, command, img = conf
            else:
                in_label, command = conf
                img = ""
            if not command:
                pm.menuItem(divider=True)
                continue
            if not label:
                command(m)
                pm.setParent(m, menu=True)
                continue

            pm.menuItem(label=in_label, command=command, image=img)

        return m

    except Exception as ex:
        template = ("An exception of type {0} occured. "
                    "Arguments:\n{1!r}")
        message = template.format(type(ex).__name__, ex.args)
        pm.displayError(message)