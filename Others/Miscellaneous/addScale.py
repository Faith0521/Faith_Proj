'''
Copyright (c) 2021 Roman Gar-Nevsky
so_dareg@bk.ru

addScale v1.1

Last fix: 14.04.2021

- fix start deformations
- add rotate 

#copy script to script folder

#import addScale as addScale
#reload(addScale)
#addScale.utilities().UI()

'''

import maya.cmds as mc

class utilities():

    def __init__(self):

        self.attrsS = [".sx", ".sy", ".sz"]
        self.attrsR = [".rx", ".ry", ".rz"]
        
    def UI(self):

        # create a window
        window_name = "toolsUtilitiesUI"
        if mc.window(window_name, ex = True):
            mc.deleteUI(window_name)
        window = mc.window(window_name, t = "addScale",w= 200, h = 130, s = False, rtf = True)

        # create a main layout
        mainLayout = mc.formLayout(w = 200)

        # create an axes layout
        axesLayout = mc.columnLayout(adj = True)
        mc.separator(h = 7, w = 200, st = "singleDash")
        mc.text(l = "     Choose the axis of influence", fn = 'plainLabelFont', al = "center")
        mc.separator(h = 7, w = 200, st = "singleDash")
        
        self.switchSc_field = mc.checkBoxGrp(ncb = 1, l = "Scale:  ", l1 = "All", cw = [(1, 50)], v1 = True, cc = self.switchSc)
        mc.separator(h = 7, st = "none")
        
        self.attrsSc_field = mc.checkBoxGrp(ncb = 3, l = "", la3 = ["X", "Y", "Z"], cw = [(1, 50), (2, 50), (3, 50)], v1 = False, v2 = False, v3 = False, cc = self.switchScAll)
        mc.separator(h = 7, st = "none")
        
        self.switchRot_field = mc.checkBoxGrp(ncb = 1, l = "Rotate:  ", l1 = "All", cw = [(1, 50)], v1 = True, cc = self.switchR)
        mc.separator(h = 7, st = "none")
        
        self.attrsRot_field = mc.checkBoxGrp(ncb = 3, l = "", la3 = ["X", "Y", "Z"], cw = [(1, 50), (2, 50), (3, 50)], v1 = False, v2 = False, v3 = False, cc = self.switchRotAll)
        
        mc.columnLayout(adjustableColumn=True )
        mc.separator(h = 7, st = "none")
        mc.button(label='1. SELECT CONTROL', ann = 'to create control attributes', bgc = [0.45,0.59,0.51], command=self.main )
        mc.separator(h = 3, st = "none")
        mc.button(label='2. SELECT OBJECT and PUSH', ann = 'select target', bgc = [0.81,0.77,0.51], command=self.bone )
        
        mc.setParent("..")
       
        # show a window
        mc.showWindow(window)

    # scale
    
    def switchSc(self, *args):

        switchS = mc.checkBoxGrp(self.switchSc_field, q = True, v1 = True)
        
        if switchS:
            
            mc.checkBoxGrp(self.attrsSc_field, e = True, v1 = False, v2 = False, v3 = False)
            
    def switchR(self, *args):

        switchRot = mc.checkBoxGrp(self.switchRot_field, q = True, v1 = True)
        
        if switchRot:
            
            mc.checkBoxGrp(self.attrsRot_field, e = True, v1 = False, v2 = False, v3 = False)
   
    def switchScAll(self, *args):

        attrsSx = mc.checkBoxGrp(self.attrsSc_field, q = True, v1 = True)
        attrsSy = mc.checkBoxGrp(self.attrsSc_field, q = True, v2 = True)
        attrsSz = mc.checkBoxGrp(self.attrsSc_field, q = True, v3 = True)
        
                
        if (attrsSx + attrsSy + attrsSz) > 0:
            
            mc.checkBoxGrp(self.switchSc_field, e = True, v1 = False)
            
        else:
            
            mc.checkBoxGrp(self.switchSc_field, e = True, v1 = True)
            
                    
    def switchRotAll(self, *args):

                
        attrsRx = mc.checkBoxGrp(self.attrsRot_field, q = True, v1 = True)
        attrsRy = mc.checkBoxGrp(self.attrsRot_field, q = True, v2 = True)
        attrsRz = mc.checkBoxGrp(self.attrsRot_field, q = True, v3 = True)
                    
        if (attrsRx + attrsRy + attrsRz) > 0:
            
            mc.checkBoxGrp(self.switchRot_field, e = True, v1 = False)
            
        else:
            
            mc.checkBoxGrp(self.switchRot_field, e = True, v1 = True)
            

    # attributes state
    
    def attrsState(self):

        self.attrsScAll = mc.checkBoxGrp(self.switchSc_field, q = True, v1 = True)
         
        self.attrsSx = mc.checkBoxGrp(self.attrsSc_field, q = True, v1 = True) + self.attrsScAll
        self.attrsSy = mc.checkBoxGrp(self.attrsSc_field, q = True, v2 = True) + self.attrsScAll
        self.attrsSz = mc.checkBoxGrp(self.attrsSc_field, q = True, v3 = True) + self.attrsScAll

        self.valuesS = [self.attrsSx, self.attrsSy, self.attrsSz, self.attrsScAll]
        
        self.chS = [self.attrsSx + self.attrsSy + self.attrsSz]
        
        
        self.attrsRotAll = mc.checkBoxGrp(self.switchRot_field, q = True, v1 = True)
         
        self.attrsRx = mc.checkBoxGrp(self.attrsRot_field, q = True, v1 = True) + self.attrsRotAll
        self.attrsRy = mc.checkBoxGrp(self.attrsRot_field, q = True, v2 = True) + self.attrsRotAll
        self.attrsRz = mc.checkBoxGrp(self.attrsRot_field, q = True, v3 = True) + self.attrsRotAll

        self.valuesR = [self.attrsRx, self.attrsRy, self.attrsRz, self.attrsRotAll]
        
        self.chR = [self.attrsRx + self.attrsRy + self.attrsRz]
        
        
    def main(self, *args):
    
        self.ctrl = mc.ls(sl = True)
        
        self.attrsState()
                
        if len(self.ctrl) == 1:
            
            if self.chS[0] != 0:
                
                print self.chS
                
                mc.addAttr(longName='volumeScale', attributeType = 'float' , min = -1.0, k = True)
                mc.addAttr(longName='falloffScale', attributeType = 'float' , min = 0.0, k = True)
                mc.addAttr(longName='positionScale', attributeType = 'float' , min = -1.0, k = True)
                
                
                
            if self.chR[0] != 0:
                
                print self.chR
                
                mc.addAttr(longName='angle', attributeType = 'float', k = True)
                mc.addAttr(longName='falloffRotation', attributeType = 'float' , min = 0.0, k = True)
                mc.addAttr(longName='positionRotation', attributeType = 'float', min = -1.0, k = True)
            
            mc.select(d=True)
                
        else:
                
            mc.warning('Select control!')              
    
    #rig

    def bone(self, *args):
        
        self.attrsState()
        
        self.jj = mc.ls(sl=True)
                   
        for a in range (len(self.jj)):
                        
            if self.chS[0] != 0:
                
                self.MDF = mc.createNode('multiplyDivide', name = self.ctrl[0] + '_MUL_F_scale')
                mc.connectAttr( self.ctrl[0] + '.falloffScale', self.MDF + '.input1X')
                mc.setAttr(self.MDF + '.input2X', -1 )
                
                self.RMV = mc.createNode('remapValue', name = self.jj[a] + '_RMV_scale')
            
                self.PMAa = mc.createNode('plusMinusAverage', name = self.jj[a] + '_PMA_a_scale')
                               
                mc.connectAttr( self.MDF + '.outputX', self.PMAa + '.input3D[0].input3Dx')
                mc.connectAttr( self.ctrl[0] + '.falloffScale', self.PMAa + '.input3D[0].input3Dy')
                
                mc.setAttr(self.PMAa + '.input3D[1].input3Dx', a)
                mc.setAttr(self.PMAa + '.input3D[1].input3Dy', a+1)
                 
                mc.connectAttr( self.ctrl[0] + '.positionScale', self.RMV + '.inputValue')
                            
                mc.connectAttr( self.PMAa + '.output3D.output3Dx', self.RMV + '.inputMin')
                mc.connectAttr( self.PMAa + '.output3D.output3Dy', self.RMV + '.inputMax')
            
                self.PMAb = mc.createNode('plusMinusAverage', name = self.jj[a] + '_PMA_b_scale')
                self.MD = mc.createNode('multiplyDivide', name = self.jj[a] + '_MUL_scale')
                mc.connectAttr( self.ctrl[0] + '.volumeScale', self.MD + '.input1X')
                mc.connectAttr( self.RMV + '.outValue', self.MD + '.input2X')
                
                mc.connectAttr( self.MD + '.outputX', self.PMAb + '.input1D[0]')
                mc.setAttr(self.PMAb + '.input1D[1]', 1)
                
                mc.setAttr(self.RMV + '.value[0].value_Position', 0 )
                mc.setAttr(self.RMV + '.value[0].value_FloatValue', 0 )
                mc.setAttr(self.RMV + '.value[1].value_Position', 1 )
                mc.setAttr(self.RMV + '.value[1].value_FloatValue', 0 )
                mc.setAttr(self.RMV + '.value[3].value_Position', 0.5 )
                mc.setAttr(self.RMV + '.value[3].value_FloatValue', 1 )
                mc.setAttr(self.RMV + '.value[3].value_Interp', 2 )
                mc.setAttr(self.RMV + '.value[0].value_Interp', 2 )
                
                if self.valuesS[3]:
                
                    mc.connectAttr( self.PMAb + '.output1D', self.jj[a] + self.attrsS[0] )
                    mc.connectAttr( self.PMAb + '.output1D', self.jj[a] + self.attrsS[1] )
                    mc.connectAttr( self.PMAb + '.output1D', self.jj[a] + self.attrsS[2] )
                    
                else:
                
                    if self.valuesS[0]:
                        
                        mc.connectAttr( self.PMAb + '.output1D', self.jj[a] + self.attrsS[0] )
                   
                    if self.valuesS[1]:
                        
                        mc.connectAttr( self.PMAb + '.output1D', self.jj[a] + self.attrsS[1] )
                  
                    if self.valuesS[2]:
                        
                        mc.connectAttr( self.PMAb + '.output1D', self.jj[a] + self.attrsS[2] )
                      
                
            if self.chR[0] != 0:
                
                self.MDF_R = mc.createNode('multiplyDivide', name = self.ctrl[0] + '_MUL_F_rotate')
                mc.connectAttr( self.ctrl[0] + '.falloffRotation', self.MDF_R + '.input1X')
                mc.setAttr(self.MDF_R + '.input2X', -1 )
                
                self.RMV_R = mc.createNode('remapValue', name = self.jj[a] + '_RMV_rotate')
            
                self.PMAa_R = mc.createNode('plusMinusAverage', name = self.jj[a] + '_PMA_a_rotate')
                                
                mc.connectAttr( self.MDF_R + '.outputX', self.PMAa_R + '.input3D[0].input3Dx')
                mc.connectAttr( self.ctrl[0] + '.falloffRotation', self.PMAa_R + '.input3D[0].input3Dy')
                
                mc.setAttr(self.PMAa_R + '.input3D[1].input3Dx', a)
                mc.setAttr(self.PMAa_R + '.input3D[1].input3Dy', a+1)
                 
                mc.connectAttr( self.ctrl[0] + '.positionRotation', self.RMV_R + '.inputValue')
                            
                mc.connectAttr( self.PMAa_R + '.output3D.output3Dx', self.RMV_R + '.inputMin')
                mc.connectAttr( self.PMAa_R + '.output3D.output3Dy', self.RMV_R + '.inputMax')
                
                
                self.PMAb_R = mc.createNode('plusMinusAverage', name = self.jj[a] + '_PMA_b_rotate')
                self.MD_R = mc.createNode('multiplyDivide', name = self.jj[a] + '_MUL_rotate')
                mc.connectAttr( self.ctrl[0] + '.angle', self.MD_R + '.input1X')
                mc.connectAttr( self.RMV_R + '.outValue', self.MD_R + '.input2X')
                  
                mc.connectAttr( self.MD_R + '.outputX', self.PMAb_R + '.input1D[0]')
                mc.setAttr(self.PMAb_R + '.input1D[1]', 0)
                
                mc.setAttr(self.RMV_R + '.value[0].value_Position', 0 )
                mc.setAttr(self.RMV_R + '.value[0].value_FloatValue', 0 )
                mc.setAttr(self.RMV_R + '.value[1].value_Position', 1 )
                mc.setAttr(self.RMV_R + '.value[1].value_FloatValue', 0 )
                mc.setAttr(self.RMV_R + '.value[3].value_Position', 0.5 )
                mc.setAttr(self.RMV_R + '.value[3].value_FloatValue', 1 )
                mc.setAttr(self.RMV_R + '.value[3].value_Interp', 2 )
                mc.setAttr(self.RMV_R + '.value[0].value_Interp', 2 )
               
                    
                if self.valuesR[3]:
                    
                    mc.connectAttr( self.PMAb_R + '.output1D', self.jj[a] + self.attrsR[0] )
                    mc.connectAttr( self.PMAb_R + '.output1D', self.jj[a] + self.attrsR[1] )
                    mc.connectAttr( self.PMAb_R + '.output1D', self.jj[a] + self.attrsR[2] )
                    
                else:
                
                    if self.valuesR[0]:
                        
                        mc.connectAttr( self.PMAb_R + '.output1D', self.jj[a] + self.attrsR[0] )
                   
                    if self.valuesR[1]:
                        
                        mc.connectAttr( self.PMAb_R + '.output1D', self.jj[a] + self.attrsR[1] )
                  
                    if self.valuesR[2]:
                        
                        mc.connectAttr( self.PMAb_R + '.output1D', self.jj[a] + self.attrsR[2] )
 