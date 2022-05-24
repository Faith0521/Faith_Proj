'''Config Module

Modifying this module allows you to customize the naming convention of Brigks
'''

from collections import OrderedDict


DATA_ATTRIBUTE = "_userProps"
BINDPOSE_ATTRIBUTE = "bindMatrix"

USE_ORG = "Org"
USE_GDE = "Gde"
USE_BFR = "Bfr"
USE_CTL = "Ctl"
USE_RIG = "Rig"
USE_JNT = "Jnt"
USE_NDE = "Nde"

# LOC_LEFT = "L"
# LOC_RIGHT = "R"
# LOC_MIDDLE = "M"
# LOC_TOP = "T"
# LOC_BOTTOM = "B"
# LOC_SYMMETRY = "X"

TOKENS = "{use}_{loc}_{name}_{part}"


# SYSTEMS
LOCATIONS = OrderedDict()
LOCATIONS["M"] = "M"
LOCATIONS["T"] = "T"
LOCATIONS["B"] = "B"
LOCATIONS["L"] = "L"
LOCATIONS["R"] = "R"
LOCATIONS["X"] = "X"
	