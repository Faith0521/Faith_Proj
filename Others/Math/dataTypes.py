# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-06-10 19:21:36
# @Last Modified by:   Admin
# @Last Modified time: 2022-06-11 10:56:21
import math

EPSION = 1e-8

class Point:

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.data = (self.x, self.y, self.z)

    def __repr__(self):
        """

        :return:
        """
        return 'Point([' + (','.join(list(map(str, self.data)))) + '])'

    def __str__(self):
        """

        :return:
        """
        return '[' + ','.join(list(map(str, self.data))) + ']'

class Vector:

    def __init__(self, x=0.0, y=0.0, z=0.0):
        """

        :param x:
        :param y:
        :param z:
        """
        self.x = x
        self.y = y
        self.z = z
        self.values = [self.x, self.y, self.z]

    @property
    def xAxis(self):
        return self.x

    @xAxis.setter
    def xAxis(self, value):
        return value

    @property
    def yAxis(self):
        return self.y

    @yAxis.setter
    def yAxis(self, value):
        return value

    @property
    def zAxis(self):
        return self.z

    @zAxis.setter
    def zAxis(self, value):
        return value

    def __repr__(self):
        """

        :return:
        """
        return "Vector([{0},{1},{2}])".format(self.x, self.y, self.z)

    def __str__(self):
        """

        :return:
        """
        return "[{}]".format(", ".join(str(e) for e in self.values))

    def __contains__(self, value):
        """

        :param item:
        :return:
        """
        return True if value in self.values else False

    def __eq__(self, other):
        """

        :param other:
        :return:
        """
        return self.values == other.values

    def __xor__(self, other):
        """

        :param other:
        :return:
        """
        return Vector((self.y*other.z-other.y*self.z),
                      -(self.x*other.z-other.x*self.z),
                      self.x*other.y-other.x*self.y)

    def __abs__(self):
        """

        :return:
        """
        return math.hypot(self.x, self.y, self.z)

    def __iter__(self):
        """

        :return:
        """
        return self.values.__iter__()

    def __add__(self, other):
        """

        :param other:
        :return:
        """
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """

        :param other:
        :return:
        """
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        """

        :param other:
        :return:
        """
        t = other.__class__
        if t == int or t == float:
            return Vector(self.x*other, self.y*other, self.z*other)
        return (self.x*other.x + self.y*other.y + self.z*other.z)

    def __truediv__(self, other):
        """

        :param other:
        :return:
        """
        return Vector(1.0/self.x * other.x, 1.0/self.y * other.y, 1.0/self.z * other.z)

    def __getitem__(self, item):
        """

        :param item:
        :return:
        """
        return self.values[item]

    def __pos__(self):
        """

        :return:
        """
        return Vector(1.0*self.x, 1.0*self.y, 1.0*self.z)

    def __neg__(self):
        """

        :return:
        """
        return Vector(-1.0 * self.x, -1.0 * self.y, -1.0 * self.z)

    def __len__(self):
        """

        :return:
        """
        return len(self.values)

    def angle(self, other):
        """

        :param other:
        :return:
        """
        dot = self * other
        length_dot = self.length() * other.length()
        return math.acos(dot / length_dot)

    def length(self):
        """

        :return:
        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normal(self):
        """

        :return:
        """
        if self.length() < EPSION:
            raise ZeroDivisionError("Vector length can not be zero.")
        return Vector(self.x / self.length(), self.y / self.length(), self.z / self.length())

    def normalize(self):
        """

        :return:
        """
        if self.length() < EPSION:
            raise ZeroDivisionError("Vector length can not be zero.")
        vec = self.normal()
        self.x = vec.x
        self.y = vec.y
        self.z = vec.z

    @classmethod
    def distance(cls, vecA, vecB):
        """

        :param vecA:
        :param vecB:
        :return:
        """
        if not isinstance(vecA, Vector) or not isinstance(vecB, Vector):
            raise ValueError("distance object is not instance of Vector.")
        dx = vecA.x - vecB.x
        dy = vecA.y - vecB.y
        dz = vecA.z - vecB.z
        return math.sqrt(dx**2 + dy**2 + dz**2)

    @classmethod
    def cross(cls, vecA, vecB):
        """

        :param vecA:
        :param vecB:
        :return:
        """
        if not isinstance(vecA, Vector) or not isinstance(vecB, Vector):
            raise ValueError("distance object is not instance of Vector.")
        return cls((vecA.y * vecB.z - vecB.y * vecA.z),
                      -(vecA.x * vecB.z - vecB.x * vecA.z),
                      vecA.x * vecB.y - vecB.x * vecA.y)

class Matrix:

    def __init__(self, matrix=None):
        """

        :param matrix:
        """
        if matrix is None:
            matrix = [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        self.matrix = matrix

    def __repr__(self):
        """

        :return:
        """
        return 'Matrix([\n' + (',\n'.join(list(map(str, self.matrix)))) + ',\n])'

    def __str__(self):
        """

        :return:
        """
        return '\n'.join(list(map(str, self.matrix)))

    def __add__(self, other):
        """

        :param other:
        :return:
        """
        if isinstance(other, Matrix):
            result = Matrix([[0 for j in range(len(other.matrix[0]))] for i in range(len(self.matrix))])
            for i in range(len(self.matrix)):
                for j in range(len(self.matrix[0])):
                    result.matrix[i][j] = self.matrix[i][j] + other.matrix[i][j]
            return result
        else:
            raise ValueError("Can not add with the type of {}.".format(str(type(other)).split('\'')[1]))

    def __mul__(self, other):
        """

        :param other:
        :return:
        """
        if isinstance(other, Matrix):
            result = Matrix([[0 for j in range(len(other.matrix[0]))] for i in range(len(self.matrix))])
            for i in range(len(self.matrix)):
                for j in range(len(result.matrix[0])):
                    for m in range(len(self.matrix[0])):
                        result.matrix[i][j] += self.matrix[i][m] * other.matrix[m][j]
            return result
        elif isinstance(other, Vector):
            return Vector(
                self.matrix[0][0]*other.x + self.matrix[0][1]*other.y + self.matrix[0][2]*other.z,
                self.matrix[1][0] * other.x + self.matrix[1][1] * other.y + self.matrix[1][2] * other.z,
                self.matrix[2][0] * other.x + self.matrix[2][1] * other.y + self.matrix[2][2] * other.z
            )

if __name__ == '__main__':

    # vec1 = Vector(2.0,5.0,2.5)
#     # # vec2 = Vector(2.0,3.0,5.0)
#     # # Vector.angle(vec1, vec2)
#     # A = Matrix([[2.0, 1.0, 0.0, 0.0], [0.0, 3.0, 0.0, 0.0], [0.0, 2.0, 6.0, 0.0], [-5.404136004755982, 7.199411018297219, 0.0, 1.0]])
#     # B = Matrix([[2.0, 5.0, 2.5, 0.0], [2.0, 5.0, 2.5, 0.0], [2.0, 5.0, 2.5, 0.0], [2.0, 5.0, 2.5, 0.0]])
#     # print(A * vec1)
    ptA = Point()
    print(ptA)


























