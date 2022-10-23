# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-18 20:48:28
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-18 20:48:49

from functools import partial

from importlib import reload
from turtle import circle

from maya import cmds as mc
from pymel import core as pm
# import module
from Faith.guide import guide_base
from Faith.guide import rig_base
from Faith.maya_utils import guide_path_utils as util
reload(guide_base)
reload(util)
reload(rig_base)

VERSION = "0.0.1"
colors_dict = {
    "yellow"    : 17,
    "red"       : 13,
    "blue"      : 6,
    "cyan"      : 18,
    "green"     : 7,
    "darkRed": 4,
    "darkBlue": 15,
    "white": 16,
    "black": 1,
    "gray": 3,
}

shape_dict = {
    "root" : " 3 86 0 no 3\n\t\t91 24 24 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45\n\t\t 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72\n\t\t 72 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97\n\t\t 98 99 100 101 102 103 104 105 106 107 108 108 108\n\t\t89\n\t\t1.3072133485625613e-15 -1.1177970774370868e-15 5.0458403244651073\n\t\t0.2137395454383075 -1.6982989875933816e-15 4.5168820671634577\n\t\t0.64121863631491993 -1.2557823195177887e-15 4.8822689169886857\n\t\t1.2714658439831006 -1.3992689047053277e-15 4.7569049528769805\n\t\t1.8799579185438013 -1.5188136109827291e-15 4.5503497266827431\n\t\t2.456283391895405 -1.6123709952815256e-15 4.2661374555940714\n\t\t2.9905811754012683 -1.6783402648173601e-15 3.9091310903678242\n\t\t3.4737092858502732 -1.7155926670983436e-15 3.4854391088938823\n\t\t3.8974012673242084 -1.7234908031931178e-15 3.0023109984448779\n\t\t4.2544076325504605 -1.7018995338033345e-15 2.4680132149390119\n\t\t4.5386199036391357 -1.6511882915344891e-15 1.8916877415874107\n\t\t4.7451751298333704 -1.5722247598015974e-15 1.2831956670267128\n\t\t4.8705390939450623 -1.4663600265254493e-15 0.6529484593585323\n\t\t4.3224588192072346 -2.3994466520389713e-15 0.011729823043610537\n\t\t4.8705390939450641 -1.1816017489832208e-15 -0.62948881327130712\n\t\t4.7451751298333713 -1.0075804977958017e-15 -1.2597360209394841\n\t\t4.5386199036391357 -8.163192649370029e-16 -1.868228095500182\n\t\t4.2544076325504614 -6.1109058312867602e-16 -2.4445535688517941\n\t\t3.8974012673242084 -3.9540597201669917e-16 -2.9788513523576587\n\t\t3.4737092858502732 -1.7295585509626944e-16 -3.4619794628066614\n\t\t2.9905811754012692 5.245358445727907e-17 -3.8856714442805895\n\t\t2.456283391895405 2.76965528637883e-16 -4.2426778095068443\n\t\t1.8799579185438042 4.9673851583413899e-16 -4.5268900805955115\n\t\t1.2714658439831035 7.0801216930254041e-16 -4.7334453067897577\n\t\t0.64121863631492548 9.0717153825611295e-16 -4.8588092709014461\n\t\t1.2001519507380662e-15 1.9195573216311759e-15 -4.3107289961636246\n\t\t-0.64121863631491938 1.2557823195177893e-15 -4.8588092709014603\n\t\t-1.2714658439831006 1.3992689047053287e-15 -4.7334453067897648\n\t\t-1.8799579185438013 1.5188136109827308e-15 -4.5268900805955221\n\t\t-2.4562833918954072 1.6123709952815271e-15 -4.2426778095068478\n\t\t-2.9905811754012719 1.6783402648173619e-15 -3.8856714442805962\n\t\t-3.4737092858502767 1.715592667098344e-15 -3.4619794628066654\n\t\t-3.897401267324212 1.7234908031931194e-15 -2.978851352357661\n\t\t-4.2544076325504632 1.701899533803337e-15 -2.4445535688517954\n\t\t-4.5386199036391437 1.6511882915344895e-15 -1.8682280955001869\n\t\t-4.7451751298333757 1.5722247598015984e-15 -1.259736020939487\n\t\t-4.870539093945065 1.4663600265254493e-15 -0.6294888132713089\n\t\t-4.3224588192072346 2.3994466520389705e-15 0.011729823043611597\n\t\t-4.870539093945065 1.1816017489832208e-15 0.65294845935853052\n\t\t-4.7451751298333757 1.0075804977958006e-15 1.2831956670267126\n\t\t-4.5386199036391446 8.1631926493700409e-16 1.8916877415874107\n\t\t-4.2544076325504614 6.1109058312867592e-16 2.4680132149390142\n\t\t-3.897401267324212 3.9540597201669927e-16 3.0023109984448775\n\t\t-3.4737092858502741 1.7295585509626934e-16 3.4854391088938845\n\t\t-2.9905811754012719 -5.2453584457279045e-17 3.9091310903678242\n\t\t-2.456283391895405 -2.7696552863788365e-16 4.2661374555940723\n\t\t-1.8799579185438013 -4.9673851583413988e-16 4.5503497266827404\n\t\t-1.2714658439831006 -7.0801216930254071e-16 4.7569049528769805\n\t\t-0.64121863631492049 -9.0717153825611472e-16 4.8822689169886857\n\t\t-0.21373954543830614 -1.582095393839489e-15 4.5168820671634577\n\t\t1.3072133485625613e-15 -1.1177970774370868e-15 5.0458403244651073\n\t\t-0.29723365214720365 -1.0536489487664425e-15 5.1208263958092131\n\t\t-0.89170095644160885 -8.8050383509625918e-16 5.0688172458466374\n\t\t-1.7563080305441963 -5.9403250111802658e-16 4.8371464785706149\n\t\t-2.567550573873445 -2.8951179018827089e-16 4.4588578679950386\n\t\t-3.3007793922588249 2.3805589986319215e-17 3.945445522129003\n\t\t-3.933715699085397 3.3639964935538686e-16 3.3125092153024349\n\t\t-4.447128044951433 6.3877237560522502e-16 2.5792803969170528\n\t\t-4.8254166555270057 9.2173632645671916e-16 1.7680378535878083\n\t\t-5.0570874228030229 1.1766937854499107e-15 0.9034307794852191\n\t\t-5.13510114774689 1.3958979992079935e-15 0.011729823043610621\n\t\t-5.0570874228030229 1.5726885586186105e-15 -0.87997113339799771\n\t\t-4.8254166555270057 1.7016937719944103e-15 -1.7445782075005856\n\t\t-4.447128044951433 1.778993881206757e-15 -2.5558207508298354\n\t\t-3.933715699085397 1.8022401615529771e-15 -3.2890495692152162\n\t\t-3.3007793922588293 1.7707262865679419e-15 -3.9219858760417785\n\t\t-2.5675505738734445 1.685409789396266e-15 -4.4353982219078274\n\t\t-1.7563080305441954 1.5488829686322912e-15 -4.8136868324833886\n\t\t-0.89170095644160796 1.3652941226390277e-15 -5.0453575997594164\n\t\t1.6116420868652803e-15 1.1402215056015338e-15 -5.1233713247032808\n\t\t0.8917009564416104 8.8050383509625701e-16 -5.0453575997593987\n\t\t1.7563080305441954 5.9403250111802648e-16 -4.8136868324833841\n\t\t2.5675505738734397 2.8951179018827084e-16 -4.435398221907815\n\t\t3.3007793922588222 -2.3805589986319236e-17 -3.9219858760417714\n\t\t3.9337156990853899 -3.3639964935538563e-16 -3.2890495692152122\n\t\t4.447128044951433 -6.3877237560522492e-16 -2.555820750829831\n\t\t4.8254166555269959 -9.2173632645671798e-16 -1.7445782075005811\n\t\t5.057087422803022 -1.1766937854499106e-15 -0.87997113339799604\n\t\t5.1351011477468784 -1.3958979992079922e-15 0.011729823043611573\n\t\t5.0570874228030211 -1.5726885586186095e-15 0.90343077948521888\n\t\t4.8254166555270013 -1.701693771994407e-15 1.768037853587807\n\t\t4.447128044951433 -1.7789938812067551e-15 2.579280396917051\n\t\t3.9337156990853899 -1.8022401615529763e-15 3.3125092153024327\n\t\t3.3007793922588227 -1.7707262865679379e-15 3.9454455221289959\n\t\t2.5675505738734397 -1.6854097893962656e-15 4.4588578679950386\n\t\t1.7563080305441954 -1.5488829686322884e-15 4.8371464785706086\n\t\t0.89170095644160796 -1.3652941226390253e-15 5.0688172458466374\n\t\t0.29723365214720182 -1.2152457112806955e-15 5.1208263958092131\n\t\t1.3072133485625613e-15 -1.117797077437087e-15 5.0458403244651073\n\t\t;",
    "pole" : " 1 12 0 no 3\n\t\t13 0 1 2 3 4 5 6 7 8 9 10 11 12\n\t\t13\n\t\t0.5 0 0\n\t\t0 0 0.5\n\t\t-0.5 0 0\n\t\t0 0 -0.5\n\t\t0.5 0 0\n\t\t0 0.5 0\n\t\t-0.5 0 0\n\t\t0 -0.5 0\n\t\t0 0 -0.5\n\t\t0 0.5 0\n\t\t0 0 0.5\n\t\t0 -0.5 0\n\t\t0.5 0 0\n\t\t;",
    "finger" : " 3 8 2 no 3\n\t\t13 -2 -1 0 1 2 3 4 5 6 7 8 9 10\n\t\t11\n\t\t1.871981849540608e-17 0.4667727477199381 -0.30571783649685047\n\t\t-3.7990549347274899e-33 0.64275993689642075 6.2043275454972651e-17\n\t\t-1.8719818495406061e-17 0.46677274771993821 0.30571783649684997\n\t\t-2.2185363318579492e-17 0.3670141435056305 0.36231447849332232\n\t\t-2.2185363318579492e-17 0.3670141435056305 0.36231447849332232\n\t\t-3.7990549347274892e-33 0.56751794090090757 6.2043275454972651e-17\n\t\t2.2185363318579511e-17 0.36701414350563027 -0.36231447849332271\n\t\t2.2185363318579511e-17 0.36701414350563022 -0.36231447849332271\n\t\t1.871981849540608e-17 0.4667727477199381 -0.30571783649685047\n\t\t-3.7990549347274899e-33 0.64275993689642075 6.2043275454972651e-17\n\t\t-1.8719818495406061e-17 0.46677274771993821 0.30571783649684997\n\t\t;",
    "cube" : " 1 15 0 no 3\n\t\t16 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n\t\t16\n\t\t0.5 0.5 0.5\n\t\t0.5 0.5 -0.5\n\t\t-0.5 0.5 -0.5\n\t\t-0.5 -0.5 -0.5\n\t\t0.5 -0.5 -0.5\n\t\t0.5 0.5 -0.5\n\t\t-0.5 0.5 -0.5\n\t\t-0.5 0.5 0.5\n\t\t0.5 0.5 0.5\n\t\t0.5 -0.5 0.5\n\t\t0.5 -0.5 -0.5\n\t\t-0.5 -0.5 -0.5\n\t\t-0.5 -0.5 0.5\n\t\t0.5 -0.5 0.5\n\t\t-0.5 -0.5 0.5\n\t\t-0.5 0.5 0.5\n\t\t;",
    "loc" : " 1 7 0 no 3\n\t\t8 0 1 2 3 4 5 6 7\n\t\t8\n\t\t-1 0 0\n\t\t1 0 0\n\t\t0 0 0\n\t\t0 0 1\n\t\t0 0 -1\n\t\t0 0 0\n\t\t0 1 1.8761019415568463e-17\n\t\t6.123233995736766e-17 -1 -6.2536731385228211e-18\n\t\t;",
    "ball" : " 3 46 0 no 3\n\t\t51 2 2 2 3 4 4 4 5 6 6 6 7 8 8 8 9 10 10 10 11 12 12 12 13 14 14 14 15 16 16\n\t\t 16 17 18 18 18 19 20 20 20 21 22 22 22 23 24 24 24 25 26 26 26\n\t\t49\n\t\t-0.5 0 5.5511151231257827e-17\n\t\t-0.50000000000000022 -0.13060193748187082 1.7645117349922589e-17\n\t\t-0.39180581244561219 -0.39180581244561224 9.7703728183612522e-18\n\t\t-0.13060193748187082 -0.50000000000000011 1.975851338064811e-17\n\t\t0 -0.5 5.5511151231257827e-17\n\t\t0.13060193748187063 -0.50000000000000022 3.5752637850609668e-17\n\t\t0.39180581244561213 -0.39180581244561241 5.7752746228245928e-17\n\t\t0.50000000000000011 -0.1306019374818706 7.8877457307290243e-17\n\t\t0.5 0 5.5511151231257827e-17\n\t\t0.50000000000000011 0.13060193748187107 9.3377185112593072e-17\n\t\t0.39180581244561213 0.39180581244561247 1.0125192964415441e-16\n\t\t0.13060193748187071 0.50000000000000022 9.1263789081867545e-17\n\t\t-2.7755575615628914e-17 0.49999999999999978 8.3266726846886765e-17\n\t\t-0.13060193748187077 0.50000000000000011 7.5269664611905974e-17\n\t\t-0.39180581244561224 0.39180581244561213 5.3269556234269701e-17\n\t\t-0.50000000000000022 0.13060193748187066 3.2144845155225411e-17\n\t\t-0.50000000000000022 -8.3266726846886741e-17 0\n\t\t-0.5 7.9970622349807932e-18 -0.13060193748187079\n\t\t-0.39180581244561213 2.3991186704942356e-17 -0.39180581244561208\n\t\t-0.13060193748187079 3.061616997868383e-17 -0.49999999999999994\n\t\t0 0 -0.49999999999999994\n\t\t0.13060193748187079 3.0616169978683824e-17 -0.49999999999999989\n\t\t0.39180581244561252 2.3991186704942341e-17 -0.39180581244561186\n\t\t0.50000000000000022 7.997062234980767e-18 -0.13060193748187038\n\t\t0.50000000000000011 -1.6177811532852781e-32 3.0531133177191805e-16\n\t\t0.49999999999999994 -7.9970622349807994e-18 0.13060193748187099\n\t\t0.39180581244561191 -2.3991186704942363e-17 0.39180581244561224\n\t\t0.13060193748187052 -3.0616169978683836e-17 0.50000000000000022\n\t\t0 0 0.5\n\t\t-5.9615625589289494e-17 0.13060193748187088 0.5\n\t\t-1.1098955353675924e-16 0.39180581244561224 0.39180581244561208\n\t\t-1.1901936469749647e-16 0.50000000000000011 0.1306019374818706\n\t\t-1.1102230246251565e-16 0.5 -9.7144514654701197e-17\n\t\t-1.0302524022753486e-16 0.5 -0.13060193748187079\n\t\t-6.3007180126874498e-17 0.39180581244561213 -0.39180581244561208\n\t\t1.6167143680782006e-18 0.13060193748187079 -0.49999999999999994\n\t\t3.0616169978683836e-17 1.3877787807814457e-17 -0.49999999999999994\n\t\t5.9615625589289469e-17 -0.13060193748187079 -0.49999999999999989\n\t\t1.1098955353675929e-16 -0.39180581244561252 -0.39180581244561186\n\t\t1.1901936469749647e-16 -0.50000000000000022 -0.13060193748187038\n\t\t1.1102230246251565e-16 -0.50000000000000011 3.0531133177191805e-16\n\t\t1.0302524022753484e-16 -0.49999999999999994 0.13060193748187099\n\t\t6.3007180126874449e-17 -0.39180581244561191 0.39180581244561224\n\t\t-1.6167143680782592e-18 -0.13060193748187052 0.50000000000000022\n\t\t-3.0616169978683873e-17 1.8041124150158794e-16 0.5\n\t\t-0.13060193748187088 -3.061616997868383e-17 0.5\n\t\t-0.39180581244561224 -2.3991186704942347e-17 0.39180581244561208\n\t\t-0.50000000000000011 -7.9970622349807762e-18 0.1306019374818706\n\t\t-0.5 8.4740917553038378e-33 -9.7144514654701197e-17\n\t\t;",
    "square" : " 1 4 0 no 3\n\t\t5 0 1 2 3 4\n\t\t5\n\t\t0.5 0.5 -1.1102230246251565e-16\n\t\t-0.5 0.5 -1.1102230246251565e-16\n\t\t-0.5 -0.5 1.1102230246251565e-16\n\t\t0.5 -0.5 1.1102230246251565e-16\n\t\t0.5 0.5 -1.1102230246251565e-16\n\t\t;"
}

class guideBase(guide_base.guideSetup):

    def __init__(self, userGuideName, rigType, CLASS, NAME, DESCRIPTION, *args):

        self.attr_names = []
        self.attr_defs = {}
        self.values = {}

        self.userGuideName = userGuideName
        self.rigType = rigType
        self.guideModuleName = CLASS
        self.name = NAME
        self.description = DESCRIPTION

        self.initializeAttrs()

        self.addPrivateAttrs()

        self.guideNamespace = self.guideModuleName + "__" + self.userGuideName

        mc.namespace(setNamespace=":")
        self.namespaceExists = mc.namespace(exists=self.guideNamespace)

        self.guideName = self.guideNamespace + ":"
        self.root = self.guideName + "Base"

        if not self.namespaceExists:
            mc.namespace(add=self.guideNamespace)
            self.createGuide()

    def createGuide(self):
        return

    def initializeAttrs(self):
        """

        :return:
        """
        self.guide_base = self.addAttr("guide_base", "bool", True)
        self.guide_type = self.addAttr("guide_type", "string", self.rigType)
        self.module_name = self.addAttr("module_name", "string", self.guideModuleName)
        self.user_name = self.addAttr("user_name", "string", self.userGuideName)
        self.prefix_name = self.addAttr("prefix_name", "string", "")
        self.mirror_on = self.addAttr("mirror_on", "bool", False)
        self.mirror_axis = self.addAttr("mirror_axis", "string", "x")
        self.mirror_name = self.addAttr("mirror_name", "string", "L-->R")
        self.shape_size = self.addAttr("shape_size", "double", 1.0)
        self.version = self.addAttr("version", "string", VERSION)

    def addRoot(self):
        self.ctrl = controlBase(self.root)
        self.root = self.ctrl.cvBase(self.root, 4)

        for name in self.attr_names:
            attrDef = self.attr_defs[name]
            attrDef.add(self.root)

        return self.root

    def confirmModules(self):
        """

        :param args:
        :return:
        """
        if mc.objExists(self.root):
            if mc.objExists(self.root + '.guide_base'):
                if mc.getAttr(self.root + '.guide_base') == 1:
                    return True
                else:
                    try:
                        self.deleteModule()
                    except:
                        pass
                    return False
        return False

    def deleteModule(self, *args):
        """

        :param args:
        :return:
        """
        try:
            mc.delete(self.root[:self.root.find(":")] + "_MirrorGrp")
        except:
            pass


        return

    def addPrivateAttrs(self):
        """

        :return:
        """
        return

    def rigModule(self, *args):
        return


class controlBase(guide_base.guideSetup):

    code = """setAttr ".cc" -type "nurbsCurve" """

    def __init__(self, moduleGrp=None, *args):
        self.moduleGrp = moduleGrp
        self.value = {}

    def ctrlCode(self, type="root"):
        return self.code + shape_dict[type]
    
    def createCtrl(self, type, name):
        mc.select(clear = True)
        code = self.ctrlCode(type=type)
        if type in shape_dict.keys():
            ctrlTransform = mc.createNode("transform", name = name)
            nurbsCrv = mc.createNode("nurbsCurve", p=ctrlTransform)
            mc.select(ctrlTransform, r=True)
            pm.mel.eval(code)

            self.renameShape([ctrlTransform])
            return ctrlTransform
        else:
            return False

    def colorShape(self, objList, color, rgb=False, *args):
        """

        :param objList:
        :param color:
        :param rgb: 
        :param args:
        :return:
        """
        if rgb:
            pass
        elif (color in colors_dict):
            iColorIdx = colors_dict[color]
        else:
            iColorIdx = color

        # find shapes and apply the color override:
        shapeTypeList = ['nurbsCurve', 'nurbsSurface', 'mesh', 'subdiv']
        if objList:
            for objName in objList:
                objType = mc.objectType(objName)
                # verify if the object is the shape type:
                if objType in shapeTypeList:
                    # set override as enable:
                    mc.setAttr(objName+".overrideEnabled", 1)
                    # set color override:
                    if rgb:
                        mc.setAttr(objName+".overrideRGBColors", 1)
                        mc.setAttr(objName+".overrideColorR", color[0])
                        mc.setAttr(objName+".overrideColorG", color[1])
                        mc.setAttr(objName+".overrideColorB", color[2])
                    else:
                        mc.setAttr(objName+".overrideRGBColors", 0)
                        mc.setAttr(objName+".overrideColor", iColorIdx)
                # verify if the object is a transform type:
                elif objType == "transform":
                    # find all shapes children of the transform object:
                    shapeList = mc.listRelatives(objName, shapes=True, children=True, fullPath=True)
                    if shapeList:
                        for shape in shapeList:
                            # set override as enable:
                            mc.setAttr(shape+".overrideEnabled", 1)
                            # set color override:
                            if rgb:
                                mc.setAttr(shape+".overrideRGBColors", 1)
                                mc.setAttr(shape+".overrideColorR", color[0])
                                mc.setAttr(shape+".overrideColorG", color[1])
                                mc.setAttr(shape+".overrideColorB", color[2])
                            else:
                                mc.setAttr(shape+".overrideRGBColors", 0)
                                mc.setAttr(shape+".overrideColor", iColorIdx)

    def renameShape(self, transformList, *args):
        resultList = []
        for obj in transformList:
            childrenShapeList = mc.listRelatives(
                obj, shapes=True, children=True, fullPath=True
            )
            if childrenShapeList:
                for i,child in enumerate(childrenShapeList):
                    shapeName = "%sShape"%(obj + str(i))
                    shape = mc.rename(child, shapeName)
                    resultList.append(shape)
        return resultList

    def cvBase(self, ctrlName, r=1, *args):
        """

        :param ctrlName:
        :param r:
        :param args:
        :return:
        """
        circle = mc.circle(n=ctrlName, ch=False, o=True, nr=(0,1,0), d=3, s=8, radius=r)[0]
        self.renameShape([circle])

        self.colorShape([circle], 'yellow')
        mc.setAttr("%s0Shape.lineWidth"%circle, 2)
        mc.select(d = True)

        self.lockGuide(circle)
        return circle

    def lockGuide(self, ctrlName, *args):
        """

        :param ctrlName:
        :param args:
        :return:
        """
        if not ctrlName.endswith("_LocEnd"):
            if not mc.objExists("%s.lock_guide"%ctrlName):
                mc.addAttr(ctrlName, longName="lock_guide", attributeType='bool')
                mc.setAttr(ctrlName+".lock_guide", channelBox=True)
                mc.addAttr(ctrlName, longName="lockGuideConstraint", attributeType="message")
                mc.scriptJob(attributeChange=[str(ctrlName+".lock_guide"), lambda nodeName=ctrlName: self.jobPinGuide(nodeName)], killWithScene=True, compressUndo=True)
            if mc.getAttr(ctrlName+".lock_guide"):
                    self.setLockedGuideColor(ctrlName, True, "red")

    def lockGuideJob(self, ctrlName, *args):
        transformAttrList = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
        if mc.getAttr(ctrlName + '.lock_guide'):
            namespace = None
            mc.namespace(set = ':')
            if ":" in ctrlName:
                if "|" in ctrlName:
                    namespace = ctrlName[ctrlName.rfind("|")+1:ctrlName.rfind(":")]
                else:
                    namespace = ctrlName[:ctrlName.rfind(":")]
            parentCon = ctrlName + "_lockGuide_pc"
            lockVal = mc.getAttr(ctrlName + ".lock_guide")
            if lockVal:
                if not mc.objExists(parentCon):
                    if mc.objExists("guide_static_grp"):
                        if namespace:
                            mc.namespace(set = namespace)
                        mc.parentConstraint("guide_static_grp", ctrlName, maintainOffset=True, name=parentCon)

    def connectShapeSize(self, clust, *args):
        mc.connectAttr(self.moduleGrp + ".shape_size", clust + ".scaleX", force=True)
        mc.connectAttr(self.moduleGrp + ".shape_size", clust + ".scaleY", force=True)
        mc.connectAttr(self.moduleGrp + ".shape_size", clust + ".scaleZ", force=True)

        self.temp_static_grp = "guide_static_grp"
        if not mc.objExists(self.temp_static_grp):
            mc.group(name=self.temp_static_grp, empty=True)
            mc.setAttr(self.temp_static_grp+".visibility", 0)
            mc.setAttr(self.temp_static_grp+".template", 1)
            mc.setAttr(self.temp_static_grp+".hiddenInOutliner", 1)
            self.setLockHide([self.temp_static_grp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        mc.parent(clust, self.temp_static_grp)

        





























