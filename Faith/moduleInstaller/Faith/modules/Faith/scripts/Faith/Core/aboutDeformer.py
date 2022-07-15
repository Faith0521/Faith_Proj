# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-01 21:32:26
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-01 21:36:21

import xml
import pymel.core as pm
import maya.cmds as mc
from . import aboutLog

class Twist(object):
	
	def __repr__(self):
		return "Twist ({0})".format(self.node)

	@property
	def handle(self):
		transform = pm.listConnections(self.node + ".matrix", d = True)[0]
		return transform

	@property
	def start_angle(self):
		value = pm.getAttr(self.node + ".startAngle")
		return value
	




































