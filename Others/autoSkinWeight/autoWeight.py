# -*- coding: utf-8 -*-
#autoWeight v2.4
import maya.cmds as cmds
import pymel.core as pm
import math
class autoWeightClass(object):
    ''' 根据函数计算vtx百分比分配skin权重'''
    use=None


    @classmethod
    def showUI(cls,uiPath):
        tempIns = cls(uiPath)
        tempIns.createUI()


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


    def createUI(self):
        if cmds.window(self.window,q=True,ex=True):
            cmds.deleteUI(self.window)
        try:
            cmds.windowPref(self.window,r=True)
        except:
            pass
        windowName = cmds.loadUI(uiFile=self.uiPath,verbose=False)
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
        cmds.headsUpMessage(u'权重分配完成')


    def getJointIndexInSkinCluster(self,jointName,skinClusterName):
        searchIndex = cmds.skinCluster(skinClusterName,q=True,inf=True).index(jointName)
        connectIndex = cmds.listAttr('%s.ma'%skinClusterName,m=True)[searchIndex]
        return int(connectIndex.strip('matrix[]'))


    #oldVersion
    def sumSkinWeight(self,fromJointList,toJoint,skinClusterName):
        #print fromJointList
        #print toJoint
        #print skinClusterName
        skinClusterName = pm.PyNode(skinClusterName)
        toJointIndex = self.getJointIndexInSkinCluster(toJoint,skinClusterName.name())
        for fromJointE in fromJointList:
            jointIndex = self.getJointIndexInSkinCluster(fromJointE,skinClusterName.name())
            for wlE in skinClusterName.wl:
                for wE in wlE.w:
                    if wE.index() == jointIndex and wE.get():
                        wlE.w[toJointIndex].set( wlE.w[toJointIndex].get() + wE.get())
                        wE.set(0)

    # #newVersion
    # def sumSkinWeight(self,fromJointList,toJoint,skinClusterName):
    #     #print fromJointList
    #     #print toJoint
    #     #print skinClusterName
    #     toJointIndex = self.getJointIndexInSkinCluster(toJoint,skinClusterName)
    #     sumDataList = []
    #     if not toJoint in fromJointList:
    #         fromJointList.append(toJoint)
    #     #zero weight and sum weightList
    #     for fromJointE in fromJointList:
    #         jointIndex = self.getJointIndexInSkinCluster(fromJointE,skinClusterName)
    #         if sumDataList == []:
    #             sumDataList = cmds.getAttr('%s.wl[*].w[%s]'%(skinClusterName,jointIndex))
    #         else:
    #             vtxSize = len(sumDataList)
    #             zeroList = [0]*vtxSize
    #             tempList = cmds.getAttr('%s.wl[*].w[%s]'%(skinClusterName,jointIndex))
    #             sumDataList = [(sumDataList[i]+tempList[i]) for i in range(vtxSize)]
    #             cmds.setAttr('%s.wl[*].w[%s]'%(skinClusterName,jointIndex),*zeroList)
    #     #set
    #     cmds.setAttr('%s.wl[*].w[%s]'%(skinClusterName,toJointIndex),*sumDataList)
    #     cmds.refresh(f=True)


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
            geoSkinCluster = pm.listHistory(skinedGeo,pdo=1,type='skinCluster')[0]
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
                startExpand,endExpand = endExpand,startExpand
                outReverse = True
        for vtxIndex,vtx in enumerate(vtxList):
            #ItVtx
            if calculationPattern == 0 or calculationPattern == 'distance':
                #distanceMode
                endTranslateJoint.setTranslation( space = 'world',vector = vtx.getPosition(space = 'world') )
                currentValue = endTranslateJoint.tx.get()
            elif calculationPattern == 1 or calculationPattern == 'nurbs':
                #nurbsMode
                cposNode.ip.set( vtx.getPosition(space = 'world') )
                currentValue = cposNode.u.get()
            #common
            medianValue = maxValue-minValue
            minDistance = minValue-(startExpand*medianValue)
            maxDistance = maxValue+(endExpand*medianValue)
            normalizePar = pm.mel.linstep(minDistance,maxDistance,currentValue)
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

            elif calculationMode == 'CV5_01111':
                #cv
                pointList_5 = [pm.datatypes.Vector(-1,0,0),pm.datatypes.Vector(-0.66666666666,1,0),pm.datatypes.Vector(0,1,0),pm.datatypes.Vector(0.666666666666,1,0),pm.datatypes.Vector(1,1,0)]
                midPointA = (pointList_5[1] + pointList_5[2])*0.5
                midPointC = (pointList_5[2] + pointList_5[3])*0.5
                midPointB = (midPointA + midPointC)*0.5
                pointList_7A = [pointList_5[0],pointList_5[1],midPointA,midPointB]
                pointList_7B = [midPointB,midPointC,pointList_5[3],pointList_5[4]]
                listLength = len(pointList_7A)
                degreeNum = 3
                useList = []
                t = normalizePar
                if t <=0.5:
                    useList = pointList_7A
                    t = t*2.0
                elif t >= 0.5:
                    useList = pointList_7B
                    t = 2*t-1
                outPosition = pm.datatypes.Vector(0,0,0)
                for i2,pE in enumerate(useList):
                    if i2 == 0:
                        outPosition += pE*(1-t)**degreeNum
                    elif i2 == listLength-1:
                        outPosition += pE*t**degreeNum
                    else:
                        outPosition += degreeNum * pE * (1-t)**(listLength-i2-1) * t**i2
                outPercent = outPosition[1]

            elif calculationMode == 'CV5_00111':
                #cv
                pointList_5 = [pm.datatypes.Vector(-1,0,0),pm.datatypes.Vector(-0.66666666666,0,0),pm.datatypes.Vector(0,1,0),pm.datatypes.Vector(0.666666666666,1,0),pm.datatypes.Vector(1,1,0)]
                midPointA = (pointList_5[1] + pointList_5[2])*0.5
                midPointC = (pointList_5[2] + pointList_5[3])*0.5
                midPointB = (midPointA + midPointC)*0.5
                pointList_7A = [pointList_5[0],pointList_5[1],midPointA,midPointB]
                pointList_7B = [midPointB,midPointC,pointList_5[3],pointList_5[4]]
                listLength = len(pointList_7A)
                degreeNum = 3
                useList = []
                t = normalizePar
                if t <=0.5:
                    useList = pointList_7A
                    t = t*2.0
                elif t >= 0.5:
                    useList = pointList_7B
                    t = 2*t-1
                outPosition = pm.datatypes.Vector(0,0,0)
                for i2,pE in enumerate(useList):
                    if i2 == 0:
                        outPosition += pE*(1-t)**degreeNum
                    elif i2 == listLength-1:
                        outPosition += pE*t**degreeNum
                    else:
                        outPosition += degreeNum * pE * (1-t)**(listLength-i2-1) * t**i2
                outPercent = outPosition[1]
            else:
                cmds.error('calculationMode Error !!!')
            #
            fromValue = pm.skinPercent( geoSkinCluster , vtx ,q=1,t=startJoint)
            if(outPercent != 0 and fromValue != 0):
                pm.skinPercent( geoSkinCluster,vtx,tv=(endJoint,outPercent*fromValue) )
            #progress
            self.setProgress( (vtxIndex/(vtxSize-1)+currentProgress)/maxProgress * 100 )
            #print vtxIndex,(vtxSize-1)
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
        geoSkinCluster = pm.listHistory(geoName,pdo=True,type='skinCluster')[0]
        self.sumSkinWeight(jointList[1:],jointList[0],geoSkinCluster.name())
        for i in range(listLen-1):
            self.autoSkinWeight(jointList[i],jointList[i+1],geoName,vtxList,nurbsName,startExpand,endExpand,calculationPattern,calculationMode,i,listLen-1)
            #progress
            #self.setProgress( (i+1)*100/(listLen-1) )
