import Faith.menu

def install():
    commands = (
        ("Module System", str_show_guide_manager, "module_system.png"),
    )
    Faith.menu.install("Rigging Tool", commands, image = "rig_tool.png")

str_show_guide_manager = """
print('show manager')
"""




















