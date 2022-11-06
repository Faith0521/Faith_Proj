# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-15 16:14:02
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-15 16:14:12

import datetime,getpass,imp,inspect,time,\
json,re,sys,os,shutil,subprocess,traceback
from operator import truediv
from functools import partial

from imp import reload

from maya import cmds as mc
from pymel import core as pm
# import module
from Faith.maya_utils import guide_path_utils as util
from Faith.maya_utils import attribute_utils as attribute
from Faith.maya_utils import naming_utils as naming
reload(util)
reload(attribute)
reload(naming)
# string type in py2 and py3
if sys.version_info[0] == 2:
    string_types = (basestring, )
else:
    string_types = (str, )


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

class guideAttributes(object):

    def __init__(self):
        self.baseName = "GUIDE_1"
        self.attr_names = []
        self.attr_defs = {}
        self.values = {}

    def addAttributes(self, parent):
        """

        :param parent:
        :return:
        """
        for guideName in self.attr_names:
            attrDef = self.attr_defs[guideName]
            attrDef.add(parent)

        return parent


    def addAttr(self, attrName, valueType, value,
                minimum=None, maximum=None, keyable=False,
                readable=True, storable=True, writable=True,
                niceName=None, shortName=None):
        """

        :param attrName:
        :param valueType:
        :param value:
        :param minimum:
        :param maximum:
        :param keyable:
        :param readable:
        :param storable:
        :param writable:
        :param niceName:
        :param shortName:
        :return:
        """

        attrDef = attribute.attrDef_create(attrName, valueType, value, niceName,
                                          shortName, minimum, maximum, keyable,
                                          readable, storable, writable)
        self.attr_defs[attrName] = attrDef
        self.values[attrName] = value
        self.attr_names.append(attrName)

        return attrDef


    # def addEnumAttr(self, attrName, enum, value=False):
    #     """
    #
    #     :param attrName:
    #     :param enum:
    #     :param value:
    #     :return:
    #     """
    #     attrDef = attribute.enumParamDef(attrName, enum, value)
    #     self.attr_defs[attrName] = attrDef
    #     self.values[attrName] = value
    #     self.attr_names.append(attrName)
    #
    #     return attrDef


    def setAttrDefValue(self, attrName, value):
        """
        给attribute函数设置匹配的value
        :param attrName: 添加的属性名称
        :param value: 新的value数据
        :return: False (如果属性找不到)
        """

        if attrName not in self.attr_defs.keys():
            return False

        self.attr_defs[attrName].value = value
        self.values[attrName] = value

        return True


class guideSetup(guideAttributes):

    def __init__(self):
        self.instanceList = []
        self.attr_names = []
        self.attr_defs = {}
        self.values = {}
        self.index = []

        self.allGuidesList = []
        self.guideModuleList = []
        
        self.ctrl = controlBase()
        self.radius = 1.0
        self.getMoudleInfo()

    def get_guide(self, type):
        """
        获取guide的文件路径
        :param type:
        :return:
        """
        module = util.importDefGuide(type)
        reload(module)
        module_guide_class = getattr(module, "guide")
        return module_guide_class

    def getUserName(self):
        """

        :return:
        """
        mc.namespace(setNamespace=":")
        namespaceList = mc.namespaceInfo(listOnlyNamespaces=True)

        for i in range(len(namespaceList)):
            if namespaceList[i].find("__") != -1:
                namespaceList[i] = namespaceList[i].partition("__")[2]

        newSuffix = util.findLastNumber(namespaceList, "GUIDE_") + 1
        # print(namespaceList)
        userGuideName = "GUIDE_" + str(newSuffix)
        return userGuideName

    def setup_new_guide(self, type):
        """
        创建新的guide
        :param parent: the parent guide
        :param type: type of the guide
        :return:d
        """
        guide = self.get_guide(type)
        if not guide:
            return
        userGuideName = self.getUserName()
        guideInstance = guide(userGuideName, type)
        mc.select(clear = True)
        return guideInstance

    def rig(self, prefix):
        """

        :return:
        """
        mc.refresh()

        self.attr_names = []
        self.attr_defs.clear()

        self.modulesToBeRiggedList = util.getModulesToBeRigged(self.instanceList)

        self.rigModule = {}
        self.guidesActionsDic = {}
        if self.modulesToBeRiggedList:
            progressAmount = 0
            mc.progressWindow(title='GuideRigSystem', progress=progressAmount,
                              status='Rigging : %0', isInterruptable=False)
            maxProcess = len(self.modulesToBeRiggedList)

            if mc.objExists('guideMirror_Grp'):
                mc.delete('guideMirror_Grp')

            # for module in self.modulesToBeRiggedList:
            #     module.checkParentMirror()

            self.data = util.getRigCollections()

            self.createBaseRigGrp(prefix)

            for module in self.modulesToBeRiggedList:
                guideModuleCustomName = mc.getAttr(module.root + '.module_name')
                progressAmount += 1
                mc.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount,
                                    status=('Rigging : ' + repr(progressAmount) + ' ' + str(guideModuleCustomName)))

                module.rigModule()
                mc.refresh()
                if module.guideActionsDic:
                    self.guidesActionsDic[module.root] = module.guideActionsDic["module"]
            # print(self.data)
            for guideModule in self.modulesToBeRiggedList:
                self.itemGuideModule = self.data[guideModule.root]["guideName"]
                self.itemGuideInstance = self.data[guideModule.root]["guideInstance"]
                self.itemGuideCustomName = self.data[guideModule.root]["guideCustomName"]
                self.itemGuideMirrorAxis = self.data[guideModule.root]["guideMirrorAis"]
                self.itemGuideMirrorName = self.data[guideModule.root]["guideMirrorName"]

                self.itemMirrorNameList = [""]
                    
                # get itemGuideName:
                if self.itemGuideMirrorAxis != "off":
                    self.itemMirrorNameList = self.itemGuideMirrorName
                
                for i,side in enumerate(self.itemMirrorNameList):
                    if self.itemGuideCustomName:
                        self.itemGuideName = side + self.prefix + self.itemGuideModule + "_0" + self.itemGuideCustomName[-1]
                    else:
                        self.itemGuideName = side + self.prefix + self.itemGuideModule + "_0" + self.itemGuideInstance[-1]
                    
                    # get hook groups info:
                    self.itemRiggedGrp = self.itemGuideName + "_Grp"
                    self.staticDataGrp = self.itemRiggedGrp
                    self.ctrlDataGrp = ""
                    self.scalableDataGrp = ""
                    self.rootDataGrp = ""
                    
                    riggedChildList = mc.listRelatives(self.itemRiggedGrp, children=True, type='transform')
                    if riggedChildList:
                        for child in riggedChildList:
                            if mc.objExists(child+".ctrlData") and mc.getAttr(child+".ctrlData") == 1:
                                self.ctrlDataGrp = child
                            elif mc.objExists(child+".scalableData") and mc.getAttr(child+".scalableData") == 1:
                                self.scalableDataGrp = child
                            elif mc.objExists(child+".staticData") and mc.getAttr(child+".staticData") == 1:
                                self.staticDataGrp = child
                            elif mc.objExists(child+".rootData") and mc.getAttr(child+".rootData") == 1:
                                self.rootDataGrp = child
                    
                    # get guideModule hierarchy data:
                    self.fatherGuide  = self.data[guideModule.root]['guideParent']
                    self.parentNode   = self.data[guideModule.root]['parentNode']
                    
                    # get father info:
                    if self.fatherGuide:
                        self.fatherModule              = self.data[guideModule.root]['parentModule']
                        self.fatherInstance            = self.data[guideModule.root]['parentInstance']
                        self.fatherNode                = self.data[guideModule.root]['fatherNode']
                        self.fatherGuideLoc            = self.data[guideModule.root]['parentGuideEnd']
                        self.fatherCustomName          = self.data[guideModule.root]['parentCustomName']
                        self.fatherMirrorAxis          = self.data[guideModule.root]['parentMirrorAis']
                        self.fatherGuideMirrorNameList = self.data[guideModule.root]['parentMirrorName']
                        
                        # working with father mirror:
                        self.fatherMirrorNameList = [""]
                        
                        # get fatherName:
                        if self.fatherMirrorAxis != "off":
                            self.fatherMirrorNameList = self.fatherGuideMirrorNameList
                        
                        for f, sideFatherName in enumerate(self.fatherMirrorNameList):
                            
                            if self.fatherCustomName:
                                self.fatherName = sideFatherName + self.prefix + self.fatherModule + "_0" + self.fatherCustomName[-1]
                            else:
                                self.fatherName = sideFatherName + self.prefix + self.fatherModule + "_0" + self.fatherInstance[-1]
                    
                    elif self.parentNode:
                        # parent module control to just a node in the scene:
                        mc.parent(self.ctrlDataGrp, self.parentNode)
                        # make ctrlHookGrp inactive:
                        mc.setAttr(self.ctrlDataGrp+".ctrlData", 0)
                    else:
                        # parent module control to default masterGrp:
                        mc.parent(self.ctrlDataGrp, self.ctrlsVisGrp)
                        # make ctrlHookGrp inactive:
                        mc.setAttr(self.ctrlDataGrp+".ctrlData", 0)
                    
                    if self.rootDataGrp:
                        # parent module rootHook to rootCtrl:
                        mc.parent(self.rootDataGrp, self.ctrlsVisGrp)
                        # make rootHookGrp inactive:
                        mc.setAttr(self.rootDataGrp+".rootData", 0)
                    
                    # put static and scalable groups in dataGrp:
                    if self.staticDataGrp:
                        mc.parent(self.staticDataGrp, self.staticGrp)
                        # make staticHookGrp inative:
                        mc.setAttr(self.staticDataGrp+".staticData", 0)
                    if self.scalableDataGrp:
                        mc.parent(self.scalableDataGrp, self.scaleGrp)
                        # make scalableHookGrp inative:
                        mc.setAttr(self.scalableDataGrp+".scalableData", 0)

                if self.guidesActionsDic:
                    pass
            mc.progressWindow(endProgress=True)
        
        self.guideMirrorGrp = 'GuideMirror_Grp'
        if mc.objExists(self.guideMirrorGrp):
            mc.delete(self.guideMirrorGrp)
        
        print("Rigging successfully ! ")

    def getMoudleInfo(self):
        """
        获取场景中的namespace 存放到列表中为rig做准备
        :return:
        """
        moduleList = util.findAllModules()
        self.guideModuleList = moduleList
        namespaceList = mc.namespaceInfo(listOnlyNamespaces=True)

        for n in namespaceList:
            divString = n.partition("__")
            if divString[1] != "":
                module = divString[0]
                userSpecName = divString[2]
                if module in moduleList:
                    index = moduleList.index(module)
                    # check if there is this module guide base in the scene:
                    curGuideName = moduleList[index] + "__" + userSpecName + ":Base"
                    if mc.objExists(curGuideName):
                        self.allGuidesList.append([moduleList[index], userSpecName, curGuideName])

        if self.allGuidesList:
            for module in self.allGuidesList:
                guide = self.get_guide(module[0])
                instance = guide(module[1], module[0])
                self.instanceList.append(instance)

    def validRigGrp(self, nodeGrp, *args):
        rigGrpAttrList = [
            "ctrls_grp", "ctrls_visibility_grp", "data_grp", "static_grp", "blendShapes_grp", 
            "global_ctrl", "local_ctrl", "all_ctrl", "settings_ctrl"
        ]
        for rigAttr in rigGrpAttrList:
            if not mc.objExists("%s.%s"%(nodeGrp, rigAttr)):
                mc.setAttr(nodeGrp+".rigGrp", 0)
                return False
        return mc.getAttr(nodeGrp+".rigGrp")

    def createBaseRigGrp(self, prefix):

        self.prefix = prefix
        self.masterGrp = ""

        rigAllGrp = "rig_grp"
        globalgrpList = []
        createAllGrp = True

        allTransformList = mc.ls(self.prefix + "*", selection=False, type="transform")
        for item in allTransformList:
            if mc.objExists(item + ".rigGrp"):
                if not mc.referenceQuery(item, isNodeReferenced=True):
                    globalgrpList.append(item)
        
        self.localTime = str( time.asctime( time.localtime(time.time()) ) )

        if globalgrpList:
            # validate master (All_Grp) node
            # If it doesn't work, the user need to clean the current scene to avoid duplicated names, for the moment.
            for nodeGrp in globalgrpList:
                if self.validRigGrp(nodeGrp):
                    self.masterGrp = nodeGrp
                    createAllGrp = False
        if createAllGrp:
            if mc.objExists(rigAllGrp):
                # rename existing All_Grp node without connections as All_Grp_Old
                mc.rename(rigAllGrp, rigAllGrp+"_Old")
            #Create Master Grp
            self.masterGrp = mc.createNode("transform", name=self.prefix+rigAllGrp)
            self.addMasterAttrs(self.masterGrp)

        # 创建rig组
        self.ctrlsGrp = self.createBaseGrpNode(self.prefix + "ctrlsGrp", "ctrls_grp")
        self.ctrlsVisGrp = self.createBaseGrpNode(self.prefix + "ctrlsVisibilityGrp", "ctrls_visibility_grp")
        self.dataGrp = self.createBaseGrpNode(self.prefix + "dataGrp", "data_grp")
        self.staticGrp = self.createBaseGrpNode(self.prefix + "staticGrp", "static_grp")
        self.scaleGrp = self.createBaseGrpNode(self.prefix + "scaleGrp", "scale_grp")
        self.bsGrp = self.createBaseGrpNode(self.prefix + "blendShapesGrp", "blendShapes_grp")

        if createAllGrp:
            if self.masterGrp == self.prefix + rigAllGrp:
                mc.parent(self.ctrlsGrp, self.dataGrp, self.masterGrp)
                mc.parent(self.staticGrp, self.bsGrp, self.scaleGrp, self.dataGrp)
        
        mc.select(clear = True)

        loclList = [self.masterGrp, self.ctrlsGrp, self.dataGrp, self.staticGrp, self.ctrlsVisGrp]
        self.ctrl.LockHide(loclList, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        shapeSizeList = []

        for guide in self.allGuidesList:
            guide_root = guide[-1]
            shapeSizeList.append(mc.getAttr("%s.sx"%guide_root))
        
        self.radius = 2.0 * (sum(shapeSizeList)/len(shapeSizeList)) # 计算控制器的大小

        self.global_ctrl = self.getBaseCtrl("root", "global_ctrl", self.prefix + "global_ctrl", self.radius, "yellow", 2.0)
        self.local_ctrl = self.getBaseCtrl("circle", "local_ctrl", self.prefix + "local_ctrl", 1.45*self.radius, "blue", 2.0)
        self.all_ctrl = self.getBaseCtrl("circle", "all_ctrl", self.prefix + "all_ctrl", 1.45*self.radius*0.9, "cyan", 2.0)

        self.ctrl.LockHide([self.global_ctrl, self.local_ctrl], ['sx', 'sy', 'sz'])
        self.ctrl.LockHide([self.scaleGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'v'])

        mc.parent(self.ctrlsVisGrp, self.all_ctrl)
        mc.parent(self.all_ctrl, self.local_ctrl)
        mc.parent(self.local_ctrl, self.global_ctrl)
        mc.parent(self.global_ctrl, self.ctrlsGrp)

        mc.select(None)


    def getBaseCtrl(self, sCtrlType, sAttrName, sCtrlName, fRadius, color, lineWidth):
        nCtrl = sCtrlName
        self.ctrlCreated = False
        
        if not mc.objExists(self.masterGrp+"."+sAttrName):
            mc.addAttr(self.masterGrp, longName=sAttrName, attributeType="message")
        if not mc.objExists(sCtrlName):
            if (sCtrlName != (self.prefix + "settings_ctrl")):
                nCtrl = self.ctrl.createCtrl(sCtrlType, sCtrlName, r=fRadius, color=color, addAttr=True, lineWidth=lineWidth)
            # else:
            #     nCtrl = self.ctrls.cvCharacter(sCtrlType, sCtrlName, r=(fRadius*0.2))
            mc.setAttr(nCtrl+".rotateOrder", 3)
            mc.connectAttr(sCtrlName+".message", self.masterGrp+"."+sAttrName, force=True)
            self.ctrlCreated = True
        return nCtrl

    def addMasterAttrs(self, nodeName, *args):
        self.rigGrp = self.addAttr("rigGrp", "bool", True)
        self.date = self.addAttr("date_time", "string", self.localTime)
        self.mayaVersion = self.addAttr("maya_version", "string", str(mc.about(version=True)))
        self.user = self.addAttr("user", "string", str(getpass.getuser()))
        self.name = self.addAttr("name", "string", self.masterGrp)
        for guideType in self.guideModuleList:
            guideCount = self.addAttr(guideType + "Count", "long", 0)

        self.addAttributes(nodeName)

    def createBaseGrpNode(self, grpName, attrName):
        if not mc.objExists(grpName):
            mc.createNode("transform", name=grpName)
        if not mc.objExists("%s.%s"%(self.masterGrp, attrName)):
            mc.addAttr(self.masterGrp, longName=attrName, attributeType="message")
        if not mc.listConnections("%s.%s"%(self.masterGrp, attrName), destination=False, source=True):
            mc.connectAttr(grpName+".message", "%s.%s"%(self.masterGrp, attrName), force=True)
        return grpName


class controlBase(guideSetup):
    
    code = """setAttr ".cc" -type "nurbsCurve" """
    attrList = ["type", "size", "rotX", "rotY", "rotY"]
    def __init__(self, moduleGrp=None, *args):
        self.attr_names = []
        self.attr_defs = {}
        self.moduleGrp = moduleGrp
        self.values = {}

    def ctrlCode(self, type="root"):
        return self.code + shape_dict[type]
    
    def createCtrl(self, type, name, r=1, color="blue", addAttr=False, lineWidth=1.0):
        mc.select(clear = True)

        if type in shape_dict.keys():
            code = self.ctrlCode(type=type)
            ctrlTransform = mc.createNode("transform", name = name)
            nurbsCrv = mc.createNode("nurbsCurve", p=ctrlTransform)
            mc.select(ctrlTransform, r=True)
            pm.mel.eval(code)
            
        elif type == "circle":
            ctrlTransform = mc.circle(n=name, ch=False, o=True, nr=(0,1,0), d=3, s=8, radius=r)[0]
        
        self.shapeList = self.renameShape([ctrlTransform])

        mc.select(ctrlTransform + ".cv[*]", r=True)
        mc.scale(1.0*r, 1.0*r, 1.0*r)
        
        if color in colors_dict.keys():
            self.colorShape([ctrlTransform], color=color)
        
        [mc.setAttr(shape + ".lineWidth", lineWidth) for shape in self.shapeList]

        if addAttr:
            self.type = self.addAttr("type", "string", type)
            self.size = self.addAttr("size", "double", 1.0 * r)
            self.rotX = self.addAttr("rotX", "double", 0.0)
            self.rotY = self.addAttr("rotY", "double", 0.0)
            self.rotZ = self.addAttr("rotZ", "double", 0.0)
            self.addAttributes(ctrlTransform)

        mc.select(d = True)

        return ctrlTransform

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

    def cvLocator(self, ctrlName, r=0.3, *args):
        locCtrl = self.createCtrl("loc", name=ctrlName, r=r, addAttr=True)
        self.renameShape([locCtrl])
        self.addGuideAttrs(locCtrl)
        mc.select(d=True)
        return locCtrl

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

    def cvJntLoc(self, ctrlName, r=0.3, guide=True, *args):
        locCtrl = self.createCtrl("loc", name=ctrlName, r=r)
        self.colorShape([locCtrl], "cyan")

        self.ball = self.createCtrl("ball", name=ctrlName, r=r)
        ballShapeList = mc.listRelatives(self.ball, shapes=True, children=True, fullPath=True)
        for shape in ballShapeList:
            mc.setAttr(shape + ".template", 1)
            mc.parent(shape, locCtrl, r=True, s=True)
        
        mc.delete(self.ball)
        self.renameShape([locCtrl])

        if guide:
            self.addGuideAttrs(locCtrl)

        mc.select(clear = True)

        return locCtrl

    def addGuideAttrs(self, ctrlName, *args):
        mc.addAttr(ctrlName, longName="joint_num", attributeType='long')
        mc.setAttr(ctrlName+".joint_num", 1)
        # colorize curveShapes:
        self.colorShape([ctrlName], 'cyan')
        # shapeSize setup:
        self.shapeSizeSetup(ctrlName)
        # pinGuide:
        self.lockGuide(ctrlName)

    def shapeSizeSetup(self, transformNode, *args):
        clusterHandle = None
        childShapeList = mc.listRelatives(transformNode, shapes=True, children=True)

        if childShapeList:
            thisNamespace = childShapeList[0].split(":")[0]
            mc.namespace(set=thisNamespace, force=True)
            clusterName = transformNode.split(":")[1]+"_ShapeSizeClus"
            clusterHandle = mc.cluster(childShapeList, name=clusterName)[1]
            mc.setAttr(clusterHandle+".visibility", 0)
            mc.xform(clusterHandle, scalePivot=(0, 0, 0), worldSpace=True)
            mc.namespace(set=":")
        else:
            print("There are not children shape to create shapeSize setup of:", transformNode)
        if clusterHandle:
            self.connectShapeSize(clusterHandle)

    def LockHide(self, objList, attrList, l=True, k=False, *args):
        """Set lock or hide to attributes for object in lists.
        """
        if objList and attrList:
            for obj in objList:
                for attr in attrList:
                    try:
                        # set lock and hide of given attributes:
                        mc.setAttr(obj+"."+attr, lock=l, keyable=k)
                    except:
                        print("Error: Cannot set", obj, ".", attr, "as lock=", l, "and keyable=", k)

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
            mc.scriptJob(attributeChange=[str(ctrlName+".lock_guide"), lambda nodeName=ctrlName: self.lockGuideJob(nodeName)],
                         killWithScene=True, compressUndo=True)
            if mc.getAttr(ctrlName+".lock_guide"):
                self.setLockedGuideColor(ctrlName, 1, "red")

    def unLockGuide(self, guideBase, *args):
            """ Remove pinGuide setup.
            """
            if mc.objExists(guideBase):
                pcName = guideBase+"_PinGuide_PaC"
                if mc.objExists(pcName):
                    mc.delete(pcName)
                childrenList = mc.listRelatives(guideBase, children=True, allDescendents=True, fullPath=True, type="transform")
                if childrenList:
                    for childNode in childrenList:
                        if mc.objExists(childNode+".lock_guide"):
                            mc.setAttr(childNode+".lock_guide", 0)
                            self.lockGuideJob(childNode)
                if mc.objExists(guideBase+".lock_guide"):
                    mc.setAttr(guideBase+".lock_guide", 0)
                    self.lockGuide(guideBase)

    def lockGuideJob(self, ctrlName, *args):
        transformAttrList = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
        if mc.objExists(ctrlName + '.lock_guide'):
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
                        self.setLockedGuideColor(ctrlName, 1, "red")
            else:
                pConstList = mc.listRelatives(ctrlName, children=True, type="parentConstraint")
                if pConstList:
                    for pConst in pConstList:
                        if "lockGuide" in pConst:
                            mc.delete(pConst)
                self.setLockedGuideColor(ctrlName, 0, "red")
            
            for attr in transformAttrList:
                mc.setAttr(ctrlName+"."+attr, lock=lockVal)
            mc.namespace(set=":")

    def setLockedGuideColor(self, ctrlName, switch, color, *args):
        """

        :param switch:
        :param color:
        :return:
        """
        mc.setAttr(ctrlName + ".overrideEnabled", switch)
        mc.setAttr(ctrlName + ".overrideColor", colors_dict[color])
        shapeList = mc.listRelatives(ctrlName, children=True, fullPath=False, shapes=True)
        if shapeList:
            for shape in shapeList:
                if switch:
                    mc.setAttr(shape + ".overrideEnabled", 0)
                else:
                    mc.setAttr(shape + ".overrideEnabled", 1)

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
            self.LockHide([self.temp_static_grp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        mc.parent(clust, self.temp_static_grp)


