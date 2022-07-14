from operator import truediv
from pymel import core as pm
from pymel.core import datatypes as datatypes

class BlendShape(object):

    def CorrectiveShapeVectorMove(self,
                                  TweakVertexName,
                                  BaseModelVertexName,
                                  WorldPos, targetPos,
                                  relPos):
        self.tempPos = datatypes.Vector()
        self.Matrix = datatypes.Matrix()

        pm.setAttr("{0}.xVertex".format(TweakVertexName), relPos[0] + 1)
        self.tempPos = pm.pointPosition(BaseModelVertexName, w = True)
        self.Matrix[0] = self.tempPos[0] - WorldPos[0]
        self.Matrix[4] = self.tempPos[1] - WorldPos[1]
        self.Matrix[8] = self.tempPos[2] - WorldPos[2]





































