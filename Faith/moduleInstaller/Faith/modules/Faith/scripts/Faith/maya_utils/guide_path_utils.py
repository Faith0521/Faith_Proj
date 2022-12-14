# -*- coding: utf-8 -*-
# @Author: 尹宇飞
# @Date:   2022-10-15 16:22:25
# @Last Modified by:   尹宇飞
# @Last Modified time: 2022-10-15 16:22:34

import os,sys,re

from maya import cmds as mc
from Faith import modules

GUIDE_ENV_KEY = "FAITH_GUIDE_PATH"


def getDirectories():
    """
    get the module path
    :return:
    """
    return gatherCustomModuleDirectories(
        GUIDE_ENV_KEY,
        [os.path.join(os.path.dirname(modules.__file__))])


def gatherCustomModuleDirectories(envvarkey,
                                  defaultModulePath,
                                  component=False):
    """
    returns component directory
    :param envvarkey: The environment variable key name, that is searched
    :param defaultModulePath:The default module path for search in.
    :param component: dict()
    :return:
    """
    results = {}

    if not isinstance(defaultModulePath, list):
        defaultModulePath = [defaultModulePath]

    for dp in defaultModulePath:
        if not os.path.exists(dp):
            return {}
        # 将文件路径里的文件夹名字放在字典里
        results[dp] = sorted(os.listdir(dp))

    envVarval = os.environ.get(envvarkey, "")

    for path in envVarval.split(os.pathsep):
        if not path or not os.path.exists(path):
            continue
        if component:
            init_py_path = os.path.join(path, "__init__.py")
            if not os.path.exists(init_py_path):
                continue

        modules = sorted(os.listdir(path))
        modules = [x for x in modules if os.path.isdir(os.path.join(path, x))]

        results[path] = modules

    return results


def importDefGuide(type):
    """

    :param type:
    :return:
    """
    dirs = getDirectories()
    defFmt = "Faith.guide.{}"
    customFmt = "{}.guide"

    module = importFromStandardOrCustomDirectories(
        dirs, defFmt, customFmt, type)
    return module

def getModuleBasePath(directories, moduleName):
    """search component path"""
    # moduleBasePath = ""
    dic_items = directories.items
    for basepath, modules in dic_items():
        if moduleName in modules:
            # moduleBasePath = os.path.basename(basepath)
            moduleBasePath = basepath
            break
    else:
        moduleBasePath = ""

    return moduleBasePath

def importFromStandardOrCustomDirectories(directories,
                                          defaultFormatter,
                                          customFormatter,
                                          moduleName):
    """Return imported module

    Arguments:
        directories: the directories for search in. this is got by
            gatherCustomModuleDirectories
        defaultFormatter: this represents module structure for default
            module. for example "mgear.core.shifter.component.{}"
        customFormatter:  this represents module structure for custom
            module. for example "{0}.{1}"

    Returns:
        module: imported module

    """
    # Import module and get class
    level = -1 if sys.version_info < (3, 3) else 0
    try:
        module_name = defaultFormatter.format(moduleName)
        module = __import__(module_name, globals(), locals(), ["*"], level)

    except ImportError:
        moduleBasePath = getModuleBasePath(directories, moduleName)
        module_name = customFormatter.format(moduleName)
        if mc.dirmap(cd=moduleBasePath) not in sys.path:
            sys.path.append(mc.dirmap(cd=moduleBasePath))
        module = __import__(module_name, globals(), locals(), ["*"], level)

    return module

def findAllModules():
    dirs = getDirectories()
    pyFilesList = []
    removeClassList = ["__pycache__", ]
    for path, fileList in dirs.items():
        for file in fileList:
            path_ = path + '//' + file
            if os.path.isdir(path_) and str(file) not in removeClassList:
                pyFilesList.append(file)

    return pyFilesList

def findLastNumber(nameList, basename):
    """

    :param nameList:
    :param baseName:
    :return:
    """
    existValue = 0
    numberList = []
    # list all transforms and find the existing value in them names:
    transformList = mc.ls(selection=False, transforms=True)
    for transform in transformList:
        if basename in transform:
            endNumber = transform.partition(basename)[2]
            if "_" in endNumber and not ":" in endNumber:
                number = endNumber[:endNumber.find("_")]
                try:
                    if int(number) not in numberList:
                        numberList.append(int(number))
                except ValueError:
                    pass

    # sorted(numberList) doesn't work properly as expected after 5 elements.
    numberList.sort()
    numberList.reverse()
    if numberList:
        # get the greather value (first item):
        existValue = numberList[0]

    # work with created guides in the scene:
    lastValue = 0
    for n in nameList:
        # verify if there the basename in the name:
        if n.find(basename) == 0:
            # get the number in the end of the basename:
            suffix = n.partition(basename)[2]
            # verify if the got suffix has numbers:
            if re.match("^[0-9]*$", suffix):
                # store this numbers as integers:
                numberElement = int(suffix)
                # verify if this got number is greather than the last number (value) in order to return them:
                if numberElement > lastValue:
                    lastValue = numberElement

    # analysis which value must be returned:
    if lastValue > existValue:
        finalValue = lastValue
    else:
        finalValue = existValue
    return finalValue

def findModuleLastNumber(className, typeName):
    """ Find the last used number of this type of module.
        Return its highest number.
    """
    # work with rigged modules in the scene:
    numberList = []
    guideTypeCount = 0
    # list all transforms and find the existing value in them names:
    transformList = mc.ls(selection=False, transforms=True)
    for transform in transformList:
        if mc.objExists(transform+"."+typeName):
            if mc.getAttr(transform+"."+typeName) == className:
                numberList.append(className)
        # try check if there is a masterGrp and get its counter:
        if mc.objExists(transform+".rigGrp") and mc.getAttr(transform+".rigGrp") == 1:
            guideTypeCount = mc.getAttr(transform+'.'+className+'Count')
    if(guideTypeCount > len(numberList)):
        return guideTypeCount
    else:
        return len(numberList)

def getModulesToBeRigged(instanceList):
    modulesToBeRiggedList = []
    allNamespaceList = mc.namespaceInfo(listNamespace=True)
    for guideModule in instanceList:
        if guideModule.confirmModules():
            guideNamespaceName = guideModule.guideNamespace
            if guideNamespaceName in allNamespaceList:
                    modulesToBeRiggedList.append(guideModule)
    return modulesToBeRiggedList

def getMirroredParentGuide(nodeName):
    parentList = mc.listRelatives(nodeName, parent=True, type="transform")
    if parentList:
        loop = True
        while loop:
            if mc.objExists(parentList[0] + ".guide_base"):
                return parentList[0]
                loop = False
            else:
                parentList = mc.listRelatives(parentList[0], parent=True, type='transform')
                if parentList : loop = True
                else: loop = False

def makeZeroObj(nodeName):
    axisList = ["x", "y", "z"]
    for axis in axisList:
        mc.setAttr(nodeName + ".t" + axis, 0)
        mc.setAttr(nodeName + ".r" + axis, 0)
        mc.setAttr(nodeName + ".s" + axis, 1)

def clearNodeGrp(nodeGrpName='GuideMirror_Grp', attrFind='guide_base_mirror', unparent=False):
    """ Check if there is any node with the attribute attrFind in the nodeGrpName and then unparent its children and delete it.
    """
    if mc.objExists(nodeGrpName):
        foundChildrenList = []
        childrenList = mc.listRelatives(nodeGrpName, children=True, type="transform")
        if childrenList:
            for child in childrenList:
                if mc.objExists(child+"."+attrFind) and mc.getAttr(child+"."+attrFind) == 1:
                    foundChildrenList.append(child)
        if len(foundChildrenList) != 0:
            if unparent:
                for item in foundChildrenList:
                    mc.parent(item, world=True)
                mc.delete(nodeGrpName)
        else:
            mc.delete(nodeGrpName)

def addData(objName="", dataType="staticData"):
    if objName != "":
        mc.addAttr(objName, longName=dataType, attributeType='bool')
        mc.setAttr(objName+"."+dataType, 1)

def zeroGrp(transformList=[]):
    zeroList = []
    if not transformList:
        transformList = mc.ls(selection=True)
    if transformList:
        for transform in transformList:
            suffix = "_Zero_0_Grp"
            transformName = transform
            if transformName.endswith("_Grp"):
                transformName = extractSuffix(transformName)
                if "_Zero_" in transformName:
                    needAddNumber = True
                    while needAddNumber:
                        nodeNumber = str(int(transformName[transformName.rfind("_")+1:])+1)
                        transformName = (transformName[:transformName.rfind("_")+1])+nodeNumber
                        suffix = "_Grp"
                        if not mc.objExists(transformName+suffix):
                            needAddNumber = False
            zeroGrp = mc.duplicate(transform, name=transformName+suffix)[0]
            zeroUserAttrList = mc.listAttr(zeroGrp, userDefined=True)
            if zeroUserAttrList:
                for zUserAttr in zeroUserAttrList:
                    try:
                        mc.deleteAttr(zeroGrp+"."+zUserAttr)
                    except:
                        pass
            allChildrenList = mc.listRelatives(zeroGrp, allDescendents=True, children=True, fullPath=True)
            if allChildrenList:
                mc.delete(allChildrenList)
            sdkGrp = mc.duplicate(zeroGrp, name=transform+'_Sdk_Grp')[0]
            offsetGrp = mc.duplicate(zeroGrp, name=transform+'_Offset_Grp')[0]
            mc.parent(transform, sdkGrp, absolute=True)
            mc.parent(sdkGrp, offsetGrp, absolute=True)
            mc.parent(offsetGrp, zeroGrp, absolute=True)
            
            zeroList.append(zeroGrp)
    return zeroList

def extractSuffix(nodeName):
    """ Remove suffix from a node name and return the base name.
    """
    endSuffixList = ["_Mesh", "_Geo", "_Bs", "_Sk", "_Tgt", "_Ctrl", "_Grp", "_Crv"]
    for endSuffix in endSuffixList:
        if nodeName.endswith(endSuffix):
            baseName = nodeName[:nodeName.rfind(endSuffix)]
            return baseName
        if nodeName.endswith(endSuffix.lower()):
            baseName = nodeName[:nodeName.rfind(endSuffix.lower())]
            return baseName
        if nodeName.endswith(endSuffix.upper()):
            baseName = nodeName[:nodeName.rfind(endSuffix.upper())]
            return baseName
    return nodeName

def getRigCollections():
    data = {}
    allList = mc.ls(type='transform')
    for item in allList:
        if mc.objExists(item + '.guide_base') and mc.getAttr(item + '.guide_base') == 1:
            # module info
            guideNamespace      = item[:item.find(':')]
            guideName           = item[:item.find('__')]
            guideInstance       = item[item.rfind('__') + 2:item.find(':')]
            guideCustomName     = mc.getAttr(item + '.prefix_name')
            guideMirrorAis      = mc.getAttr(item + '.mirror_axis')
            mirrorName          = mc.getAttr(item + '.mirror_name')
            guideMirrorName = [mirrorName[0] + "_", mirrorName[len(mirrorName) - 1:] + "_"]

            guideChildrenList = []
            childrenList = mc.listRelatives(item, allDescendents=True, type='transform')
            if childrenList:
                for child in childrenList:
                    if mc.objExists(child + '.guide_base'):
                        if mc.getAttr(child + '.guide_base') == 1:
                            guideChildrenList.append(child)
            guideParentList = []
            parentNodeList = []
            parentNode = ''
            parentList = mc.listRelatives(item, parent=True, type='transform')
            if parentList:
                next_ = True
                while next_:
                    if mc.objExists(parentList[0] + '.guide_base') and \
                        mc.getAttr(parentList[0] + '.guide_base') == 1:
                        guideParentList.append(parentList[0])
                        next_ = False
                    else:
                        if not parentNodeList:
                            parentNodeList.append(parentList[0])
                        parentList = mc.listRelatives(parentList[0], parent=True, type='transform')
                        if parentList: next_ = True
                        else: next_ = False
                
                if guideParentList:
                    guideParent         = guideParentList[0]
                    parentModule        = guideParent[:guideParent.find('__')]
                    parentInstance      = guideParent[guideParent.rfind('__')+2:guideParent.find(":")] 
                    parentCustomName    = mc.getAttr(guideParent + '.prefix_name')
                    parentMirrorAis     = mc.getAttr(guideParent + '.mirror_axis')
                    mirrorName          = mc.getAttr(guideParent + '.mirror_name')
                    parentMirrorName    = [mirrorName[0]+"_" , mirrorName[len(mirrorName)-1:]+"_"]

                    # if parentNodeList:
                    parentGuideEnd = parentNodeList[0][parentNodeList[0].find(':') + 1:]
                    
                parentNode = mc.listRelatives(item, parent=True, type='transform')[0]

                # print(guideParentList, guideChildrenList)
            if guideParentList and guideChildrenList:
                data[item] = {
                    "guideNamespace"    : guideNamespace,
                    "guideName"         : guideName,
                    "guideInstance"     : guideInstance,
                    "guideCustomName"   : guideCustomName,
                    "guideMirrorAis"    : guideMirrorAis,
                    "guideMirrorName"   : guideMirrorName,
                    "guideParent"       : guideParent,
                    "fatherNode"        : parentNodeList[0],
                    "parentModule"      : parentModule,
                    "parentInstance"    : parentInstance,
                    "parentCustomName"  : parentCustomName,
                    "parentMirrorAis"   : parentMirrorAis,
                    "parentMirrorName"  : parentMirrorName,
                    "parentGuideEnd"    : parentGuideEnd,
                    "parentNode"        : parentNode,
                    "childrenList"      : guideChildrenList
                }
            elif guideParentList:
                data[item] = {
                    "guideNamespace"    : guideNamespace,
                    "guideName"         : guideName,
                    "guideInstance"     : guideInstance,
                    "guideCustomName"   : guideCustomName,
                    "guideMirrorAis"    : guideMirrorAis,
                    "guideMirrorName"   : guideMirrorName,
                    "guideParent"       : guideParent,
                    "fatherNode"        : parentNodeList[0],
                    "parentModule"      : parentModule,
                    "parentInstance"    : parentInstance,
                    "parentCustomName"  : parentCustomName,
                    "parentMirrorAis"   : parentMirrorAis,
                    "parentMirrorName"  : parentMirrorName,
                    "parentGuideEnd"    : parentGuideEnd,
                    "parentNode"        : parentNode,
                    "childrenList"      : []
                }
            elif guideChildrenList:
                data[item] = {
                "guideNamespace"    : guideNamespace,
                "guideName"         : guideName,
                "guideInstance"     : guideInstance,
                "guideCustomName"   : guideCustomName,
                "guideMirrorAis"    : guideMirrorAis,
                "guideMirrorName"   : guideMirrorName,
                "guideParent"       : "",
                "fatherNode"        : "",
                "parentModule"      : "",
                "parentInstance"    : "",
                "parentCustomName"  : "",
                "parentMirrorAis"   : "",
                "parentMirrorName"  : "",
                "parentGuideEnd"    : "",
                "parentNode"        : parentNode,
                "childrenList"      : guideChildrenList
            }
            else:
                data[item] = {
                "guideNamespace"    : guideNamespace,
                "guideName"         : guideName,
                "guideInstance"     : guideInstance,
                "guideCustomName"   : guideCustomName,
                "guideMirrorAis"    : guideMirrorAis,
                "guideMirrorName"   : guideMirrorName,
                "guideParent"       : "",
                "fatherNode"        : "",
                "parentModule"      : "",
                "parentInstance"    : "",
                "parentCustomName"  : "",
                "parentMirrorAis"   : "",
                "parentMirrorName"  : "",
                "parentGuideEnd"    : "",
                "parentNode"        : parentNode,
                "childrenList"      : []
            }


    return  data




