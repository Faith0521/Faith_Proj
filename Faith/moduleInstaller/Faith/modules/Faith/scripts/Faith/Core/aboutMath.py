# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-06 20:03:08
# @Last Modified by:   Admin
# @Last Modified time: 2022-06-09 19:44:43

import math
import pymel.core as pm,maya.cmds as mc
from pymel.core.datatypes import Vector,Point,Matrix,Quaternion,EulerRotation


class Spline(object):

    def NoneZero(self, value):
        """

        :param value:
        :return:
        """
        if value == 0.0:
            return 1.0
        else:
            return value

    def get_knots(self, n, degree):
        """

        :param n:
        :param degree:
        :return:
        """
        return [0.0] * degree + [i * 1.0 / (n - degree) for i in range(n - degree + 1)] + [1.0] * degree

    def getSpline_w(self, knots, degree, param, i):
        """

        :param knots:
        :param degree:
        :param param:
        :param i:
        :return:
        """
        if degree == 0:
            if (knots[i] <= param < knots[i + 1]):
                return 1.0
            if (knots[i] <= param < knots[i + 1]) and param == 1.0:
                return 1.0
            else:
                return 0.0
        else:
            return (param - knots[i]) / self.NoneZero((knots[i + degree] - knots[i])) \
                   * self.getSpline_w(knots, degree - 1, param, i) + \
                   (knots[i + degree + 1] - param) / self.NoneZero((knots[i + degree + 1] - knots[i + 1])) * \
                   self.getSpline_w(knots, degree - 1, param, i + 1)

    def getSpline_ws(self, knots, degree, param, n):
        return [self.getSpline_w(knots, degree, param, i) for i in range(n)]

    def spline(self, pts, param, degree):
        """

        :param pts:
        :param param:
        :param degree:
        :return:
        """
        count = len(pts)
        knots = self.get_knots(count, degree)
        ws = self.getSpline_ws(knots, degree, param, count)
        points = [w * p for w, p in zip(ws, pts)]
        p = points.pop(0)
        return sum(points, p)

    def spline_2(self, ps, param):
        span_num = len(ps) - 3
        span_length = 1.0 / span_num
        span_index = int(param / span_length)
        t = (param - span_index * span_length) / span_length
        if span_index == span_num:
            span_index -= 1
            t = 1.0
        p1, p2, p3, p4 = ps[span_index + 0], ps[span_index + 1], ps[span_index + 2], ps[span_index + 3]
        w1 = pow(1 - t, 3) / 6
        w2 = (3 * pow(t, 3) - 6 * pow(t, 2) + 4) / 6
        w3 = (-3 * pow(t, 3) + 3 * pow(t, 2) + 3 * t + 1) / 6
        w4 = pow(t, 3) / 6
        return p1 * w1 + p2 * w2 + p3 * w3 + p4 * w4

    def tail_compute(self, cms, count, direction):
        """

        :param cms:
        :param count:
        :param direction:
        :return:
        """
        cps = [Point(0, 0, 0) * cm for cm in cms]
        # cps = list(cps)
        cps.append(cps[-1] + (cps[-1] - cps[-2]))
        cps.insert(0, cps[0] + (cps[0] - cps[1]))

        jps = [self.spline_2(cps, i * 1.0 / (count - 1)) for i in range(count)]
        return jps

    # def tail(self, joints):
    #     cms = [i.worldMatrix[0].get() for i in pm.selected()]
    #     jn = 19
    #     d = True
    #     jps = self.tail_compute(cms, jn, d)
    #     print(cms, jps)
    #     for joint, p in zip(joints, jps):
    #         joint.setTranslation(p, space="world")



























































