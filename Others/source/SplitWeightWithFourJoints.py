#coding=utf-8
from maya import cmds
from maya import mel
import sys

class SplitWeightWithFourJoints_UI():

    def __init__(self):
        self.buildUI()
        self.showUI()

    def showUI(self):
        self.ui_refreshHeight()
        cmds.showWindow(self.ui)

    def ui_refreshHeight(self):
        cmds.window(self.ui,e=1,h=1,w=400)

    def buildUI(self):
        self.name = u"边缘权重拆分 v1.2"
        self.ui = "SplitWeightWithFourJoints_Window"

        try:
            cmds.deleteUI(self.ui)
        except:
            pass

        cmds.window(self.ui,t=self.name,w=400)#topLeftCorner
        
        #
        column_main = cmds.columnLayout(adj=1)
        cmds.separator(style='none')
        #
        cmds.rowLayout(numberOfColumns=3,cw=([1,125],[2,175],[3,50]),ct3=['right','both','both'])
        cmds.text(l=u'权重源关节:',align='left') 
        self.srcJoint_Field = cmds.textField(tx='',w=125,en=0) 
        #cmds.button(l=u'加载',c= lambda*args:self.update_inf_field(),en=True) 
        cmds.iconTextButton(style="textOnly",label=u'加载',font='fixedWidthFont',w=50,bgc=[0.75,0.75,0.75],c=lambda*args:self.update_inf_field(),en=True) 
        cmds.setParent('..') 
        #
        cmds.rowLayout(numberOfColumns=4,cw=([1,125],[2,200],[3,15],[4,10]),ct4=['right','both','both','both'])
        cmds.text(l=u'选择/创建UV曲线: ',align='left') 
        self.nurbsGeometry_Option = cmds.optionMenu(label='',changeCommand=lambda*args: self.update_inf_scroll())
        cmds.iconTextButton(style="textOnly",label=u'+',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.convertEdgeToCurve(),en=True)
        cmds.setParent('..')
        #
        cmds.rowLayout(numberOfColumns=4,cw=([1,125],[2,200],[3,15],[4,10]),ct4=['right','both','both','both'])
        cmds.text(l=u'目标关节: ',align='left') 
        self.dstJoints_Option = cmds.optionMenu(label='',changeCommand=lambda*args: self.update_inf_scroll())
        cmds.iconTextButton(style="textOnly",label=u'+',font='fixedWidthFont',bgc=[0.75,0.75,0.75],w=25,h=20,c= lambda *args:self.createJointSet(),en=True)
        cmds.setParent('..')
        #
        cmds.text(l=u' 关节列表: ',align='left',w=200)
        cmds.separator(style='none',h=5)
        cmds.rowLayout(numberOfColumns=3,cw=([1,5],[2,400],[3,5]),ct3=['right','both','left'])
        cmds.separator(style='none')
        cmds.setParent('..')
        self.dstJoints_Scroll = cmds.textScrollList(allowMultiSelection=1)
        #
        self.update_nurbsGeometry_Option() 
        self.update_srcInf_Option()
        self.update_inf_scroll()
        
        #
        advanced_option_frame = cmds.frameLayout(label=u"局部控制",hlc=[0.3,0.3,0.3],bgc=[0.35,0.35,0.35],
                                    collapseCommand=lambda *args:self.ui_refreshHeight(),
                                    cll=True,cl=True)
        self.AdvUI(advanced_option_frame)
        cmds.setParent('..')
        
        #
        quickly_select_frame = cmds.frameLayout(label=u"快速选点",hlc=[0.3,0.3,0.3],bgc=[0.35,0.35,0.35],
                                    collapseCommand=lambda *args:self.ui_refreshHeight(),
                                    cll=True,cl=False)
        self.VtxUI(quickly_select_frame)
        cmds.setParent('..')
        #
        cmds.separator( style='none',h=3)
        #
        cmds.rowLayout(numberOfColumns=2,cw=([1,100],[2,300]),ct2=['right','left']) 
        cmds.iconTextButton(style="textOnly",label=u'创建分型节点',font='fixedWidthFont',bgc=[0.325,0.325,0.325],
                            w=100,h=50,c= lambda *args:self.crtFractalNode(),en=True) 
        cmds.iconTextButton(style="textOnly",label=u'分解权重',font='fixedWidthFont',bgc=[0.3,0.0,0.0],
                            w=300,h=50,c= lambda *args:self.setWeights(),en=True) 
        cmds.setParent('..')
        cmds.text(l=" @Pan ",h=15,align='right',bgc=[0.1,0.1,0.1]) 

    def AdvUI(self,Parent):
        #
        cmds.separator( style='double',h=10) 
        cmds.rowLayout(numberOfColumns=2,cw=([1,255],[2,100]),ct2=['both','left'],adj=True,ad1=True) 
        self.element_uvalue_floatSlider = cmds.floatSliderGrp('jointScaleFloatSlider',field=1,pre=5,
                                            min=0.00,max = 1.00,fmn=0.01,fmx=100.0,
                                            v = 0.5,
                                            dc=lambda *args:'',
                                            cc=lambda *args:self.setWeights(),
                                            en=True) 
        cmds.iconTextButton(style="textOnly",label=u'获取目标元素UV值',bgc=[0.75,0.75,0.75],c=lambda *args:self.getSelVtxUvalue(),en=True) 
        cmds.setParent('..') 
        #
        self.uValue_blend_floatSlider = cmds.floatSliderGrp('jointScaleFloatSlider',field=1,pre=5,
                                            min=0.00,max = 1.00,fmn=0.01,fmx=100.0,
                                            v = 0.0,
                                            dc=lambda *args:'',
                                            cc=lambda *args:self.setWeights(),
                                            en=True) 
           
        cmds.separator( style='double',h=10)
        #
        cmds.setParent(Parent) 

    def VtxUI(self,Parent):
        #
        cmds.separator( style='double',h=10) 
        #
        cmds.rowLayout(numberOfColumns=3,cw=([1,125],[2,125],[3,125]),ct3=['right','both','left']) 
        cmds.iconTextButton(style="textOnly",label=u'添加边界',font='fixedWidthFont',w=100,bgc=[0.75,0.75,0.75],c=lambda *args:self.create_edge_set(),en=True) 
        cmds.iconTextButton(style="textOnly",label=u'查看边界',font='fixedWidthFont',w=100,bgc=[0.75,0.75,0.75],c=lambda *args:self.select_all_vtxEdge(),en=True) 
        cmds.iconTextButton(style="textOnly",label=u'快速选择',font='fixedWidthFont',w=100,bgc=[0.75,0.75,0.75],c=lambda *args:self.getLoopVtxs(),en=True) 
        cmds.setParent('..') 
        #
        cmds.separator( style='double',h=10) 
        #
        cmds.setParent(Parent) 

    #
    def convertEdgeToCurve(self): 
        sel = cmds.ls(sl=True,fl=True) 
        crv=sel[0] 
        if '.e[' in sel[0]: 
            crv = mel.eval('polyToCurve -form 2 -degree 1 -conformToSmoothMeshPreview 0')[0] 
            for node in crv: 
                if 'polyEdgeToCurve'  in node: 
                    cmds.delete(node) 
        if not cmds.objExists('splitWeight_Curve_Set'):
            cmds.select(cl=True)
            cmds.sets(n='splitWeight_Curve_Set')
        cmds.sets(crv,e=True,forceElement='splitWeight_Curve_Set')
        if not cmds.objExists('splitWeight_Set'):
            cmds.select(cl=True)
            cmds.sets(n='splitWeight_Set')
        cmds.sets('splitWeight_Curve_Set',e=True,forceElement='splitWeight_Set')
        self.update_nurbsGeometry_Option()
        return crv
    #
    def createJointSet(self):
        listSet = cmds.ls('Inf_List_*_Set')
        if listSet:
            n = len(listSet)
        else:
            n=0
        Set_Add = cmds.sets(n='Inf_List_%d_Set'%(n+1))
        if not cmds.objExists('splitWeight_Inf_Set'):
            cmds.select(cl=True)
            cmds.sets(n='splitWeight_Inf_Set')
        cmds.sets(Set_Add,e=True,fe='splitWeight_Inf_Set')
        if not cmds.objExists('splitWeight_Set'):
            cmds.select(cl=True)
            cmds.sets(n='splitWeight_Set')
        cmds.sets('splitWeight_Inf_Set',e=True,forceElement='splitWeight_Set')
        self.update_srcInf_Option()
    #
    def update_nurbsGeometry_Option(self):
        option_menu = self.nurbsGeometry_Option

        menuList = []
        menuItems = cmds.optionMenu(option_menu,q=True,ill=True)
        
        activate = None
        if menuItems:
            activate = cmds.optionMenu(option_menu,v=True,q=True)
            for item in menuItems:
                label = cmds.menuItem(item,label=True,q=True)
                menuList.append(label)
            cmds.deleteUI(menuItems)
        #
        if cmds.objExists('splitWeight_Curve_Set'):
            cmds.select('splitWeight_Curve_Set',r=True) 
        List = cmds.ls(sl=True) 
        if List:
            for item in List:
                cmds.setParent(option_menu,menu=True)
                cmds.menuItem(label=item,p=option_menu)
                if not item in menuList:
                    try:
                        activate = item
                    except:
                        activate = None

            if not activate == None:
                cmds.optionMenu(option_menu,v=activate,e=True)
    #
    def update_srcInf_Option(self):
        option_menu = self.dstJoints_Option 

        menuList = []
        menuItems = cmds.optionMenu(option_menu,q=True,ill=True)
        
        activate = None
        if menuItems:
            activate = cmds.optionMenu(option_menu,v=True,q=True)
            for item in menuItems:
                label = cmds.menuItem(item,label=True,q=True)
                menuList.append(label)
            cmds.deleteUI(menuItems)
        #
        List = cmds.ls('Inf_List_*_Set')
        if List:
            for item in List:
                cmds.setParent(option_menu,menu=True)
                cmds.menuItem(label=item,p=option_menu)
                if not item in menuList:
                    try:
                        activate = item
                    except:
                        activate = None

            if not activate == None:
                cmds.optionMenu(option_menu,v=activate,e=True)
        #
        menuItems = cmds.optionMenu(option_menu,q=True,ill=True)
        if not menuItems == None:
            self.update_inf_scroll()
    #
    def update_inf_scroll(self):
        option_menu = self.dstJoints_Option
        inf_scroll = self.dstJoints_Scroll
        cmds.textScrollList(inf_scroll,e=True,removeAll=True)
        set = cmds.optionMenu(option_menu,q=True,v=True)
        
        if not set: 
            return 
            
        list = cmds.sets(set,q=True) 
        if list:
            for i in list:
                cmds.textScrollList(inf_scroll,e=True,append=i,deselectAll=True)
            cmds.select(list,r=True)
    #
    def update_inf_field(self):
        Inf = None
        try:
            Inf = cmds.ls(sl=True)[0] 
        except:
            Inf = ''
        inf_field = self.srcJoint_Field
        cmds.textField(inf_field,e=True,text=Inf) 

    def qInfo(self):
        nurbsGeometry = cmds.optionMenu(self.nurbsGeometry_Option,q=True,v=True) 
        srcJoint = cmds.textField(self.srcJoint_Field,q=True,tx=True) 
        srcJoint_set = cmds.optionMenu(self.dstJoints_Option,q=True,v=True) 
        dstJoints = cmds.sets(srcJoint_set,q=True) 
        percentValue = cmds.floatSliderGrp(self.element_uvalue_floatSlider,q=True,v=True)
        blendValue = cmds.floatSliderGrp(self.uValue_blend_floatSlider,q=True,v=True)
        return nurbsGeometry,srcJoint,dstJoints,percentValue,blendValue

    def setWeights(self):
        nurbsGeometry,srcJoint,dstJoints,percentValue,blendValue = self.qInfo() 
        SplitWeightWithFourJoints(srcJoint,dstJoints,nurbsGeometry,percentValue,blendValue).setWeights()

        sel = cmds.ls(sl=True) 
        fitLoc = 'Flag_Locator'
        if not cmds.objExists(fitLoc):cmds.spaceLocator(n=fitLoc) 
        SplitWeightWithFourJoints(srcJoint,dstJoints,nurbsGeometry,percentValue,blendValue).move_to_nurbsGeometry(fitLoc,nurbsGeometry,percentValue,True) 
        cmds.select(sel,r=True) 

    #
    def crtFractalNode(self):
        nurbsGeometry,srcJoint,dstJoints,percentValue,blendValue = self.qInfo() 
        SplitWeightWithFourJoints(srcJoint,dstJoints,nurbsGeometry,percentValue,blendValue).crtFractalNode() 

    def getSelVtxUvalue(self):
        #
        Sel=cmds.ls(sl=True,fl=1) 
        Vtxs=[] 
        for i in Sel: 
            if '.vtx[' in i: 
                Vtxs.append(i) 

        nurbsGeometry,srcJoint,dstJoints,percentValue,blendValue = self.qInfo() 
        SplitWeightWithFourJoints(srcJoint,dstJoints,nurbsGeometry,percentValue,blendValue).setWeights() 
        uValue = SplitWeightWithFourJoints(srcJoint,dstJoints,nurbsGeometry,percentValue,blendValue).analyseParameter(Vtxs[0],nurbsGeometry) 
        cmds.floatSliderGrp(self.element_uvalue_floatSlider,e=True,v=uValue) 
        cmds.select(Sel,r=True)

    def select_all_vtxEdge(self):
        Set='splitWeight_Edge_Set'
        if cmds.objExists(Set):
            cmds.select(Set,r=True)#,ne=True) 

    #create_edge_set()
    def create_edge_set(self):
        #
        Sel=cmds.ls(sl=True)
        #
        Big_Set='splitWeight_Edge_Set'
        if not cmds.objExists(Big_Set):
            cmds.select(cl=True)
            cmds.sets(n=Big_Set)
        if not cmds.objExists('splitWeight_Set'):
            cmds.select(cl=True)
            cmds.sets(n='splitWeight_Set')
        cmds.sets('splitWeight_Edge_Set',e=True,forceElement='splitWeight_Set')

        Sets = cmds.ls('Edge_*_Set')
        if Sets:
            n = len(Sets)
        else:
            n = 0

        Set_Name = 'Edge_%d_Set'%(n+1)
        if cmds.objExists(Set_Name):
            sys.stdout.write("//Result: The set is already in scene.\n") 
            #selectMember([Set_Name])
            return

        if Sel:
            cmds.select(Sel,r=True)
            S_Add = cmds.sets(n=Set_Name)
            cmds.sets(S_Add,e=True,fe=Big_Set)
        else:
            sys.stdout.write("//Result: please select something.\n") 

    #选择一个区域的顶点
    #getLoopVtx(['M_Head_base.vtx[1424]']) 
    def getLoopVtx(self,V=[],V_Edge=[],I=25):
        if I==25:
            V_Edge=[]
        #
        edge_sets = cmds.ls('Edge_*_Set')
        vtxs = []
        for set in edge_sets:
            vtxs = vtxs + cmds.sets(set,q=True)
        vtxs = cmds.ls(vtxs,fl=True)
        #
        if I>0:
            sys.stdout.write("//Result: Need "+str(I)+" more times.\n")
            cmds.select(V,r=True)
            cmds.polySelectConstraint(pp=True,t=0x0001)
            #cmds.GrowLoopPolygonSelectionRegion()
            cmds.select(V,d=True)
            #
            V_Filter = []
            V_Extend = cmds.ls(sl=True,fl=True)
            for v in V_Extend:
                if v in vtxs:
                    V_Edge.append(v)
                    continue
                V_Filter.append(v)
            
            V = V + V_Filter
            return self.getLoopVtx(V,V_Edge,I-1) 
        else:
            V = V + V_Edge
            return V

    #选择多个区域的顶点
    #getLoopVtxs() 
    def getLoopVtxs(self):
        Vtxs = cmds.ls(sl=True,fl=True)
        if len(Vtxs)>10: 
            sys.stdout.write('//Result: 不要选择太多的顶点(超过十个视为误操作).') 
            return 
        L = []
        for v in Vtxs:
            L = L + self.getLoopVtx([v],[]) 
        cmds.select(L,r=True)
        return L







class SplitWeightWithFourJoints:
    def __init__(self,srcJoint,dstJoints,nurbsGeometry,percentValue,blendValue): 
        self.srcJoint = srcJoint 
        self.dstJoints = dstJoints 
        self.nurbsGeometry = nurbsGeometry 
        self.percentValue = percentValue
        self.blendValue = blendValue
        self.fractalNode='splitWeight_node'

    # 查询物体关联的蒙皮节点 
    def qSkinCluster(self,Elements=None): 
        Selected = cmds.ls(sl=True,fl=True) 
        if Elements == None: 
            Elements = Selected 
        if not len(Elements): 
            return 
        History = cmds.listHistory(Elements) 
        SkinNode = None 
        for node in History: 
            if cmds.nodeType(node)=='skinCluster': 
                SkinNode = node 
                break 
        return (SkinNode) 

    # 创建一个驱动关键帧节点用来分解权重; 
    def crtFractalNode(self,fractalNode=None,Peak=0.667): 
        if fractalNode == None:
            fractalNode = self.fractalNode
        if not cmds.objExists(fractalNode): 
            fractalNode = cmds.createNode('animCurveUU',n=fractalNode) 
            cmds.setKeyframe(fractalNode,f=-1, value=0,itt='flat',ott='flat') 
            cmds.setKeyframe(fractalNode,f=3,  value=0,itt='flat',ott='flat') 
            cmds.setKeyframe(fractalNode,f=-0, value=(1-Peak)/2.0,itt='clamped',ott='clamped') 
            cmds.setKeyframe(fractalNode,f=2, value=(1-Peak)/2.0,itt='clamped',ott='clamped') 
            cmds.setKeyframe(fractalNode,f=1, value=Peak,itt='flat',ott='flat') 
        return fractalNode 

    # 根据点的UV值查询曲线按照最多四骨骼拆分权重;
    def split_weight(self,Param,KeyFrameNode,Peak=0.667):
        if not cmds.objExists(KeyFrameNode):
            self.key_frame_node(KeyFrameNode,Peak) 
        cmds.setAttr('%s.input'%KeyFrameNode,-Param) 
        W1 = cmds.getAttr('%s.output'%KeyFrameNode) 
        cmds.setAttr('%s.input'%KeyFrameNode,1-Param) 
        W2 = cmds.getAttr('%s.output'%KeyFrameNode) 
        cmds.setAttr('%s.input'%KeyFrameNode,Param) 
        W3 = cmds.getAttr('%s.output'%KeyFrameNode) 
        cmds.setAttr('%s.input'%KeyFrameNode,Param-1) 
        W4 = cmds.getAttr('%s.output'%KeyFrameNode) 
        '''
        W1 = float('%.6f' % W1)'''
        W1 = round(W1,6)
        W2 = round(W2,6)
        W3 = round(W3,6)
        W4 = round(W4,6)
        return [W1,W2,W3,W4]

    # analyseUValue('M_Head_base.vtx[204]','polyToCurve1')
    def analyseUValue(self,Element):
        nurbsGeometry = self.nurbsGeometry
        percentValue = self.percentValue
        blendValue = self.blendValue 
        uValue = self.analyseParameter(Element,nurbsGeometry,True) 
        uValue = uValue*(1-blendValue) + percentValue*blendValue
        return uValue 

    #获取物体相对于一个曲线的uValue值
    #Param = analyseParameter('M_Head_base.vtx[410]','loftedSurface1')
    #Param = analyseParameter('M_Head_base.vtx[410]','PolyEdges_Convert_1_Curve')
    def analyseParameter(self,Element,nurbsGeometry,FractionMode=True):
        SkinCluster = self.qSkinCluster(Element) 
        try: 
            cmds.setAttr('%s.envelope'% SkinCluster, 0) 
        except: 
            pass 
        #
        nurbsGeometryShape = cmds.listRelatives(nurbsGeometry,s=True)[0] 
        uValue = None
        if cmds.nodeType(nurbsGeometryShape) == 'nurbsCurve':
            CurveShape = nurbsGeometryShape
            # 获取uValue(0-#)
            NearestNode = cmds.createNode('nearestPointOnCurve')
            cmds.connectAttr("%s.worldSpace[0]"%CurveShape, "%s.inputCurve"%NearestNode)
            Pos = cmds.xform(Element,q=True,ws=True,t=True)
            cmds.setAttr("%s.inPosition"%NearestNode,Pos[0],Pos[1],Pos[2],type='float3')
            uValue = cmds.getAttr("%s.parameter"%NearestNode) 
            cmds.delete(NearestNode)
            # 截取弧长
            DimensionNode = cmds.createNode('arcLengthDimension')
            cmds.connectAttr('%s.worldSpace[0]'%CurveShape,'%s.nurbsGeometry'%DimensionNode)
            cmds.setAttr('%s.uParamValue'%DimensionNode,uValue)
            ArcLen = cmds.getAttr('%s.arcLength'%DimensionNode)
            try:
                cmds.delete(DimensionNode)
                cmds.delete(DimensionNode.replace('Shape',''))
            except:
                pass
            # 获取曲线总长
            CurveInfoNode = cmds.createNode('curveInfo')
            cmds.connectAttr('%s.worldSpace[0]'%CurveShape,'%s.inputCurve'%CurveInfoNode)
            CurveLen = cmds.getAttr('%s.arcLength'%CurveInfoNode)
            cmds.delete(CurveInfoNode)
            #计算uValue(0-1)
            Parameter = ArcLen/CurveLen 
            if FractionMode == True:
                uValue = Parameter 
        elif cmds.nodeType(nurbsGeometryShape) == 'nurbsSurface':
            SurfaceShape = nurbsGeometryShape
            NearestNode = cmds.createNode('closestPointOnSurface')
            cmds.connectAttr("%s.worldSpace[0]"%SurfaceShape, "%s.inputSurface"%NearestNode)
            Pos = cmds.xform(Element,q=True,ws=True,t=True)
            cmds.setAttr("%s.inPosition"%NearestNode,Pos[0],Pos[1],Pos[2],type='float3')
            uValue = cmds.getAttr("%s.parameterU"%NearestNode)
            cmds.delete(NearestNode)
            # 截取弧长
            DimensionNode = cmds.createNode('arcLengthDimension')
            cmds.connectAttr('%s.worldSpace[0]'%SurfaceShape,'%s.nurbsGeometry'%DimensionNode)
            cmds.setAttr('%s.uParamValue'%DimensionNode,uValue)
            ArcLen = cmds.getAttr('%s.arcLength'%DimensionNode)
            try:
                cmds.delete(DimensionNode)
                cmds.delete(DimensionNode.replace('Shape',''))
            except:
                pass
            # 获取曲线总长
            SpansU = cmds.getAttr('%s.spansU'%SurfaceShape)
            DimensionNode = cmds.createNode('arcLengthDimension')
            cmds.connectAttr('%s.worldSpace[0]'%SurfaceShape,'%s.nurbsGeometry'%DimensionNode)
            cmds.setAttr('%s.uParamValue'%DimensionNode,SpansU)
            CurveLen = cmds.getAttr('%s.arcLength'%DimensionNode)
            try:
                cmds.delete(DimensionNode)
                cmds.delete(DimensionNode.replace('Shape',''))
            except:
                pass
            #计算uValue(0-1)
            Parameter = ArcLen/CurveLen 
            if FractionMode == True: 
                uValue = Parameter 
        try: 
            cmds.setAttr('%s.envelope'% SkinCluster, 1) 
        except: 
            pass 
        #print (uValue) 
        return uValue 

    # 查询骨骼对应曲线的uValue值,并创建loc记录uValue值
    # crtJointsDummy('L_UpLip1_A_jnt','polyToCurve1')
    def crtJointsDummy(self,Joint,nurbsGeometry):
        param = self.analyseParameter(Joint,nurbsGeometry,True) 
        #
        location_node = '%s_uLocation'%(Joint) 
        '''
        if cmds.objExists(location_node):
            param = self.analyseParameter(location_node,nurbsGeometry,True) 
        else: 
            location_node = cmds.createNode('transform',n=location_node)
            cmds.setAttr('%s.displayRotatePivot'%location_node,True) 
            cmds.addAttr(location_node,ln="uValue",keyable=True,at='double',dv=0) 
            cmds.setAttr('%s.uValue'%location_node,param) 
            #cmds.matchTransform(location_node,Joint) 
            self.move_to_nurbsGeometry(location_node,nurbsGeometry,param,True)'''
        return param 

    def move_to_nurbsGeometry(self,fitNode,nurbsGeometry,percentValue=0,FractionMode=False):
        nurbsGeometryShape = cmds.listRelatives(nurbsGeometry,s=True)[0] 
        Pos = [] 
        if cmds.nodeType(nurbsGeometryShape) == 'nurbsCurve':
            PinNode = cmds.createNode('motionPath') 
            cmds.setAttr (PinNode+".fractionMode",FractionMode) 
            cmds.setAttr (PinNode+".uValue",percentValue) 
            cmds.connectAttr(nurbsGeometryShape+".worldSpace", PinNode+".geometryPath") 
            Pos = cmds.getAttr(PinNode+".allCoordinates")[0] 
            cmds.delete(PinNode) 
            
        elif cmds.nodeType(nurbsGeometryShape) == 'nurbsSurface':
            PinNode = cmds.createNode('follicle') 
            cmds.connectAttr(nurbsGeometryShape+".local", PinNode+".inputSurface") 
            cmds.connectAttr(nurbsGeometryShape+".worldMatrix", PinNode+".inputWorldMatrix") 
            cmds.setAttr (PinNode+".parameterV",0) 
            cmds.setAttr (PinNode+".parameterU",percentValue) 
            Pos = cmds.getAttr(PinNode+".outTranslate")[0] 
            cmds.delete(PinNode) 
        cmds.xform(fitNode,t=Pos,ws=True) 

    # 把参与分解权重的骨骼和对应的uValue生成字典
    def dictJointsParameter(self): 
        nurbsGeometry = self.nurbsGeometry
        Joints = self.dstJoints
        dic ={} 
        for jj in Joints: 
            uValue = self.crtJointsDummy(jj,nurbsGeometry) 
            dic[jj] = uValue 
        return dic 

    '''
    Vtx = cmds.ls(sl=True,fl=True)[0]
    print analyseInflunce(Vtx,Curve,Joints,Dict)'''
    # 查询一个点对应的骨骼列表
    def analyseInflunce(self,Vtx,DICT=None): 
        if DICT == None:
            DICT = self.dictJointsParameter() 
        uValue = self.analyseUValue(Vtx) 
        #
        DICT_COPY = DICT.copy() 
        DICT_COPY['vtx'] = uValue 
        List_D2 = sorted(DICT_COPY.items(), key=lambda kv: kv[1]) 
        IDs = List_D2.index(('vtx',uValue)) 
        #
        List_D = sorted(DICT.items(), key=lambda kv: kv[1]) 
        Param = None 
        if IDs == len(List_D):
            Param = 1
        elif IDs == 0:
            Param = 0
        else:
            Param = (uValue-List_D[IDs-1][1])/(List_D[IDs][1]-List_D[IDs-1][1]) 
        #
        K = IDs-1
        LJ=[] 
        for i in range(-1,3,1):
            ii = K + i
            try:
                if ii < 0:
                    LJ.append(None) 
                else:
                    LJ.append(List_D[ii][0]) 
            except:
                LJ.append(None) 
        #
        return Param,LJ
    #
    def recomputeWeight(self,Vtx,Weight_KeyFrame_Node,DICT): 
        Param,InfArray = self.analyseInflunce(Vtx,DICT) 
        Weights = self.split_weight(Param,Weight_KeyFrame_Node) 
        InfArray,Weights = self.listFilter(InfArray,Weights) 
        return InfArray,Weights 
    #
    def listFilter(self,A,B):
        N = len(A)
        TempWeight=0.0
        for i in range(0,N,1):
            if A[i] == None:
                TempWeight += B[i]
                B[i] = None
            elif not A[i] == None:
                B[i] += TempWeight
                break
        #
        TempWeight=0.0
        for i in range(N,0,-1):
            ii = i-1
            if A[ii] == None:
                TempWeight += B[ii]
                B[ii] = None
            elif not A[ii] == None:
                B[ii] += TempWeight
                break
                
        C=[]
        D=[]        
        for i in A:
            if not i == None:
                C.append(i)
        for i in B:
            if not i == None:
                D.append(i)
        return (C,D)  

    #
    def setWeight(self,vtx,Weight_KeyFrame_Node,DICT): 

        Joints = self.dstJoints 
        SourceInfluence = self.srcJoint 

        #分析一个点的uValue,骨骼列表和权重列表 
        InfArray,Weights = self.recomputeWeight(vtx,Weight_KeyFrame_Node,DICT) 

        #根据点的名称获取网格名称和蒙皮节点名称 
        SkinNode = self.qSkinCluster(vtx) 
        
        #锁定所有蒙皮骨骼 
        allInf = cmds.skinCluster(SkinNode,q=True,wi=True) 
        for jnt in allInf: 
            cmds.setAttr("%s.liw"%(jnt),1) 

        #对一个点的权重进行分析,加和所有的骨骼权重 
        LJ = [] 
        LW = [] 
        weightScale = 1.0 
        cobinWeit = 0.0 
        #
        IL = Joints 
        if (SourceInfluence not in IL) and ( SourceInfluence != ''): 
            IL.append(SourceInfluence) 
        #
        for inf in IL:
            cmds.setAttr("%s.liw"%(inf),0) 
            inf_weight_value = cmds.skinPercent(SkinNode,vtx,t=inf,q=True) 
            cobinWeit = cobinWeit + inf_weight_value 

        #根据当前可供分配的总的权重算一个百分比,平摊到计算结果中去
        weightScale = cobinWeit/1.0  
        for i in range(len(Weights)):
            Weights[i] = Weights[i]*weightScale
        L=[] 
        for i in range(len(Weights)):
            L.append([InfArray[i],Weights[i]]) 
        print (u'"%s"-可分配权重-%f'% (vtx,weightScale)) 
        print (InfArray) 
        print (Weights) 

        #进行分配权重
        cmds.skinPercent( SkinNode, vtx, transformValue=L) 
    #
    def setWeights(self): 
        #把选中顶点放进列表
        Sel=cmds.ls(sl=True,fl=1) 
        Vtxs=[]
        for i in Sel:
            if '.vtx[' in i:
                Vtxs.append(i) 

        #创建分型用动画曲线节点
        Fractal_Node = self.fractalNode
        isDel = False
        if not cmds.objExists(Fractal_Node):
            isDel = True
            Fractal_Node = self.crtFractalNode(Fractal_Node) 
        #获取骨骼和对应的uValue形成的字典
        DICT = self.dictJointsParameter() 
        #
        for vtx in Vtxs:
            self.setWeight(vtx,Fractal_Node,DICT) 

        #删除动画曲线节点
        if isDel == True:
            cmds.delete(Fractal_Node) 
        cmds.select(Vtxs,r=True)
        sys.stdout.write(u"//Result: 分割权重完成.\n") 
        return

'''
import os
f = 'E:/USync/UShelves/scripts/tools/权重计算脚本/4骨骼分配权重方案0906.py'
if os.path.isfile(f):
    execfile(f)'''
