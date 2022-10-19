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














