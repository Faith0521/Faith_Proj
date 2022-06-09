# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-11 19:14:47
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-29 12:45:18

"""

"""
import pymel.core as pm
from pymel.core.datatypes import Vector,Point,Matrix
import math

class aboutMatrix(object):

    def __init__(self, m = Matrix()):
        """

        :param m:
        """
        if not isinstance(m, Matrix):
            raise ValueError("Input param is not matrix value.")
        self._matrix = m

    def translate_matrix(self, tx, ty, tz):
        """
        位移矩阵
        :param tx:
        :param ty:
        :param tz:
        :return:
        """
        data = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [tx, ty, tz, 0.0]
        ]
        return data

    def scale_matrix(self, sx, sy, sz):
        """
        缩放矩阵
        :param sx:
        :param sy:
        :param sz:
        :return:
        """
        data = [
            [sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        return data

    def rotateX_matrix(self, rx):
        """
        旋转X矩阵
        :param rx:
        :return:
        """
        cx = math.cos(rx)
        sx = math.sin(rx)
        data = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cx, sx, 0.0],
            [0.0, -sx, cx, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        return data

    def rotateY_matrix(self, ry):
        """
        旋转Y矩阵
        :param ry:
        :return:
        """
        cy = math.cos(ry)
        sy = math.sin(ry)
        data = [
            [cy, 0.0, -sy, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [sy, 0.0, cy, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        return data

    def rotateZ_matrix(self, ry):
        """
        旋转Z矩阵
        :param rz:
        :return:
        """
        cz = math.cos(rz)
        sz = math.sin(rz)
        data = [
            [cz, sz, 0.0, 0.0],
            [-sz, cz, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        return data

    def rotate_matrix(self, rx, ry, rz):
        """
        旋转矩阵
        :param rx:
        :param ry:
        :param rz:
        :return:
        """
        return self.rotateX_matrix(rx)*self.rotateY_matrix(ry)*self.rotateZ_matrix(rz)

    def compose(self, t, r, s):
        """

        :param t:
        :param r:
        :param s:
        :return:
        """
        return self.scale_matrix(*s)*self.rotate_matrix(*r)*self.translate_matrix(*t)

    def decompose(self):
        tx, ty, tz = self._matrix[3][0], self._matrix[3][1], self._matrix[3][2]
        sx = Vector(*self._matrix[0]).length()
        sy = Vector(*self._matrix[1]).length()
        sz = Vector(*self._matrix[3]).length()
        rx = math.atan2(self._matrix[1][2]/sy, self._matrix[2][2]/sz)/math.pi*180
        ry = math.asin(-self._matrix[0][2]/sx)/math.pi*180
        rz = math.atan2(self._matrix[0][1]/sx, self._matrix[0][0]/sx)/math.pi*180

        return [[tx,ty,tz],[rx,ry,rz],[sx,sy,sz]]



















