# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-27 17:04:09
# @Last Modified by:   yinyufei
# @Last Modified time: 2022-04-27 17:27:32

"""Guide base Torso module"""

from functools import partial

# pymel
import pymel.core as pm
import pymel.core.datatypes as datatypes

# faith
import Faith
from Faith.Guide.Component import guide

from imp import reload
from Faith.Core import aboutTransform, aboutAttribute

# reload
reload(aboutTransform)
reload(aboutAttribute)
reload(guide)

# guide info
AUTHOR = "Yin Yu Fei(Copyright by mgear)"
EMAIL = "463146085@qq.com"
VERSION = [0, 0, 1]
TYPE = "torso01"
NAME = "torso"
DESCRIPTION = ". \n"

##########################################################
# CLASS
##########################################################


class Guide(guide.ComponentGuide):
    """Component Guide Class"""

    guideType = TYPE
    guideName = NAME
    description = DESCRIPTION

    author = AUTHOR
    email = EMAIL
    version = VERSION

    connectors = [""]