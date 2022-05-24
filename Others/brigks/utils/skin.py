
from math3d.matrixN import Matrix4

from maya import cmds


def resetBindPose(skinCluster):
    for index in cmds.getAttr(skinCluster+".bindPreMatrix", mi=True):
        matrix = cmds.getAttr(skinCluster+".matrix[{}]".format(index))

        matrix = Matrix4(matrix)
        bindMatrix = matrix.inverse().flattened()

        matrix = cmds.setAttr(skinCluster+".bindPreMatrix[{}]".format(index), bindMatrix, type="matrix")