# -*- coding: utf-8 -*-
#autoWeight v2.4
import maya.cmds as cmds
import pymel.core as pm
import math,time
class autoWeightClass(object):
    ''' 根据函数计算vtx百分比分配skin权重'''
    use=None

    @classmethod
    def showUI(cls,uiPath):
        tempIns = cls(uiPath)
        tempIns.createUI()
        return tempIns


    def __init__(self,uiPath):
        autoWeightClass.use = self
        self.uiPath = uiPath
        self.window = 'autoSkinWeight_Window'
        self.calculation_comboBox = '%s|gridLayout|calculation_comboBox'%(self.window)
        self.algorithm_comboBox = '%s|gridLayout|algorithm_comboBox'%(self.window)
        self.geometryVtx_lineEdit = '%s|gridLayout|geometryVtx_lineEdit'%(self.window)
        self.joint_lineEdit = '%s|gridLayout|joint_lineEdit'%(self.window)
        self.nurbs_lineEdit = '%s|gridLayout|nurbs_lineEdit'%(self.window)
        self.startExpand_convert = '%s|gridLayout|hide|startExpand_convert'%(self.window)
        self.endExpand_convert = '%s|gridLayout|hide|endExpand_convert'%(self.window)
        self.QProgressBar = '%s|gridLayout|QProgressBar'%(self.window)
        self.calculation_comboBox_Value = ''
        self.algorithm_comboBox_Value = ''
        self.geometryVtx_lineEdit_Value = ''
        self.joint_lineEdit_Value = ''
        self.nurbs_lineEdit_Value = ''
        self.startExpand_convert_Value = ''
        self.endExpand_convert_Value = ''



    def loadConfig(self):
        ''' '''
        self.calculation_comboBox_Value = cmds.optionMenu(self.calculation_comboBox,q=True,v=True)
        self.algorithm_comboBox_Value = cmds.optionMenu(self.algorithm_comboBox,q=True,v=True)
        self.geometryVtx_lineEdit_Value = cmds.textField(self.geometryVtx_lineEdit,q=True,tx=True)
        self.joint_lineEdit_Value = cmds.textField(self.joint_lineEdit,q=True,tx=True)
        self.nurbs_lineEdit_Value = cmds.textField(self.nurbs_lineEdit,q=True,tx=True)
        self.startExpand_convert_Value = cmds.textField(self.startExpand_convert,q=True,tx=True)
        self.endExpand_convert_Value = cmds.textField(self.endExpand_convert,q=True,tx=True)

    def setConfig(self):
        ''' '''
        cmds.optionMenu(self.calculation_comboBox,e=True,v=self.calculation_comboBox_Value)
        cmds.optionMenu(self.algorithm_comboBox,e=True,v=self.algorithm_comboBox_Value)
        cmds.textField(self.geometryVtx_lineEdit,e=True,tx=self.geometryVtx_lineEdit_Value)
        cmds.textField(self.joint_lineEdit,e=True,tx=self.joint_lineEdit_Value)
        cmds.textField(self.nurbs_lineEdit,e=True,tx=self.nurbs_lineEdit_Value)
        cmds.textField(self.startExpand_convert,e=True,tx=self.startExpand_convert_Value)
        cmds.textField(self.endExpand_convert,e=True,tx=self.endExpand_convert_Value)

    def createUI(self):
        if cmds.window(self.window,q=True,ex=True):
            self.loadConfig()
            cmds.deleteUI(self.window)
        try:
            cmds.windowPref(self.window,r=True)
        except:
            pass
        windowName = cmds.loadUI(uiFile=self.uiPath,verbose=False)
        self.setConfig()
        cmds.window(windowName,e=True,tlb=True,tlc=(200,200),s=False,vis=True)


    def setProgress(self,value):
        cmds.progressBar(self.QProgressBar,e=True,pr=value)

    def geometryVtx_pushButton_cmd(self,*args):
        vtxList = cmds.ls(sl=True,fl=True)
        outStr = ','.join(vtxList)
        cmds.textField(self.geometryVtx_lineEdit,e=True,tx=outStr)

    def joint_pushButton_cmd(self,*args):
        jointList = cmds.ls(sl=True,fl=True,type='joint')
        outStr = ','.join(jointList)
        cmds.textField(self.joint_lineEdit,e=True,tx=outStr)

    def nurbs_pushButton_cmd(self,*args):
        nurbsList = cmds.ls(sl=True,fl=True,tr=True)[0]
        cmds.textField(self.nurbs_lineEdit,e=True,tx=nurbsList)

    def apply_pushButton_cmd(self,*args):
        stTime = time.clock()
        #progress
        self.setProgress( 0 )
        #getArgument
        vtxStr = cmds.textField(self.geometryVtx_lineEdit,q=True,tx=True)
        vtxList = pm.ls(vtxStr.split(','),fl=True)
        jointStr = cmds.textField(self.joint_lineEdit,q=True,tx=True)
        jointList = cmds.ls(jointStr.split(','),fl=True)
        nurbsName = cmds.textField(self.nurbs_lineEdit,q=True,tx=True)
        startExpand = float(cmds.textField(self.startExpand_convert,q=True,tx=True).strip('%'))/100.0
        endExpand = float(cmds.textField(self.endExpand_convert,q=True,tx=True).strip('%'))/100.0
        calculationPattern = cmds.optionMenu(self.calculation_comboBox,q=True,v=True)
        calculationMode = cmds.optionMenu(self.algorithm_comboBox,q=True,v=True)
        #apply
        cmds.select(cl=True)
        self.applyAutoSkinWeight(vtxList,jointList,nurbsName,startExpand,endExpand,calculationPattern,calculationMode)
        cmds.headsUpMessage(u'权重分配完成  耗时  %s  秒'%(time.clock()-stTime))


    def getJointIndexInSkinCluster(self,jointName,skinClusterName):
        searchIndex = cmds.skinCluster(skinClusterName,q=True,inf=True).index(jointName)
        connectIndex = cmds.listAttr('%s.ma'%skinClusterName,m=True)[searchIndex]
        return int(connectIndex.strip('matrix[]'))


    def getSkinWeight(self,skinClusterName,jointName,vtxIndex=''):
        jointIndex = self.getJointIndexInSkinCluster(jointName,skinClusterName)
        if not vtxIndex:
            vtxIndex = '*'
        return cmds.getAttr('%s.wl[%s].w[%s]'%(skinClusterName,vtxIndex,jointIndex))


    # oldVersion
    # def sumSkinWeight(self,fromJointList,toJoint,skinClusterName):
    #     #print fromJointList
    #     #print toJoint
    #     #print skinClusterName
    #     skinClusterName = pm.PyNode(skinClusterName)
    #     toJointIndex = self.getJointIndexInSkinCluster(toJoint,skinClusterName.name())
    #     for fromJointE in fromJointList:
    #         jointIndex = self.getJointIndexInSkinCluster(fromJointE,skinClusterName.name())
    #         for wlE in skinClusterName.wl:
    #             for wE in wlE.w:
    #                 if wE.index() == jointIndex and wE.get():
    #                     wlE.w[toJointIndex].set( wlE.w[toJointIndex].get() + wE.get())
    #                     wE.set(0)


    #newVersion
    def sumSkinWeight(self,fromJointList,toJoint,skinClusterName):
        #print fromJointList
        #print toJoint
        #print skinClusterName
        toJointIndex = self.getJointIndexInSkinCluster(toJoint,skinClusterName)
        sumDataList = []
        if not toJoint in fromJointList:
            fromJointList.append(toJoint)
        #zero weight and sum weightList
        for fromJointE in fromJointList:
            jointIndex = self.getJointIndexInSkinCluster(fromJointE,skinClusterName)
            if sumDataList == []:
                sumDataList = cmds.getAttr('%s.wl[*].w[%s]'%(skinClusterName,jointIndex))
            else:
                vtxSize = len(sumDataList)
                zeroList = [0]*vtxSize
                tempList = cmds.getAttr('%s.wl[*].w[%s]'%(skinClusterName,jointIndex))
                sumDataList = [(sumDataList[i]+tempList[i]) for i in range(vtxSize)]
                cmds.setAttr('%s.wl[*].w[%s]'%(skinClusterName,jointIndex),*zeroList)
        #set
        cmds.setAttr('%s.wl[*].w[%s]'%(skinClusterName,toJointIndex),*sumDataList)
        cmds.refresh(f=True)


    def lockInfluences(self,jointList,skinClusterName):
        ''' jointList中的骨骼会解锁  其他锁定'''
        skinClusterName = pm.PyNode(skinClusterName)
        for jointE in pm.skinCluster(skinClusterName,q=1,inf=1):
            if jointE in jointList:
                jointE.liw.set(0)
            else:
                jointE.liw.set(1)


    def autoSkinWeight(self,startJoint,endJoint,skinedGeo,vtxList,nurbsName,startExpand=0.0,endExpand=0.0,calculationPattern='',calculationMode='defualt',currentProgress=1.0,maxProgress=1.0):
        ''' mainUnit'''
        #currentProgress
        currentProgress = float(currentProgress)
        maxProgress = float(maxProgress)
        vtxSize = float(len(vtxList))
        #start
        startJoint = pm.PyNode(startJoint)
        endJoint = pm.PyNode(endJoint)
        try:
            geoSkinCluster = pm.listHistory(skinedGeo,pdo=1,type='skinCluster')[0].name()
        except:
            pm.error('geometry has no skinCluster history !!!')
        #lockInfluences
        self.lockInfluences([startJoint,endJoint],geoSkinCluster)
        #build
        outReverse = False
        if calculationPattern == 0 or calculationPattern == 'distance':
            #distanceMode
            startTranslateJoint = pm.joint(p = startJoint.getRotatePivot(space = 'world') ,n = 'startTranslateJoint')
            endTranslateJoint = pm.joint(p = endJoint.getRotatePivot(space = 'world') ,n = 'endTranslateJoint')
            pm.joint( startTranslateJoint ,e=1,zso=1,oj='xyz',sao='yup')
            #getMinMax
            minValue = 0.0
            maxValue = endTranslateJoint.tx.get()
        elif calculationPattern == 1 or calculationPattern == 'nurbs':
            #nurbsMode
            nurbsNode = pm.PyNode(nurbsName)
            cposNode = pm.createNode('closestPointOnSurface',n='%s_closestPointOnSurface'%nurbsName)
            nurbsNode.worldSpace[0] >> cposNode.inputSurface
            #getMinMax
            cposNode.ip.set( startJoint.getRotatePivot('world') )
            minValue = cposNode.u.get()
            cposNode.ip.set( endJoint.getRotatePivot('world') )
            maxValue = cposNode.u.get()
            if minValue > maxValue:
                minValue,maxValue = maxValue,minValue
                outReverse = True


        #vtxLoop
        vtxTime = time.clock()

        for vtxIndex,vtx in enumerate(vtxList):
            #ItVtx
            if calculationPattern == 0 or calculationPattern == 'distance':
                #distanceMode
                pointPosition = vtx.getPosition(space = 'world')
                stJoint_inverseMatrix = startTranslateJoint.getMatrix(ws=True).inverse()
                currentValue = (stJoint_inverseMatrix * pointPosition).x

                #endTranslateJoint.setTranslation( space = 'world',vector = vtx.getPosition(space = 'world') )
                #currentValue = endTranslateJoint.tx.get()
            elif calculationPattern == 1 or calculationPattern == 'nurbs':
                #nurbsMode
                cposNode.ip.set( vtx.getPosition(space = 'world') )
                currentValue = cposNode.u.get()
            #common
            medianValue = maxValue-minValue
            minDistance = minValue-(startExpand*medianValue)
            maxDistance = maxValue+(endExpand*medianValue)
            normalizePar = pm.mel.linstep(minDistance,maxDistance,currentValue)
            print (minDistance,maxDistance,currentValue)
            
            if outReverse:
                normalizePar = 1-normalizePar
            if calculationMode == 'linear':
                #linear
                outPercent = normalizePar
            elif calculationMode == 'smooth':
                #smooth
                outPercent = pm.mel.smoothstep(0,1,normalizePar)
            elif calculationMode == 'after':
                #smoothstep after
                normalizePar *= 0.5
                outPercent = pm.mel.smoothstep(0,1,normalizePar)*2
            elif calculationMode == 'before':
                #smoothstep before
                normalizePar *= 0.5
                normalizePar += 0.5
                outPercent = (pm.mel.smoothstep(0,1,normalizePar)-0.5)*2
            elif calculationMode == 'formula':
                #formula
                outPercent = pow(math.cos(math.pi*(normalizePar-1)/2.0),0.5)
            else:
                cmds.error('calculationMode Error !!!')
            #
            # fromValue = cmds.skinPercent( geoSkinCluster , vtx ,q=1,t=startJoint)
            fromValue = self.getSkinWeight(geoSkinCluster,startJoint,vtxIndex)
            if(outPercent != 0 and fromValue != 0):
                cmds.skinPercent(geoSkinCluster,vtx,tv=(endJoint,outPercent*fromValue) )
            #progress
            self.setProgress( (vtxIndex/(vtxSize-1)+currentProgress)/maxProgress * 100 )
            #print vtxIndex,(vtxSize-1)
        print u'%s  vtx耗时'%(time.clock()-vtxTime)
        #clean
        #endTranslateJoint.t.set(maxValue,0,0)
        if calculationPattern == 0 or calculationPattern == 'distance':
            pm.delete(startTranslateJoint,endTranslateJoint)
        elif calculationPattern == 1 or calculationPattern == 'nurbs':
            pm.delete(cposNode)


    def applyAutoSkinWeight(self,vtxList,jointList,nurbsName='',startExpand=0.0,endExpand=0.0,calculationPattern='distance',calculationMode='smooth'):
        #apply
        #vtxList = pm.ls(sl=1,fl=1)
        #jointList = ['L_upper_eyeLidIn_jnt1','L_upper_eyeLid_jnt1','L_upper_eyeLidOut_jnt1']
        listLen = len(jointList)
        geoName = pm.listRelatives(vtxList[0],p=1)[0].getParent().name()
        geoSkinCluster = pm.listHistory(geoName,pdo=True,type='skinCluster')[0].name()
        self.sumSkinWeight(jointList[1:],jointList[0],geoSkinCluster)
        for i in range(listLen-1):
            self.autoSkinWeight(jointList[i],jointList[i+1],geoName,vtxList,nurbsName,startExpand,endExpand,calculationPattern,calculationMode,i,listLen-1)