# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-05-11 19:14:47
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-14 18:58:06

"""
Make Matrix Constraint
"""
from imp import  reload
import pymel.core as pm
import maya.cmds as mc

from . import aboutPublic
from . import aboutUI
reload(aboutUI)
reload(aboutPublic)

class abouMatrix(aboutUI.aboutUI):
    def __init__(self):
        pass
    # ------------------------------------------------------------------------------------------------------------------------------------------------------#
    def loadMatrixPlugin(self):
        pluginList = ['matrixNodes.mll', 'quatNodes.mll']
        for plug in pluginList:
            if not pm.pluginInfo(plug, query=True, l=True):
                pm.loadPlugin(plug)


    def setFourByFour(self , inputObj, worldMatrix=True):
        """

        Args:
            inputObj: make constraint obj
            worldMatrix: os/ws

        Returns: FourByFourNode

        """
        # init
        self.loadMatrixPlugin()

        # name
        if worldMatrix:
            suffix = 'worldMtx_Fbf'
        else:
            suffix = 'worldRevMtx_Fbf'

        name = '{0}_{1}'.format(inputObj, suffix)

        cheek = pm.objExists(name)
        if cheek:
            return pm.PyNode(name)

        # getMatrix
        loc = pm.spaceLocator()
        pm.delete(pm.parentConstraint(inputObj, loc, mo=False))

        if worldMatrix:
            matrix = loc.getMatrix()  # output
            pm.delete(loc)
        else:
            locRev = pm.spaceLocator()
            dec = pm.createNode('decomposeMatrix')
            pm.connectAttr(loc + '.worldInverseMatrix[0]', dec + '.inputMatrix')
            #
            pm.connectAttr(dec + '.outputRotate', locRev + '.rotate')
            pm.connectAttr(dec + '.outputScale', locRev + '.scale')
            pm.connectAttr(dec + '.outputTranslate', locRev + '.translate')
            matrix = locRev.getMatrix()  # output
            pm.delete(loc)
            pm.delete(locRev)

        # set value
        mtxLs = []
        for i in matrix:
            for j in i:
                mtxLs.append(j)
        fbf = pm.createNode('fourByFourMatrix', n=name)
        fbflis = ['in00', 'in01', 'in02', 'in03',
                  'in10', 'in11', 'in12', 'in13',
                  'in20', 'in21', 'in22', 'in23',
                  'in30', 'in31', 'in32', 'in33']
        for i in range(len(fbflis)):
            pm.setAttr('{}.{}'.format(fbf, fbflis[i]), mtxLs[i])
        #
        return fbf


    def oneToOneMatrix(self , targetObj , aimObj, T = True,
                       R = True, S = False, pInverseLink = True):
        """

        :param targetObj:
        :param aimObj:
        :param offset:
        :param T:
        :param R:
        :param S:
        :param pInverseLink:
        :return:
        """
        # aboutMatrix.oneToOneMatrix(targetObj='pCube1', aimObj='pCube2', T=True, R=True, S=False, offset=True, pInverseLink=True)
        # init
        self.loadMatrixPlugin()
        multMtxName = 'multMtx'
        decomposeMtxName = 'decMtx'

        # set
        multMtx = pm.createNode('multMatrix', n='{0}_{1}'.format(aimObj, multMtxName))
        aimObjMtxFbf = self.setFourByFour(aimObj, worldMatrix=True)
        pm.connectAttr(aimObjMtxFbf + '.output', multMtx + '.matrixIn[0]')
        targeRevMtxFbf = self.setFourByFour(targetObj, worldMatrix=False)
        pm.connectAttr(targeRevMtxFbf + '.output', multMtx + '.matrixIn[1]')
        pm.connectAttr(pm.PyNode(targetObj) + '.worldMatrix[0]', multMtx + '.matrixIn[2]')

        #  parentWorldInverseMatrix
        if pInverseLink:
            aimObjP = pm.listRelatives(aimObj, p = True)
            if aimObjP:
                pObj = aimObjP[0]
                pm.connectAttr(pObj + '.worldInverseMatrix[0]', multMtx + '.matrixIn[3]')

        decMtx = pm.createNode('decomposeMatrix', n='{0}_{1}'.format(aimObj, decomposeMtxName))
        pm.connectAttr(multMtx + '.matrixSum', decMtx + '.inputMatrix')

        #
        if T:
            pm.connectAttr(decMtx + '.outputTranslate', pm.PyNode(aimObj) + '.t')
        if R:
            pm.connectAttr(decMtx + '.outputRotate', pm.PyNode(aimObj) + '.r')
        if S:
            pm.connectAttr(decMtx + '.outputScale', pm.PyNode(aimObj) + '.s')


    def weighGrp(self , targetList = [], aimObj = ''):
        # init
        weightAttrName = '_weight'

        # create weight bridge
        weightGrp = pm.group(em=True, n='{0}_{1}'.format(aimObj, 'mtxWeight'))
        baseAttr = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v']
        for i in baseAttr:
            pm.setAttr(weightGrp + i, k=False, cb=False, l=True)
        pm.parent(weightGrp, aimObj)

        #
        tgtNameList = [str(i) + weightAttrName for i in targetList]
        for i in tgtNameList:
            pm.addAttr(weightGrp, ln=i, k=True, dv=1.0 / len(tgtNameList))
        return weightGrp


    def manyToOneMatrix(self , targetList, aimObj, weightList=[],
                        T = True , R = True, S = True , pInverseLink = True):
        """

        :param targetList:
        :param aimObj:
        :param weightList:
        :param offset:
        :param T:
        :param R:
        :param pInverseLink:
        :return:
        """
        # targetList = ['pCube1', 'pCube2']
        # aimObj = 'pCube3'
        # aboutMatrix.manyToOneMatrix(targetList, aimObj, offset=True, T=True, R=True, pInverseLink=True)
        # init
        self.loadMatrixPlugin()
        wtMtxName = 'wtMtx'
        multMtxName = 'multMtx'
        decomposeMtxName = 'decMtx'

        #
        outputWtMtx = pm.createNode('wtAddMatrix', n='{0}_{1}'.format(aimObj, wtMtxName))
        outputMultMtx = pm.createNode('multMatrix', n='{0}_{1}'.format(aimObj, multMtxName))
        outputDecMtx = pm.createNode('decomposeMatrix', n='{0}_{1}'.format(aimObj, decomposeMtxName))
        weightGrp = self.weighGrp(targetList, aimObj)

        aimObjMatrixFbf = self.setFourByFour(aimObj, worldMatrix=True)
        #
        pm.connectAttr(aimObjMatrixFbf + '.output', outputMultMtx + '.matrixIn[0]')
        pm.connectAttr(outputWtMtx + '.matrixSum', outputMultMtx + '.matrixIn[1]')
        pm.connectAttr(outputMultMtx + '.matrixSum', outputDecMtx + '.inputMatrix')

        #  parentWorldInverseMatrix
        if pInverseLink:
            aimObjP = pm.listRelatives(aimObj, p=True)
            if aimObjP:
                pObj = aimObjP[0]
                pm.connectAttr(pObj + '.worldInverseMatrix[0]', outputMultMtx + '.matrixIn[2]')

        #
        weightAttrList = weightGrp.listAttr(ud=True)
        if weightList:
            for i, n in enumerate(weightAttrList):
                n.set(weightList[i])
        #
        for i, n in enumerate(targetList):
            multMtx = pm.createNode('multMatrix', n='{0}_{1}_offset_{2}'.format(n, aimObj, multMtxName))
            nRevMtxFbf = self.setFourByFour(n, worldMatrix=False)
            pm.connectAttr(nRevMtxFbf + '.output', multMtx + '.matrixIn[0]')
            pm.connectAttr(n + '.worldMatrix[0]', multMtx + '.matrixIn[1]')
            pm.connectAttr(multMtx + '.matrixSum', pm.PyNode(outputWtMtx + '.wtMatrix[{0}].matrixIn'.format(i)))

            #
            pm.connectAttr(weightAttrList[i], pm.PyNode(outputWtMtx + '.wtMatrix[{0}].weightIn'.format(i)))
        #
        if T:
            pm.connectAttr(outputDecMtx + '.outputTranslate', aimObj + '.t')
        if R:
            pm.connectAttr(outputDecMtx + '.outputRotate', aimObj + '.r')
        if S:
            pm.connectAttr(outputDecMtx + '.outputScale', aimObj + '.s')

        result = {'output': outputDecMtx}
        return result


    def matrixTwist(self , rollObj, nonRollObj, twistObj, weightList=[1, 0], axis='y'):
        """
        :param rollObj:
        :param nonRollObj
        :param twistObj:
        :param weightList:
        :param axis:
        :return:
        """
        # init
        self.loadMatrixPlugin()
        targetList = [rollObj, nonRollObj]
        result = self.manyToOneMatrix(targetList, twistObj, weightList = weightList, T = True, R = False,
                                      S = False , pInverseLink = True)
        quatEul = pm.createNode('quatToEuler', n='{0}_quatEul'.format(twistObj))
        #
        decMtx = result['output']
        axis = axis.upper()
        pm.connectAttr(decMtx + '.outputQuat.outputQuat' + axis, quatEul + '.inputQuat.inputQuat' + axis)
        pm.connectAttr(decMtx + '.outputQuat.outputQuatW', quatEul + '.inputQuat.inputQuatW')
        pm.connectAttr(quatEul + '.outputRotate' + axis, twistObj + '.rotate' + axis)


    # Deformer Matrix
    # ---------------------------------------------------------------------------------------------------
    def connectBindPreMatrix(self , skinJnt, reverseJnt, skinNode=None):
        skinMatrixList = []
        worldMatrixAttr = skinJnt + '.worldMatrix'

        if skinNode is None:
            skinMatrixList = mc.listConnections(worldMatrixAttr, d=True, p=True)
        else:
            skinMatrixs = mc.listConnections(worldMatrixAttr, d=True, p=True)
            for attr in skinMatrixs:
                if skinNode in attr:
                    skinMatrixList.append(attr)

        for matrix in skinMatrixList:
            bindPreMatrixAttr = matrix.replace('matrix', 'bindPreMatrix')
            isConnect = mc.listConnections(bindPreMatrixAttr, s=True, p=True)
            if isConnect is None:
                mc.connectAttr(reverseJnt + '.worldInverseMatrix[0]', bindPreMatrixAttr)
            else:
                pass


    def reverseMatrix(self , needRevJnts=None, skinNode=None, parentLayer=1):
        # create reverse matrix joints for secound joint
        # > get use reverse joints
        if parentLayer is None:
            parentLayer = self.promptDialogWin(titleDialog='Which Layer', instrunctions='Parent Layer:',
                                                  buttons=['OK', 'Cancel'], text=3)
        if needRevJnts is None:
            needRevJnts = mc.ls(sl=1)

        if parentLayer is not None:
            for jnt in needRevJnts:
                mc.select(jnt)
                reverseJntName = jnt + '_reverse'

                if mc.objExists(reverseJntName):
                    reverseJnt = reverseJntName
                else:
                    for i in range(int(parentLayer)):
                        mc.pickWalk(d='up')
                    reverseJnt = mc.joint(p=(0, 0, 0), name=jnt + '_reverse')
                    aboutPublic.snapAtoB(reverseJnt, jnt)

                self.connectBindPreMatrix(jnt, reverseJnt, skinNode)
        else:
            pass