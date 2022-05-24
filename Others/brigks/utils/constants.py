'''Constants Module

This module offer constants value useful in a rig builder
'''
from math3d.vectorN import Vector3 

ROT_ORDERS = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]

ATTRS_TRS = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
ATTRS_TR = ("tx", "ty", "tz", "rx", "ry", "rz")
ATTRS_TS = ("tx", "ty", "tz", "sx", "sy", "sz")
ATTRS_T = ("tx", "ty", "tz")
ATTRS_R = ("rx", "ry", "rz")

AXIS_X = Vector3([1,0,0])
AXIS_Y = Vector3([0,1,0])
AXIS_Z = Vector3([0,0,1])
AXIS_NX = Vector3([-1,0,0])
AXIS_NY = Vector3([0,-1,0])
AXIS_NZ = Vector3([0,0,-1])
