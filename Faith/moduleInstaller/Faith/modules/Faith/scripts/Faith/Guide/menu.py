import Faith.menu


def install():
    commands = (
        ("Module Rigging", str_show_guide_manager, "module_system.png"),
        ("Import Module Guide", str_import_guide, ""),
    )
    Faith.menu.install("Rigging Manager", commands, image = "rig_tool.png")


str_show_guide_manager = """
from Faith.Guide import guide_gui
guide_gui.show_ui()
"""
str_import_guide = """

"""




















