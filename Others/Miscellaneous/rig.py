# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.0 (tags/v3.8.0:fa919fd, Oct 14 2019, 19:37:50) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: b'D:\\google\xb6\xb3\xba\xdd\xb5w\xba\xd0\\th_tools\\ThRogToolsVersion\\2018\\ThRigTools\\thRigToolsFiles\\thLibrary\\data\\rig.py'
# Compiled at: 2021-10-20 13:25:01
import maya.cmds as cmds, maya.mel as mel, maya.OpenMayaUI as omui, maya.api.OpenMaya as om2, maya.api.OpenMayaAnim as omAnim2, threading, pprint, os, sys, copy, json, cPickle, time, re, random, webbrowser
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
from functools import partial
from ctypes import windll, Structure, c_long, byref

def thAssignNSolverF(objList):
    u"""創建解算器"""
    for n in objList:
        cmds.select(n, r=True)
        mel.eval('assignNSolver ""')


def thSelCreateNonlinearF(list, type):
    u"""創建 nonlinear"""
    melDict = {'bend': 'nonLinear -type bend -lowBound -1 -highBound 1 -curvature 0;', 
       'flare': 'nonLinear -type flare -lowBound -1 -highBound 1 -startFlareX 1 -startFlareZ 1 -endFlareX 1 -endFlareZ 1 -curve 0;', 
       'sine': 'nonLinear -type sine -lowBound -1 -highBound 1 -amplitude 0 -wavelength 2 -dropoff 0 -offset 0;', 
       'squash': 'nonLinear -type squash -lowBound -1 -highBound 1 -startSmoothness 0 -endSmoothness 0 -maxExpandPos 0.5 -expand 1 -factor 0;', 
       'twist': 'nonLinear -type twist -lowBound -1 -highBound 1 -startAngle 0 -endAngle 0;', 
       'wave': 'nonLinear -type wave -minRadius 0 -maxRadius 1 -amplitude 0 -wavelength 1 -dropoff 0 -offset 0;'}
    for n in list:
        cmds.select(n, r=True)
        mel.eval(melDict[type])

    cmds.select(list, r=True)


def reAnimAttrAppF():
    u"""指定屬性移出動畫層"""
    selectList = cmds.ls(sl=True)
    attrList = cmds.channelBox('mainChannelBox', q=True, sma=True)
    if not attrList or not selectList:
        return
    animLayerList = cmds.ls(type='animLayer')
    for n in selectList:
        for attr in attrList:
            for animLayer in animLayerList:
                cmds.animLayer(animLayer, e=True, ra=('{}.{}').format(n, attr))


def thTimeToFrameF(hour=0, minute=0, second=0, frame=0, fps=30, addFrame=0):
    u"""時間換算影格"""
    minute = hour * 60 + minute
    second = minute * 60 + second
    frame = second * fps + frame
    frame += addFrame
    sys.stdout.write(frame)


def thBatchSetKeyToFrameF():
    selectList = cmds.ls(sl=True)
    attrs = cmds.channelBox('mainChannelBox', q=True, sma=True)
    for sel in selectList:
        for attr in attrs:
            try:
                cmds.setKeyframe(('{}.{}').format(sel, attr), time=0, value=0, breakdown=0)
            except:
                continue

        for i, attr in enumerate(attrs, 1):
            for ii, attr1 in enumerate(attrs, 1):
                value = 1 if i == ii else 0
                try:
                    cmds.setKeyframe(('{}.{}').format(sel, attr1), time=i, value=value)
                except:
                    continue

        else:
            for attr1 in attrs:
                try:
                    cmds.setKeyframe(('{}.{}').format(sel, attr1), time=i + 1, value=0)
                except:
                    continue


def thAdsorptionAndConstrain(list_):
    u"""吸附並約束"""
    thEditPivot(list_[:-1], list_[(-1)])
    for n in list_[:-1]:
        cmds.parentConstraint([list_[(-1)], n], mo=True, weight=1)
        cmds.scaleConstraint([list_[(-1)], n], offset=[1, 1, 1], weight=1)


def thDuplicateWithoutChildren(nodes, label='', keepShapes=True):
    u"""複製不帶子層級之物件"""
    if not nodes:
        return []
    duplicates = []
    for obj in nodes:
        dup = cmds.duplicate(obj, n=('{}{}').format(label, obj), rc=True)[0]
        children = cmds.listRelatives(dup, fullPath=True)
        if children:
            if keepShapes:
                children = list(set(children) - set(cmds.ls(children, shapes=True, long=True)))
            if children:
                cmds.delete(children)
        duplicates.append(dup)

    if duplicates:
        cmds.select(duplicates, r=True)
    return duplicates


def thFollowObjAnimF(inObj, outObj, mode='next', ifT=True, ifR=True, start=False, end=False):
    """
    :type mode: str 'next' | 'previous'
    """
    mainGrp = cmds.group(em=True)
    loc = cmds.duplicate(inObj, rr=True, po=True, rc=True)[0]
    locGrp = cmds.group(loc)
    cmds.parent(locGrp, mainGrp)
    cmds.parentConstraint([outObj, loc], mo=True, weight=1)
    range_ = 1
    if start is not None and end is not None:
        cmds.currentTime(start)
        range_ = end - start
    for i in range(range_):
        mel.eval(('nextOrPreviousFrame "{}"').format(mode))
        if ifT:
            cmds.xform(inObj, wd=True, t=cmds.xform(loc, q=True, wd=True, t=True))
        if ifR:
            cmds.xform(inObj, wd=True, ro=cmds.xform(loc, q=True, wd=True, ro=True))
        cmds.setKeyframe(inObj, breakdown=0, hierarchy='none', controlPoints=0, shape=0)

    cmds.delete(mainGrp)
    cmds.select([inObj, outObj], r=True)
    return


def thFaceToCam(obj):
    u"""選擇面向攝影機的面"""
    minAngle = 180
    angleScalar = mel.eval(('sind({})').format(minAngle))
    faces = cmds.polyInfo(obj, fn=True)
    cameraName = cmds.lookThru(cmds.paneLayout('viewPanes', q=True, activePane=True), q=True)
    cameraMatrix = cmds.xform(cameraName, q=True, m=True, ws=True)
    camAx = [0, 0, 1]
    camAxis = mel.eval(('pointMatrixMult({{{}}}, {{{}}})').format(str(camAx)[1:-1], str(cameraMatrix)[1:-1]))
    facesSelected = []
    index = 0
    for face in faces:
        buffer = [ n for n in face[:-1].split(' ') if n ]
        faceNum = int(buffer[1][:-1])
        axis = [
         float(buffer[2]), float(buffer[3]), float(buffer[4])]
        transform = cmds.xform(obj, q=True, m=True, ws=True)
        worldAxis = mel.eval(('pointMatrixMult({{{}}}, {{{}}})').format(str(axis)[1:-1], str(transform)[1:-1]))
        dotProd = mel.eval(('dotProduct({{{}}}, {{{}}}, 1)').format(str(worldAxis)[1:-1], str(camAxis)[1:-1]))
        if dotProd > angleScalar:
            facesSelected.append(faceNum)

    doSelect = [ ('{}.f[{}]').format(obj, n) for n in facesSelected ]
    cmds.select(doSelect, r=True)


def thPivotToWorld(list_):
    u"""軸心到世界中心"""
    cmds.xform(list_, ws=True, a=True, rp=[0, 0, 0])
    cmds.xform(list_, ws=True, a=True, sp=[0, 0, 0])


def thPrintUseNucleus():
    u"""打印使用的解算器名稱"""
    selectList = cmds.ls(sl=True)
    if not selectList:
        return
    shapeList = cmds.listRelatives(selectList, f=True, s=True)
    nucleusList = []
    for n in shapeList:
        nucleus = cmds.listConnections(n + '.currentState', s=False)
        if nucleus:
            nucleusList.append(nucleus[0])

    nucleusList = list(set(nucleusList))
    sys.stdout.write(nucleusList)


def thDeleteNotNucleus():
    u"""刪除未使用的解算器"""
    delList = []
    nucleusList = cmds.ls(type='nucleus')
    for n in nucleusList:
        objs = cmds.listConnections(n + '.startFrame', s=False)
        if not objs:
            delList.append(n)

    if delList:
        cmds.delete(delList)


def thSetPaintWeightFree(list_):
    u"""關閉選擇物件權重限制"""
    skinNodeList = thFindSkinNode(list_)
    for skinNode in skinNodeList:
        cmds.setAttr(skinNode + '.maintainMaxInfluences', 0)


def thFilterNameList(list_, str_, mode='yes'):
    u"""篩選指定字符物件"""
    newList = []
    if mode == 'yes':
        for n in list_:
            if str_ in n:
                newList.append(n)

    elif mode == 'no':
        for n in list_:
            if str_ not in n:
                newList.append(n)

    return newList


def thGetPolyUvPos(vertexList):
    """get vertex uv pos"""
    uvList = []
    uvListPos = []
    for n in vertexList:
        uv = cmds.polyListComponentConversion(n, fvf=True, tuv=True, vfa=True)[0]
        uvPos = cmds.polyEditUV(uv, q=True)
        uvList.append(uv)
        uvListPos.append(uvPos)

    return [
     uvList, uvListPos]


def thPlayBlast(start, end):
    cmds.playblast(format='image', sequenceTime=0, clearCache=1, viewer=1, showOrnaments=1, fp=4, percent=97, compression='maya', quality=100, st=start, et=end)


def thFilterTransformMove(round_=3):
    u"""篩選有數值的 transform"""
    selectList = cmds.ls(sl=True)
    if not selectList:
        return
    findList = [
     'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    findData = [0, 0, 0, 0, 0, 0, 1, 1, 1]
    newList = []
    for n in selectList:
        for ii, nn in enumerate(findList):
            data = cmds.getAttr(('{}.{}').format(n, nn))
            data = round(data, round_)
            if data != findData[ii]:
                newList.append(n)
                break

    cmds.select(newList, r=True)
    return newList


def thBatchSetKey(list_, attr, value, startFrame, addFeame):
    u"""批量 set key"""
    isAddFeame = addFeame
    for i, n in enumerate(list_):
        for ii, nn in enumerate(list_):
            isValue = value if i == ii else 0
            cmds.setKeyframe(nn, time=startFrame + i + isAddFeame, at=attr, value=isValue, itt='linear', ott='linear')

        isAddFeame += addFeame


def thAverageData(dataList, max=1.0):
    u"""回傳列表數值加總為 1 之數值"""
    sum_ = sum(dataList)
    if sum_ == 0:
        len_ = len(dataList)
        return [ max / len_ for i in dataList ]
    else:
        div_ = max / sum_
        data = [ i * div_ for i in dataList ]
        return data


def thFindBlendShapeNode(mesh):
    u"""找連接模型的 blendShape node"""
    hisList = cmds.listHistory(mesh)
    blendNode = [ n for n in hisList if cmds.nodeType(n) == 'blendShape' ]
    return blendNode


def thKeyTangentMode(mode):
    u"""更改 set key tangent"""
    cmds.keyTangent(g=True, itt=mode)
    cmds.keyTangent(g=True, ott=mode)
    sys.stdout.write(('設定 key 模式: {}').format(mode))


def thSwitchJointScaleAttr(joints):
    u"""設置 joint scale 屬性"""
    data = cmds.getAttr(joints[0] + '.segmentScaleCompensate')
    set_data = 0 if data else 1
    for j in joints:
        cmds.setAttr(j + '.segmentScaleCompensate', set_data)

    sys.stdout.write((' set: {}').format(set_data))


def thResetBindPose():
    u"""重設 skin bind pose"""
    dagPoseList = cmds.ls(typ='dagPose')
    if dagPoseList:
        cmds.delete(dagPoseList)
    cmds.dagPose(save=True, bindPose=True)


def thFromPythonPrintSelect():
    u"""以 python 語法打印當前選擇物件"""
    selecyList = cmds.ls(sl=True, fl=True)
    print '-' * 40 + '  Python  ' + '-' * 40
    text = "\nimport maya.cmds as cmds\nreName = ''  # 移除指定字符\naddName = ''  # 添加命名空間\nnotExistsList = []  # 找不到的名稱\nnewList = []  # 新列表\nselecyList = {}\ndoList = [n.replace(reName,'') for n in selecyList] if reName else selecyList\ndoList = [addName+n for n in doList] if addName else doList\nfor n in doList:\n    if cmds.objExists(n):\n        newList.append(n)\n    else:\n        notExistsList.append(n)\ncmds.select(newList, r=True)\nif notExistsList:\n    print(u'找不到: {{}}'.format(notExistsList))\n"
    text = text.format(selecyList)
    print text
    print '-' * 40 + '  Python  ' + '-' * 40


def thIntegrationList(list_1, list_2, quantity):
    u"""隨機抽樣並整合兩個列表"""
    if not len(list_1) == len(list_2):
        return
    index_list = range(len(list_1))
    index_rand = random.sample(index_list, quantity)
    index_other = list(set(index_list) - set(index_rand))
    new_list_1 = [ list_1[i] for i in index_rand ]
    new_list_2 = [ list_2[i] for i in index_other ]
    combine_list = new_list_1 + new_list_2
    cmds.select(combine_list, r=True)


def thDeleteRepeatMaterial(print_=True):
    u"""刪除重複的材質球.
    - 本功能適用於 reference or import
    - 執行會套用最新材質，刪除舊材質
    - 場景中不要存在多個 namespase
    - 執行完成後，請自行刪除 namespase
    """
    materials = cmds.ls(type=['phong', 'lambert', 'blinn', 'phongE'])
    deleteList = []
    splitNamespaseList = []
    namespaseList = []
    noNamespaseList = []
    for n in materials:
        if ':' in n:
            splitNamespaseList.append(n.split(':')[1])
            namespaseList.append(n)
        else:
            noNamespaseList.append(n)

    for n in noNamespaseList:
        if n in splitNamespaseList:
            index = splitNamespaseList.index(n)
            cmds.hyperShade(o=n)
            sel = cmds.ls(sl=True)
            sg = cmds.listConnections(namespaseList[index], type='shadingEngine')[0]
            cmds.sets(sel, e=True, fe=sg)
            deleteList.append(n)
            cmds.delete(n)

    if print_:
        sys.stdout.write((' Delete: {}').format(str(deleteList)))
    return deleteList


def thFindLayerObj(layer):
    u"""返回 animLayer 中的物件"""
    attrs = cmds.animLayer(layer, q=True, attribute=True)
    objs = set([ attr.split('.')[0] for attr in attrs ])
    return objs


def thSelectAnimLayer(select):
    u"""選擇動畫層"""
    root = cmds.animLayer(q=True, r=True)
    layers = cmds.ls(typ='animLayer')
    layer_list = [ l for l in layers if l != root ]
    for layer in cmds.ls(typ='animLayer'):
        if layer != select:
            mel.eval(('animLayerEditorOnSelect("{}", 0)').format(layer))
        else:
            mel.eval(('animLayerEditorOnSelect("{}", 1)').format(layer))

    cmds.animLayer(forceUIRefresh=True)


def thVertexCreateLoc(vtx_list, name='followCv', con_rotate_obj=''):
    u"""頂點創建 follow locator"""
    if not cmds.objExists('def'):
        cmds.group(em=True, n='def')
    if not cmds.objExists('vtxToLoc_grp'):
        cmds.group(em=True, n='vtxToLoc_grp')
        cmds.group(em=True, n='vtxToLocCv_grp')
        cmds.group(em=True, n='vtxToLocCtrl_grp')
        cmds.hide('vtxToLocCv_grp')
        cmds.parent('vtxToLocCv_grp', 'vtxToLocCtrl_grp', 'vtxToLoc_grp')
        cmds.parent('vtxToLoc_grp', 'def')
    if not cmds.objExists(name + '_vtxToLocLoc_grp'):
        cmds.group(em=True, n=name + '_vtxToLocLoc_grp')
        cmds.parent(name + '_vtxToLocLoc_grp', 'vtxToLocCtrl_grp')
    if con_rotate_obj:
        if not cmds.objExists(('{}_vtxToLocRotate_{}').format(name, con_rotate_obj)):
            cmds.group(em=True, n=('{}_vtxToLocRotate_{}').format(name, con_rotate_obj))
            cmds.group(('{}_vtxToLocRotate_{}').format(name, con_rotate_obj), n=('{}_vtxToLocRotate_{}_grp').format(name, con_rotate_obj))
            AdsorptionObj([
             ('{}_vtxToLocRotate_{}_grp').format(name, con_rotate_obj)], con_rotate_obj)
            cmds.orientConstraint([
             con_rotate_obj, ('{}_vtxToLocRotate_{}').format(name, con_rotate_obj)], mo=True, weight=1)
            cmds.parent(('{}_vtxToLocRotate_{}_grp').format(name, con_rotate_obj), 'vtxToLocCtrl_grp')
    loc_list = []
    for index, n in enumerate(vtx_list, 1):
        edges = cmds.polyListComponentConversion(n, fvf=True, te=True, vfa=True)
        edgesList = cmds.filterExpand(edges, ex=1, sm=32)
        cv = cmds.polyToCurve(edgesList[0], form=2, degree=3)
        cv_0 = cmds.rename(cv[0], name + '_vtxToLoc_cv#')
        cv_1 = cmds.rename(cv[1], name + '_vtxToLocEdge_cv#')
        cmds.select(cl=True)
        locator = cmds.spaceLocator(p=[0, 0, 0], n=name + '_vtxToLoc_loc#')[0]
        loc_list.append(locator)
        cmds.createNode('pointOnCurveInfo')
        poitInfo = cmds.createNode('pointOnCurveInfo', n=('{}_vtxToLocLoc_info{}').format(name, index))
        cmds.connectAttr(cv_0 + '.worldSpace', poitInfo + '.inputCurve', f=True)
        getPosition = cmds.getAttr(poitInfo + '.position')[0]
        getMove = cmds.pointPosition(n)
        for ii in range(3):
            ifMove = round(getMove[ii], 2) == round(getPosition[ii], 2)
            if not ifMove:
                cmds.setAttr(poitInfo + '.parameter', 1)
                break

        cmds.connectAttr(poitInfo + '.position', locator + '.translate', f=True)
        if con_rotate_obj:
            cmds.connectAttr(('{}_vtxToLocRotate_{}.r').format(name, con_rotate_obj), locator + '.r', f=True)
        cmds.parent(locator, name + '_vtxToLocLoc_grp')
        cmds.parent(cv_0, 'vtxToLocCv_grp')

    cmds.select(loc_list, r=True)
    return loc_list


def thDisconnectHairNucleus(hair_sys_list):
    u"""斷開 hair sys 與 nucleus 連接"""
    hair_sys_shape_list = cmds.listRelatives(hair_sys_list, f=True, s=True)
    for hair in hair_sys_shape_list:
        in_attr = cmds.connectionInfo(hair + '.startFrame', sfd=True)
        cmds.disconnectAttr(in_attr, hair + '.startFrame')
        in_attr = cmds.connectionInfo(hair + '.nextState', sfd=True)
        cmds.disconnectAttr(in_attr, hair + '.nextState')
        out_attrs = cmds.connectionInfo(hair + '.startState', dfs=True)
        for attr in out_attrs:
            cmds.disconnectAttr(hair + '.startState', attr)

        out_attrs = cmds.connectionInfo(hair + '.currentState', dfs=True)
        for attr in out_attrs:
            cmds.disconnectAttr(hair + '.currentState', attr)


def thBatchOffset(obj_list, con_attr, obj_follow, on_off=True, reverse=False):
    u"""批量物件啟動"""
    if reverse:
        obj_list = obj_list[::-1]
    obj_strat = 0
    obj_end = 1
    if not on_off:
        obj_strat = 1
        obj_end = 0
    cmds.setAttr(obj_follow, 0)
    for n in obj_list:
        cmds.setAttr(n + '.' + con_attr, obj_strat)
        cmds.setDrivenKeyframe(n + '.' + con_attr, cd=obj_follow, itt='linear', ott='linear')

    key_list = [ n + '.' + con_attr for n in obj_list ]
    offset = 10.0 / len(obj_list)
    index = 0
    for i, n in enumerate(obj_list):
        if i < len(obj_list) - 1:
            index += offset
        else:
            index = 10
        cmds.setAttr(obj_follow, index)
        cmds.setAttr(n + '.' + con_attr, obj_end)
        cmds.setDrivenKeyframe(key_list, cd=obj_follow, itt='linear', ott='linear')


def thCopyAndAlign(objs, main):
    u"""複製並對齊"""
    newList = []
    for obj in objs:
        new = cmds.duplicate(main, rr=True, rc=True)[0]
        AdsorptionObj([new], obj, 'tr')
        newList.append(new)

    cmds.delete(main)
    cmds.select(newList, r=True)


def thEditPivot(objs, main):
    u"""編輯軸心"""
    pivot = cmds.xform(main, q=True, ws=True, rp=True)
    for obj in objs:
        cmds.xform(obj, ws=True, a=True, rp=[pivot[0], pivot[1], pivot[2]])
        cmds.xform(obj, ws=True, a=True, sp=[pivot[0], pivot[1], pivot[2]])

    cmds.select(objs, r=True)


def thVtxJoint(vertex_list):
    u"""頂點創建 joint"""
    for vertex in vertex_list:
        coordinate = cmds.xform(vertex, q=True, ws=True, t=True)
        cmds.select(cl=True)
        joint = cmds.joint()
        cmds.xform(joint, t=coordinate)


def thCreateTxt(txt, objs, size=1, font='Courier', isCenterPivot=False, rotate=[0, 0, 0]):
    u"""創建說明文字"""
    list_ = []
    for obj in objs:
        node = cmds.textCurves(f=font, t=txt, n=obj, ch=False)
        new_name = cmds.rename(node[0], obj + '_txt_grp#')
        list_.append(new_name)
        children = cmds.listRelatives(new_name, c=True, typ='transform')
        cmds.ungroup(children)
        children = cmds.listRelatives(new_name, c=True, typ='transform')
        for c in children:
            cmds.rename(c, obj + '_txt#')

        cmds.setAttr(new_name + '.template', 1)
        if isCenterPivot:
            cmds.xform(new_name, cp=True)
        cmds.rotate(rotate[0], rotate[1], rotate[2], new_name, r=False, os=True, fo=True)
        AdsorptionObj([new_name], obj, 't')
        cmds.setAttr(new_name + '.s', size, size, size)
        cmds.parent(new_name, obj)

    cmds.select(list_, r=True)
    return list_


def thSetShapeAttr(objs, attr):
    u"""設定 shape attr"""
    shape_list = cmds.listRelatives(objs, f=True, s=True)
    data = cmds.getAttr(shape_list[0] + '.' + attr)
    data = 0 if data else 1
    for shape in shape_list:
        cmds.setAttr(shape + '.' + attr, data)


def thDataTransfer(refList, newList, clean=True, addUp=False, addUpScale=False, scaleList=None, scaleValue=None):
    u"""數值傳遞"""
    attrs = [
     'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    data_0 = []
    for n in refList:
        data_1 = []
        for attr in attrs:
            data_1.append(cmds.getAttr(('{}.{}').format(n, attr)))

        data_0.append(data_1)

    if scaleList:
        defData = [
         0, 0, 0, 0, 0, 0, 1, 1, 1]
        for i, n in enumerate(refList):
            if n not in scaleList:
                continue
            for ii, attr in enumerate(attrs):
                data_0[i][ii] = (data_0[i][ii] - defData[ii]) * scaleValue + defData[ii]

    if addUp:
        addAttr = attrs if addUpScale else attrs[:6]
        for i, n in enumerate(newList):
            for ii, attr in enumerate(addAttr):
                data = cmds.getAttr(('{}.{}').format(n, attr))
                data_0[i][ii] += data

    for i, n in enumerate(newList):
        for ii, attr in enumerate(attrs):
            cmds.setAttr(('{}.{}').format(n, attr), data_0[i][ii])

    if clean:
        stratData = [
         0, 0, 0, 0, 0, 0, 1, 1, 1]
        for n in refList:
            for ii, attr in enumerate(attrs):
                cmds.setAttr(('{}.{}').format(n, attr), stratData[ii])


def thDeleteDrivenKey(objs):
    u"""刪除 driven key"""
    type = ['animCurveUA', 'animCurveUL', 'animCurveUU']
    for obj in objs:
        list_ = cmds.listConnections(obj)
        for n in list_:
            for t in type:
                if cmds.nodeType(n) == t:
                    cmds.delete(n)
                    break


def thPrintMaxInfluencesData():
    u"""打印 max influences"""
    list_ = []
    objs = cmds.ls(sl=True)
    node = thFindSkinNode(objs)
    for i, obj in enumerate(objs):
        data = cmds.getAttr(node[i] + '.maxInfluences')
        list_.append(('{}: {}').format(obj, data))

    sys.stdout.write((', ').join(list_))


def thDynOutliner(objs, main, rename=True):
    u"""歸納力學物件"""
    if main:
        label = main.replace('_dyn_grp', '')
        obj_types = thType(objs)
        types = [
         [
          'hairSystem'], ['nCloth'],
         [
          'nucleus'], ['nRigid'], ['mesh'],
         [
          'airField', 'dragField', 'gravityField',
          'newtonField', 'radialField', 'turbulenceField',
          'uniformField', 'vortexField']]
        tx = [
         'hairSystem', 'nCloth',
         'nucleus', 'nRigid', 'mesh',
         'field']
        if not cmds.objExists('dyn'):
            cmds.group(em=True, n='dyn')
        if not cmds.objExists(label + '_dyn_grp'):
            cmds.group(em=True, n=label + '_dyn_grp')
            cmds.parent(label + '_dyn_grp', 'dyn')
        for i, obj in enumerate(objs):
            inbex = None
            for ii, type_0 in enumerate(types):
                for type_1 in type_0:
                    if obj_types[i] == type_1:
                        inbex = ii
                        break

            typ = 'other' if inbex is None else tx[inbex]
            grp = ('{}_dyn_{}_grp').format(label, typ)
            if not cmds.objExists(grp):
                cmds.group(em=True, n=grp)
                cmds.parent(grp, label + '_dyn_grp')
            n_name = obj
            if rename:
                n_name = cmds.rename(obj, ('{}_dyn_{}#').format(label, obj_types[i]))
            cmds.parent(n_name, grp)

    return


def thFieldTurbulence(meshList, ctrl, dynNode, name='object'):
    u"""假風場"""
    if not meshList:
        return
    field = cmds.turbulence(n=name + '_turbulenceField#', pos=[
     0, 0, 0], m=5, att=1, f=1, phaseX=0, phaseY=0, phaseZ=0, noiseLevel=0, noiseRatio=0.707, mxd=1, vsh='none', vex=0, vof=[0, 0, 0], vsw=360, tsr=0.5)[0]
    dynNodeShape = cmds.listRelatives(dynNode, s=True)[0]
    cmds.connectDynamic(dynNodeShape, f=field)
    cmds.setAttr(field + '.attenuation', 0)
    cmds.setAttr(field + '.useMaxDistance', 0)
    cmds.addAttr(ctrl, k=True, ln='field', at='enum', en='------:------:')
    cmds.setAttr(ctrl + '.field', e=True, channelBox=True)
    cmds.addAttr(ctrl, k=True, ln='magnitude_', at='double', dv=5)
    cmds.addAttr(ctrl, k=True, ln='frequency_', at='double', dv=1)
    cmds.addAttr(ctrl, k=True, ln='field_wind_X', at='double', dv=1)
    cmds.addAttr(ctrl, k=True, ln='field_wind_Y', at='double', dv=0)
    cmds.addAttr(ctrl, k=True, ln='field_wind_Z', at='double', dv=0)
    ex = ''
    ex += '{0}.magnitude = {1}.magnitude_;\n'
    ex += '{0}.frequency = {1}.frequency_;\n'
    ex += '{0}.tx = frame * {1}.field_wind_X;\n'
    ex += '{0}.ty = frame * {1}.field_wind_Y;\n'
    ex += '{0}.tz = frame * {1}.field_wind_Z;'
    ex = ex.format(field, ctrl)
    cmds.expression(n=('{}_dynField_EX#').format(name), s=ex)


def thGrpParent(objs, reverse=False, layout_=0, select=True, ret=False):
    u"""物件 parent to group.
    :return: str
        頂級父物件
    """
    if reverse:
        objs = objs[::-1]
    grp = objs[:-1]
    obj = objs[1:]
    for i, g in enumerate(grp):
        find = g
        for ii in range(layout_):
            find = cmds.listRelatives(find, ap=True)[0]

        cmds.parent([find, obj[i]])

    if select:
        cmds.select(objs, r=True)
    if ret:
        father = objs[(-1)]
        for i in range(layout_):
            father = cmds.listRelatives(father, ap=True)[0]

        return father


def thCvToFollowLoc(cv_list, quantity, name='obj'):
    u"""曲線上創建跟隨 locator"""
    loc_list = []

    def app(cv, quantity, name):
        loc_list = []
        shape = cmds.listRelatives(cv, f=True, s=True)[0]
        open = cmds.getAttr(shape + '.form')
        open_close = 0 if open else 1
        max_vertex = cmds.getAttr(shape + '.maxValue')
        add_time = max_vertex / (quantity - open_close)
        add = 0
        for i in range(quantity):
            poci = cmds.createNode('pointOnCurveInfo', n=('{}_pointOnCurveInfo{}').format(name, i + 1))
            cmds.setAttr(poci + '.parameter', add)
            cmds.connectAttr(shape + '.worldSpace[0]', poci + '.inputCurve')
            loc = cmds.spaceLocator(n=('{}_locator{}').format(name, i + 1))[0]
            loc_list.append(loc)
            cmds.connectAttr(poci + '.position', loc + '.translate')
            add += add_time
            if add > max_vertex:
                add = max_vertex

        return loc_list

    for i, n in enumerate(cv_list, 1):
        loc_list.extend(app(n, quantity, ('{}{}').format(name, i)))

    cmds.select(loc_list, r=True)
    return loc_list


def thSetNoAni(objs):
    u"""設置不動"""
    if not cmds.objExists('def'):
        cmds.group(em=True, n='def')
    grpList = thLocatorGrp(objs, 'nAnim')
    sys = cmds.group(em=True, n='thNoAnimObjSys#')
    cmds.parent(sys, 'def')
    for i, n in enumerate(objs):
        cGrp1 = cmds.group(em=True, n=('nLoc_{}1').format(grpList[i]))
        cGrp2 = cmds.group(cGrp1, n=('nLoc_{}2').format(grpList[i]))
        cmds.parent(cGrp2, sys)
        cmds.parentConstraint([sys, cGrp1], mo=True, weight=1)
        cmds.connectAttr(('{}.t').format(n), ('{}.t').format(cGrp2))
        cmds.connectAttr(('{}.r').format(n), ('{}.r').format(cGrp2))
        cmds.connectAttr(('{}.t').format(cGrp1), ('{}.t').format(grpList[i]))
        cmds.connectAttr(('{}.r').format(cGrp1), ('{}.r').format(grpList[i]))


def thDelNamespace():
    u"""刪除命名空間"""
    list_ = cmds.namespaceInfo(r=True, lon=True)
    list_ = list_[::-1]
    list_.remove('UI')
    list_.remove('shared')
    for n in list_:
        objs = cmds.namespaceInfo(n, lod=True)
        if objs is None:
            cmds.namespace(rm=n)
        elif not cmds.referenceQuery(objs[0], inr=True):
            cmds.namespace(force=True, mv=[n, ':'])
            cmds.namespace(rm=n)

    return


def thDelUnknown():
    u"""刪除未知節點"""
    nodes = cmds.ls(typ='unknown')
    for n in nodes:
        if cmds.lockNode(n, q=True, l=True):
            cmds.lockNode(n, l=False)

    if nodes:
        cmds.delete(nodes)


def thRandData(objs, attr_list, min, max):
    u"""隨機數值"""
    for obj in objs:
        for attr in attr_list:
            data = random.uniform(min, max)
            cmds.setAttr(obj + '.' + attr, data)


def thSoftToCluster():
    selection = cmds.ls(sl=True)
    sel = selection[0].split('.')
    richSel = om2.MGlobal.getRichSelection()
    richSelList = richSel.getSelection()
    path, component = richSelList.getComponent(0)
    componentFn = om2.MFnSingleIndexedComponent(component)
    cluster = cmds.cluster(rel=True)
    clusterSet = cmds.listConnections(cluster, type='objectSet')
    cmds.select(selection[0], r=True)
    for i in range(0, componentFn.getCompleteData()):
        weight = componentFn.weight(i)
        v = componentFn.element(i)
        w = weight.influence
        vtx = (sel[0] + '.vtx[%d]') % v
        cmds.sets(vtx, add=clusterSet[0])
        cmds.percent(cluster[0], vtx, v=w)

    cmds.select(cluster)


def thFindVtxSame(objs):
    u"""篩選頂點數量相同物件"""
    new_list = []
    type = thType(objs)
    for i, obj in enumerate(objs):
        if type[i] == 'mesh':
            new_list.append(obj)

    new_objs = []
    if len(new_list) > 1:
        main_size = cmds.polyEvaluate(new_list[(-1)], v=True)
        for obj in new_list[:-1]:
            size = cmds.polyEvaluate(obj, v=True)
            if size == main_size:
                new_objs.append(obj)

    new_objs.append(new_list[(-1)])
    return new_objs


def thType(objs):
    u"""回傳物件 type"""
    type_list = []
    for obj in objs:
        shapes = cmds.listRelatives(obj, s=True)
        if shapes:
            type_list.append(cmds.nodeType(shapes[0]))
        else:
            type_list.append(cmds.nodeType(obj))

    return type_list


def thClearStr(list_, str_):
    u"""清除指定字符"""
    new_name_list = []
    for n in list_:
        new_name = n.replace(str_, '')
        new_name_list.append(new_name)
        if new_name != n:
            cmds.rename(n, new_name)

    cmds.select(new_name_list, r=True)
    THRemoveDuplicateNames(new_name_list).app()


def thJointDrawStyle(joints):
    u"""joint 的 displat style"""
    app_dict = {0: 2, 2: 0}
    if not joints:
        joints = cmds.ls(type='joint')
    if joints:
        data = cmds.getAttr(joints[0] + '.drawStyle')
        for j in joints:
            cmds.setAttr(j + '.drawStyle', app_dict[data])


def thGetMouseCoordinates():
    u"""讀取滑鼠座標"""

    class POINT(Structure):
        _fields_ = [
         (
          'x', c_long), ('y', c_long)]

    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return [pt.x, pt.y]


def thSelectJointVtx(joints, mesh):
    u"""選擇與骨骼連接的 vertex"""
    skin_node = thFindSkinNode([mesh])[0]
    vtx_list = []
    for j in joints:
        cmds.select(cl=True)
        cmds.skinCluster(skin_node, e=True, siv=j)
        vtx_list.extend(cmds.ls(sl=True, fl=True))

    cmds.select(list(set(vtx_list)), r=True)


def thGetMaterial(objs):
    u"""讀取材質球名稱"""
    shape = cmds.listRelatives(objs, f=True, s=True)
    sgList = cmds.listConnections(shape, type='shadingEngine')
    matList = [ cmds.listConnections(sg + '.surfaceShader')[0] for sg in sgList ]
    matList = list(set(matList))
    return matList


def thUseSelMaterial(objs):
    u"""套用最後選擇模型之材質"""
    shape = cmds.listRelatives(objs[(-1)], s=True)
    sg = cmds.listConnections(shape, type='shadingEngine')[0]
    for obj in objs[:-1]:
        cmds.sets(obj, e=True, forceElement=sg)


def thBatchEnable(obj_follow, obj_offset, obj_list, con_attr, segmentation=None):
    u"""控制物件屬性依序以 0 至 1 數值啟動.
    :type obj_follow: str 控制跟隨的屬性
    :type obj_offset: str 控制偏移的屬性
    :type obj_list: list 物件列表
    :type con_attr: str 被控制的屬性
    :type segmentation: int
        分割段數，通常等於 len(obj_list)
    """
    out_value = []
    add = 10.0 / segmentation if segmentation else 10.0 / len(obj_list)
    max = add
    min = 0
    for i, obj in enumerate(obj_list):
        max_pma = cmds.createNode('plusMinusAverage', n=obj + '_follow_max_PMA#')
        cmds.setAttr(max_pma + '.operation', 1)
        cmds.setAttr(max_pma + '.input1D[0]', max)
        cmds.connectAttr(obj_offset, max_pma + '.input1D[1]')
        min_pma = cmds.createNode('plusMinusAverage', n=obj + '_follow_min_PMA#')
        cmds.setAttr(min_pma + '.operation', 2)
        cmds.setAttr(min_pma + '.input1D[0]', min)
        cmds.connectAttr(obj_offset, min_pma + '.input1D[1]')
        max_sr = cmds.createNode('setRange', n=obj + '_follow_max_SR#')
        cmds.connectAttr(max_pma + '.output1D', max_sr + '.valueX')
        cmds.setAttr(max_sr + '.oldMaxX', 10)
        cmds.setAttr(max_sr + '.oldMinX', 0)
        cmds.setAttr(max_sr + '.maxX', 10)
        cmds.setAttr(max_sr + '.minX', 0)
        min_sr = cmds.createNode('setRange', n=obj + '_follow_min_SR#')
        cmds.connectAttr(min_pma + '.output1D', min_sr + '.valueX')
        cmds.setAttr(min_sr + '.oldMaxX', 10)
        cmds.setAttr(min_sr + '.oldMinX', 0)
        cmds.setAttr(min_sr + '.maxX', 10)
        cmds.setAttr(min_sr + '.minX', 0)
        sr = cmds.createNode('setRange', n=obj + '_follow_SR#')
        cmds.connectAttr(obj_follow, sr + '.valueX')
        cmds.connectAttr(max_sr + '.outValueX', sr + '.oldMaxX')
        cmds.connectAttr(min_sr + '.outValueX', sr + '.oldMinX')
        cmds.setAttr(sr + '.maxX', 1)
        cmds.setAttr(sr + '.minX', 0)
        cmds.connectAttr(sr + '.outValueX', obj + '.' + con_attr)
        min += add
        max += add


def thOpenPath(mode):
    u"""打開該檔資料夾.
    :type mode: str
        'file' | 'temp' | 'default'
    """
    path = None
    if mode == 'file':
        path = os.path.dirname(cmds.file(q=True, sn=True))
    elif mode == 'temp':
        path = mel.eval('getenv TMPDIR')
    elif mode == 'default':
        path = cmds.workspace(q=True, rd=True)
    os.startfile(path)
    return


def thBatchRename(objs, name, change_children=False):
    u"""批量重新命名
    :type objs: list
    :type name: str
    :type change_children: bool
    """
    new_name = []
    if not change_children:
        for obj in objs:
            new_name.append(cmds.rename(obj, name + '#'))

    else:
        new_list = []
        for obj in objs:
            all_child_list = []
            child_list = cmds.listRelatives(obj, ad=True)
            if child_list:
                all_child_list = child_list
            all_child_list.append(obj)
            new_list.append(all_child_list[::-1])

        index1 = 1
        for list_ in new_list:
            for n in list_:
                new_name.append(cmds.rename(n, ('{}{}_#').format(name, index1)))

            index1 += 1

    return new_name


def thFindJointConnectMesh(jointList):
    u"""Find 連接 joint 的 mesh"""
    skinNodeList = []
    for joint in jointList:
        try:
            skinNodeList.extend(cmds.listConnections(joint + '.lockInfluenceWeights', t='skinCluster'))
        except:
            pass

    skinNodeList = list(set(skinNodeList))
    skinNodeSetList = []
    for skinNode in skinNodeList:
        setList = cmds.listConnections(skinNode + '.message', t='objectSet')
        skinNodeSetList.append(setList[0])

    objList = []
    for skinNodeSet in skinNodeSetList:
        meshList = cmds.listConnections(skinNodeSet + '.memberWireframeColor')
        if meshList:
            objList.append(meshList[0])

    return objList


def thFindSkinJoint(objs):
    u"""回傳連接 skin 的 joint.
    :type objs: list
    """
    joint_list = []
    for n in objs:
        try:
            list_ = cmds.skinCluster(n, q=True, inf=True)
            joint_list.extend(list_)
        except:
            pass

    return joint_list or None


def thSelCreateJoint(objs):
    u"""依據選擇物件中心創建 joint"""
    cl = cmds.cluster(objs)[1]
    cmds.select(cl=True)
    jo = cmds.joint()
    AdsorptionObj([jo], cl, 't')
    cmds.delete(cl)
    return jo


def thMirrorJoint(joints, axial, rename_name=[
 '', ''], automatic_re=True):
    u"""鏡像 joint
    :type joints: list
    :type axial: str
        'x' | 'y' | 'z'
    :type rename_name: list
        [str, str]
    """
    new_joint = []
    l_lift = [
     'left', 'left_', '_left',
     'L_', '_L', 'Left', 'Left_', '_Left']
    r_list = ['right', 'right_', '_right',
     'R_', '_R', 'Right', 'Right_', '_Right']
    find_list = l_lift + r_list
    list_center = len(find_list) / 2
    axial_data = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}
    for j in joints:
        if automatic_re:
            rename_name = [
             '', '']
            if_in = False
            index = 0
            for n in find_list:
                if n in j:
                    if_in = True
                    break
                index += 1

            if if_in:
                rename_name[0] = find_list[index]
                rename_name[1] = None
                if index < list_center:
                    rename_name[1] = find_list[(index + list_center)]
                else:
                    rename_name[1] = find_list[(index - list_center)]
        new_joint.append(cmds.mirrorJoint(j, mb=True, myz=axial_data[axial][0], mxz=axial_data[axial][1], mxy=axial_data[axial][2], sr=rename_name)[0])

    cmds.select(new_joint, r=True)
    return new_joint


def thReplaceJoint(old_joint_list, new_joint_list, if_del=True, if_freeze=True):
    u"""替換 joint"""
    if if_freeze:
        cmds.makeIdentity(new_joint_list, apply=True, t=True, r=True, s=True, n=False, pn=True)
    cmds.delete(old_joint_list, sc=True, c=True, uac=False)
    for i, old_joint in enumerate(old_joint_list):
        child = cmds.listRelatives(old_joint, c=True)
        father = cmds.listRelatives(old_joint, p=True)
        new_joint_father = cmds.listRelatives(new_joint_list[i], p=True)
        if new_joint_father != father:
            cmds.parent(new_joint_list[i], father)
        if child:
            cmds.parent(child, w=True)
        skin_node = thFindSkinNode([old_joint])
        for n in skin_node:
            cmds.skinCluster(n, e=True, mjm=True)

        AdsorptionObj([old_joint], new_joint_list[i], 't')
        xyz = cmds.getAttr(new_joint_list[i] + '.jointOrient')[0]
        cmds.setAttr(old_joint + '.jointOrient', xyz[0], xyz[1], xyz[2])
        for n in skin_node:
            cmds.skinCluster(n, e=True, mjm=False)

        if child:
            cmds.parent(child, old_joint)

    if if_del:
        cmds.delete(new_joint_list)
    cmds.select(cl=True)


def thWeightToCtrl(main_obj, obj, vl_size=1):
    u"""以少數控制多數.
    :type main_obj: list
    :type obj: list
    :type vl_size: float
    """
    vl_cls = THVtxLocator(objs=obj, name='WTC', if_vl=True, vl_size=vl_size)
    vl_cls.create_vl_and_follicle()
    for i, follicle in enumerate(vl_cls.follicle_list):
        cmds.parentConstraint([follicle, obj[i]], mo=True, weight=1)

    joint_list = []
    for n in main_obj:
        cmds.select(cl=True)
        joint_ = cmds.joint(n=n + '_WTC_joint#')
        AdsorptionObj([joint_], n, 'tr')
        joint_list.append(joint_)
        cmds.parent(joint_, n)

    cmds.skinCluster(joint_list, vl_cls.vl, mi=5, dr=4.0, tsb=True)
    cmds.hide(joint_list)
    vl_cls.unite_wight([vl_cls.vl])
    return joint_list


def thRemoveStrNum(str_, if_clear_hyphen=True):
    u"""去掉字符字尾數字.
    :return: list
        [新的字串, 去掉的字符]
    """
    tx = str_
    index = re.search('\\d*$', tx).start()
    tx = tx[:index]
    if if_clear_hyphen:
        index = re.search('_*$', tx).start()
        tx = tx[:index]
    return [
     tx, str_[index:]]


def thLocatorGrp(objs, name=None):
    u"""創建與物件相同軸向的 grp"""
    new_grp_list = []
    for obj in objs:
        remove_num = thRemoveStrNum(obj)
        new_name = None
        if re.search('_*[Gg]rp$', remove_num[0]):
            new_name = remove_num[0] + '#'
        else:
            new_name = remove_num[0] + remove_num[1] + '_grp#'
        if name:
            if not re.search('^' + name, new_name):
                new_name = ('{}_{}').format(name, new_name)
        father = cmds.listRelatives(obj, p=True, f=True)
        new_grp = cmds.group(em=True, n=new_name)
        AdsorptionObj([new_grp], obj)
        if father:
            cmds.parent(new_grp, father[0])
            cmds.makeIdentity(new_grp, apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.parent(obj, new_grp)
        new_grp_list.append(new_grp)

    return new_grp_list


def thObjForObjSkin(obj1, obj2):
    u"""依據物件 skin 物件"""
    joints = thGetSkinJoint([obj1])
    cmds.skinCluster(joints, obj2, mi=5, dr=4.0, tsb=True)


def thDefSineSwirlRig(obj):
    u"""Sine 變形器設定漩渦 rig effects.
    :type obj: str
    """
    sine_node1 = cmds.nonLinear(obj, type='sine', n='def_swirl_sine#')
    sine_node2 = cmds.nonLinear(obj, type='sine', n='def_swirl_sine#')
    cmds.setAttr(sine_node1[0] + '.dropoff', 1)
    cmds.setAttr(sine_node1[0] + '.amplitude', 0.6)
    cmds.setAttr(sine_node1[0] + '.wavelength', 0.5)
    cmds.setAttr(sine_node2[0] + '.offset', 0.13)
    main_grp = cmds.group([sine_node1[1], sine_node2[1]], n='def_swirl_sine_grp#')
    cmds.group([sine_node1[1], sine_node2[1]], n='def_swirl_sine_grp#')
    cmds.rotate(0, 0, 0, sine_node1[1])
    cmds.rotate(0, 90, 0, sine_node2[1])
    cmds.rotate(90, 0, 0, main_grp)
    cmds.connectAttr(sine_node1[0] + '.amplitude', sine_node2[0] + '.amplitude')
    cmds.connectAttr(sine_node1[0] + '.wavelength', sine_node2[0] + '.wavelength')
    cmds.connectAttr(sine_node1[0] + '.dropoff', sine_node2[0] + '.dropoff')
    cmds.select(main_grp, r=True)


def thCtrlDefaultPose(objs, setAttrList=None):
    u"""物件回到初始值"""
    data = {'tx': 0, 'ty': 0, 'tz': 0, 'rx': 0, 'ry': 0, 'rz': 0, 'sx': 1, 'sy': 1, 'sz': 1}
    setAttrList = setAttrList if setAttrList else data.keys()
    for obj in objs:
        for attr in setAttrList:
            if attr not in data:
                continue
            try:
                cmds.setAttr(obj + '.' + attr, data[attr])
            except:
                pass


def thDeleteConstrainNode(objs):
    u"""刪除 constrain node"""
    type_list = [
     'pointConstraint', 'aimConstraint',
     'orientConstraint', 'scaleConstraint',
     'parentConstraint', 'pointOnPolyConstraint',
     'tangentConstraint']
    for obj in objs:
        for type in type_list:
            node = eval('cmds.' + type + '(obj, q=True)')
            if node:
                cmds.delete(node)

    node = cmds.listRelatives(objs, typ=type_list, c=True, f=True)
    if node:
        cmds.delete(node)


def thReplaceCurveShape(objs):
    u"""替換 curve shape.
    :type objs: list
        [被替換的, 主要的 shape]
    """
    out_shape = cmds.listRelatives(objs[(-1)], s=True)
    for obj in objs[:-1]:
        new = cmds.duplicate(objs[(-1)], n='th_copy_shape#', rr=True)
        new_shape = cmds.listRelatives(new, s=True)
        in_shape = cmds.listRelatives(obj, s=True, f=True)
        cmds.parent(new_shape, obj, r=True, s=True)
        cmds.delete(new, in_shape)
        cmds.rename(new_shape, obj + 'Shape')

    cmds.select(objs[:-1])


def thReverseConnect(sel, ctrl_attr, con_attr):
    u"""一對多控制 0 與 1 切換數值.
    :type sel: list
    :type ctrl_attr: list (ctrl, attr)
    :type con_attr: str
    """
    pma = cmds.createNode('plusMinusAverage', n=ctrl_attr[0] + '_' + ctrl_attr[1] + '_conPMA#')
    cmds.setAttr(pma + '.operation', 2)
    cmds.setAttr(pma + '.input1D[0]', 1)
    cmds.connectAttr(ctrl_attr[0] + '.' + ctrl_attr[1], pma + '.input1D[1]')
    for n in sel:
        cmds.connectAttr(pma + '.output1D', n + '.' + con_attr)


def thGetSkinJoint(mesh):
    u"""讀取 skin 的 joint.
    :type mesh: list
    """
    joint_list = []
    for n in mesh:
        skin = thFindSkinNode([n])[0]
        joint = cmds.skinCluster(skin, q=True, wi=True)
        joint_list.extend(joint)

    return joint_list


def thSetCtrlColor(objs, color):
    u"""設定控制器 color.
    :type objs: list
    :type color: int
    """
    shape = cmds.listRelatives(objs, f=True, s=True)
    if color:
        for n in shape:
            cmds.setAttr(n + '.overrideEnabled', 1)
            cmds.setAttr(n + '.overrideColor', color)

    else:
        for n in shape:
            cmds.setAttr(n + '.overrideEnabled', 0)


def thMyController(name=None, style='circle', axial='y', scale=1.0, color=0, lock_hide_attr=[
 0, 0, 0, 0]):
    """Create my style controller.
    :type name: str
    :type style: str
        'square' | 'cube' | 'cones' | 
        'circle' | 'ball' | 'x' | 'locator' | 'joint'
        'grp' | 'handles'
    :type axial: str
        'x' | 'y' | 'z'
    """
    apply_dict = {'square': '\ncurve -d 1 -p -1 0 -1 -p 1 0 -1 -p 1 0 1 \n    -p -1 0 1 -p -1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4', 
       'cube': '\ncurve -d 1 -p -0.5 0.5 0.5 -p -0.5 0.5 -0.5 \n    -p 0.5 0.5 -0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 \n    -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 \n    -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 \n    -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 \n    -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 \n    -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 \n    -k 13 -k 14 -k 15\n', 
       'cones': '\ncurve -d 1 -p 0 0.625442 0 -p 0.5 0 0.5 -p -0.5 0 0.5 \n    -p 0 0.625442 0 -p -0.5 0 -0.5 -p 0.5 0 -0.5 -p 0 0.625442 0 \n    -p 0.5 0 0.5 -p 0.5 0 -0.5 -p 0 -0.625442 0 -p 0.5 0 0.5 \n    -p 0 -0.625442 0 -p -0.5 0 0.5 -p -0.5 0 -0.5 -p 0 -0.625442 0 \n    -p 0.5 0 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 \n    -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15\n', 
       'circle': '\ncircle -c 0 0 0 -nr 0 1 0 -sw 360 -r 1 -d 3 \n    -ut 0 -tol 0.01 -s 8 -ch 0\n', 
       'ball': '\ncurve -d 1 -p 0 1 0 -p 0 0.866025 0.5 -p 0 0.5 0.866025 \n    -p 0 0 1 -p 0 -0.5 0.866025 -p 0 -0.866025 0.5 -p 0 -1 0 \n    -p 0 -0.866025 -0.5 -p 0 -0.5 -0.866025 -p 0 0 -1 \n    -p 0 0.5 -0.866025 -p 0 0.866025 -0.5 -p 0 1 0 \n    -p -0.5 0.866025 0 -p -0.866025 0.5 0 -p -1 0 0 \n    -p -0.866025 -0.5 0 -p -0.5 -0.866025 0 -p 0 -1 0 \n    -p 0.5 -0.866025 0 -p 0.866025 -0.5 0 -p 1 0 0 \n    -p 0.866025 0.5 0 -p 0.5 0.866025 0 -p 0 1 0 -p 0.5 0.866025 0 \n    -p 0.866025 0.5 0 -p 1 0 0 -p 0.866025 0 -0.5 -p 0.5 0 -0.866025 \n    -p 0 0 -1 -p -0.5 0 -0.866025 -p -0.866025 0 -0.5 -p -1 0 0 \n    -p -0.866025 0 0.5 -p -0.5 0 0.866025 -p 0 0 1 -p 0.5 0 0.866025 \n    -p 0.866025 0 0.5 -p 1 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 \n    -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 \n    -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -k 25 -k 26 -k 27 \n    -k 28 -k 29 -k 30 -k 31 -k 32 -k 33 -k 34 -k 35 -k 36 -k 37 \n    -k 38 -k 39\n', 
       'x': '\ncurve -d 1 -p -1 0 0 -p 0 0 0 -p 1 0 0 -p 0 0 0 \n    -p 0 0 -1 -p 0 0 0 -p 0 0 1 -p 0 0 0 -p 0 1 0 -p 0 0 0 \n    -p 0 -1 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10\n', 
       'locator': 'spaceLocator -p 0 0 0', 
       'joint': 'select -cl; joint()', 
       'triangle': '\ncurve -d 1 -p -0.866025 0 -0.75 -p 0.866025 0 -0.75 \n    -p -5.96046e-008 0 0.75 -p -0.866025 0 -0.75 -k 0 -k 1 -k 2 -k 3\n', 
       'arrow': '\ncurve -d 1 -p 0 0 -1.618848 -p -0.693792 0 -0.925056 \n    -p -0.231264 0 -0.925056 -p -0.231264 0 -0.231264 \n    -p -0.925056 0 -0.231264 -p -0.925056 0 -0.693792 \n    -p -1.618848 0 0 -p -0.925056 0 0.693792 \n    -p -0.925056 0 0.231264 -p -0.231264 0 0.231264 \n    -p -0.231264 0 0.925056 -p -0.693792 0 0.925056 \n    -p 0 0 1.618848 -p 0.693792 0 0.925056 -p 0.231264 0 0.925056 \n    -p 0.231264 0 0.231264 -p 0.925056 0 0.231264 \n    -p 0.925056 0 0.693792 -p 1.618848 0 0 -p 0.925056 0 -0.693792 \n    -p 0.925056 0 -0.231264 -p 0.231264 0 -0.231264 \n    -p 0.231264 0 -0.925056 -p 0.693792 0 -0.925056 \n    -p 0 0 -1.618848 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 \n    -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 \n    -k 21 -k 22 -k 23 -k 24\n', 
       'angle1': '\ncurve -d 1 -p 0 0 3.335615 -p -0.667123 0 2.001369 \n    -p -2.001369 0 2.001369 \n    -p -2.001369 0 0.667123 -p -3.335615 0 0 -p -2.001369 0 -0.667123 \n    -p -2.001369 0 -2.001369 -p -0.667123 0 -2.001369 -p 0 0 -3.335615 \n    -p 0.667123 0 -2.001369 -p 2.001369 0 -2.001369 \n    -p 2.001369 0 -0.667123 \n    -p 3.335615 0 0 -p 2.001369 0 0.667123 -p 2.001369 0 2.001369 \n    -p 0.667123 0 2.001369 -p 0 0 3.335615 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 \n    -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16\n', 
       'angle2': '\ncurve -d 1 -p -0.361582 0 -2.61372 -p 0.351251 0 -2.61372 \n    -p 0.885875 0 -0.903955 -p 2.61372 0 -0.361582 \n    -p 2.61372 0 0.361582 -p 0.885875 0 0.903955 \n    -p 0.351251 0 2.61372 -p -0.361582 0 2.61372 \n    -p -0.896206 0 0.903955 -p -2.61372 0 0.361582 \n    -p -2.61372 0 -0.361582 -p -0.896206 0 -0.903955 \n    -p -0.361582 0 -2.61372 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 \n    -k 10 -k 11 -k 12\n', 
       'angle3': '\ncurve -d 1 -p -0.999557 0 0.333186 -p -0.999557 0 -0.333186 \n    -p -0.333186 0 -0.333186 -p -0.333186 0 -0.999557 \n    -p 0.333186 0 -0.999557 -p 0.333186 0 -0.333186 \n    -p 0.999557 0 -0.333186 -p 0.999557 0 0.333186 \n    -p 0.333186 0 0.333186 -p 0.333186 0 0.999557 \n    -p -0.333186 0 0.999557 -p -0.333186 0 0.333186 \n    -p -0.999557 0 0.333186 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 \n    -k 7 -k 8 -k 9 -k 10 -k 11 -k 12    \n', 
       'grp': '\ngroup -em\n', 
       'handles': '\ncurve -d 1 -p 1.5 0 0 -p 2 0.5 0 -p 2.5 0 0 -p 2 -0.5 0 \n    -p 1.5 0 0 -p 0 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 ;\n', 
       'hexagon': '\ncurve -d 1 -p -0.5 0 -0.866026 -p -1 0 -1.49012e-07 \n    -p -0.5 0 0.866025 -p 0.5 0 0.866025 -p 1 0 0 \n    -p 0.5 0 -0.866025 -p -0.5 0 -0.866026 \n-k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 ;\n'}
    ctrl = mel.eval(apply_dict[style])
    if isinstance(ctrl, list):
        ctrl = ctrl[0]
    rotate_dict = {'x': 'cmds.setAttr(ctrl+".r", 0, 0, 90)', 
       'z': 'cmds.setAttr(ctrl+".r", 90, 0, 0)'}
    if axial != 'y':
        exec rotate_dict[axial]
    if scale != 1.0:
        cmds.setAttr(ctrl + '.s', scale, scale, scale)
    if axial != 'y' or scale != 1.0:
        cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0, pn=1)
    if color and style != 'joint':
        thSetCtrlColor([ctrl], color)
    if name is not None:
        ctrl = cmds.rename(ctrl, name + '#')
    thLockHiddenAttr([ctrl], lock_hide_attr)
    return ctrl


def thFindSkinNode(objs):
    """Find skin node.
    :type objs: list
    """
    doList = []
    for n in objs:
        if '.' in n:
            doList.append(n.split('.')[0])
        else:
            doList.append(n)

    doList = list(set(doList))
    skin_node_list = []
    for n in doList:
        try:
            node = mel.eval(('findRelatedSkinCluster {}').format(n))
            if node:
                skin_node_list.append(node)
        except:
            pass

    return skin_node_list


def thObjectCurve(objs, if_rebuild=True, if_del_obj=False, if_re_coordinate=True):
    u"""依據物件創建 curve.
    :type objs: list
    :type if_smooth: bool
    :type if_del_obj: bool
    :rtype: str
    """
    xyz = []
    for obj in objs:
        xyz.append(cmds.xform(obj, q=True, ws=True, t=True))

    cv = cmds.curve(d=1, p=xyz)
    data = len(objs) - 1
    if if_rebuild:
        cmds.rebuildCurve(cv, ch=False, rpo=True, rt=False, end=True, kr=False, kcp=False, kep=True, kt=False, s=data, d=3, tol=0.01)
        if if_re_coordinate:
            for i, n in enumerate(objs):
                cmds.xform(('{}.ep[{}]').format(cv, i), ws=True, t=xyz[i])

    if if_del_obj:
        cmds.delete(objs)
    cmds.select(cv, r=True)
    return cv


def thSetSkinWeightInfluences(mesh_list, influences):
    u"""限制 skin weight influences.
    :type mesh_list: list
    :type influences: int
    """
    progressBar = ThQProgressBar(2)
    progressBar.setStrat(0, 'Mesh', len(mesh_list))
    for m in mesh_list:
        progressBar.setFrame(0)
        skin_node = thFindSkinNode([m])[0]
        if THCheckInfluences([m]).max_inf > influences:
            vertex_num = cmds.polyEvaluate(m, v=True)
            joint_list = thGetSkinJoint([m])
            for j in joint_list:
                cmds.setAttr(j + '.liw', 0)

            progressBar.setStrat(1, 'Vertex', vertex_num)
            for v in range(vertex_num):
                progressBar.setFrame(1)
                vertex = ('{0}.vtx[{1}]').format(m, v)
                data = {}
                for joint_ in joint_list:
                    weight = cmds.skinPercent(skin_node, vertex, t=joint_, query=True, value=True)
                    if weight > 0:
                        data[joint_] = weight

                if len(data) > influences:
                    sort_weight = sorted(data.items(), reverse=True, key=lambda item: item[1])
                    for w in sort_weight[influences:]:
                        cmds.skinPercent(skin_node, vertex, tv=[w[0], 0])

            cmds.setAttr(skin_node + '.maxInfluences', influences)
        else:
            cmds.setAttr(skin_node + '.maxInfluences', influences)

    progressBar.deleteLater()


def thDoRoundSkinWeight(mesh_list, round_weight):
    u"""權重值四捨五入.
    :type mesh_list: list
    :type round: int
    """
    progressBar = ThQProgressBar(2)
    progressBar.setStrat(0, 'Mesh', len(mesh_list))
    for mesh in mesh_list:
        progressBar.setFrame(0)
        vertex_num = cmds.polyEvaluate(mesh, v=True)
        joint_list = thGetSkinJoint([mesh])
        skin_node = thFindSkinNode([mesh])[0]
        joint_size = len(joint_list)
        for j in joint_list:
            cmds.setAttr(j + '.liw', 0)

        progressBar.setStrat(1, 'Joint', len(joint_list))
        for joint_ in joint_list:
            progressBar.setFrame(1)
            for v in range(vertex_num):
                vertex = ('{0}.vtx[{1}]').format(mesh, v)
                weight = cmds.skinPercent(skin_node, vertex, t=joint_, query=True, value=True)
                new_weight = round(weight, round_weight)
                if new_weight != weight:
                    cmds.skinPercent(skin_node, vertex, tv=[
                     joint_, new_weight])

            cmds.setAttr(joint_ + '.liw', 1)

        for j in joint_list:
            cmds.setAttr(j + '.liw', 0)

    progressBar.deleteLater()


def thLockHiddenAttr(objs, trsv, on_off=True):
    u"""鎖定並隱藏屬性.
    :type objs: list
    :type trsv: list
        [bool, bool, bool, bool]
    :type on_off: bool
    """
    if sum(trsv):
        reverse = 0 if on_off else 1
        attr = [
         [
          'tx', 'ty', 'tz'],
         [
          'rx', 'ry', 'rz'],
         [
          'sx', 'sy', 'sz'],
         [
          'v']]
        for obj in objs:
            for i, n in enumerate(trsv):
                if not n:
                    continue
                for nn in attr[i]:
                    cmds.setAttr(obj + '.' + nn, lock=on_off)
                    cmds.setAttr(obj + '.' + nn, keyable=reverse)


class ThCreateInBetweenAttr(object):
    """創建 in between 屬性"""

    def __init__(self, list_=None, attrList=None):
        self.list_ = list_ if list_ else cmds.ls(sl=True)
        self.attrList = attrList if attrList else cmds.channelBox('mainChannelBox', q=True, sma=True)
        if not self.list_ or not self.attrList:
            return
        ex = ''
        for n in self.list_:
            for attr in self.attrList:
                addAttr = ('INB_{}').format(attr)
                cmds.addAttr(n, ln=addAttr, k=True, at='double', dv=0)
                ex += ('{0}.{1} = sin({0}.{2} * 3.14159);\n').format(n, addAttr, attr)

        cmds.expression(n='InBetweenAttr_EX#', s=ex)


class ThGrpSaveData(object):
    """保存數據"""

    def __init__(self, sys='ThGrpSaveData_data'):
        self.sys = sys

    def saveF(self, data):
        self.data = data
        if not cmds.objExists(self.sys):
            cmds.group(em=True, n=self.sys)
            cmds.addAttr(self.sys, sn='nts', ln='notes', dt='string')
            cmds.setAttr(self.sys + '.notes', self.data, type='string')

    def getF(self):
        if cmds.objExists(self.sys):
            self.data = eval(cmds.getAttr(self.sys + '.notes'))
            return self.data


class ThEditSelectJointSkinWeight(object):
    """編輯指定骨骼權重"""

    def editF(self, mesh, jointList, copyWeightMode='copy'):
        if cmds.objExists('ThEditSelectJointSkinWeight_data'):
            cmds.warning('數據已存在，請先手動刪除應用 "ThEditSelectJointSkinWeight_data" 在執行本功能!')
            return
        self.mesh = mesh
        self.jointList = [ j for j in jointList if cmds.nodeType(j) == 'joint' ]
        self.copyWeightMode = copyWeightMode
        self.skinNode = thFindSkinNode([self.mesh])[0]
        self._reJointListF(self.mesh, self.jointList)
        self._getSkinVtxF()
        self._copySkinMeshF()
        self._copyEditSkinMeshF()
        self._saveF()
        cmds.parent(self.newMesh, self.newEditMesh, 'ThEditSelectJointSkinWeight_data')
        cmds.select(self.newEditMesh, r=True)

    def modifyF(self):
        gsa = ThGrpSaveData('ThEditSelectJointSkinWeight_data')
        data = gsa.getF()
        THMoveSkinWeightOm2(objs=[
         data['newMesh']], old_joint_list=data['jointList'][:-1], new_joint_list=[
         data['jointList'][(-1)]])
        self._reJointListF(data['newEditMesh'], data['jointList'])
        ThTwoObjWeightBlend(refObj=data['newEditMesh'], mainObjList=[
         data['newMesh']], refJointList=data['jointList'], mainJointList=[
         data['jointList'][(-1)]], om2=True, doPruneWeightsArgList=False)

    def _reJointListF(self, mesh, jointList):
        u"""添加骨骼列表"""
        skinJointList = thFindSkinJoint([mesh])
        for j in jointList:
            if j not in skinJointList:
                cmds.skinCluster(self.skinNode, e=True, ai=j, wt=0)

    def _saveF(self):
        u"""保存數據"""
        data = {'mesh': self.mesh, 
           'jointList': self.jointList, 
           'newMesh': self.newMesh, 
           'newEditMesh': self.newEditMesh}
        gsd = ThGrpSaveData('ThEditSelectJointSkinWeight_data')
        gsd.saveF(data)

    def _copyEditSkinMeshF(self):
        u"""複製編輯權重模型"""
        self.newEditMesh = cmds.duplicate(self.newMesh, rr=True)[0]
        newEditMeshVtxList = [ ('{}.{}').format(self.newEditMesh, n) for n in self.skinVtxList ]
        newEditMeshFaceList = cmds.polyListComponentConversion(newEditMeshVtxList, tf=True)
        cmds.select(newEditMeshFaceList, r=True)
        cmds.select(('{}.f[*]').format(self.newEditMesh), tgl=True)
        if cmds.ls(sl=True):
            cmds.delete()
        skinObjList = self.jointList + [self.newEditMesh]
        if self.copyWeightMode == 'copy':
            cmds.skinCluster(skinObjList, tsb=True)
            tcsaw = THCopySkinAndWeight([self.mesh], [self.newEditMesh], 'name')
            tcsaw.copy_skin()
            tcsaw.copy_weight()
            tcsaw.set_max_influences()
        elif self.copyWeightMode == 'skin':
            cmds.skinCluster(skinObjList, mi=1, dr=4, tsb=True)

    def _copySkinMeshF(self):
        u"""複製權重模型"""
        self.newMesh = cmds.duplicate(self.mesh, rr=True)[0]
        ThClearChShapeNode([self.newMesh], False)
        ThCopyWeightApi().copyWeightF(self.mesh, self.newMesh)

    def _getSkinVtxF(self):
        u"""獲取 vtx list"""
        self.skinVtxList = []
        for joint in self.jointList:
            cmds.select(cl=True)
            cmds.skinCluster(self.skinNode, siv=joint, e=True)
            selVtx = cmds.ls(sl=True, fl=True)
            if '.' in selVtx[0]:
                self.skinVtxList.extend([ n.split('.')[1] for n in selVtx ])

        self.skinVtxList = list(set(self.skinVtxList))


class ThSmoothAnimCv(object):

    def __init__(self, timeSlider=None):
        self.timeSlider = timeSlider
        self._getCvF()

    def _getCvF(self):
        u"""獲取曲線屬性列表"""
        self.selCvList = cmds.keyframe(q=True, name=True, sl=True)
        if self.selCvList == None:
            cmds.warning('請選擇動畫曲線後再執行本功能!')
            return
        else:
            if self.timeSlider == 'play':
                self.staet = int(cmds.playbackOptions(q=True, min=True))
                self.end = int(cmds.playbackOptions(q=True, max=True))
            else:
                cvData = cmds.keyframe(self.selCvList[0], q=True, timeChange=True, sl=True)
                self.staet = cvData[0]
                self.end = cvData[(-1)]
            return

    def smoothF(self, strongValue=1, keepValue=1):
        u"""
        :type strongValue: int 循環次數
        :type keepValue: float 設定值乘數
        """
        for cv in self.selCvList:
            for k in range(int(strongValue)):
                cvValueList = cmds.keyframe(cv, q=True, time=(self.staet, self.end), valueChange=True)
                cvTimeList = cmds.keyframe(cv, q=True, time=(self.staet, self.end), timeChange=True)
                newCvValueList = []
                newCvValueList.append(cvValueList[0])
                for i in range(1, len(cvValueList) - 1):
                    now = cvValueList[i]
                    past = cvValueList[(i - 1)]
                    future = cvValueList[(i + 1)]
                    average = (now + past + future) / 3
                    deviation = average - now
                    newValue = now + deviation * keepValue
                    newCvValueList.append(newValue)

                newCvValueList.append(cvValueList[(len(cvValueList) - 1)])
                for i in range(len(newCvValueList) - 1):
                    try:
                        cmds.keyframe(cv, e=True, time=(cvTimeList[i],), valueChange=newCvValueList[i])
                    except:
                        pass

    def filterCurveF(self, timeTolerance=0.06):
        selectList = cmds.ls(sl=True)
        for cv in self.selCvList:
            cmds.filterCurve(cv, s=self.staet, e=self.end, filter='simplify', tto=timeTolerance)
            cmds.bakeResults(cv, sb=1, osr=1, t=(self.staet, self.end), pok=1, sac=0)

        cmds.select(selectList, r=True)


class ThBackMocapRotate(object):

    def __init__(self, objectList, timeRange=None):
        self.objectList = objectList
        self.mainGrp = 'backMocapRotate_grp'
        useAnimLayer = cmds.animLayer(objectList, q=True, blr=True) or []
        useAnimLayerLen = len(useAnimLayer)
        if useAnimLayerLen > 1:
            sys.stdout.write('選擇物件處於不同動畫層中!')
            return
        else:
            if timeRange is None:
                timeRange = thGetObjAnimRange(self.objectList)
                if timeRange is None:
                    sys.stdout.write('Not find key node!')
                    return
            cmds.group(em=True, n='backMocapRotate_grp')
            conObjList = []
            for n in self.objectList:
                conObjList.append(self._ctrl(n))

            cmds.bakeResults(conObjList, t=(timeRange[0], timeRange[1]), sm=True)
            cmds.delete(objectList, channels=True, unitlessAnimationCurves=False, hierarchy=False, controlPoints=False, shape=False)
            for i, n in enumerate(objectList):
                cmds.parentConstraint([conObjList[i], n], mo=True, weight=1)

            baseLayer = cmds.animLayer(q=True, r=True)
            if useAnimLayerLen == 1 and baseLayer != useAnimLayer[0]:
                cmds.bakeResults(objectList, t=(timeRange[0], timeRange[1]), dl=useAnimLayer[0], sm=True, rba=True)
            else:
                cmds.bakeResults(objectList, t=(timeRange[0], timeRange[1]), sm=True)
            cmds.delete(self.mainGrp)
            cmds.select(objectList, r=True)
            return

    def _ctrl(self, object):
        mainGrp = cmds.group(em=True, n=object + '_BMR_grp')
        cmds.parent(mainGrp, self.mainGrp)
        cmds.select(cl=True)
        joint1 = cmds.joint(n=object + '_BMR_joint1')
        joint2 = cmds.joint(n=object + '_BMR_joint2')
        cmds.parent(joint1, mainGrp)
        AdsorptionObj([joint1], object, 'tr')
        cmds.makeIdentity(joint1, apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.setAttr(joint2 + '.tx', 1)
        ikNode = cmds.ikHandle(n=object + '_BMR_ik', sj=joint1, ee=joint2, sol='ikSCsolver')
        cmds.parent(ikNode[0], mainGrp)
        locMainGrp = cmds.group(em=True, n=object + '_BMR_locator_main_grp')
        AdsorptionObj([locMainGrp], object, 'tr')
        cmds.parent(locMainGrp, mainGrp)
        locator1 = cmds.spaceLocator(n=object + '_BMR_locator1')[0]
        locatorGrp1 = cmds.group(locator1, n=locator1 + '_grp')
        AdsorptionObj([locatorGrp1], joint2, 'tr')
        cmds.parent(locatorGrp1, locMainGrp)
        locator2 = cmds.spaceLocator(n=object + '_BMR_locator2')[0]
        locatorGrp2 = cmds.group(locator2, n=locator2 + '_grp')
        AdsorptionObj([locatorGrp2], object, 'tr')
        cmds.parent(locatorGrp2, locMainGrp)
        cmds.parent(ikNode[0], locator1)
        cmds.setAttr(locator2 + '.ty', -1)
        cmds.pointConstraint([object, joint1], mo=True, weight=1)
        cmds.parentConstraint([object, locMainGrp], mo=True, weight=1)
        return joint1


class ThLoopValueRangeLimit(object):
    """列表屬性值 0 到 1 循環"""

    def __init__(self, list_, ctrlAttr, attr, range_=1, speed=0.1):
        self.list_ = list_
        self.ctrlAttr = ctrlAttr
        self.attr = attr
        self.range_ = range_
        self.speed = speed
        self.sys = 'ThLoopValueRangeLimit_EX#'
        exStart = ('if ({} < 0)').format(ctrlAttr)
        ex1 = ''
        ex2 = ''
        for n in self.list_:
            value = cmds.getAttr(('{}.{}').format(n, self.attr))
            ex1 += ('    {}.{} = 1 - (((abs({}) * {}) + (1 - {})) % {});\n').format(n, self.attr, ctrlAttr, self.speed, value, self.range_)
            ex2 += ('    {}.{} = (({} * {}) + {}) % {};\n').format(n, self.attr, ctrlAttr, self.speed, value, self.range_)

        ex = exStart + '{\n' + ex1 + '} else {\n' + ex2 + '}'
        cmds.expression(n=self.sys, s=ex)


class ThConversionMatrix(object):
    """列表與矩陣轉換"""

    def convertMatrixF1(self, list_, len_):
        u"""數量分割"""
        list_0 = []
        list_1 = []
        for i, n in enumerate(list_, 1):
            list_1.append(n)
            if i % 4 == 0:
                list_0.append(list_1)
                list_1 = []

        return list_0

    def convertMatrixF2(self, list_, horizontal):
        u"""區間分割"""
        rusList_ = []
        for i in range(horizontal):
            rusList_.append(list_[i::horizontal][0:horizontal])

        return rusList_

    def combineListF(self, list_):
        u"""合併"""
        rusList = [ nn for n in list_ for nn in n ]
        return rusList

    def switchMatrixF(self, list_):
        u"""行列轉換"""
        rusList_0 = []
        vertical = len(list_)
        horizontal = len(list_[0])
        for i in range(horizontal):
            rusList_1 = []
            for ii in range(vertical):
                rusList_1.append(list_[ii][i])

            rusList_0.append(rusList_1)

        return rusList_0


class ThDefToSkin(object):
    """變形器轉換蒙皮權重"""

    def applyF(self, meshList, jointList, offsct=1, ifNewMesh=False, ifDelLattice=False, ifDelDeltaMush=False, ifDelTension=False, dir='y'):
        self.jointList = jointList
        self.offsct = offsct
        self.ifNewMesh = ifNewMesh
        self.ifDelLattice = ifDelLattice
        self.ifDelDeltaMush = ifDelDeltaMush
        self.ifDelTension = ifDelTension
        self.dir = dir
        self.dirId = {'x': 0, 'y': 1, 'z': 2}[self.dir]
        dc = ThDisconnectConnect('ThDefToSkin_ThDisconnectConnect_data')
        dc.switchF(self.jointList, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        rp = ThReconstructionParent(list_=self.jointList, sys='ThDefToSkin_ThReconstructionParent_data')
        rp.apply()
        for mesh in meshList:
            skinData = self._getWeightF(mesh)
            newMesh = self._copySkinMeshF(mesh)
            cwa = ThCopyWeightApi()
            cwa.mesh = newMesh
            cwa.data = [self.jointList, skinData]
            cwa.setWeightDataF(False)

        rp.apply()
        dc.switchF()
        self._delDefF(mesh)
        cmds.select(cl=True)

    def _delDefF(self, mesh):
        u"""刪除變形器"""
        defList = []
        defList += ['baseLattice', 'lattice'] if self.ifDelLattice else []
        defList += ['deltaMush'] if self.ifDelDeltaMush else []
        defList += ['tension'] if self.ifDelTension else []
        his = cmds.listHistory(mesh)
        delList = []
        for n in his:
            for nn in defList:
                if cmds.nodeType(n) == nn:
                    delList.append(n)

        if delList:
            cmds.delete(delList)

    def _copySkinMeshF(self, mesh):
        u"""複製新模型"""
        newMesh = mesh
        if self.ifNewMesh:
            newMesh = cmds.duplicate(mesh, rr=True)[0]
            ThClearChShapeNode(objList=[newMesh], ifPrint=False)
            if not cmds.objExists('defToSkin_mesh_grp'):
                cmds.group(n='defToSkin_mesh_grp', em=True)
            cmds.parent(newMesh, 'defToSkin_mesh_grp')
        else:
            skinNode = thFindSkinNode([mesh])
            if skinNode:
                cmds.delete(skinNode)
        return newMesh

    def _getWeightF(self, mesh):
        u"""獲取權重數據"""
        defVtxData = self._getVtxDataF(mesh)
        skWeightList = []
        for n in self.jointList:
            jointAttr = ('{}.t{}').format(n, self.dir)
            jointAttrData = cmds.getAttr(jointAttr)
            cmds.setAttr(jointAttr, jointAttrData + self.offsct)
            vtxData = self._getVtxDataF(mesh)
            weightList = []
            for ii, nn in enumerate(vtxData):
                weightList.append(abs(nn - defVtxData[ii]))

            skWeightList.extend(weightList)
            cmds.setAttr(jointAttr, jointAttrData)

        skWeightMatrix = ThConversionMatrix().convertMatrixF2(skWeightList, len(defVtxData))
        averageSkWeightMatrix = []
        for n in skWeightMatrix:
            averageSkWeightMatrix.append(thAverageData(n))

        skWeightList = ThConversionMatrix().combineListF(averageSkWeightMatrix)
        return skWeightList

    def _getVtxDataF(self, mesh):
        u"""獲取頂點位置"""
        meshList = om2.MSelectionList().add(mesh)
        meshDagPath = meshList.getDagPath(0)
        fnMesh = om2.MFnMesh(meshDagPath)
        pointList = fnMesh.getPoints(om2.MSpace.kWorld)
        weightList = []
        for n in pointList:
            weightList.append(n[self.dirId])

        return weightList


class ThJointLayoutGrp(object):
    """依據子骨骼數量創建歸納群組"""

    def __init__(self, type='joint', objList=None):
        self.type = type
        self.objList = objList if objList else cmds.ls(sl=True)
        for n in self.objList:
            objLen = len(cmds.listRelatives(n, ad=True, f=True, type=self.type))
            grpName = ('_{}LayGrp_{}').format(self.type, objLen)
            if not cmds.objExists(grpName):
                cmds.group(n=grpName, em=True)
            cmds.parent(n, grpName)

        cmds.select(cl=True)


class ThMoveSkinWeightToNewJoint(object):
    """移動權重到新骨骼"""

    def __init__(self, jointList):
        self.jointList = jointList
        self.newJointList = []
        for j in self.jointList:
            skinMeshList = thFindJointConnectMesh([j])
            if not skinMeshList:
                continue
            cmds.select(cl=True)
            newJoint = cmds.joint(n=('in_{}#').format(j))
            self.newJointList.append(newJoint)
            AdsorptionObj([newJoint], j, 'tr')
            cmds.parent(newJoint, j)
            cmds.makeIdentity(newJoint, apply=True, t=True, r=True, s=True, n=False, pn=True)
            msw = THMoveSkinWeightOm2(objs=skinMeshList, old_joint_list=[j], new_joint_list=[newJoint], opacity=1, ifRemoveInfluence=True)

        cmds.select(self.newJointList, r=True)


class ThSplitAttrData(object):
    """分割屬性權重"""

    def __init__(self, objList=None, attrList=None, sysId=1):
        self.objList = objList if objList else cmds.ls(sl=True)
        self.attrList = attrList if attrList else cmds.channelBox('mainChannelBox', q=True, sma=True)
        self.sys = ('thSplitAttrData_EX{}').format(sysId)
        if not cmds.objExists(self.sys):
            cmds.createNode('expression', n=self.sys)
        self.exData = cmds.expression(self.sys, q=True, s=True) or ''

    def unLockF(self, lock, data=None):
        data = data if data else self.exData
        doAttrList = [ n.split(' = ')[0] for n in data.split('\n') ]
        for n in doAttrList:
            if n:
                cmds.setAttr(n, lock=lock)

    def createF(self):
        self.debugF()
        self.unLockF(False)
        ex = self.exData + '\n'
        for obj in self.objList:
            doAttrList = [ n for n in self.attrList if ('+ {}.{}_2;').format(obj, n) not in self.exData ]
            udAttrList = cmds.listAttr(obj, ud=True) or []
            for n in doAttrList:
                dv = [cmds.getAttr(('{}.{}').format(obj, n)), 0]
                for ii in range(2):
                    addAttr = ('{}_{}').format(n, ii + 1)
                    if addAttr not in udAttrList:
                        cmds.addAttr(obj, ln=addAttr, k=True, at='double', dv=dv[ii])

                ex += ('{0}.{1} = {0}.{1}_1 + {0}.{1}_2;\n').format(obj, n)

        cmds.expression(self.sys, e=True, s=ex)
        self.unLockF(True, ex)
        cmds.select(self.objList, r=True)

    def debugF(self):
        exList = self.exData.split('\n')
        eExList = copy.copy(exList)
        for n in exList:
            if '.O[' in n:
                eExList.remove(n)

        ex = ('\n').join(eExList)
        self.exData = ex
        if self.exData != ex:
            cmds.expression(self.sys, e=True, s=ex)


class ThDelNoneConGrp(object):
    """清理層級下無作用的 group"""

    def __init__(self, list_):
        self.list_ = list_
        grpList = cmds.listRelatives(list_, f=0, ad=True)
        grpTypeList = thType(grpList)
        grpList = [ grp for i, grp in enumerate(grpList) if grpTypeList[i] == 'transform' ]
        grpList = [ grp for grp in grpList if len(cmds.listHistory(grp, leaf=True)) <= 1 ]
        attrList = [
         'tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        attrDataList = [0, 0, 0, 0, 0, 0, 1, 1, 1]
        ungroupList = []
        for grp in grpList:
            for i, attr in enumerate(attrList):
                if cmds.getAttr(('{}.{}').format(grp, attr)) != attrDataList[i]:
                    break
            else:
                try:
                    cmds.ungroup(grp)
                    ungroupList.append(grp)
                except:
                    continue

        sys.stdout.write(('刪除了: {} 個物件').format(len(ungroupList)))


class ThSelectIsTypeCtrl(object):

    def __init__(self, list_, base):
        self.list_ = list_
        self.base = base
        maxValue = cmds.getAttr(('{}.maxValue').format(self.base))
        shape = cmds.listRelatives(self.base, f=True, s=True)[0]
        color = cmds.getAttr(('{}.overrideColor').format(shape))
        result = []
        for n in self.list_:
            cMaxValue = cmds.getAttr(('{}.maxValue').format(n))
            cShape = cmds.listRelatives(n, f=True, s=True)[0]
            cColor = cmds.getAttr(('{}.overrideColor').format(cShape))
            if cMaxValue == maxValue and cColor == color:
                result.append(n)

        if result:
            cmds.select(result + [self.base], r=True)
        else:
            cmds.select(cl=True)


class ThCreateFaceCtrlData(object):
    """創建表情控制器"""
    data = {'cEyeA': [
               'L_eyeild_joint1', 'L_eyeild_joint2'], 
       'cEyeB': [
               'in_L_eyeild_joint1', 'in_L_eyeild_joint2'], 
       'cEyebrows': [
                   'L_eyebrow_joint6'], 
       'chin': 'chin_joint1', 
       'dnEyeA': [
                'L_dn_eyeild_joint1', 'L_dn_eyeild_joint2', 'L_dn_eyeild_joint3'], 
       'dnEyeB': [
                'in_L_dn_eyeild_joint1',
                'in_L_dn_eyeild_joint2',
                'in_L_dn_eyeild_joint3'], 
       'dnMain': 'dn_face_main_joint', 
       'dnMainCheek': [
                     'L_cheek_joint9',
                     'L_cheek_joint10',
                     'C_cheek_joint1',
                     'C_cheek_joint2'], 
       'dnMainEyeA': 'L_dn_eyeild_main_joint', 
       'dnMainEyeB': 'in_L_dn_eyeild_main_joint', 
       'dnOralCavity': [
                      'C_dn_oralCavity_joint2',
                      'L_dn_oralCavity_joint2',
                      'L_dn_oralCavity_joint6'], 
       'dnTeeth': 'dn_teeth_joint', 
       'eyebrows': [
                  'L_eyebrow_joint1',
                  'L_eyebrow_joint2',
                  'L_eyebrow_joint3',
                  'L_eyebrow_joint4',
                  'L_eyebrow_joint5'], 
       'jawCtrl': 'jaw_ctrl', 
       'main': 'face_main_joint', 
       'mainCheek': [
                   'L_none_joint3',
                   'L_none_joint1',
                   'L_cheek_joint2',
                   'L_none_joint2',
                   'L_cheek_joint1'], 
       'mainEye': 'L_eyeild_main_joint', 
       'mainEyebrow': 'L_eyebrow_main_joint', 
       'mainNose': 'nose_main_joint', 
       'noses': [
               'C_nose_joint4',
               'L_nose_joint4',
               'C_nose_joint1',
               'C_none_joint2',
               'L_nose_joint6'], 
       'replaceStr': [
                    'L_', 'R_'], 
       'tongues': [
                 'tongue_joint1',
                 'tongue_joint2',
                 'tongue_joint3',
                 'tongue_joint4',
                 'tongue_joint5'], 
       'upEyeA': [
                'L_up_eyeild_joint1', 'L_up_eyeild_joint2', 'L_up_eyeild_joint3'], 
       'upEyeB': [
                'in_L_up_eyeild_joint1',
                'in_L_up_eyeild_joint2',
                'in_L_up_eyeild_joint3'], 
       'upMain': 'up_face_main_joint', 
       'upMainEyeA': 'L_up_eyeild_main_joint', 
       'upMainEyeB': 'in_L_up_eyeild_main_joint', 
       'upOralCavity': [
                      'C_up_oralCavity_joint4',
                      'L_up_oralCavity_joint4',
                      'L_up_oralCavity_joint8'], 
       'upTeeth': 'up_teeth_joint'}


class ThCreateFaceCtrl(ThCreateFaceCtrlData):

    def __init__(self):
        self.cto = THCtrlToObject(if_use_obj_name=True, replace_str='_joint', ctrl_style='hexagon', ctrl_axial='z', ctrl_color=22, if_parent=False, if_create_main_grp=False)
        if not cmds.objExists(self.data['jawCtrl']):
            self.data['jawCtrl'] = cmds.group(em=True, n='jawOtherCtrlGrp')
        mainCtrl = self.cto.create([self.data['main']])
        upMainCtrl = self.cto.create([self.data['upMain']])
        dnMainCtrl = self.cto.create([self.data['dnMain']])
        cmds.parent(upMainCtrl[1] + dnMainCtrl[1], mainCtrl[0])
        mainEyeCtrlList = self._ctrlF(self.data['mainEye'], 13, upMainCtrl[0][0], 'hexagon')
        upMainEyeACtrlList = self._ctrlF(self.data['upMainEyeA'], 22, mainEyeCtrlList[0][0][0], 'triangle')
        dnMainEyeACtrlList = self._ctrlF(self.data['dnMainEyeA'], 22, mainEyeCtrlList[0][0][0], 'triangle')
        upMainEyeBCtrlList = self._ctrlF(self.data['upMainEyeB'], 6, mainEyeCtrlList[0][0][0], 'square')
        dnMainEyeBCtrlList = self._ctrlF(self.data['dnMainEyeB'], 6, mainEyeCtrlList[0][0][0], 'square')
        for n in self.data['upEyeA']:
            self._ctrlF(n, 14, upMainEyeACtrlList[0][0][0], 'hexagon')

        for n in self.data['cEyeA']:
            self._ctrlF(n, 14, mainEyeCtrlList[0][0][0], 'hexagon')

        for n in self.data['dnEyeA']:
            self._ctrlF(n, 14, dnMainEyeACtrlList[0][0][0], 'hexagon')

        self.cto.ctrl_size = 1.5
        for n in self.data['upEyeB']:
            self._ctrlF(n, 18, upMainEyeBCtrlList[0][0][0], 'hexagon')

        for n in self.data['cEyeB']:
            self._ctrlF(n, 18, mainEyeCtrlList[0][0][0], 'hexagon')

        for n in self.data['dnEyeB']:
            self._ctrlF(n, 18, dnMainEyeBCtrlList[0][0][0], 'hexagon')

        self.cto.ctrl_size = 1
        for n in self.data['mainCheek']:
            self._ctrlF(n, 1, mainCtrl[0][0], 'hexagon')

        for n in self.data['dnMainCheek']:
            self._ctrlF(n, 1, self.data['jawCtrl'], 'hexagon')

        chinCtrlList = self._ctrlF(self.data['chin'], 22, self.data['jawCtrl'], 'hexagon')
        mainEyebrowCtrlList = self._ctrlF(self.data['mainEyebrow'], 13, upMainCtrl[0][0], 'square')
        if mainEyebrowCtrlList:
            for n in self.data['eyebrows']:
                self._ctrlF(n, 22, mainEyebrowCtrlList[0][0][0], 'hexagon')

        for n in self.data['cEyebrows']:
            self._ctrlF(n, 22, upMainCtrl[0][0], 'hexagon')

        self.cto.ctrl_size = 1.5
        mainNoseCtrlList = self._ctrlF(self.data['mainNose'], 13, mainCtrl[0][0], 'hexagon')
        self.cto.ctrl_size = 1
        if mainNoseCtrlList:
            for n in self.data['noses']:
                self._ctrlF(n, 22, mainNoseCtrlList[0][0][0], 'hexagon')

        self.cto.ctrl_size = 4
        self.cto.ctrl_axial = 'y'
        upTeethCtrlList = self._ctrlF(self.data['upTeeth'], 22, dnMainCtrl[0][0], 'hexagon')
        upTeethCtrlList = self._ctrlF(self.data['dnTeeth'], 22, self.data['jawCtrl'], 'hexagon')
        self.cto.ctrl_size = 0.7
        for n in self.data['upOralCavity']:
            self._ctrlF(n, 30, dnMainCtrl[0][0], 'cube')

        self.cto.ctrl_axial = 'z'
        for n in self.data['dnOralCavity']:
            self._ctrlF(n, 30, self.data['jawCtrl'], 'cube')

        self.cto.ctrl_size = 1
        self.cto.ctrl_color = 18
        self.cto.ctrl_style = 'cube'
        self.cto.ctrl_axial = 'x'
        self.cto.if_parent = True
        tonguesCtrl = self.cto.create(self.data['tongues'])
        cmds.parent(tonguesCtrl[1][0], self.data['jawCtrl'])

    def _ctrlF(self, obj, color, father=None, ctrlStyle='hexagon'):
        if not cmds.objExists(obj):
            return
        else:
            father = father if cmds.objExists(father) else None
            splitObj = obj.replace(self.data['replaceStr'][0], self.data['replaceStr'][1])
            objList = [obj] + [splitObj] if splitObj != obj else [obj]
            fatherList = [father] + [father.replace(self.data['replaceStr'][0], self.data['replaceStr'][1])] if father else father
            dataList = []
            self.cto.ctrl_color = color
            self.cto.ctrl_style = ctrlStyle
            for i, obj in enumerate(objList):
                data = self.cto.create([obj])
                dataList.append(data)
                if father:
                    cmds.parent(data[1], fatherList[i])

            return dataList


class ThDuplicateObjConGrpWeight(object):
    """物件變換屬性添加權重設定"""

    def __init__(self, objList, attrList=[
 'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']):
        newCtrlList = []
        for obj in objList:
            newCtrl = cmds.duplicate(obj, po=True, n=('W_{}').format(obj))[0]
            newCtrlList.append(newCtrl)
            father = cmds.listRelatives(obj, ap=True)
            child = cmds.listRelatives(obj, c=True, type='transform')
            cmds.parent(child, newCtrl)
            ex = ''
            for attr in attrList:
                wAttr = ('weight_{}').format(attr)
                cmds.addAttr(newCtrl, ln=wAttr, at='double', k=True, dv=1)
                ex1 = '{newCtrl}.{attr} = {obj}.{attr} * {newCtrl}.{wAttr};\n'
                ex1 = ex1.format(newCtrl=newCtrl, attr=attr, obj=obj, wAttr=wAttr)
                ex += ex1

            cmds.expression(n=('{}_scaleAttr_EX#').format(obj), s=ex)

        cmds.select(newCtrlList, r=True)


class ThDuplicateWithoutChildrenCon(object):
    """複製控制器並連接屬性"""

    def __init__(self, objList):
        self.objList = objList
        self.parentData = []

    def createConCtrlF(self, ifCon=True, ifAffectGrp=True):
        self.newObjList = thDuplicateWithoutChildren(self.objList, 'con_')
        self.newObjGrpList1 = thLocatorGrp(self.newObjList)
        self.newObjGrpList2 = thLocatorGrp(self.newObjGrpList1)
        grp = self._parentF('duplicateWithoutChildrenCon', self.newObjList, self.newObjGrpList2, not ifAffectGrp)
        cto = THCtrlToObject(obj_list=[
         grp], name='duplicateWithoutChildren', ctrl_style='hexagon', ctrl_method='parent', ctrl_size=2, ctrl_color=12, ctrl_axial='z', grp_layout=2, if_create_main_grp=False)
        newMainCtrlGrp = cto.create()[1][0]
        if ifCon:
            self._connectF()
        if ifAffectGrp:
            self._affectGrpF()
        cmds.select(newMainCtrlGrp, r=True)

    def _affectGrpF(self):
        u"""增加連動"""
        self.newLocList = []
        for i, obj in enumerate(self.objList):
            newLoc = cmds.duplicate(obj, po=True, n=('loc_{}').format(obj))[0]
            self.newLocList.append(newLoc)
            father = cmds.listRelatives(obj, ap=True)[0]
            cmds.parentConstraint([father, newLoc], mo=True, weight=1)
            cmds.scaleConstraint([father, newLoc], offset=[1, 1, 1], weight=1)
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                cmds.connectAttr(('{}.{}').format(newLoc, attr), ('{}.{}').format(self.newObjGrpList1[i], attr))

        self.newLocGrpList = thLocatorGrp(self.newLocList)
        self._parentF('duplicateWithoutChildrenLoc', self.newLocList, self.newLocGrpList, False)

    def _connectF(self):
        """connect"""
        for i, obj in enumerate(self.objList):
            listAttr = cmds.listAttr(obj, m=True, k=True, r=True, se=True, v=True, w=True, c=True, u=True)
            for attr in listAttr:
                try:
                    cmds.connectAttr(('{}.{}').format(self.newObjList[i], attr), ('{}.{}').format(obj, attr))
                except:
                    pass

    def _getFatherF(self):
        u"""獲取父層級 ID"""
        if not self.parentData:
            for obj in self.objList:
                lnObjList = cmds.ls(obj, l=True)
                spLnObjList = str(lnObjList).split('|')[-2:0:-1]
                for spLnObj in spLnObjList:
                    if spLnObj in self.objList:
                        self.parentData.append(self.objList.index(spLnObj))
                        break
                else:
                    self.parentData.append(None)

        return

    def _parentF(self, mainGrp, ctrlList, ctrlGrpList, ifParentFather=True):
        """parent"""
        grp = cmds.group(em=True, n=mainGrp + '#')
        if ifParentFather:
            self._getFatherF()
            for i, ctrlGrp in enumerate(ctrlGrpList):
                if self.parentData[i] is None:
                    cmds.parent(ctrlGrp, grp)
                else:
                    cmds.parent(ctrlGrp, ctrlList[self.parentData[i]])

        else:
            cmds.parent(ctrlGrpList, grp)
        cmds.xform(grp, cp=True)
        return grp

    def createConLocF(self, ifParent=False, ifParentFather=True):
        u"""創建連接 grp 的 loc"""
        newList = []
        for n in self.objList:
            strList = n.split('_')
            newStrList = []
            len_ = len(strList)
            len_ = 1 if len_ <= 2 else len_ - 2
            for i in range(len_):
                newStrList.append(strList[i])

            newList.append(('_').join(newStrList))

        newLocList = []
        newLocGrpList = []
        for i, n in enumerate(newList):
            lo = cmds.spaceLocator(n=n + '_loc#')[0]
            newLocList.append(lo)
            grp = cmds.group(lo, n=lo + '_grp#')
            newLocGrpList.append(grp)
            AdsorptionObj([grp], self.objList[i], 'tr')
            attrs = [
             'tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            for attr in attrs:
                cmds.connectAttr(lo + '.' + attr, self.objList[i] + '.' + attr)

        return_ = [
         newLocList, newLocGrpList]
        if ifParent:
            grp = self._parentF('connectLocatorSys', newLocList, newLocGrpList, ifParentFather)
            return_ += [grp]
        cmds.select(newLocList, r=True)
        return return_


class ThSwitchSkinAll(object):
    """設定所有 skin 節點屬性"""
    envelope = 1
    attr = None

    def __init__(self, attr='envelope'):
        nodeList = cmds.ls(typ='skinCluster')
        if not nodeList:
            return
        if ThSwitchSkinAll.attr == attr:
            ThSwitchSkinAll.envelope = 1 if ThSwitchSkinAll.envelope == 0 else 0
        else:
            ThSwitchSkinAll.attr = attr
            ThSwitchSkinAll.envelope = 0
        errorList = []
        for node in nodeList:
            try:
                cmds.setAttr(('{}.{}').format(node, attr), ThSwitchSkinAll.envelope)
            except:
                errorList.append(node)
                continue

        if errorList:
            cmds.select(errorList, r=True)
        sys.stdout.write(('設定 "{}" 屬性值為: {}, 無法持行的物件數量為: {}').format(attr, ThSwitchSkinAll.envelope, len(errorList)))


class ThPtInpObjChangeEx(object):
    """列表屬性驅動 0 到 1 屬性值"""

    def __init__(self, inpObjList):
        self.inpObjList = inpObjList
        self.inpObjAttrList = []
        for n in self.inpObjList:
            list_ = cmds.listAttr(n, m=True, k=True, r=True, se=True, v=True, w=True, c=True, u=True)
            list_ = [ ('{}.{}').format(n, nn) for nn in list_ if '.' not in nn ]
            self.inpObjAttrList.extend(list_)

        self.startData = {}
        self.endData = {}

    def getDataF(self, mode):
        doDict = {'start': self.startData, 'end': self.endData}
        for n in self.inpObjAttrList:
            doDict[mode][n] = cmds.getAttr(n)

    def printF(self, objAttr, ifEx=True):
        doDict = {}
        for k, v in self.startData.items():
            if v == self.endData[k]:
                continue
            doDict[k] = v

        exList = []
        for k, v in doDict.items():
            oldValue = k
            oldMin = self.startData[k]
            oldMax = self.endData[k]
            oldRange = oldMax - oldMin
            exList.append(('clamp(0,1,({}-({}))/{})').format(oldValue, oldMin, oldRange))

        ex = ('{} = ({})/{};').format(objAttr, ('+').join(exList), len(doDict))
        sys.stdout.write(ex)
        if ifEx:
            cmds.expression(s=ex)


class ThSimplifyPolyDoSkin(object):
    sys = 'ThSimplifyPolyDoSkin_data'

    def __init__(self, select=None):
        self.select = select
        self.newMesh = None
        self.base = None
        self.newMesh = None
        self.select = cmds.polyListComponentConversion(self.select, tv=True)
        self._getDataF()
        return

    def hiddenF(self, mode='show'):
        if not cmds.objExists(self.sys):
            return
        if mode == 'show':
            cmds.showHidden(self.sys)
        else:
            cmds.hide(self.sys)

    def _dataF(self):
        u"""保存數據"""
        if not cmds.objExists(self.sys):
            cmds.group(n=self.sys, em=True)
            cmds.addAttr(self.sys, sn='nts', ln='notes', dt='string')
            data = str({'mesh': self.newMesh, 'select': self.select, 'base': self.base})
            cmds.setAttr(self.sys + '.notes', data, type='string')
            print self.select

    def simplifyF(self):
        if cmds.objExists(self.sys):
            cmds.warning('請先刪除 data 再執行!')
            return
        self.base = self.select[0].split('.')[0]
        self.newMesh = cmds.duplicate(self.base, rr=True, rc=True)[0]
        self._dataF()
        cmds.parent(self.newMesh, self.sys)
        face = cmds.polyListComponentConversion(self.select, tf=True)
        newFace = [ ('{}.{}').format(self.newMesh, n.split('.', 1)[1]) for n in face ]
        cmds.select(newFace, r=True)
        cmds.select(('{}.f[*]').format(self.newMesh), tgl=True)
        cmds.delete()
        csaw = THCopySkinAndWeight([self.base], [self.newMesh], 'point')
        csaw.copy_skin()
        csaw.copy_weight()
        csaw.set_max_influences()
        cmds.select(self.newMesh, r=True)

    def _getDataF(self):
        self.data = None
        if cmds.objExists(self.sys):
            self.data = eval(cmds.getAttr(self.sys + '.notes'))
        return

    def copyWeightF(self):
        if not self.data:
            return
        if not cmds.objExists(self.data['mesh']):
            cmds.warning('局部模型不存在!')
            return
        if not cmds.objExists(self.data['base']):
            cmds.warning('base 模型不存在!')
            return
        newMesh = cmds.duplicate(self.data['base'], rr=True)[0]
        ThClearChShapeNode(objList=[newMesh], ifPrint=False)
        csaw = THCopySkinAndWeight([self.data['mesh']], [newMesh], 'point')
        csaw.copy_skin()
        csaw.copy_weight()
        vtxList = cmds.ls(self.data['select'], fl=True)
        vtxListId = [ int(n.split('[')[1][:-1]) for n in vtxList ]
        cwaBase = ThCopyWeightApi()
        cwaBase.getWeightDataF(self.data['base'])
        cwaNew = ThCopyWeightApi()
        cwaNew.getWeightDataF(newMesh)
        cmds.delete(newMesh)
        for joint in cwaBase.data[0]:
            for i in vtxListId:
                cwaBase.dataDict[joint][i] = cwaNew.dataDict[joint][i]

        cwaBase.setWeightDataF()
        cmds.select(self.data['base'], r=True)

    def deleteF(self):
        if cmds.objExists(self.sys):
            cmds.delete(self.sys)


class ThSetListAttrDataToSelect(object):

    def __init__(self):
        u"""先選擇節點最後加選控制器列表"""
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        attrList = cmds.listAttr(selectList[0], m=True, k=True, r=True, se=True, v=True, w=True, c=True)
        data = {}
        for attr in attrList:
            try:
                data[attr] = cmds.getAttr(('{}.{}').format(selectList[0], attr))
            except:
                pass

        for obj in selectList[1:]:
            for attr, value in data.items():
                try:
                    cmds.setAttr(('{}.{}').format(obj, attr), value)
                except:
                    pass


class ThClearChShapeNode(object):
    """刪除多餘 shape"""

    def __init__(self, objList=None, ifPrint=True):
        self.objList = objList
        self.ifPrint = ifPrint
        objShapeList = None
        if self.objList is not None:
            objShapeList = cmds.listRelatives(self.objList, f=True, s=True)
        else:
            objShapeList = cmds.ls(type='shape')
        if not objShapeList:
            return
        else:
            delList = []
            for objShape in objShapeList:
                value = cmds.getAttr(('{}.intermediateObject').format(objShape))
                if value:
                    con = cmds.listConnections(objShape, c=True)
                    if not con:
                        delList.append(objShape)

            if self.ifPrint:
                if delList:
                    cmds.delete(delList)
                    sys.stdout.write(('刪除多餘 shape: {}').format(delList))
            return


class ThSetHIKAttr(object):

    @staticmethod
    def setArmIkF():
        dataList = [0, 1, 1, 1, 1]
        for n in ['Left', 'Right']:
            for nn in ['Arm', 'ForeArm']:
                for iii, nnn in enumerate(dataList, 1):
                    cmds.setAttr(('HIKproperties1.ParamLeaf{}{}Roll{}').format(n, nn, iii), nnn)
                    cmds.setAttr(('HIKproperties1.ParamLeaf{}{}Roll{}').format(n, nn, iii), nnn)


class ThEditBlendShape(object):

    def isSkinWeightCreateJointF(self, node, mesh):
        attrList = cmds.listAttr(('{}.w').format(node), m=True)
        moveTy = 0
        jointList = []
        for attr in attrList:
            joint = thSelCreateJoint(mesh)
            sysName = ('SW_{}').format(attr)
            if cmds.objExists(sysName):
                cmds.select(joint, r=True)
                cmds.warning('場景中有該規範名稱，請先進行清理後再次執行!')
                return
            joint = cmds.rename(joint, sysName)
            jointList.append(joint)
            cmds.move(0, moveTy, 0, joint, r=True)
            moveTy += 1

        cmds.skinCluster(jointList + [mesh], mi=5, dr=4.0, tsb=True)

    def isSkinWeightF(self, node, mesh):
        u"""依據 skin 權重設定 bs 權重"""
        cwa = ThCopyWeightApi()
        cwa.getWeightDataF(mesh, True)
        for joint, weightList in cwa.dataDict.items():
            joint = joint.replace('SW_', '')
            bsId = self.findeIdAttrF(node, joint)[7:-1]
            for vtx, weight in enumerate(weightList):
                cmds.setAttr(('{}.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]').format(node, bsId, vtx), weight)

    def createBlendShapeF(self, objects=None, delHis=False, editShape=False, data=1):
        selectList = objects if objects else cmds.ls(sl=True)
        if not selectList:
            return
        node = cmds.blendShape(selectList, automatic=True)[0]
        for i in range(len(selectList) - 1):
            cmds.setAttr(('{}.w[{}]').format(node, i), data)

        if delHis:
            cmds.delete(selectList, ch=True)
        if editShape:
            cmds.sculptTarget(node, e=True, target=0)
        return node

    def baseShapeF(self, meshList):
        newMeshList = []
        for mesh in meshList:
            his = cmds.listHistory(mesh)
            typeList = ['blendShape', 'skinCluster']
            defList = cmds.ls(his, type=typeList)
            for n in defList:
                cmds.setAttr(n + '.envelope', 0)

            newMesh = cmds.duplicate(mesh, rr=True, rc=True)[0]
            newMeshList.append(newMesh)
            for n in defList:
                cmds.setAttr(n + '.envelope', 1)

            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                cmds.setAttr(('{}.{}').format(newMesh, attr), lock=False, keyable=True)

        return newMeshList

    def differenceF(self, baseMesh, stratMesh, endMesh, ifCopy=True):
        node = cmds.blendShape([endMesh, stratMesh, baseMesh], automatic=True)[0]
        cmds.setAttr(node + '.w[0]', 1)
        cmds.setAttr(node + '.w[1]', -1)
        new = None
        if ifCopy:
            new = cmds.duplicate(baseMesh, rr=True, rc=True)[0]
            cmds.delete(node)
        else:
            new = baseMesh
            cmds.delete(baseMesh, ch=True)
        return new

    def findIdF(self, node):
        attrList = cmds.aliasAttr(node, q=True)
        attrList = attrList[1::2] if attrList else None
        idList = [ int(n.strip('weight')[1:-1]) for n in attrList ] if attrList else []
        index = 0
        for i in idList:
            if index not in idList:
                break
            index += 1

        return index

    def findeIdAttrF(self, node, attr):
        """
        :return: str 'weight[...]'
        """
        attrIDList = cmds.aliasAttr(node, q=True)
        attrList = attrIDList[0::2]
        idList = attrIDList[1::2]
        if attr not in attrList:
            return
        index = attrList.index(attr)
        return idList[index]

    def ctrlF(self, node, base, target, ctrl, mode='up', ctrlMode='addAndCtrl'):
        """
        :type mode: str 
            'up' | 'dn' | 'left' | 'right'
            'upLeft' | 'upRight' | 'dnLeft' | 'dnRight'
        :type ctrlMode: str 'addAndCtrl' | 'ctrl'
        """
        newName = ('{}_{}').format(ctrl, mode)
        if ctrlMode == 'addShape':
            newName = cmds.rename(target, newName)
            self.addF(node, base, [newName])
        elif ctrlMode == 'fromAttr':
            id = self.findeIdAttrF(node, target)
            cmds.aliasAttr(newName, ('{}.{}').format(node, id))
        ex = None
        if mode in ('up', 'dn', 'left', 'right'):
            axial = {'up': ['', 'ty'], 'dn': ['-', 'ty'], 'left': [
                      '-', 'tx'], 
               'right': ['', 'tx']}
            ex = '{}.{} = clamp(0,1,{}{}.{});'
            ex = ex.format(node, newName, axial[mode][0], ctrl, axial[mode][1])
        else:
            axial = {'upLeft': [
                        '', '-'], 
               'upRight': ['', ''], 'dnLeft': [
                        '-', '-'], 
               'dnRight': ['-', '']}
            ex = '{0}.{1} = clamp(0,1,{2}{3}.ty) * clamp(0,1,{4}{3}.tx);'
            ex = ex.format(node, newName, axial[mode][0], ctrl, axial[mode][1])
        cmds.expression(n=newName + '_EX#', s=ex)
        cmds.select(ctrl, r=True)
        return

    def findSelectListIdF(self):
        sel = cmds.optionVar(q='blendShapeEditorTreeViewSelection')
        sel = list(set(sel))
        while '' in sel:
            sel.remove('')

        while '0' in sel:
            sel.remove('0')

        sel = sel[0].split('/')
        while '' in sel:
            sel.remove('')

        return sel

    def findSelectListIdAttrOneF(self):
        sel = self.findSelectListIdF()[0]
        node, id = sel.split('.')
        attrID = ('weight[{}]').format(id)
        attrIDList = cmds.aliasAttr(node, q=True)
        attrList = attrIDList[0::2]
        idList = attrIDList[1::2]
        index = idList.index(attrID)
        return attrList[index]

    def offEditF(self):
        nodeList = cmds.ls(type='blendShape')
        for n in nodeList:
            try:
                cmds.sculptTarget(n, e=True, target=-1)
            except:
                pass

    def getDiffF(self, skinMesh, baseMesh, changeMesh):
        u"""獲取差異"""
        skinNode = thFindSkinNode([skinMesh])
        if not skinNode:
            cmds.warning('需要 skin 節點!')
        shapeNode = self.createBlendShapeF(objects=[baseMesh, skinMesh], editShape=True)
        ThSetMeshPoint().apply(changeMesh, skinMesh)
        newShape = cmds.duplicate(baseMesh, rr=True, rc=True)[0]
        cmds.delete(shapeNode)
        return newShape

    def addF(self, node, base, inpMeshList, data=0, edit=False, nameList=None):
        indexList = []
        for i, n in enumerate(inpMeshList):
            index = self.findIdF(node)
            indexList.append(index)
            cmds.blendShape(node, e=True, t=[base, index, n, 1], w=[index, data])
            if edit:
                cmds.sculptTarget(node, e=True, target=index)
            if nameList:
                cmds.aliasAttr(nameList[i], ('{}.w[{}]').format(node, index))

        return indexList

    def wrapF(self, oldObj, newObj, oldObjBs, wrapMesh=''):
        ThClearChShapeNode([newObj])
        doWrapMesh = wrapMesh
        if wrapMesh == '':
            doWrapMesh = cmds.duplicate(newObj, rr=True, rc=True)[0]
            cmds.select([doWrapMesh, oldObj], r=True)
            mel.eval('doWrapArgList "7" {"1","0","1","2","0","1","0"}')
        self.resetBlendShapeF(doWrapMesh, oldObjBs, False, newObj)
        if wrapMesh == '':
            cmds.delete(doWrapMesh)
        cmds.select(newObj, r=True)

    def resetBlendShapeF(self, mesh, bsNode=None, deleteNode=True, newObj=None):
        u"""重建 BS"""
        doBsNode = bsNode if bsNode else thFindBlendShapeNode([mesh])[0]
        dc = ThDisconnectConnect('ThDisconnectConnectData_resetBlendShapeF')
        dc.switchF([doBsNode])
        attrList = cmds.listAttr(('{}.w').format(doBsNode), m=True)
        for attr in attrList:
            cmds.setAttr(('{}.{}').format(doBsNode, attr), 0)

        newBsMeshList = []
        for i, attr in enumerate(attrList):
            if i:
                cmds.setAttr(('{}.{}').format(doBsNode, attrList[(i - 1)]), 0)
            cmds.setAttr(('{}.{}').format(doBsNode, attr), 1)
            copyMesh = cmds.duplicate(mesh, rr=True, rc=True)[0]
            newBsMeshList.append(copyMesh)
        else:
            cmds.setAttr(('{}.{}').format(doBsNode, attr), 0)

        doNewObj = newObj if newObj else mesh
        newBsNode = cmds.blendShape(doNewObj, automatic=True)[0]
        self.addF(node=newBsNode, base=doNewObj, inpMeshList=newBsMeshList, nameList=attrList)
        dc.switchF()
        dc.transferF(doBsNode, [newBsNode])
        if deleteNode:
            cmds.delete(doBsNode)
        cmds.delete(newBsMeshList)


class THMirrorData(object):

    def __init__(self, referenceList, objs, axial='x', setAttrList=[
 'tx', 'ty', 'tz', 'rx', 'ry', 'rz'], reverseRder=False, transferData=True, mode='reDef'):
        u"""鏡橡數值傳遞.
        :type referenceList: list
        :type objs: list
        """
        self.referenceList = referenceList
        self.objs = objs
        self.axial = axial
        self.setAttrList = setAttrList
        self.reverseRder = reverseRder
        self.transferData = transferData
        self.mode = mode
        self.objLocList = []
        self.deleteList = []
        if self.mode == 'reDef':
            self.mirrorF()
        else:
            self.mirrorF1()

    def mirrorF(self):
        u"""執行 mirror"""
        if self.reverseRder:
            self.referenceList, self.objs = self.objs, self.referenceList
        self._createLocF()
        self._setAttrF()
        cmds.delete(self.deleteList)
        if self.transferData:
            self._transferF()
        self._setScaleF()

    def _createLocF(self):
        u"""創建左右定位器"""
        saveList = copy.copy(self.referenceList)
        saveList.extend(self.objs)
        soad_cls = ThSaveObjsAttrData(objs=saveList, attrList=self.setAttrList)
        soad_cls.save()
        thCtrlDefaultPose(saveList, self.setAttrList)
        for i, obj in enumerate(self.objs):
            ref_loc = cmds.spaceLocator()[0]
            ref_loc_grp1 = cmds.group(ref_loc)
            AdsorptionObj([ref_loc_grp1], self.referenceList[i], 'tr')
            self.deleteList.append(ref_loc_grp1)
            obj_loc = cmds.spaceLocator()[0]
            self.objLocList.append(obj_loc)
            obj_loc_grp1 = cmds.group(obj_loc)
            AdsorptionObj([obj_loc_grp1], obj, 'tr')
            obj_loc_grp2 = cmds.group(obj_loc_grp1)
            self.deleteList.append(obj_loc_grp2)
            cmds.setAttr(obj_loc_grp2 + '.s' + self.axial, -1)
            cmds.pointConstraint([ref_loc, obj_loc], mo=True, w=1)
            cmds.parentConstraint([ref_loc, obj_loc], mo=True, w=1, st=['x', 'y', 'z'])
            cmds.connectAttr(self.referenceList[i] + '.t', ref_loc + '.t')
            cmds.connectAttr(self.referenceList[i] + '.r', ref_loc + '.r')

        soad_cls.redoSave()

    def _setAttrF(self):
        u"""設置屬性"""
        for i, obj in enumerate(self.objs):
            for attr in self.setAttrList:
                data = cmds.getAttr(self.objLocList[i] + '.' + attr)
                try:
                    cmds.setAttr(obj + '.' + attr, data)
                except:
                    pass

    def _setScaleF(self):
        u"""設置縮放"""
        attrList = [
         'sx', 'sy', 'sz']
        for i, obj in enumerate(self.objs):
            for attr in attrList:
                data = cmds.getAttr(self.referenceList[i] + '.' + attr)
                try:
                    cmds.setAttr(obj + '.' + attr, data)
                except:
                    pass

    def _transferF(self):
        u"""傳遞自訂屬性的數據"""
        for i, obj in enumerate(self.objs):
            attrs = cmds.listAttr(self.referenceList[i], ud=True)
            if attrs:
                for attr in attrs:
                    try:
                        cmds.setAttr(obj + '.' + attr, cmds.getAttr(self.referenceList[i] + '.' + attr))
                    except:
                        pass


class ThBatchReference(object):
    """批量 reference"""

    def __init__(self):
        path = cmds.file(q=True, sn=True) or 'D:/'
        fileList = cmds.fileDialog2(startingDirectory=path, fm=4, okc='Select File List')
        if not fileList:
            return
        for file in fileList:
            refName = os.path.splitext(os.path.split(file)[1])[0]
            cmds.file(file, r=True, iv=True, gl=True, mnc=False, ns=refName)


class ThSplitMeshPlane(object):
    """拆分模型平面"""

    def __init__(self, defMesh, quantity=2):
        self.defMesh = defMesh
        self.quantity = quantity

    def createPlane(self):
        self.mainGrp = cmds.group(em=True, n='splitMeshToBs_grp#')
        sy = 1 if self.quantity == 2 else 3
        self.plane = cmds.polyPlane(w=1, h=1, sx=3, sy=sy, ax=[0, 0, 1], cuv=2, ch=0, n='splitMeshToBs_plane#')
        cmds.parent(self.plane[0], self.mainGrp)
        lattice = cmds.lattice(self.plane[0], divisions=[2, 2, 2], objectCentered=True, ldv=[2, 2, 2], n='splitMeshToBs_lattice#')
        cmds.parent([lattice[1], lattice[2]], self.mainGrp)
        cmds.hide(lattice)
        self.size = cmds.xform(self.defMesh, q=True, bb=True)
        cmds.move(self.size[0], [lattice[1] + '.pt[0][0:1][0]', lattice[1] + '.pt[0][0:1][1]'], x=True)
        cmds.move(self.size[3], [lattice[1] + '.pt[1][0:1][0]', lattice[1] + '.pt[1][0:1][1]'], x=True)
        cmds.move(self.size[1], [lattice[1] + '.pt[0:1][0][0]', lattice[1] + '.pt[0:1][0][1]'], y=True)
        cmds.move(self.size[4], [lattice[1] + '.pt[0:1][1][0]', lattice[1] + '.pt[0:1][1][1]'], y=True)
        self.clusterList = []
        if self.quantity == 2:
            cluster = cmds.cluster([
             self.plane[0] + '.vtx[1:2]', self.plane[0] + '.vtx[5:6]'], rel=True, n='splitMeshToBs_row_cluster#')
            self.clusterList.append(cluster[1])
            cmds.parent(cluster[1], self.mainGrp)
        else:
            cluster1 = cmds.cluster([
             self.plane[0] + '.vtx[1:2]', self.plane[0] + '.vtx[5:6]', self.plane[0] + '.vtx[9:10]', self.plane[0] + '.vtx[13:14]'], rel=True, n='splitMeshToBs_row_cluster#')
            self.clusterList.append(cluster1[1])
            cluster2 = cmds.cluster([self.plane[0] + '.vtx[4:11]'], rel=True, n='splitMeshToBs_column_cluster#')
            self.clusterList.append(cluster2[1])
            cmds.parent([cluster1[1], cluster2[1]], self.mainGrp)
        cmds.hide(self.clusterList)
        self.jointList = []
        self.mainJointGrp = cmds.group(em=True, n='splitMeshToBsJoint_grp#')
        cmds.parent(self.mainJointGrp, self.mainGrp)
        if self.quantity == 2:
            jointL = cmds.rename(thSelCreateJoint(self.plane[0] + '.f[2]'), 'splitMeshToBs_L_joint#')
            self.jointList.append(jointL)
            jointR = cmds.rename(thSelCreateJoint(self.plane[0] + '.f[0]'), 'splitMeshToBs_R_joint#')
            self.jointList.append(jointR)
            cmds.skinCluster(self.jointList, self.plane[0], mi=5, dr=4.0, tsb=True)
            cwa = ThCopyWeightApi()
            cwa.getWeightDataF(self.plane[0])
            cwa.editWeightDataF(idList=[2, 3, 6, 7], idListData=[1] * 4, joint=jointL)
            cwa.editWeightDataF(idList=[0, 1, 4, 5], idListData=[1] * 4, joint=jointR)
            cwa.setWeightDataF()
        else:
            jointLUp = cmds.rename(thSelCreateJoint(self.plane[0] + '.f[8]'), 'splitMeshToBs_LUp_joint#')
            self.jointList.append(jointLUp)
            jointRUp = cmds.rename(thSelCreateJoint(self.plane[0] + '.f[6]'), 'splitMeshToBs_RUp_joint#')
            self.jointList.append(jointRUp)
            jointLDn = cmds.rename(thSelCreateJoint(self.plane[0] + '.f[2]'), 'splitMeshToBs_LDn_joint#')
            self.jointList.append(jointLDn)
            jointRDn = cmds.rename(thSelCreateJoint(self.plane[0] + '.f[0]'), 'splitMeshToBs_RDn_joint#')
            self.jointList.append(jointRDn)
            cmds.skinCluster(self.jointList, self.plane[0], mi=5, dr=4.0, tsb=True)
            cwa = ThCopyWeightApi()
            cwa.getWeightDataF(self.plane[0])
            cwa.editWeightDataF(idList=[10, 11, 14, 15], idListData=[1] * 4, joint=jointLUp)
            cwa.editWeightDataF(idList=[8, 9, 12, 13], idListData=[1] * 4, joint=jointRUp)
            cwa.editWeightDataF(idList=[2, 3, 6, 7], idListData=[1] * 4, joint=jointLDn)
            cwa.editWeightDataF(idList=[0, 1, 4, 5], idListData=[1] * 4, joint=jointRDn)
            cwa.setWeightDataF()
        cmds.parent(self.jointList, self.mainJointGrp)
        cmds.xform(self.mainJointGrp, cp=True)
        cmds.hide(self.jointList)
        ctrlSize = (self.size[3] - self.size[0] + (self.size[5] - self.size[2])) / 2
        self.cto = THCtrlToObject(obj_list=[
         self.mainJointGrp], name='splitMeshToBs', ctrl_style='cube', ctrl_method='parent', grp_layout=1, ctrl_color=13, ctrl_size=ctrlSize)
        self.cto.create()
        cmds.parent(self.cto.main_grp, self.mainGrp)
        if self.quantity == 2:
            self._ctrl([6, 2, 1, 5], 'row', ctrlSize / 2)
        else:
            self._ctrl([14, 2, 1, 13], 'row', ctrlSize / 2)
            self._ctrl([11, 7, 4, 8], 'column', ctrlSize / 2)
        cmds.select(self.cto.new_ctrl_list[0], r=True)

    def _ctrl(self, idList, label, size):
        u"""縮放控制器"""
        xyzList = []
        for point in [ ('{}.vtx[{}]').format(self.plane[0], n) for n in idList ]:
            xyzList.append(cmds.xform(point, q=True, ws=True, t=True))

        xyzList.append(xyzList[0])
        xyzList = [ [n[0], n[1], size] for n in xyzList ]
        scaleRowCtrl = cmds.curve(d=1, p=xyzList, n=('splitMeshToBs_{}_ctrl#').format(label))
        thSetCtrlColor(scaleRowCtrl, 22)
        scaleRowCtrlGrp = cmds.group(scaleRowCtrl, n=scaleRowCtrl + '_grp#')
        cmds.parent(scaleRowCtrlGrp, self.cto.new_ctrl_list[0])
        cmds.xform(scaleRowCtrl, cp=True)
        for attr in ['t', 'r', 's']:
            cmds.connectAttr(('{}.{}').format(scaleRowCtrl, attr), ('{}.{}').format(self.clusterList[0] if label == 'row' else self.clusterList[1], attr))


class ThShootAttrAnim(object):
    """動作錄製"""

    def __init__(self):
        self.ifApp = False

    def createCvF(self, degree=2):
        u"""創建 curve"""
        cv = cmds.curve(d=degree, p=self.data)

    def keyF(self, startFrame=1):
        """key"""
        for i, dataList in enumerate(self.data, 0):
            for ii, data in enumerate(dataList):
                cmds.setKeyframe(self.obj, time=i + startFrame, at=self.attr[ii], value=float(data))

    def endF(self, ifClearData=True):
        u"""結束"""
        self.ifClearData = ifClearData
        self.ifApp = False
        if self.ifClearData:
            self.data = self._reDataF(self.data)

    def startF(self, obj, attr=['tx', 'ty', 'tz'], fps=24):
        u"""開始"""
        self.obj = obj
        self.attr = attr
        self.fps = fps
        self.data = []
        self.ifApp = True
        th = threading.Thread(target=self._saveF)
        th.start()

    def _saveF(self):
        u"""紀錄動作"""
        sleep = 1.0 / self.fps
        while self.ifApp:
            time.sleep(sleep)
            data = []
            for n in self.attr:
                data.append(cmds.getAttr(('{}.{}').format(self.obj, n)))

            self.data.append(data)

    def _reDataF(self, data):
        u"""清理起始與結束多餘數據"""
        start = None
        end = None
        for i, n in enumerate(data):
            if n != data[0]:
                start = i
                break

        for i, n in enumerate(data[::-1]):
            if n != data[(-1)]:
                end = i
                break

        newData = [
         data[0]] + data[start:end * -1] + [data[(-1)]]
        return newData


class ThCoordinateCreateMeshEx(object):
    """座標創建 mesh"""

    def __init__(self, list_, offset=0.1, aim='x', inf=5, ifLoop=True):
        self.list_ = list_
        self.offset = offset
        self.aim = aim
        self.inf = inf
        self.ifLoop = ifLoop
        self.appList = self.list_
        if self.ifLoop:
            self.appList = self.list_ + [self.list_[0]]
        aimDict = {'x': 0, 'y': 1, 'z': 2}
        offset1 = []
        newMeshList = []
        range_ = len(self.appList) - 1
        for i in range(range_):
            coordinate1 = cmds.xform(self.appList[i], q=True, ws=True, rp=True)
            coordinate2 = cmds.xform(self.appList[(i + 1)], q=True, ws=True, rp=True)
            coordinate3 = [coordinate2[0], coordinate2[1], coordinate2[2]]
            coordinate4 = [coordinate1[0], coordinate1[1], coordinate1[2]]
            coordinate1[aimDict[self.aim]] += self.offset
            coordinate2[aimDict[self.aim]] += self.offset
            coordinate3[aimDict[self.aim]] -= self.offset
            coordinate4[aimDict[self.aim]] -= self.offset
            coordinateList = [
             coordinate1, coordinate2, coordinate3, coordinate4]
            newMeshList.append(cmds.polyCreateFacet(tx=1, s=1, ch=False, p=coordinateList)[0])

        newMesh = None
        if range_ == 1:
            newMesh = newMeshList[0]
        else:
            newMesh = cmds.polyUnite(newMeshList, ch=False, mergeUVSets=True, centerPivot=True)[0]
            cmds.polyMergeVertex(newMesh, d=0.01, am=True, ch=False)
        cmds.skinCluster(self.list_, newMesh, mi=self.inf, dr=4.0, tsb=True)
        cmds.select(newMesh, r=True)
        return


class ThModifyJointQuantity(object):
    """調整骨骼鍊段數"""

    def __init__(self, start, end, quantity):
        self.start = start
        self.end = end
        self.quantity = quantity
        if self.quantity < 2:
            return
        cmds.parent(self.end, w=True)
        inJointList = cmds.listRelatives(self.start, ad=True, type='joint') or []
        jointList = [self.end] + inJointList + [self.start]
        if self.quantity == 2:
            cmds.parent(self.end, self.start)
        else:
            curve = thObjectCurve(objs=jointList)
            cmds.rebuildCurve(curve, ch=False, rpo=True, rt=False, end=True, kr=False, kcp=False, kep=True, kt=False, s=len(jointList) * 10, d=1, tol=0.01)
            ccj = ThCurveCreateJoint([curve], self.quantity)
            newJointList = ccj.joint_list_all
            cmds.parent(newJointList[(-2)], self.start)
            cmds.parent(end, newJointList[1])
            cmds.delete(curve)
            cmds.delete([newJointList[0], newJointList[(-1)]])
        if inJointList:
            cmds.delete(inJointList)
        cmds.select([self.start, self.end], r=True)


class ThFrameToTime(object):

    def toTime(self, frame, fps=30):
        u"""影格換算時間"""
        key = frame % fps
        second = int(frame / fps)
        minute = 0
        if second >= 60:
            minute = int(second / 60)
            second = second % 60
        hour = 0
        if minute >= 60:
            hour = int(minute / 60)
            minute = minute % 60
        result = ('{}:{}:{}:{}\n').format(hour, minute, second, key)
        sys.stdout.write(result)

    def toFrame(self, Time, fps=30):
        u"""時間換算影格"""
        pass


class ThSetMeshPoint(object):
    """頂點數值傳遞"""
    appSpace = {'object': om2.MSpace.kObject, 'world': om2.MSpace.kWorld}
    inPointList = None
    inMesh = None

    def apply(self, outMesh, inMesh, space='object'):
        self.outMesh = outMesh
        self.inMesh = inMesh
        self.space = space
        self.inPointList = self.getCoordinate(self.inMesh, self.space)
        self.outPointList = self.getCoordinate(self.outMesh, self.space)
        self.setCoordinate(self.inMesh, self.outPointList)
        ThSetMeshPoint.inPointList = self.inPointList
        ThSetMeshPoint.inMesh = self.inMesh

    def getCoordinate(self, mesh, space='object'):
        u"""讀取座標"""
        meshList = om2.MSelectionList().add(mesh)
        meshDagPath = meshList.getDagPath(0)
        fnMesh = om2.MFnMesh(meshDagPath)
        return fnMesh.getPoints(self.appSpace[space])

    def setCoordinate(self, mesh, data):
        u"""設置座標"""
        meshList = om2.MSelectionList().add(mesh)
        meshDagPath = meshList.getDagPath(0)
        fnMesh = om2.MFnMesh(meshDagPath)
        fnMesh.setPoints(data)

    def resetCoordinate(self):
        if self.inPointList:
            self.setCoordinate(self.inMesh, self.inPointList)


class ThPrintSetAttrData(object):
    """打印設定物件屬性數值"""

    def __init__(self, useAttrList=[
 'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']):
        self.useAttrList = useAttrList
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        dataDict = {}
        for n in selectList:
            attrList = []
            if self.useAttrList:
                attrList = self.useAttrList
            else:
                attrList = cmds.listAttr(n, m=True, k=True, r=True, se=True, v=True, w=True, c=True) or []
            for attr in attrList:
                objAttr = ('{}.{}').format(n, attr)
                dataDict[objAttr] = cmds.getAttr(objAttr)

        print '-' * 40 + '  Python  ' + '-' * 40
        text = "\nimport maya.cmds as cmds\nreName = ''  # 移除指定字符\naddName = ''  # 添加命名空間\ndataDict = {}\ndoDataDict = {{k.replace(reName,''):v for k, v in dataDict.items()}} if reName else dataDict\ndoDataDict = {{addName+k:v for k, v in doDataDict.items()}} if addName else doDataDict\nfor k, v in doDataDict.items():\n    try:\n        cmds.setAttr(k, v)\n    except:\n        pass\ncmds.select([n.split('.')[0] for n in doDataDict.keys()], r=True)\n"
        text = text.format(dataDict)
        print text
        print '-' * 40 + '  Python  ' + '-' * 40


class ThVertexFollicle(object):
    """在選擇的 vertexList 上創建 follicle.
    :type vertexList: list
    """

    def __init__(self, vertexList=None, name='obj', rotateObj=None):
        self.vertexList = vertexList
        self.name = name
        self.rotateObj = rotateObj

    def apply(self):
        follicleNew = []
        if not cmds.objExists('def'):
            cmds.group(em=True, n='def')
        if not cmds.objExists('follicle_grp'):
            cmds.group(em=True, n='follicle_grp')
            cmds.parent('follicle_grp', 'def')
        self.mainGrp = cmds.group(em=True, n=self.name + '_follicle_grp#')
        cmds.parent(self.mainGrp, 'follicle_grp')
        uvPosList = thGetPolyUvPos(self.vertexList)[1]
        mesh = self.vertexList[0].split('.', 1)[0]
        meshShape = cmds.listRelatives(mesh, c=True, f=True, type='shape')[0]
        for uvPos in uvPosList:
            follicleShape = cmds.createNode('follicle')
            follicle = cmds.listRelatives(follicleShape, p=True)[0]
            cmds.connectAttr(meshShape + '.outMesh', follicleShape + '.inputMesh', f=True)
            cmds.connectAttr(meshShape + '.worldMatrix', follicleShape + '.inputWorldMatrix', f=True)
            cmds.connectAttr(follicleShape + '.outTranslate', follicle + '.translate', f=True)
            if self.rotateObj:
                cmds.orientConstraint([self.rotateObj, follicle], mo=True, weight=1)
            else:
                cmds.connectAttr(follicleShape + '.outRotate', follicle + '.rotate', f=True)
            cmds.setAttr(follicleShape + '.parameterU', uvPos[0])
            cmds.setAttr(follicleShape + '.parameterV', uvPos[1])
            cmds.parent(follicle, self.mainGrp)
            follicleNew.append(cmds.rename(follicle, self.name + '_follicle#'))

        cmds.select(follicleNew, r=True)
        return follicleNew


class ThCoordinateCreateMesh(object):
    """座標創建 mesh"""

    def __init__(self, list_):
        self.list_ = list_
        coordinateList = []
        for n in list_:
            coordinateList.append(cmds.xform(n, q=True, ws=True, rp=True))

        self.newMesh = cmds.polyCreateFacet(tx=1, s=1, ch=False, p=coordinateList)[0]


class ThCreateChPoly(object):
    """依據選擇物件之 child 創建 mesh"""

    def __init__(self, list_, bake=False, skin=True, inf=5):
        if len(list_) <= 1:
            return
        self.list_ = list_ + [list_[0]] if bake else list_
        newMeshList = []
        coordinateList1 = self._getCoordinate(self.list_[0])
        for i in range(len(self.list_) - 1):
            coordinateList2 = self._getCoordinate(self.list_[(i + 1)])
            len_ = self._findMax(coordinateList1 + coordinateList2)
            doCoordinateList1 = coordinateList1[0]
            doCoordinateList2 = coordinateList2[0]
            for ii in range(len_):
                try:
                    doCoordinateList3 = coordinateList2[(ii + 1)]
                except:
                    doCoordinateList3 = doCoordinateList2

                try:
                    doCoordinateList4 = coordinateList1[(ii + 1)]
                except:
                    doCoordinateList4 = doCoordinateList1

                newMeshList.append(cmds.polyCreateFacet(tx=1, s=1, ch=False, p=[
                 doCoordinateList1, doCoordinateList2,
                 doCoordinateList3, doCoordinateList4])[0])
                doCoordinateList1 = doCoordinateList4
                doCoordinateList2 = doCoordinateList3

            coordinateList1 = coordinateList2

        newMesh = cmds.polyUnite(newMeshList, ch=False, mergeUVSets=True, centerPivot=True)[0]
        cmds.polyMergeVertex(newMesh, d=0.01, am=True, ch=False)
        if skin:
            skinJointList = cmds.listRelatives(list_, ad=True, type='joint')
            skinJointList.extend(list_)
            cmds.skinCluster(skinJointList, newMesh, mi=inf, dr=4.0, tsb=True)
        cmds.select(newMesh, r=True)

    def _findMax(self, listL1):
        u"""找出最大循環次數"""
        lenList = [ len(listL1) for list in listL1 ]
        sortList = sorted(lenList, reverse=True)
        return sortList[0]

    def _getCoordinate(self, father):
        u"""回傳座標列表"""
        objList = cmds.listRelatives(father, ad=True, type='joint')
        objList.append(father)
        coordinateList = []
        for n in objList:
            coordinateList.append(cmds.xform(n, q=True, ws=True, rp=True))

        return coordinateList[::-1]


class ThEditSkinWeightSmooth(object):

    def __init__(self, list_, quantity=1, jointList=None, value=1, ifRange=False):
        self.list_ = list_
        self.quantity = quantity
        self.jointList = jointList
        self.value = value
        self.ifRange = ifRange
        if '.' in self.list_[0]:
            mesh = self.list_[0].split('.')[0]
            cmds.select(cmds.polyListComponentConversion(self.list_, tv=True), r=True)
            self.doApply(mesh)
        else:
            for mesh in self.list_:
                cmds.select(mesh, r=True)
                self.doApply(mesh)

        cmds.select(self.list_, r=True)

    def doApply(self, mesh):
        nodeList = thFindSkinNode([mesh])
        if nodeList:
            cmds.skinCluster(nodeList[0], e=True, fnw=True, normalizeWeights=2)
            cmds.ArtPaintSkinWeightsToolOptions()
            mel.eval('artAttrPaintOperation artAttrSkinPaintCtx Smooth')
            mel.eval(('artAttrSkinPaintCtx -e -opacity {} `currentCtx`').format(self.value))
            jointList = self.jointList if self.jointList else thFindSkinJoint([mesh])
            for joint in jointList:
                mel.eval(('setSmoothSkinInfluence {}').format(joint))
                if self.ifRange:
                    cmds.skinCluster(nodeList[0], e=True, siv=joint)
                for i in range(self.quantity):
                    mel.eval('FloodSurfaces')


class ThJointAxialToWorld(object):
    """調整末端骨骼軸向到世界"""

    def __init__(self, jointList=None):
        if not jointList:
            jointList = cmds.ls(typ='joint')
        else:
            list_ = cmds.listRelatives(jointList, ad=True, f=True, type='joint') or []
            list_.extend(jointList)
            jointList = list_
        applyList = []
        for joint in jointList:
            child = cmds.listRelatives(joint, c=True)
            if not child:
                applyList.append(joint)

        len_ = 0
        for joint in applyList:
            ifConSkin = True
            conList = cmds.listConnections(joint) or []
            for n in conList:
                if cmds.nodeType(n) == 'skinCluster':
                    ifConSkin = False
                    break

            if ifConSkin:
                len_ += 1
                cmds.joint(joint, e=True, oj='none', ch=True, zso=True)

        sys.stdout.write(('Modify joint quantity: {}').format(len_))


class ThTransformDisplay(object):
    """變換顯示工具"""

    def __init__(self, selectList, attr='axes', parent=False, type=None):
        applyAttrDict = {'axes': '.displayLocalAxis', 
           'handles': '.displayHandle'}
        if parent:
            applyFunc = 'cmds.listRelatives(selectList, ad=True, f=True)'
            if type:
                applyFunc = 'cmds.listRelatives(selectList, ad=True, f=True, type=type)'
            parentList = eval(applyFunc) or []
            parentList.extend(selectList)
            selectList = parentList
        applyValue = cmds.getAttr(selectList[0] + applyAttrDict[attr])
        applyValue = False if applyValue else True
        for n in selectList:
            cmds.setAttr(n + applyAttrDict[attr], applyValue)


class ThRenameExchange(object):
    """交換名稱"""

    def __init__(self, list1, list2):
        ccNameList = []
        for n in list1:
            ccNameList.append(cmds.rename(n, 'cc_' + n))

        for i, n in enumerate(ccNameList):
            cmds.rename(list2[i], list1[i])
            cmds.rename(n, list2[i])


class ThRenameClearLen(object):
    """清除長度"""

    def __init__(self, list_, dir):
        dirLen = '[dir:]' if dir > 0 else '[:dir]'
        for n in list_:
            newName = eval(('"{}"{}').format(n, dirLen))
            cmds.rename(n, newName)


class ThSkinSplitBlendShape(object):

    def __init__(self, mesh, blendNode):
        self.mesh = mesh
        self.blendNode = blendNode
        cwa = ThCopyWeightApi()
        cwa.getWeightDataF(mesh)
        self.data = cwa.data
        self.weightList = []
        self.layerLen = len(self.data[0])
        for i in range(self.layerLen):
            self.weightList.append(self.data[1][i::self.layerLen])

    def reWeight(self):
        for i in range(len(self.weightList[0])):
            cmds.setAttr(('{}.inputTarget[0].baseWeights[{}]').format(self.blendNode, i), 1)

    def setWeight(self, index):
        for i, weight in enumerate(self.weightList[index], 0):
            cmds.setAttr(('{}.inputTarget[0].baseWeights[{}]').format(self.blendNode, i), weight)

    def splitCopy(self):
        newMeshList = []
        for i in range(self.layerLen):
            self.setWeight(i)
            newName = ('{}_{}').format(self.data[0][i], self.mesh)
            newName = cmds.duplicate(self.mesh, rr=True, n=newName)[0]
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                cmds.setAttr(('{}.{}').format(newName, attr), lock=False, keyable=True)

            newMeshList.append(newName)

        cmds.select(newMeshList, r=True)
        return newMeshList


class ThSelectTypeObject(object):
    """選擇列別物件"""

    def __init__(self, objs=None, mode='scenes', type='mesh', transform=False):
        self.objs = objs
        self.mode = mode
        self.type = type
        self.transform = transform
        self.result = None
        app_dict = {'father': self.fatherF, 
           'select': self.selectF, 
           'scenes': self.scenesF}
        self.result = app_dict[mode]()
        if not self.result:
            return
        else:
            if transform:
                if self.ifFatherF():
                    self.result = list(set(cmds.listRelatives(self.result, ap=True, f=True)))
            return

    def selectObjsF(self):
        cmds.select(self.result, r=True)

    def ifFatherF(self):
        father = cmds.listRelatives(self.result[0], ap=True, f=True)
        if father:
            child = cmds.listRelatives(father[0], s=True, f=True)
            if child:
                if cmds.nodeType(child[0]) == self.type:
                    return True
                else:
                    return False

            else:
                return False
        else:
            return False

    def scenesF(self):
        return cmds.ls(type=self.type)

    def fatherF(self):
        objList = []
        for obj in self.objs:
            if cmds.nodeType(obj) == self.type:
                objList.append(obj)
            list_ = cmds.listRelatives(obj, ad=True, typ=self.type, f=True)
            if list_:
                objList.extend(list_[::-1])

        return objList

    def selectF(self):
        typeList = thType(self.objs)
        objList = []
        for i, obj in enumerate(self.objs):
            if typeList[i] == self.type:
                objList.append(obj)

        return objList


class ThCopyWeightApi(object):
    mesh = None
    data = None
    dataDict = None

    def copyWeightF(self, inMesh, outMesh):
        u"""複製權重"""
        skinNode = thFindSkinNode([outMesh])
        if skinNode:
            cmds.delete(skinNode)
        self.getWeightDataF(inMesh, False)
        self.mesh = outMesh
        self.setWeightDataF(False)

    def findMinF(self, mesh):
        self.getWeightDataF(mesh)
        sortedData = list(sorted(set(self.data[1])))
        return sortedData

    def editWeightDataF(self, idList, idListData, joint, otherJointList=None, findUnLockJoint=False):
        u"""
        idList = 要更動的頂點
        idListData = 更動的數值
        joint = 更動的骨骼
        """
        if not self.data:
            return
        else:
            if otherJointList is None:
                otherJointList = copy.copy(self.data[0])
                otherJointList.remove(joint)
                if findUnLockJoint:
                    otherJointList = [ j for j in otherJointList if cmds.getAttr(j + '.liw') == 0 ]
            if not otherJointList:
                return
            for i in range(len(idList)):
                otherJointWeightList = []
                for j in otherJointList:
                    otherJointWeightList.append(self.dataDict[j][idList[i]])

                jointWeight = self.dataDict[joint][idList[i]]
                sum_ = sum(otherJointWeightList + [jointWeight])
                difference = 0 if idListData[i] > sum_ else sum_ - idListData[i]
                otherJointWeightList = thAverageData(otherJointWeightList, difference)
                mainWeight = sum_ if idListData[i] > sum_ else idListData[i]
                self.dataDict[joint][idList[i]] = mainWeight
                for ii, j in enumerate(otherJointList):
                    self.dataDict[j][idList[i]] = otherJointWeightList[ii]

            return

    def setWeightDataF(self, toLlist=True):
        u"""設置權重"""
        if toLlist:
            self._toListF()
        skinNodeList = thFindSkinNode([self.mesh])
        if not skinNodeList:
            skinNodeList = cmds.skinCluster(self.data[0], self.mesh, mi=5, omi=5, dr=4.0, tsb=True)
        meshList = om2.MSelectionList()
        meshList.add(self.mesh)
        meshPath = meshList.getDagPath(0)
        skinList = om2.MSelectionList()
        skinList.add(skinNodeList[0])
        skinNode = skinList.getDependNode(0)
        skinFn = omAnim2.MFnSkinCluster(skinNode)
        vertexComp = om2.MFnSingleIndexedComponent().create(om2.MFn.kMeshVertComponent)
        infDags = skinFn.influenceObjects()
        infIndexes = om2.MIntArray(range(len(infDags)))
        weightData = om2.MDoubleArray(self.data[1])
        skinFn.setWeights(meshPath, vertexComp, infIndexes, weightData)
        cmds.skinCluster(skinNodeList[0], e=True, fnw=True)

    def getWeightDataF(self, mesh, toDict=True):
        u"""讀取權重"""
        self.mesh = mesh
        skinNodeList = thFindSkinNode([mesh])
        if not skinNodeList:
            return
        meshList = om2.MSelectionList()
        meshList.add(mesh)
        meshPath = meshList.getDagPath(0)
        skinList = om2.MSelectionList()
        skinList.add(skinNodeList[0])
        skinNode = skinList.getDependNode(0)
        skinFn = omAnim2.MFnSkinCluster(skinNode)
        infDags = skinFn.influenceObjects()
        jointList = [ n.partialPathName() for n in infDags ]
        vertexComp = om2.MFnSingleIndexedComponent().create(om2.MFn.kMeshVertComponent)
        weightData = skinFn.getWeights(meshPath, vertexComp)[0]
        weightDataList = list(weightData)
        self.data = [jointList, weightDataList]
        if toDict:
            self._toDictF()

    def exportWeightFileF(self, meshList):
        u"""輸出權重檔"""
        if not meshList:
            cmds.error('請先選擇模型)')
            return
        fileList = cmds.fileDialog2(startingDirectory=cmds.file(q=True, sn=True) or 'D:/', fileFilter='Maya skin weight (*.weight);;All Files (*.*)', dialogStyle=2)
        if not fileList:
            return
        ThClearChShapeNode(meshList)
        progressBar = ThQProgressBar(1)
        progressBar.setStrat(0, 'Export', 3)
        progressBar.setFrame(0)
        dataDict = {}
        for i, m in enumerate(meshList):
            self.getWeightDataF(m, False)
            if self.data:
                dataDict[m] = self.data

        progressBar.setFrame(0)
        with open(fileList[0], 'wb') as (file):
            cPickle.dump(dataDict, file)
        progressBar.setFrame(0)
        progressBar.deleteLater()

    def importWeightFileF(self):
        u"""輸入權重檔"""
        path = cmds.file(q=True, sn=True) or 'D:/'
        fileList = cmds.fileDialog2(startingDirectory=path, fileFilter='Maya skin weight (*.weight)', fm=1)
        if not fileList:
            return
        progressBar = ThQProgressBar(1)
        progressBar.setStrat(0, 'Import', 3)
        progressBar.setFrame(0)
        data = {}
        with open(fileList[0], 'rb') as (file):
            data = cPickle.load(file)
        progressBar.setFrame(0)
        errorList = []
        for mesh, data in data.items():
            self.mesh = mesh
            self.data = data
            try:
                self.setWeightDataF(False)
            except:
                errorList.append(mesh)

        if errorList:
            cmds.select(errorList, r=True)
            cmds.warning('部分物件匯入權重失敗!')
        progressBar.setFrame(0)
        progressBar.deleteLater()

    def _toDictF(self):
        u"""轉換為字典"""
        self.dataDict = {}
        len_ = len(self.data[0])
        for i, n in enumerate(self.data[0]):
            self.dataDict[n] = self.data[1][i::len_]

    def _toListF(self):
        u"""轉換為列表"""
        weightList = []
        for i in range(len(self.dataDict[self.data[0][0]])):
            for n in self.data[0]:
                weightList.append(self.dataDict[n][i])

        self.data[1] = weightList


class ThDisconnectConnect(object):

    def __init__(self, sys='disconnectAttr_data'):
        self.sys = sys
        self.attrList = None
        return

    def _getDataF(self, objList, disconnectAttr=False):
        conDict_0 = {}
        for obj in objList:
            conDict_1 = {}
            if self.attrList is None:
                self.attrList = cmds.listAttr(obj, lf=True, m=True, r=True, se=True, v=True, w=True, c=True)
            for attr in self.attrList:
                conList = None
                try:
                    conList = cmds.listConnections(obj + '.' + attr, source=True, destination=False, plugs=True)
                except:
                    continue

                con = conList[0] if conList else None
                if not con:
                    continue
                if disconnectAttr:
                    try:
                        cmds.disconnectAttr(con, obj + '.' + attr)
                    except:
                        continue

                conDict_1[attr] = con

            if conDict_1:
                conDict_0[obj] = conDict_1

        return conDict_0

    def transferF(self, main, objList):
        u"""傳遞連接"""
        data = self._getDataF([main])
        for node, conData in data.items():
            for attr, conObj in conData.items():
                for obj in objList:
                    try:
                        cmds.connectAttr(conObj, obj + '.' + attr)
                    except:
                        pass

    def switchF(self, doList=None, attrList=None):
        u"""斷開與回復連接"""
        self.attrList = attrList
        if not cmds.objExists(self.sys):
            if not doList:
                return
            cmds.group(n=self.sys, em=True)
            cmds.addAttr(self.sys, sn='nts', ln='notes', dt='string')
            cmds.setAttr(self.sys + '.notes', '{}', type='string')
            data = self._getDataF(doList, True)
            cmds.setAttr(self.sys + '.notes', data, type='string')
            cmds.select(doList, r=True)
        else:
            data = eval(cmds.getAttr(self.sys + '.notes'))
            for node, conData in data.items():
                for attr, conObj in conData.items():
                    try:
                        cmds.connectAttr(conObj, node + '.' + attr)
                    except:
                        pass

            cmds.delete(self.sys)
            cmds.select(data.keys(), r=True)


class SoftToSkin(object):

    def __init__(self, joint, sel, useOm2=False):
        self.joint = joint
        self.sel = sel
        self.useOm2 = useOm2
        self.mesh = sel[0].split('.')[0]

    def apply(self):
        if self.useOm2:
            self.cwa = ThCopyWeightApi()
            self.cwa.getWeightDataF(self.mesh)
            try:
                self._setOm2(self.joint)
                self.cwa.setWeightDataF()
            except RuntimeError:
                cmds.warning('對象與此方法不兼容!')

        else:
            self._set(self.joint)
        cmds.select(self.joint, r=True)

    def batchApply(self):
        jointList = cmds.listRelatives(self.joint, ad=True, type='joint')[::-1]
        useJointList = [
         self.joint] + jointList[:-1]
        disList = []
        for n in jointList:
            disList.append(cmds.getAttr(n + '.tx'))

        jointDisList = []
        for i, n in enumerate(useJointList):
            jointDisList.append(sum(disList[i:]))

        cmds.softSelect(e=True, softSelectEnabled=True)
        cmds.softSelect(e=True, softSelectCurve='0,1,0,1,0,1,0,1,1')
        if self.useOm2:
            self.cwa = ThCopyWeightApi()
            self.cwa.getWeightDataF(self.mesh)
            for i, n in enumerate(useJointList):
                cmds.softSelect(e=True, softSelectDistance=jointDisList[i])
                cmds.select(self.sel, r=True)
                self._setOm2(n)

            self.cwa.setWeightDataF()
        else:
            for i, n in enumerate(useJointList):
                cmds.softSelect(e=True, softSelectDistance=jointDisList[i])
                cmds.select(self.sel, r=True)
                self._set(n)

        cmds.select(self.joint, r=True)

    def _set(self, joint):
        skin_node = thFindSkinNode([self.mesh])[0]
        richSel = om2.MGlobal.getRichSelection()
        richSelList = richSel.getSelection()
        path, component = richSelList.getComponent(0)
        componentFn = om2.MFnSingleIndexedComponent(component)
        size = componentFn.getCompleteData()
        progressBar = ThQProgressBar(1)
        progressBar.setStrat(0, 'Vertex', size)
        for i in range(0, size):
            progressBar.setFrame(0)
            weight = componentFn.weight(i)
            v = componentFn.element(i)
            w = weight.influence
            vtx = ('{}.vtx[{}]').format(self.mesh, v)
            cmds.skinPercent(skin_node, vtx, tv=[joint, w])

        progressBar.deleteLater()

    def _setOm2(self, joint):
        richSel = om2.MGlobal.getRichSelection()
        richSelList = richSel.getSelection()
        path, component = richSelList.getComponent(0)
        componentFn = om2.MFnSingleIndexedComponent(component)
        idList = []
        idListData = []
        size = componentFn.getCompleteData()
        for i in range(0, size):
            weight = componentFn.weight(i)
            idList.append(componentFn.element(i))
            idListData.append(weight.influence)

        self.cwa.editWeightDataF(idList, idListData, joint, findUnLockJoint=True)


class ThReconstructionParent(object):

    def __init__(self, list_=None, sys='ThReconstructionParent_data'):
        u"""重做 parent"""
        self.list_ = list_
        self.sys = sys

    def apply(self):
        if not cmds.objExists(self.sys):
            if not self.list_:
                return
            repeatList = []
            for n in self.list_:
                if '|' in n:
                    repeatList.append(n)

            if repeatList:
                cmds.select(repeatList, r=True)
                cmds.warning('程序未執行，選擇物件中包含重複名稱!')
                return
            self.dataList = []
            for n in self.list_:
                father = cmds.listRelatives(n, p=True)
                if father:
                    self.dataList.append([n, father[0]])
                else:
                    self.dataList.append([n, None])

            gsd = ThGrpSaveData(self.sys)
            gsd.saveF(self.dataList)
            for k, v in self.dataList:
                if v:
                    cmds.parent(k, w=True)

            cmds.select(self.list_, r=True)
        else:
            selectList = []
            self.dataList = ThGrpSaveData(self.sys).getF()
            for k, v in self.dataList:
                if v is None:
                    continue
                try:
                    cmds.parent(k, v)
                    selectList.append(k)
                except:
                    pass

            cmds.delete(self.sys)
            cmds.select([ n[0] for n in self.dataList ], r=True)
        return

    def select(self):
        if cmds.objExists(self.sys):
            self.dataList = ThGrpSaveData(self.sys).getF()
            cmds.select([ n[0] for n in self.dataList ], r=True)


class THCtrlMirrorData(object):
    sys = 'customCtrlMirror_data'

    def __init__(self, label):
        self.label = label
        if not cmds.objExists(self.sys):
            cmds.group(n=self.sys, em=True)
            cmds.addAttr(self.sys, sn='nts', ln='notes', dt='string')
            cmds.setAttr(self.sys + '.notes', '{}', type='string')
        data_dict = eval(cmds.getAttr(self.sys + '.notes'))
        if not data_dict.has_key(self.label):
            data_dict[self.label] = {'L': [], 'R': []}
            cmds.setAttr(self.sys + '.notes', data_dict, type='string')

    def add_list(self, sel, direction='L'):
        data_dict = eval(cmds.getAttr(self.sys + '.notes'))
        for n in sel:
            if n not in data_dict[self.label][direction]:
                data_dict[self.label][direction].append(n)

        cmds.setAttr(self.sys + '.notes', data_dict, type='string')
        return len(data_dict[self.label][direction])

    def clear_list(self):
        data_dict = eval(cmds.getAttr(self.sys + '.notes'))
        data_dict[self.label] = {'L': [], 'R': []}
        cmds.setAttr(self.sys + '.notes', data_dict, type='string')

    def clear_label(self):
        data_dict = eval(cmds.getAttr(self.sys + '.notes'))
        del data_dict[self.label]
        if data_dict:
            cmds.setAttr(self.sys + '.notes', data_dict, type='string')
        else:
            cmds.delete(self.sys)

    def mirror_data(self, mode='to L', axial='x'):
        data_dict = eval(cmds.getAttr(self.sys + '.notes'))
        reverse = True if mode == 'to L' else False
        THMirrorData(referenceList=data_dict[self.label]['L'], objs=data_dict[self.label]['R'], axial=axial, reverse_rder=reverse)

    def select(self, mode='L'):
        data_dict = eval(cmds.getAttr(self.sys + '.notes'))
        list_ = []
        app_dict = {'L': '[data_dict[self.label]["L"]]', 
           'R': '[data_dict[self.label]["R"]]', 
           'all': '[data_dict[self.label]["L"], data_dict[self.label]["R"]]'}
        for n in eval(app_dict[mode]):
            list_.extend(n)

        cmds.select(list_, r=True)


class THDynamicsCtrl(object):

    def __init__(self, type, font=None):
        self.type = type
        self.font = font
        self.main_ctrl = ('dyn_{}_main_ctrl').format(self.type)

    def ctrl(self):
        if not cmds.objExists(self.main_ctrl):
            cv = mel.eval('curve -d 1 -p -1 0 -1.063394 -p 1 0 -1.063394 -p 1 0 -0.936606 -p -1 0 -0.936606 -p -1 0 -1.063394 -k 0 -k 1 -k 2 -k 3 -k 4')
            cmds.rename(cv, self.main_ctrl)
            grp = cmds.group(self.main_ctrl, n=('dyn_{}_mainCtrl_grp').format(self.type))
            thLockHiddenAttr([self.main_ctrl], [1, 1, 1, 1])
            node = cmds.textCurves(t=self.type, ch=False, f=self.font)
            tx_grp = cmds.rename(node[0], ('dyn_{}_mainCtrl_tx_grp').format(self.type))
            children = cmds.listRelatives(tx_grp, c=True, typ='transform')
            cmds.ungroup(children)
            children = cmds.listRelatives(tx_grp, c=True, typ='transform')
            for c in children:
                cmds.rename(c, ('dyn_{}_mainCtrl_tx#').format(self.type))

            cmds.move(-1, 0.08, -1, tx_grp, rpr=True)
            cmds.setAttr(tx_grp + '.overrideEnabled', 1)
            cmds.setAttr(tx_grp + '.overrideDisplayType', 2)
            cmds.parent(tx_grp, self.main_ctrl)

    def children_ctrl(self, quantity):
        move_data = 0
        for i in range(quantity):
            ctrl = ('dyn_{}_ch_ctrl{}').format(self.type, i + 1)
            if not cmds.objExists(ctrl):
                cv = mel.eval('curve -d 1 -p -0.794243 0 -0.529496 -p 0.794243 0 -0.529496 -p 0.794243 0 0.529496 -p -0.794243 0 0.529496 -p -0.794243 0 -0.529496 -k 0 -k 1 -k 2 -k 3 -k 4')
                cmds.rename(cv, ctrl)
                thLockHiddenAttr([ctrl], [1, 1, 1, 1])
                grp = cmds.group(ctrl, n=ctrl + '_grp')
                cmds.parent(grp, self.main_ctrl)
                cmds.setAttr((grp + '.t'), *[0, 0, move_data])
                cmds.setAttr((grp + '.r'), *[0, 0, 0])
                cmds.setAttr((grp + '.s'), *[1, 1, 1])
                self._add_attr(ctrl)
            move_data += 1.2

        cmds.select(('dyn_{}_mainCtrl_grp').format(self.type), r=True)

    def _add_attr(self, obj):
        if self.type == 'cloth':
            cmds.addAttr(obj, k=True, ln='isDynamic', at='long', min=0, max=1, dv=0)
            cmds.addAttr(obj, k=True, ln='collisions_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.collisions_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='collide', at='long', min=0, max=1, dv=1)
            cmds.addAttr(obj, k=True, ln='selfCollide', at='long', min=0, max=1, dv=1)
            cmds.addAttr(obj, k=True, ln='thickness', at='double', min=0, dv=0.03)
            cmds.addAttr(obj, k=True, ln='selfCollideWidthScale', at='double', min=0, dv=1)
            cmds.addAttr(obj, k=True, ln='bounce', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='friction', at='double', min=0, dv=0.1)
            cmds.addAttr(obj, k=True, ln='stickiness', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='dynamic_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.dynamic_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='stretchResistance', at='double', min=0, dv=150)
            cmds.addAttr(obj, k=True, ln='compressionResistance', at='double', min=0, dv=10)
            cmds.addAttr(obj, k=True, ln='bendResistance', at='double', min=0, dv=0.1)
            cmds.addAttr(obj, k=True, ln='bendAngleDropoff', at='double', min=0, dv=0.298)
            cmds.addAttr(obj, k=True, ln='shearResistance', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='restitutionAngle', at='double', min=0, dv=720)
            cmds.addAttr(obj, k=True, ln='restitutionTension', at='double', min=0, dv=1000)
            cmds.addAttr(obj, k=True, ln='rigidity', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='deformResistance', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='inputMeshAttract', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='inputAttractMethod', at='long', min=0, max=1, dv=0)
            cmds.addAttr(obj, k=True, ln='inputAttractDamp', at='double', min=0, dv=0.5)
            cmds.addAttr(obj, k=True, ln='inputMotionDrag', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='restLengthScale', at='double', min=0, dv=1)
            cmds.addAttr(obj, k=True, ln='bendAngleScale', at='double', dv=1)
            cmds.addAttr(obj, k=True, ln='pointMass', at='double', min=0, dv=1)
            cmds.addAttr(obj, k=True, ln='lift', at='double', min=0, dv=0.05)
            cmds.addAttr(obj, k=True, ln='drag', at='double', min=0, dv=0.05)
            cmds.addAttr(obj, k=True, ln='tangentialDrag', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='damp', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='stretchDamp', at='double', min=0, dv=5)
            cmds.addAttr(obj, k=True, ln='scalingRelation', at='long', min=0, max=2, dv=1)
        elif self.type == 'collider':
            cmds.addAttr(obj, k=True, ln='collisions_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.collisions_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='isDynamic', at='long', min=0, max=1, dv=0)
            cmds.addAttr(obj, k=True, ln='collide', at='long', min=0, max=1, dv=1)
            cmds.addAttr(obj, k=True, ln='thickness', at='double', min=0, dv=0.03)
            cmds.addAttr(obj, k=True, ln='bounce', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='friction', at='double', min=0, dv=0.1)
            cmds.addAttr(obj, k=True, ln='stickiness', at='double', min=0, dv=0)
        elif self.type == 'hair':
            cmds.addAttr(obj, k=True, ln='enable', at='long', min=0, max=1, dv=1)
            cmds.addAttr(obj, k=True, ln='collisions_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.collisions_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='collide', at='long', min=0, max=1, dv=1)
            cmds.addAttr(obj, k=True, ln='selfCollide', at='long', min=0, max=1, dv=0)
            cmds.addAttr(obj, k=True, ln='collideWidthOffset', at='double', min=0, dv=1)
            cmds.addAttr(obj, k=True, ln='selfCollideWidthScale', at='double', min=0, dv=1)
            cmds.addAttr(obj, k=True, ln='bounce', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='friction', at='double', min=0, dv=0.5)
            cmds.addAttr(obj, k=True, ln='stickiness', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='staticCling', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='dynamic_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.dynamic_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='stretchResistance', at='double', min=0, dv=200)
            cmds.addAttr(obj, k=True, ln='compressionResistance', at='double', min=0, dv=10)
            cmds.addAttr(obj, k=True, ln='bendResistance', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='twistResistance', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='startCurveAttract_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.startCurveAttract_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='startCurveAttract', at='double', min=0, dv=0.2)
            cmds.addAttr(obj, k=True, ln='attractionDamp', at='double', min=0, dv=1.5)
            cmds.addAttr(obj, k=True, ln='forces_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.forces_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='mass', at='double', min=0, dv=1)
            cmds.addAttr(obj, k=True, ln='drag', at='double', min=0, dv=0.05)
            cmds.addAttr(obj, k=True, ln='tangentialDrag', at='double', min=0, dv=0.1)
            cmds.addAttr(obj, k=True, ln='motionDrag', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='damp', at='double', min=0, dv=0.5)
            cmds.addAttr(obj, k=True, ln='stretchDamp', at='double', min=0, dv=5)
            cmds.addAttr(obj, k=True, ln='dynamicsWeight', at='double', min=0, max=1, dv=1)
            cmds.addAttr(obj, k=True, ln='turbulence_', at='enum', en='------:------:')
            cmds.setAttr(obj + '.turbulence_', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='turbulenceStrength', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='turbulenceFrequency', at='double', min=0, dv=0)
            cmds.addAttr(obj, k=True, ln='turbulenceSpeed', at='double', min=0, dv=0)
        elif self.type == 'nucleus':
            cmds.addAttr(obj, k=True, ln='time_attributes', at='enum', en='------:------:')
            cmds.setAttr(obj + '.time_attributes', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='startFrame', at='double', dv=0)
            cmds.addAttr(obj, k=True, ln='scale_attributes', at='enum', en='------:------:')
            cmds.setAttr(obj + '.scale_attributes', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='timeScale', at='double', dv=1)
            cmds.addAttr(obj, k=True, ln='spaceScale', at='double', dv=0.5)
            cmds.addAttr(obj, k=True, ln='gravity_and_wind', at='enum', en='------:------:')
            cmds.setAttr(obj + '.gravity_and_wind', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='gravity', at='double', dv=9.8)
            cmds.addAttr(obj, k=True, ln='airDensity', at='double', dv=1)
            cmds.addAttr(obj, k=True, ln='windSpeed', at='double', dv=0)
            cmds.addAttr(obj, k=True, ln='windDirectionX', at='double', dv=1)
            cmds.addAttr(obj, k=True, ln='windDirectionY', at='double', dv=0)
            cmds.addAttr(obj, k=True, ln='windDirectionZ', at='double', dv=0)
            cmds.addAttr(obj, k=True, ln='windNoise', at='double', dv=0)
            cmds.addAttr(obj, k=True, ln='solver_attributes', at='enum', en='------:------:')
            cmds.setAttr(obj + '.solver_attributes', e=True, channelBox=True)
            cmds.addAttr(obj, k=True, ln='subSteps', at='long', dv=3)
            cmds.addAttr(obj, k=True, ln='maxCollisionIterations', at='long', dv=4)


class ThConnDynNode(object):
    attr_list = {'nCloth': [
                [
                 'isDynamic', 'collide', 'selfCollide',
                 'thickness', 'selfCollideWidthScale',
                 'bounce', 'friction', 'stickiness',
                 'stretchResistance', 'compressionResistance', 'bendResistance', 'bendAngleDropoff', 'shearResistance',
                 'restitutionAngle', 'restitutionTension', 'rigidity', 'deformResistance', 'inputMeshAttract',
                 'inputAttractMethod', 'inputAttractDamp', 'inputMotionDrag',
                 'restLengthScale', 'bendAngleScale', 'pointMass', 'lift', 'drag', 'tangentialDrag',
                 'damp', 'stretchDamp', 'scalingRelation'],
                15], 
       'hairSystem': [
                    [
                     'collide', 'selfCollide', 'collideWidthOffset', 'selfCollideWidthScale',
                     'bounce', 'friction', 'stickiness', 'staticCling',
                     'stretchResistance', 'compressionResistance', 'bendResistance',
                     'twistResistance', 'startCurveAttract', 'attractionDamp', 'mass',
                     'drag', 'tangentialDrag', 'motionDrag', 'damp', 'stretchDamp',
                     'dynamicsWeight', 'turbulenceStrength', 'turbulenceFrequency',
                     'turbulenceSpeed'],
                    10], 
       'nucleus': [
                 [
                  'startFrame', 'timeScale', 'spaceScale', 'gravity', 'airDensity',
                  'windSpeed', 'windDirectionX', 'windDirectionY', 'windDirectionZ',
                  'windNoise', 'subSteps', 'maxCollisionIterations'],
                 23], 
       'collider': [
                  [
                   'isDynamic', 'collide', 'thickness',
                   'bounce', 'friction', 'stickiness']]}

    def __init__(self, objs):
        self.objs = objs
        ctrl = self.objs[(-1)]
        obj_list = self.objs[:-1]
        type = thType([obj_list[0]])[0]
        cmds.delete(obj_list, channels=True, hierarchy='none', controlPoints=0, shape=1)
        for obj in obj_list:
            for attr in self.attr_list[type][0]:
                cmds.connectAttr(ctrl + '.' + attr, obj + '.' + attr, f=True)

            if type == 'hairSystem':
                cmds.setAttr(ctrl + '.enable', 0)
                cmds.setAttr(obj + '.simulationMethod', 0)
                cmds.setDrivenKeyframe(obj + '.simulationMethod', cd=ctrl + '.enable', itt='linear', ott='linear')
                cmds.setAttr(ctrl + '.enable', 1)
                cmds.setAttr(obj + '.simulationMethod', 3)
                cmds.setDrivenKeyframe(obj + '.simulationMethod', cd=ctrl + '.enable', itt='linear', ott='linear')

        thSetCtrlColor([ctrl], self.attr_list[type][1])
        cmds.select(ctrl, r=True)


class ThIKElasticity(object):

    def __init__(self, joints, name='obj', curve=None, main_ctrl=None, size=1.0, ctrl_quantity=3, color=13, use_twist_attr=True, create_twist_ctrl=False, create_elasticity=True, create_fk_ik=False, create_scale=False, constrain_objects=True, parent_ctrl=False, parent_ctrl_other=False, hair_system=False, joint_len_is_ctrl=False):
        u"""Ik spline 拉伸 RIG"""
        self.joints = joints
        self.name = name
        self.curve = curve
        self.main_ctrl = main_ctrl
        self.size = size
        self.ctrl_quantity = ctrl_quantity
        self.color = color
        self.use_twist_attr = use_twist_attr
        self.create_twist_ctrl = create_twist_ctrl
        self.create_elasticity = create_elasticity
        self.create_fk_ik = create_fk_ik
        self.create_scale = create_scale
        self.constrain_objects = constrain_objects
        self.parent_ctrl = parent_ctrl
        self.parent_ctrl_other = parent_ctrl_other
        self.hair_system = hair_system
        self.joint_len_is_ctrl = joint_len_is_ctrl
        self.main_def_grp = None
        self.main_ctrl_grp = None
        self.ik_joint = []
        self.ik_handle = None
        self.skin_cv_joint = []
        self.ik_ctrl = []
        self.ik_ctrl_grp = []
        self.ik_main_grp = None
        self.constrain_node = []
        self.ik_fk = None
        self.fk_ctrl = []
        self.fk_main_grp = None
        self.IK_alone_ctrl = []
        self.IK_alone_ctrl_grp = []
        return

    def create(self):
        self._create_joint()
        self._create_ctrl()
        self._set_ik_attr_twist()
        self._set_ik_ctrl_twist_mode()
        if self.create_elasticity:
            self._create_elasticity_ik_sys()
        if self.create_scale:
            self._create_scale_joint_sys()
        if self.constrain_objects:
            self._control_obj()
        if self.create_fk_ik:
            self._create_FK()
        if self.parent_ctrl:
            self.ctrl_parent(self.parent_ctrl_other)
        if self.hair_system:
            th_cls = THHair(cv=self.curve, name=self.name)
            th_cls.app()
        cmds.select(cl=True)

    def _create_joint(self):
        u"""創建 IK 用的 joint"""
        if not cmds.objExists('def'):
            cmds.group(em=True, n='def')
        if not cmds.objExists('IK_def_grp'):
            cmds.group(em=True, n='IK_def_grp')
            cmds.parent('IK_def_grp', 'def')
        if not cmds.objExists('IK_ctrl_grp'):
            cmds.group(em=True, n='IK_ctrl_grp')
        self.main_def_grp = cmds.group(em=True, n=self.name + '_def_grp#')
        cmds.parent(self.main_def_grp, 'IK_def_grp')
        self.main_ctrl_grp = cmds.group(em=True, n=self.name + '_ctrl_grp#')
        cmds.parent(self.main_ctrl_grp, 'IK_ctrl_grp')
        if not self.curve:
            self.curve = thObjectCurve(self.joints)
        cmds.makeIdentity(self.curve, apply=True, t=True, r=True, s=True, n=False, pn=True)
        self.curve = cmds.rename(self.curve, self.name + '_IK_curve#')
        cmds.parent(self.curve, self.main_def_grp)
        cmds.hide(self.curve)
        for j in self.joints:
            cmds.select(cl=True)
            n_j = cmds.joint(n=self.name + '_IK_joint#')
            self.ik_joint.append(n_j)
            AdsorptionObj([n_j], j, 'tr')

        thGrpParent(self.ik_joint, True)
        cmds.makeIdentity(self.ik_joint, apply=True, t=True, r=True, s=True, n=False, pn=True)
        ik_joint_main_grp = cmds.group(self.ik_joint[0], n=self.name + '_IK_joint_main_grp#')
        cmds.parent(ik_joint_main_grp, self.main_ctrl_grp)
        cmds.hide(self.ik_joint[0])
        cmds.joint(self.ik_joint[(-1)], e=True, oj='none', ch=False, zso=True)
        do_ctrl_quantity = len(self.ik_joint) if self.joint_len_is_ctrl else self.ctrl_quantity
        tcfoj_cls = THCreateFollowObjsJoint(self.ik_joint, do_ctrl_quantity)
        tcfoj_cls.app()
        self.skin_cv_joint = thBatchRename(objs=tcfoj_cls.new_joints, name=self.name + '_skin_joint')
        cmds.hide(self.skin_cv_joint)

    def _create_ctrl(self):
        u"""創建 IK spline system 與 ctrl"""
        self.ik_handle = cmds.ikHandle(sol='ikSplineSolver', n=self.name + '_ikHandle#', ccv=False, scv=False, pcv=False, sj=self.ik_joint[0], ee=self.ik_joint[(-1)], c=self.curve)
        cmds.hide(self.ik_handle)
        cmds.parent(self.ik_handle[0], self.main_def_grp)
        thcto_cls = THCtrlToObject(obj_list=self.skin_cv_joint, name=self.name + '_IK', ctrl_style='cube', ctrl_method='parent', ctrl_size=self.size, ctrl_color=self.color)
        thcto_cls.create()
        self.ik_ctrl = thcto_cls.new_ctrl_list
        self.ik_ctrl_grp = thcto_cls.new_ctrl_grp_list
        self.ik_main_grp = thcto_cls.main_grp
        skin_cv_list = self.skin_cv_joint + [self.curve]
        cmds.skinCluster(skin_cv_list, n=self.name + '_skin_node', mi=5, dr=4.0, tsb=True)
        cmds.parent(thcto_cls.main_grp, self.main_ctrl_grp)
        cmds.orientConstraint([self.ik_ctrl[(-1)], self.ik_joint[(-1)]], offset=[0, 0, 0], weight=1)

    def _set_ik_attr_twist(self):
        u"""設置 IK twist"""
        cmds.addAttr(self.ik_ctrl[0], k=True, ln='IK_spline_attr', at='enum', en='------:------:')
        cmds.setAttr(self.ik_ctrl[0] + '.IK_spline_attr', e=True, channelBox=True)
        cmds.addAttr(self.ik_ctrl[0], ln='twist', at='double', dv=0, k=True)
        cmds.connectAttr(self.ik_ctrl[0] + '.twist', self.ik_handle[0] + '.twist')

    def _set_ik_ctrl_twist_mode(self):
        u"""創建 twist ctrl mode"""
        cmds.addAttr(self.ik_ctrl[0], ln='if_ctrl_twist', at='bool', min=0, max=1, dv=self.use_twist_attr, k=True)
        cmds.connectAttr(self.ik_ctrl[0] + '.if_ctrl_twist', self.ik_handle[0] + '.dTwistControlEnable')
        if not self.create_twist_ctrl:
            self._set_ik_ctrl_twist1()
        else:
            self._set_ik_ctrl_twist2()

    def _set_ik_ctrl_twist1(self):
        u"""創建 twist ctrl mode1"""
        cmds.setAttr(self.ik_handle[0] + '.dWorldUpType', 4)
        cmds.connectAttr(self.ik_ctrl[0] + '.worldMatrix[0]', self.ik_handle[0] + '.dWorldUpMatrix')
        cmds.connectAttr(self.ik_ctrl[(-1)] + '.worldMatrix[0]', self.ik_handle[0] + '.dWorldUpMatrixEnd')
        cmds.addAttr(self.ik_ctrl[0], ln='IK_vector', at='enum', en='Y:Z:', k=True)
        ik_vectory_attr = [
         'dWorldUpAxis', 'dWorldUpVectorY', 'dWorldUpVectorZ', 'dWorldUpVectorEndY', 'dWorldUpVectorEndZ']
        ik_vectory_attr = [ self.ik_handle[0] + '.' + n for n in ik_vectory_attr ]
        cmds.setDrivenKeyframe(ik_vectory_attr, cd=self.ik_ctrl[0] + '.IK_vector', itt='linear', ott='linear')
        cmds.setAttr(self.ik_ctrl[0] + '.IK_vector', 1)
        cmds.setAttr(self.ik_handle[0] + '.dWorldUpAxis', 3)
        cmds.setAttr(self.ik_handle[0] + '.dWorldUpVectorY', 0)
        cmds.setAttr(self.ik_handle[0] + '.dWorldUpVectorZ', 1)
        cmds.setAttr(self.ik_handle[0] + '.dWorldUpVectorEndY', 0)
        cmds.setAttr(self.ik_handle[0] + '.dWorldUpVectorEndZ', 1)
        cmds.setDrivenKeyframe(ik_vectory_attr, cd=self.ik_ctrl[0] + '.IK_vector', itt='linear', ott='linear')

    def _set_ik_ctrl_twist2(self):
        u"""創建 twist ctrl mode2"""
        twist_joint_list = [
         self.ik_ctrl[0], self.ik_ctrl[(-1)]]
        new_name = [
         'start', 'end']
        control_twist_joint = []
        twist_test_grp = cmds.group(em=True, n=self.name + '_twist_text_cv#')
        cmds.parent(twist_test_grp, self.main_def_grp)
        for i, n in enumerate(twist_joint_list):
            cmds.select(cl=True)
            twist_joint1 = cmds.joint(n=self.name + '_twist_joint1_' + new_name[i] + '#')
            cmds.select(cl=True)
            twist_joint2 = cmds.joint(n=self.name + '_twist_joint2_' + new_name[i] + '#')
            control_twist_joint.append(twist_joint2)
            AdsorptionObj([twist_joint1, twist_joint2], n, 'tr', True)
            thcto_cls = THCtrlToObject(obj_list=[
             twist_joint2], name=self.name + '_twist_' + new_name[i], ctrl_style='ball', ctrl_method='parent', ctrl_size=self.size * 0.7, ctrl_color=4, grp_layout=2)
            thcto_cls.create()
            cmds.move(0, 10, 0, thcto_cls.grp_layout_list[0][1], cs=True)
            twist_joint_grp = cmds.group(em=True, n=self.name + '_twist_joint_' + new_name[i] + '_grp#')
            cmds.parent(twist_joint_grp, n)
            cmds.parent([twist_joint1, thcto_cls.main_grp], twist_joint_grp)
            test_cv = thObjectCurve([twist_joint1, twist_joint2], False)
            test_cv = cmds.rename(test_cv, self.name + '_twist_test_cv_' + new_name[i] + '#')
            cmds.parent(test_cv, twist_test_grp)
            cmds.skinCluster([twist_joint1, twist_joint2, test_cv], mi=5, dr=4.0, tsb=True)
            cmds.setAttr(test_cv + '.template', 1)

        cmds.setAttr(self.ik_handle[0] + '.dWorldUpType', 2)
        cmds.connectAttr(control_twist_joint[0] + '.worldMatrix[0]', self.ik_handle[0] + '.dWorldUpMatrix')
        cmds.connectAttr(control_twist_joint[1] + '.worldMatrix[0]', self.ik_handle[0] + '.dWorldUpMatrixEnd')

    def _create_elasticity_ik_sys(self):
        u"""創建 elasticity IK 系統"""
        cmds.addAttr(self.ik_ctrl[0], ln='elasticity', at='double', min=0, dv=1, k=True)
        self.main_elasticity_control = cmds.group(n=self.name + '_main_elasticity_control#', em=True)
        cmds.scaleConstraint([self.main_ctrl_grp, self.main_elasticity_control], offset=[1, 1, 1], weight=1)
        cmds.parent(self.main_elasticity_control, self.main_def_grp)
        elasticity_sys_grp = cmds.group(n=self.name + '_IK_elasticity_curve_grp#', em=True)
        cmds.hide(elasticity_sys_grp)
        cmds.parent(elasticity_sys_grp, self.main_def_grp)
        elasticity_cv_list = []
        self.condition_nodes = []
        for i, n in enumerate(self.joints[:-1], 1):
            elasticity_cv = thObjectCurve([n, self.joints[i]], False, False)
            elasticity_cv = cmds.rename(elasticity_cv, self.name + '_IK_elasticity_curve#')
            cmds.parent(elasticity_cv, elasticity_sys_grp)
            elasticity_cv_list.append(elasticity_cv)
            curve_info_node = cmds.createNode('curveInfo', n=self.name + '_curve_info#')
            self.elasticity_cv_shape = cmds.listRelatives(elasticity_cv, s=True)[0]
            cmds.connectAttr(self.elasticity_cv_shape + '.worldSpace[0]', curve_info_node + '.inputCurve')
            leg_ = cmds.getAttr(('{}.arcLength').format(curve_info_node))
            ex = '{joint}.tx = ((({info}.arcLength-{leg_})*{ctrl}.elasticity)*{scale}.sx)+{leg_};'
            ex = ex.format(joint=self.ik_joint[i], info=curve_info_node, leg_=leg_, scale=self.main_elasticity_control, ctrl=self.ik_ctrl[0])
            cmds.expression(n=('{}_ikeElasticity_EX#').format(self.ik_joint[i]), s=ex)

        wire_node = cmds.wire(elasticity_cv_list, gw=False, en=1.0, ce=0.0, li=0.0, n=self.name + '_wire_node#', w=self.curve)
        cmds.setAttr(wire_node[0] + '.dropoffDistance[0]', 5)

    def _create_scale_joint_sys(self):
        u"""創建 scale joint 系統"""
        dsl_cls = ThDistanceSoftLocator(objs=self.ik_joint, name=self.name, default=1, mode_soft='pipe', quantity_soft=2)
        for i, n in enumerate(dsl_cls.locator_list):
            cmds.connectAttr(n + '.ty', self.ik_joint[i] + '.sy')
            cmds.connectAttr(n + '.ty', self.ik_joint[i] + '.sz')

        cmds.addAttr(self.ik_ctrl[0], k=True, ln='soft_scale', at='enum', en='------:------:')
        cmds.setAttr(self.ik_ctrl[0] + '.soft_scale', e=True, channelBox=True)
        cmds.addAttr(self.ik_ctrl[0], ln='follow', at='double', min=0, max=10, dv=0, k=True)
        cmds.addAttr(self.ik_ctrl[0], ln='offset', at='double', min=0, max=10, dv=0, k=True)
        cmds.addAttr(self.ik_ctrl[0], ln='weight', at='double', dv=1, k=True)
        cmds.connectAttr(self.ik_ctrl[0] + '.follow', dsl_cls.soft_node[0][1] + '.follow')
        cmds.connectAttr(self.ik_ctrl[0] + '.offset', dsl_cls.soft_node[0][1] + '.offset')
        cmds.connectAttr(self.ik_ctrl[0] + '.weight', dsl_cls.soft_node[0][1] + '.ty')
        cv_info_node = cmds.createNode('curveInfo', n=self.name + '_curveInfoScale#')
        curve_shape = cmds.listRelatives(self.curve, s=True)[0]
        cmds.connectAttr(curve_shape + '.worldSpace[0]', cv_info_node + '.inputCurve')
        cmds.setAttr(dsl_cls.soft_node[1][1] + '.follow', 4.7)
        len_ = cmds.getAttr(cv_info_node + '.arcLength')
        cmds.addAttr(self.ik_ctrl[0], ln='len_scale_w', at='double', dv=0.1, k=True)
        ex = '\nif (({len_} * {scale}) > {c_len}){{\n    {con} = ((({len_} * {scale}) - {c_len}) / {scale}) * {weight} * 1.5;}}\nelse {{\n    {con} = ((({len_} * {scale}) - {c_len}) / {scale}) * {weight};}}\n'
        ex = ex.format(c_len=cv_info_node + '.arcLength', scale=self.main_elasticity_control + '.sx', len_=len_, con=dsl_cls.soft_node[1][1] + '.ty', weight=self.ik_ctrl[0] + '.len_scale_w')
        cmds.expression(n=('{}_ikeScale_EX#').format(self.name), s=ex)

    def _control_obj(self):
        u"""控制基礎物件"""
        if self.main_ctrl:
            cmds.parentConstraint([self.main_ctrl, self.main_ctrl_grp], mo=True, weight=1)
        for i, n in enumerate(self.ik_joint):
            self.constrain_node.append(cmds.parentConstraint([n, self.joints[i]], mo=True, weight=1)[0])
            cmds.connectAttr(n + '.s', self.joints[i] + '.s', f=True)

    def _create_FK(self):
        u"""創建 FK 系統"""
        thcto_cls = THCtrlToObject(obj_list=self.joints, name=self.name + '_FK', ctrl_style='circle', ctrl_method='constrain', ctrl_size=self.size, ctrl_color=18, grp_layout=2, rig_TRS=[
         1, 1, 0], ctrl_axial='x')
        thcto_cls.create()
        thcto_cls.ctrl_parent()
        cmds.parent(thcto_cls.main_grp, self.main_ctrl_grp)
        self.fk_ctrl = thcto_cls.new_ctrl_list
        self.fk_main_grp = thcto_cls.main_grp
        self.ik_fk = thMyController(name=self.name + '_IKFK', style='angle3', axial='x', color=6, lock_hide_attr=[
         1, 1, 1, 1])
        ik_fk_grp1 = cmds.group(self.ik_fk, n=self.ik_fk + '_grp#')
        cmds.parent(ik_fk_grp1, self.main_ctrl_grp)
        AdsorptionObj([ik_fk_grp1], self.ik_ctrl[0], 't')
        cmds.move(0, 5, 0, ik_fk_grp1, cs=True, r=True)
        cmds.addAttr(self.ik_fk, ln='IKFK', at='double', min=0, max=1, dv=1, k=True)
        for i, n in enumerate(self.constrain_node):
            cmds.connectAttr(self.ik_fk + '.IKFK', n + '.' + self.ik_joint[i] + 'W0')
            thReverseConnect([n], [self.ik_fk, 'IKFK'], self.fk_ctrl[i] + 'W1')

        cmds.connectAttr(self.ik_fk + '.IKFK', self.ik_main_grp + '.v')
        thReverseConnect([self.fk_main_grp], [self.ik_fk, 'IKFK'], 'v')

    def ctrl_parent(self, if_creatr_ctrl):
        u"""控制器 parent"""
        new_ctrl_list = copy.copy(self.ik_ctrl)
        new_ctrl_grp_list = copy.copy(self.ik_ctrl_grp)
        new_ctrl_list.reverse()
        new_ctrl_grp_list.reverse()
        for i, n in enumerate(new_ctrl_grp_list[:-1], 1):
            cmds.parent(n, new_ctrl_list[i])

        if if_creatr_ctrl:
            thcto_cls = THCtrlToObject(obj_list=self.skin_cv_joint, name=self.name + '_IK_alone', ctrl_axial='x', ctrl_style='circle', ctrl_method='parent', ctrl_size=self.size, ctrl_color=22, if_create_main_grp=False)
            thcto_cls.create()
            self.IK_alone_ctrl = thcto_cls.new_ctrl_list
            self.IK_alone_ctrl_grp = thcto_cls.new_ctrl_grp_list
            for i, n in enumerate(self.IK_alone_ctrl_grp):
                cmds.parent(n, self.ik_ctrl[i])

        cmds.select(self.ik_ctrl, r=True)


class THReelRig(object):

    def __init__(self):
        u"""卷軸綁定"""
        self.bend = []

    def app(self, list_, axial='z', mode='two'):
        self.list_ = list_
        self.axial = axial
        self.mode = mode
        self.reverse = True
        self.reel_sys = cmds.group(em=True, n='reel_sys#')
        self.joint_list = []
        for n in self.list_:
            cmds.select(cl=True)
            joint = cmds.joint(n='reel_joint#')
            self.joint_list.append(joint)
            AdsorptionObj([joint], n, 'tr')

        thGrpParent(self.joint_list, True, 0, False)
        cmds.makeIdentity(self.joint_list, apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.parent(self.joint_list[0], self.reel_sys)
        self._loc()
        self._cv_loc()
        self.loc_list1 = self.loc
        if self.mode == 'two':
            self.reverse = False
            self._loc()
            self._cv_loc()
            self.loc_list2 = self.loc
            TwoListSequential(list_=self.list_, con_list_A=self.loc_list2, con_list_B=self.loc_list1, main_ctrl=self.reel_sys, ctrl_method='key')
            cmds.connectAttr(self.reel_sys + '.reverse_bend', self.reel_sys + '.follow')
            cmds.setAttr(self.reel_sys + '.follow', lock=True, keyable=False, channelBox=False)
        else:
            for i, n in enumerate(self.loc_list1):
                cmds.parentConstraint([n, self.list_[i]], mo=True, weight=1)

            for n in self.bend:
                cmds.setAttr(n + '.envelope', 1)

        cmds.select(self.reel_sys, r=True)

    def _loc(self):
        self.loc = []
        self.loc_grp1 = []
        self.loc_grp2 = []
        self.prefix = 'positive' if self.reverse else 'reverse'
        self.main_grp = cmds.group(em=True, n=self.prefix + '_reel_grp#')
        cmds.parent(self.main_grp, self.reel_sys)
        for j in self.joint_list:
            loc = cmds.spaceLocator(n=self.prefix + '_reel_locator#')[0]
            grp1 = cmds.group(loc, n=loc + '_grp#')
            grp2 = cmds.group(grp1, n=loc + '_grp#')
            cmds.hide(grp2)
            self.loc.append(loc)
            self.loc_grp1.append(grp1)
            self.loc_grp2.append(grp2)
            AdsorptionObj([grp2], j)
            cmds.parent(grp2, self.main_grp)

        thGrpParent(self.loc, self.reverse, 2, False)
        for i, j in enumerate(self.joint_list):
            cmds.parentConstraint([j, self.loc_grp2[i]], mo=True, weight=1)

        do_list = self.loc_grp2[1:] if self.reverse else self.loc_grp2[:-1]
        for grp in do_list:
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                cmds.setDrivenKeyframe(grp + '.' + attr, cd=self.loc_grp2[0] + '.v', itt='linear', ott='linear')

        cmds.addAttr(self.reel_sys, k=True, ln=self.prefix, at='enum', en='------:------:')
        cmds.setAttr(self.reel_sys + '.' + self.prefix, e=True, channelBox=True)
        cmds.addAttr(self.reel_sys, ln=self.prefix + '_bend', at='double', min=0, max=10, dv=0, k=True)
        thBatchOffset(do_list, 'blendParent1', ('{}.{}_bend').format(self.reel_sys, self.prefix), False, self.reverse)
        self.con_loc = ThDuplicateWithoutChildrenCon(self.loc_grp1).createConLocF()[0]
        father = thGrpParent(self.con_loc, self.reverse, 1, False, True)
        cmds.parent(father, self.main_grp)
        cmds.hide(father)

    def _cv_loc(self):
        cv = thObjectCurve(self.joint_list)
        cv = cmds.rename(cv, self.prefix + '_reelCv#')
        cmds.parent(cv, self.main_grp)
        cmds.hide(cv)
        loc = thCvToFollowLoc([cv], len(self.joint_list), self.prefix + '_reelCv')
        grp = cmds.group(loc, n=self.prefix + '_reelCvLoc_grp#')
        cmds.parent(grp, self.main_grp)
        cmds.hide(grp)
        app = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}
        for n in loc:
            cmds.tangentConstraint([
             cv, n], worldUpType='vector', aimVector=app[self.axial], upVector=app[self.axial], worldUpVector=app[self.axial])

        bend = cmds.nonLinear(cv, type='bend', lowBound=-1, highBound=1, curvature=0)
        bend[0] = cmds.rename(bend[0], self.prefix + '_reel_bend#')
        bend[1] = cmds.rename(bend[1], self.prefix + '_reel_bendHandle#')
        self.bend.append(bend[0])
        bend_grp = cmds.group(bend[1], n=bend[1] + '_grp#')
        obj = self.joint_list[(-1)] if self.reverse else self.joint_list[0]
        AdsorptionObj([bend_grp], obj, 't')
        cmds.parent(bend_grp, self.main_grp)
        cmds.hide(bend_grp)
        set_data = {'x': [0, 0, 90], 'y': [0, 0, 0], 'z': [90, 0, 90]}
        cmds.setAttr((bend_grp + '.r'), *set_data[self.axial])
        low_bound = -10 if self.reverse else 0
        high_bound = 0 if self.reverse else 10
        cmds.setAttr(bend[0] + '.lowBound', low_bound)
        cmds.setAttr(bend[0] + '.highBound', high_bound)
        cmds.setAttr(bend[0] + '.envelope', 0)
        cmds.addAttr(self.reel_sys, ln=self.prefix + '_curvature', at='double', min=-180, max=180, dv=180, k=True)
        cmds.connectAttr(self.reel_sys + '.' + self.prefix + '_curvature', bend[0] + '.curvature')
        cmds.addAttr(self.reel_sys, ln=self.prefix + '_rotate', at='double', min=-10, max=10, dv=0, k=True)
        cmds.connectAttr(self.reel_sys + '.' + self.prefix + '_rotate', bend[1] + '.rz')
        cmds.addAttr(self.reel_sys, ln=self.prefix + '_scale', at='double', min=0, dv=1, k=True)
        cmds.connectAttr(self.reel_sys + '.' + self.prefix + '_scale', bend[1] + '.sx')
        cmds.connectAttr(self.reel_sys + '.' + self.prefix + '_scale', bend[1] + '.sy')
        cmds.connectAttr(self.reel_sys + '.' + self.prefix + '_scale', bend[1] + '.sz')
        obj = self.joint_list[0] if self.reverse else self.joint_list[(-1)]
        xyz = cmds.xform(obj, q=True, ws=True, t=True)
        cmds.setAttr(('{}.{}_bend').format(self.reel_sys, self.prefix), 0)
        key = [ bend_grp + '.' + attr for attr in ['tx', 'ty', 'tz'] ]
        cmds.setDrivenKeyframe(key, cd=('{}.{}_bend').format(self.reel_sys, self.prefix), itt='linear', ott='linear')
        cmds.setAttr(('{}.{}_bend').format(self.reel_sys, self.prefix), 10)
        cmds.xform(bend_grp, ws=True, t=xyz)
        cmds.setDrivenKeyframe(key, cd=('{}.{}_bend').format(self.reel_sys, self.prefix), itt='linear', ott='linear')
        cmds.setAttr(('{}.{}_bend').format(self.reel_sys, self.prefix), 0)
        for i, l in enumerate(loc):
            cmds.parentConstraint([l, self.con_loc[i]], mo=True, weight=1)

    def con_ctrl(self, sys, ctrl):
        cmds.addAttr(ctrl, k=True, ln='positive', at='enum', en='------:------:')
        cmds.setAttr(ctrl + '.positive', e=True, channelBox=True)
        cmds.addAttr(ctrl, ln='positive_bend', at='double', min=0, max=10, dv=0, k=True)
        cmds.connectAttr(ctrl + '.positive_bend', sys + '.positive_bend')
        cmds.addAttr(ctrl, ln='positive_curvature', at='double', min=-180, max=180, dv=180, k=True)
        cmds.connectAttr(ctrl + '.positive_curvature', sys + '.positive_curvature')
        cmds.addAttr(ctrl, ln='positive_rotate', at='double', min=-10, max=10, dv=0, k=True)
        cmds.connectAttr(ctrl + '.positive_rotate', sys + '.positive_rotate')
        cmds.addAttr(ctrl, ln='positive_scale', at='double', min=0, dv=1, k=True)
        cmds.connectAttr(ctrl + '.positive_scale', sys + '.positive_scale')
        if cmds.listAttr(sys, m=True, st='reverse'):
            cmds.addAttr(ctrl, k=True, ln='reverse', at='enum', en='------:------:')
            cmds.setAttr(ctrl + '.positive', e=True, channelBox=True)
            cmds.addAttr(ctrl, ln='reverse_bend', at='double', min=0, max=10, dv=0, k=True)
            cmds.connectAttr(ctrl + '.reverse_bend', sys + '.reverse_bend')
            cmds.addAttr(ctrl, ln='reverse_curvature', at='double', min=-180, max=180, dv=180, k=True)
            cmds.connectAttr(ctrl + '.reverse_curvature', sys + '.reverse_curvature')
            cmds.addAttr(ctrl, ln='reverse_rotate', at='double', min=-10, max=10, dv=0, k=True)
            cmds.connectAttr(ctrl + '.reverse_rotate', sys + '.reverse_rotate')
            cmds.addAttr(ctrl, ln='reverse_scale', at='double', min=0, dv=1, k=True)
            cmds.connectAttr(ctrl + '.reverse_scale', sys + '.reverse_scale')
        cmds.select(ctrl, r=True)


class TwoListSequential(object):

    def __init__(self, list_, con_list_A, con_list_B, main_ctrl=None, mode_soft='zipper', ctrl_method='soft'):
        u"""拉鍊"""
        self.list_ = list_
        self.con_list_A = con_list_A
        self.con_list_B = con_list_B
        self.main_ctrl = main_ctrl
        self.mode_soft = mode_soft
        self.ctrl_method = ctrl_method
        self.app()

    def app(self):
        if self.ctrl_method == 'soft':
            self._soft()
        else:
            self._key()

    def _key(self):
        if not cmds.listAttr(self.main_ctrl, m=True, st='follow'):
            cmds.addAttr(self.main_ctrl, ln='follow', at='double', min=0, max=10, dv=0, k=True)
        self.con_node = []
        for i, n in enumerate(self.list_):
            node = cmds.parentConstraint([self.con_list_A[i], self.con_list_B[i], n], mo=True, weight=1)[0]
            self.con_node.append(node)

        key_list = []
        for i, con in enumerate(self.con_node):
            key_list.append(con + '.' + self.con_list_A[i] + 'W0')
            key_list.append(con + '.' + self.con_list_B[i] + 'W1')
            cmds.setAttr(con + '.' + self.con_list_A[i] + 'W0', 0)
            cmds.setAttr(con + '.' + self.con_list_B[i] + 'W1', 1)
            cmds.setDrivenKeyframe([
             con + '.' + self.con_list_A[i] + 'W0', con + '.' + self.con_list_B[i] + 'W1'], cd=self.main_ctrl + '.follow', itt='linear', ott='linear')

        offset = 10.0 / len(self.con_node)
        index = 0
        for i, con in enumerate(self.con_node):
            if i < len(self.con_node) - 1:
                index += offset
            else:
                index = 10
            cmds.setAttr(self.main_ctrl + '.follow', index)
            cmds.setAttr(con + '.' + self.con_list_A[i] + 'W0', 1)
            cmds.setAttr(con + '.' + self.con_list_B[i] + 'W1', 0)
            cmds.setDrivenKeyframe(key_list, cd=self.main_ctrl + '.follow', itt='linear', ott='linear')

    def _soft(self):
        self.con_node = []
        formula = ''
        for i, n in enumerate(self.list_):
            node = cmds.parentConstraint([
             self.con_list_A[i], self.con_list_B[i], n], mo=True, weight=1)[0]
            self.con_node.append(node)
            formula += ('{0}.{1}W1 = 1 - {0}.{2}W0;\n').format(node, self.con_list_B[i], self.con_list_A[i])

        cmds.expression(n='TwoListSequential_EX#', s=formula)
        self.dsl_cls = ThDistanceSoftLocator(objs=self.list_, name='TwoListSequential', mode_soft=self.mode_soft)
        for i, con in enumerate(self.con_node):
            cmds.connectAttr(self.dsl_cls.locator_list[i] + '.ty', con + '.' + self.con_list_A[i] + 'W0')

        if self.main_ctrl:
            if not cmds.listAttr(self.main_ctrl, m=True, st='follow'):
                cmds.addAttr(self.main_ctrl, ln='follow', at='double', min=0, max=10, dv=0, k=True)
            if not cmds.listAttr(self.main_ctrl, m=True, st='offset'):
                cmds.addAttr(self.main_ctrl, ln='offset', at='double', min=0, max=10, dv=0, k=True)
            cmds.connectAttr(self.main_ctrl + '.follow', self.dsl_cls.soft_node[0][1] + '.follow')
            cmds.connectAttr(self.main_ctrl + '.offset', self.dsl_cls.soft_node[0][1] + '.offset')


class THLimitInformation(object):

    def __init__(self, objects, attr='tx', data=[-1, 1], en=[0, 0]):
        u"""限制屬性值工具"""
        self.objects = objects
        self.attr = attr
        self.data = data
        self.en = en
        app_str = 'cmds.transformLimits("{0}", {1}=self.data, e{1}=self.en)'
        for obj in self.objects:
            eval(app_str.format(obj, self.attr))


class THDefSoftCtrl(object):

    def __init__(self, objects, loc, name='obj', rig=True):
        u"""soft 變形器控制器"""
        self.objects = objects
        self.loc = loc
        self.name = name
        self.rig = rig
        self._soft()
        self._rig()

    def _soft(self):
        self.xyz = cmds.xform(self.loc, q=True, ws=True, t=True)
        self.soft_node = cmds.softMod(self.objects, n='soft#')
        cmds.setAttr((self.soft_node[1] + '.scalePivot'), *self.xyz)
        cmds.setAttr((self.soft_node[1] + '.rotatePivot'), *self.xyz)
        cmds.setAttr((self.soft_node[0] + '.falloffCenter'), *self.xyz)
        cmds.setAttr((self.soft_node[1] + 'Shape.origin'), *self.xyz)

    def _rig(self):
        if self.rig:
            tcto_cls = THCtrlToObject(obj_list=[
             self.soft_node[1]], name=self.name + '_move', ctrl_style='cube', ctrl_method='not', ctrl_size=0.7, ctrl_color=15, grp_layout=1, if_create_main_grp=False, adsorption_mode='t')
            tcto_cls.create()
            move_ctrl = tcto_cls.new_ctrl_list[0]
            tcto_cls = THCtrlToObject(obj_list=[
             self.soft_node[1]], name=self.name, ctrl_style='ball', ctrl_method='connect', ctrl_size=0.5, ctrl_color=12, grp_layout=1, if_create_main_grp=False, adsorption_mode='t')
            tcto_cls.create()
            ctrl = tcto_cls.new_ctrl_list[0]
            cmds.parent(tcto_cls.new_ctrl_grp_list[(-1)], move_ctrl)
            cmds.addAttr(ctrl, ln='falloffRadius', at='double', min=0, dv=5, k=True)
            cmds.addAttr(ctrl, ln='falloffMode', at='enum', en='volume:surface:', k=True)
            cmds.connectAttr(ctrl + '.falloffRadius', self.soft_node[0] + '.falloffRadius')
            cmds.connectAttr(ctrl + '.falloffMode', self.soft_node[0] + '.falloffMode')
            ex = ''
            ex += ('{}.falloffCenterX = {} + {}.tx;\n').format(self.soft_node[0], self.xyz[0], move_ctrl)
            ex += ('{}.falloffCenterY = {} + {}.ty;\n').format(self.soft_node[0], self.xyz[1], move_ctrl)
            ex += ('{}.falloffCenterZ = {} + {}.tz;').format(self.soft_node[0], self.xyz[2], move_ctrl)
            cmds.expression(n=('{}_dynSoft_EX#').format(self.name), s=ex)
            cmds.hide(self.soft_node[1])
            cmds.select(ctrl, r=True)


class ThExtrudeJoint(object):

    def __init__(self, joint=None, quantity=2, new_joint=None, parent_to_father=False):
        u"""創建擠壓 joint"""
        self.joint = joint
        self.quantity = quantity
        self.new_joint = new_joint or []
        self.parent_to_father = parent_to_father
        self.main_joints = [
         self.joint]
        self.ctrl_list = []

    def _note_init(self):
        u"""初始化"""
        if not cmds.objExists('extrude_data'):
            cmds.group(em=True, n='extrude_data')
            cmds.addAttr('extrude_data', sn='nts', ln='notes', dt='string')
            cmds.setAttr('extrude_data.notes', '{}', type='string')
        if self.new_joint:
            self.quantity = len(self.new_joint)
        father = cmds.listRelatives(self.joint, p=True)[0]
        if self.quantity == 2:
            self.main_joints.append(father)
        elif self.parent_to_father:
            self.main_joints[0] = father

    def create_joint(self):
        u"""創建 joint"""
        self._note_init()
        if not self.new_joint:
            for i in range(self.quantity):
                cmds.select(cl=True)
                self.new_joint.append(cmds.joint(n=self.joint + '_muscle_joint#'))
                AdsorptionObj([self.new_joint[i]], self.main_joints[i], 'tr')

            cmds.makeIdentity(self.new_joint, apply=True, t=True, r=True, s=True, n=False, pn=True)
            cmds.select(self.new_joint, r=True)
        dict_ = eval(cmds.getAttr('extrude_data.notes'))
        for i, n in enumerate(self.new_joint):
            dict_[n] = self.main_joints[i]

        cmds.setAttr('extrude_data.notes', str(dict_), type='string')

    def rig(self, ctrl_size, mesh_list):
        u"""創建控制器"""
        for i, n in enumerate(self.new_joint):
            cmds.parent(n, self.main_joints[i])

        thcto_cls = THCtrlToObject(obj_list=self.new_joint, name=self.joint + '_muscle', ctrl_style='ball', ctrl_method='constrain', ctrl_color=31, grp_layout=2, if_use_constrain_scale=True, if_create_main_grp=False, lock_hide_attr=[
         0, 0, 0, 1], ctrl_size=ctrl_size)
        thcto_cls.create()
        self.ctrl_list = thcto_cls.new_ctrl_list
        for i, n in enumerate(self.main_joints):
            main = n + '_muscle_grp'
            if not cmds.objExists(main):
                cmds.group(em=True, n=main)
                AdsorptionObj([main], n, 'tr')
                cmds.parentConstraint([n, main], mo=True, weight=1)
                cmds.scaleConstraint([n, main], mo=True, weight=1)
                cmds.parent(main, 'extrude_data')
            cmds.parent(thcto_cls.new_ctrl_grp_list[i], main)
            node_list = thFindSkinNode(mesh_list)
            for node in node_list:
                cmds.skinCluster(node, e=True, ai=self.new_joint[i], wt=0)

        cmds.select(cl=True)

    def reset_sys_data(self):
        dict_ = eval(cmds.getAttr('extrude_data.notes'))
        joints = dict_.keys()
        for j in joints:
            if not cmds.objExists(j):
                dict_.pop(j)

        if dict_:
            cmds.setAttr('extrude_data.notes', str(dict_), type='string')
        else:
            cmds.delete('extrude_data')


class ThSelectWeightVtx(object):

    def __init__(self):
        u"""回傳 weight 不為 1 的頂點"""
        self.sel = cmds.ls(sl=True, fl=True)
        self.joint = []
        self.mesh = []
        self.vtx_list = []
        self._analysis()
        self._set()

    def _analysis(self):
        for i, s in enumerate(self.sel):
            if '.' in s:
                self.vtx_list.append(s)
            else:
                type = cmds.nodeType(s)
                if type == 'joint':
                    self.joint.append(s)
                else:
                    self.mesh.append(s)

        mesh = None
        if self.vtx_list:
            mesh = self.vtx_list[0].split('.')[0]
        else:
            mesh = self.mesh[0]
            vertex_num = cmds.polyEvaluate(mesh, v=True)
            for i in range(vertex_num):
                self.vtx_list.append(('{}.vtx[{}]').format(mesh, i))

        self.skin_node = thFindSkinNode([mesh])[0]
        return

    def _set(self):
        new_vtx = []
        for vtx in self.vtx_list:
            weight = cmds.skinPercent(self.skin_node, vtx, t=self.joint[0], q=True, v=True)
            if 0 < weight < 1:
                new_vtx.append(vtx)

        cmds.select(new_vtx, r=True)


class ThTwoListTools(object):

    def __init__(self, main_list, operation_list, mode):
        u"""兩列表交互操作工具"""
        self.main_list = main_list
        self.operation_list = operation_list
        self.mode = mode
        app_dict = {'parent': self._parent, 
           'skin': self._skin, 
           'skin select': self._skin_select, 
           'blendShape': self._blend, 
           'wire': self._wire, 
           'adsorption': self._adsorption, 
           'data transfer': self._data_transfer, 
           'data transfer not': self._data_transfer_not, 
           'vtx transfer': self._vtx_transfer, 
           'wrap': self._wrap, 
           'axis adsorption': self._axisAdsorption}
        errorObj = []
        for i, main in enumerate(main_list):
            try:
                app_dict[self.mode](self.operation_list[i], main)
            except:
                errorObj.append(self.operation_list[i])
                errorObj.append(main)

        if errorObj:
            cmds.select(errorObj, r=True)

    def _vtx_transfer(self, list1, list2):
        ThSetMeshPoint().apply(list2, list1)

    def _axisAdsorption(self, list1, list2):
        thEditPivot([list2], list1)

    def _wrap(self, list1, list2):
        cmds.select([list1, list2], r=True)
        mel.eval('doWrapArgList "7" {"1","0","1","2","0","1","0"}')

    def _parent(self, list1, list2):
        cmds.parent(list1, list2)

    def _blend(self, list1, list2):
        node = cmds.blendShape(list2, list1, automatic=True)[0]
        cmds.setAttr(node + '.w[0]', 1)

    def _wire(self, list1, list2):
        cmds.wire(list1, gw=False, en=1, ce=0, li=0, w=list2)

    def _adsorption(self, list1, list2):
        AdsorptionObj([list1], list2, 'tr')

    def _data_transfer(self, obj2, obj1):
        thDataTransfer([obj1], [obj2], mode)

    def _data_transfer_not(self, obj2, obj1):
        thDataTransfer([obj1], [obj2], False)

    def _skin_select(self, list1, list2):
        cmds.skinCluster(list1, list2, mi=5, dr=4.0, tsb=True)

    def _skin(self, list1, list2):
        cmds.skinCluster(list1, list2, mi=5, dr=4.0)


class AdsorptionObj(object):

    def __init__(self, objs, main, mode='tr', ifFreeze=False, tangentAim=[0, 1, 0], funMode='constrain'):
        u"""吸附物件.
        :type objs: list
        :type mode: str
            't' | 'r' | 'tr' | 'tangent' | 'vertex'
        :return: list
            物件座標
        """
        self.objs = objs
        self.main = main
        self.mode = mode
        self.ifFreeze = ifFreeze
        self.tangentAim = tangentAim
        self.funMode = funMode
        if self.funMode == 'constrain':
            self.apply()
        elif self.funMode == 'get':
            self.applyG()

    def apply(self):
        modeDict = {'t': self._t, 
           'r': self._r, 'tr': self._tr, 'tangent': self._tangent, 
           'vertex': self._vertex}
        for obj in self.objs:
            modeDict[self.mode](obj)
            cmds.delete(self.node)

        if self.ifFreeze:
            cmds.makeIdentity(self.objs, apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.select(self.objs)

    def _t(self, obj):
        self.node = cmds.pointConstraint([self.main, obj], weight=1)

    def _r(self, obj):
        self.node = cmds.orientConstraint([self.main, obj], weight=1)

    def _tr(self, obj):
        self.node = cmds.parentConstraint([self.main, obj], weight=1)

    def _tangent(self, obj):
        self.node = cmds.tangentConstraint([
         self.main, obj], weight=1, worldUpType='vector', aimVector=[1, 0, 0], upVector=self.tangentAim, worldUpVector=self.tangentAim)

    def _vertex(self, obj):
        cmds.select([self.main, obj], r=True)
        self.node = cmds.pointOnPolyConstraint(offset=[0, 0, 0], weight=1)

    def applyG(self):
        modeDict = {'t': self._tG, 
           'r': self._rG, 'tr': self._trG, 'vertex': self._vertexG}
        modeDict[self.mode]()
        if self.ifFreeze:
            cmds.makeIdentity(self.objs, apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.select(self.objs)

    def _tG(self):
        pass

    def _rG(self):
        pass

    def _trG(self):
        pass

    def _vertexG(self):
        xyz = cmds.xform(self.main, q=True, ws=True, t=True)
        faceData = cmds.polyInfo(self.main, vf=True)[0].split(' ')
        faceData = [ n for n in faceData if n ]
        normal = cmds.polyInfo(('{}.f[{}]').format(self.main.split('.')[0], faceData[2]), fn=True)[0][:-1].split(' ')
        normal = [ n for n in normal if n ][2:]
        normal = [ float(n) for n in normal ]
        for n in self.objs:
            cmds.xform(n, ws=True, t=xyz)
            cmds.xform(n, ro=normal)


class ThRigCreateCtrl(object):
    mode_attr1 = [
     'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    mode_attr2 = ['tx', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    mode_attr3 = ['ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    mode_dict = {'nine': [
              'curve -d 1 -p 0 1 0 -p 1 1 0 -p 1 -1 0 -p -1 -1 0 \n    -p -1 1 0 -p 0 1 0 -p 0 -1 0 -p -1 -1 0 \n    -p -1 0 0 -p 1 0 0 -k 0 -k 1 -k 2 -k 3 \n    -k 4 -k 5 -k 6 -k 7 -k 8 -k 9',
              mode_attr1,
              [
               (-1, 1), (-1, 1)]], 
       'six up': [
                'curve -d 1 -p 0 1 0 -p -1 1 0 -p -1 0 0 -p 0 0 0 \n    -p 0 1 0 -p 1 1 0 -p 1 0 0 -p 0 0 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7',
                mode_attr1,
                [
                 (-1, 1), (0, 1)]], 
       'six dn': [
                'curve -d 1 -p 0 0 0 -p -1 0 0 -p -1 -1 0 -p 0 -1 0 \n    -p 0 0 0 -p 1 0 0 -p 1 -1 0 -p 0 -1 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7',
                mode_attr1,
                [
                 (-1, 1), (-1, 0)]], 
       'six left': [
                  'curve -d 1 -p 0 0 0 -p 0 1 0 -p -1 1 0 -p -1 0 0 \n    -p 0 0 0 -p 0 -1 0 -p -1 -1 0 -p -1 0 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7',
                  mode_attr1,
                  [
                   (-1, 0), (-1, 1)]], 
       'six right': [
                   'curve -d 1 -p 0 0 0 -p 0 1 0 -p 1 1 0 -p 1 0 0 \n    -p 0 0 0 -p 0 -1 0 -p 1 -1 0 -p 1 0 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7',
                   mode_attr1,
                   [
                    (0, 1), (-1, 1)]], 
       'up dn': [
               'curve -d 1 -p -0.200587 1 0 -p 0.200587 1 0 \n    -p 0.200587 0 0 -p -0.200587 0 0 -p 0.200587 0 0 \n    -p 0.200587 -1 0 -p -0.200587 -1 0 \n    -p -0.200587 1 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7\n',
               mode_attr2,
               [
                (0, 0), (-1, 1)]], 
       'left right': [
                    'curve -d 1 -p -1 0.200587 0 -p -1 -0.200587 0 \n    -p 0 -0.200587 0 -p 0 0.200587 0 -p 0 -0.200587 0 \n    -p 1 -0.200587 0 -p 1 0.200587 0 -p -1 0.200587 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 ;\n',
                    mode_attr3,
                    [
                     (-1, 1), (0, 0)]], 
       'up': [
            'curve -d 1 -p -0.200587 1 0 -p -0.200587 0 0 \n    -p 0.200587 0 0 -p 0.200587 1 0 -p -0.200587 1 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4',
            mode_attr2,
            [
             (0, 0), (0, 1)]], 
       'dn': [
            'curve -d 1 -p -0.200587 0 0 -p -0.200587 -1 0 \n    -p 0.200587 -1 0 -p 0.200587 0 0 -p -0.200587 0 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4',
            mode_attr2,
            [
             (0, 0), (-1, 0)]], 
       'left': [
              'curve -d 1 -p 0 0.200587 0 -p -1 0.200587 0 \n    -p -1 -0.200587 0 -p 0 -0.200587 0 -p 0 0.200587 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4',
              mode_attr3,
              [
               (-1, 0), (0, 0)]], 
       'right': [
               'curve -d 1 -p 0 0.200587 0 -p 1 0.200587 0 \n    -p 1 -0.200587 0 -p 0 -0.200587 0 -p 0 0.200587 0 \n    -k 0 -k 1 -k 2 -k 3 -k 4',
               mode_attr3,
               [
                (0, 1), (0, 0)]]}

    def __init__(self, name, mode):
        u"""創建拉霸控制器.
        :type mode: str
            'nine' | 
            'six_up' | 'six_dn' | 'six_left' | 'six_right' |
            'up_dn' | 'left_right' | 
            'up' | 'dn' | 'left' | 'right'
        """
        self.name = name
        self.mode = mode
        self.ctrl_name = None
        self.main_grp = None
        self.app()
        return

    def app(self):
        self.main_grp = cmds.group(em=True, n=self.name + '_main_grp#')
        self.tx_grp = cmds.group(em=True, n=self.name + '_tx_grp#')
        cmds.setAttr(self.tx_grp + '.template', 1)
        cmds.parent(self.tx_grp, self.main_grp)
        self.ctrl_str = '\ncircle -c 0 0 0 -nr 0 0 1 -sw 360 -r .2 -d 3 \n    -ut 0 -tol 0.01 -s 8 -ch 0'
        self.ctrl_name = mel.eval(self.ctrl_str)
        self.ctrl_name = cmds.rename(self.ctrl_name, self.name + '_ctrl#')
        self.ctrl_name_grp = cmds.group(self.ctrl_name, n=self.ctrl_name + '_grp#')
        cmds.parent(self.ctrl_name_grp, self.main_grp)
        thSetCtrlColor([self.ctrl_name], 22)
        for attr in self.mode_dict[self.mode][1]:
            cmds.setAttr(self.ctrl_name + '.' + attr, lock=True)
            cmds.setAttr(self.ctrl_name + '.' + attr, keyable=True)
            cmds.setAttr(self.ctrl_name + '.' + attr, keyable=False, channelBox=False)

        cmds.transformLimits(self.ctrl_name, tx=self.mode_dict[self.mode][2][0], ty=self.mode_dict[self.mode][2][1])
        cmds.transformLimits(self.ctrl_name, etx=(
         True, True), ety=(True, True))
        tx1_name = mel.eval(self.mode_dict[self.mode][0])
        tx1_name = cmds.rename(tx1_name, self.name + '_tx#')
        cmds.parent(tx1_name, self.tx_grp)
        cmds.select(self.main_grp, r=True)


class ThLockJointWeight(object):

    def __init__(self, objects, mode):
        u"""鎖定骨骼權重編輯.
        :type mode: str
            'lock' | 'nulock'
        """
        self.objects = objects
        self.mode = mode
        self._analysis()
        self._add_joint()
        self._set()
        if self.if_vtx:
            cmds.select(objects, r=True)
        else:
            cmds.select(self.mesh_list, r=True)

    def _analysis(self):
        u"""分析選擇物件"""
        self.mesh_list = []
        self.joint_list = []
        mesh = None
        self.if_vtx = False
        for obj in self.objects:
            if '.' in obj:
                mesh = obj.split('.')[0]
                self.if_vtx = True
                break

        if mesh:
            self.mesh_list.append(mesh)
        else:
            type_list = thType(self.objects)
            for i, type in enumerate(type_list):
                if type == 'mesh':
                    self.mesh_list.append(self.objects[i])
                elif type == 'joint':
                    self.joint_list.append(self.objects[i])

        return

    def _add_joint(self):
        self.skin_joints = []
        for m in self.mesh_list:
            skin_joints = thFindSkinJoint([m])
            self.skin_joints.extend(skin_joints)
            for j in self.joint_list:
                if j not in skin_joints:
                    cmds.skinCluster(m, e=True, wt=0, ai=j)
                    self.skin_joints.append(j)

    def _set(self):
        skin_list = thFindSkinNode(self.mesh_list)
        for j in self.skin_joints:
            cmds.setAttr(j + '.liw', 0)

        for i, skin in enumerate(skin_list):
            if cmds.getAttr(skin + '.normalizeWeights') != 1:
                cmds.setAttr(skin + '.normalizeWeights', 1)
                cmds.skinPercent(skin, self.mesh_list[i], normalize=True)

        app = True if self.mode == 'lock' else False
        app_dict = {}
        for j in self.skin_joints:
            app_dict[j] = app

        for j in self.joint_list:
            app_dict[j] = False if app_dict[j] else True

        for j in self.skin_joints:
            try:
                cmds.setAttr(j + '.liw', app_dict[j])
            except RuntimeError:
                pass


class ThRigMouth(object):
    """拉鍊嘴型"""

    def __init__(self, up_left, up_right, down_left, down_right, head, jaw, jaw_ctrl, ctrl_mode, mouth_corner=None, if_grp=True, if_ctrl=True, ctrl_style='hexagon', ctrl_axial='z', center_ref_loc=None, replace_str='_joint', combine_ctrl_loc_list1=None, combine_ctrl_loc_list2_1=None, combine_ctrl_loc_list2_2=None, preclude_up_list=None, preclude_dn_list=None):
        self.mouth_corner = mouth_corner
        self.up_left = up_left
        self.up_right = up_right
        self.down_left = down_left
        self.down_right = down_right
        self.head = head
        self.jaw = jaw
        self.jaw_ctrl = jaw_ctrl
        self.ctrl_mode = ctrl_mode
        self.if_grp = if_grp
        self.if_ctrl = if_ctrl
        self.ctrl_style = ctrl_style
        self.ctrl_axial = ctrl_axial
        self.center_ref_loc = center_ref_loc
        self.replace_str = replace_str
        self.combine_ctrl_loc_list1 = combine_ctrl_loc_list1
        self.combine_ctrl_loc_list2_1 = combine_ctrl_loc_list2_1
        self.combine_ctrl_loc_list2_2 = combine_ctrl_loc_list2_2
        self.preclude_up_list = preclude_up_list
        self.preclude_dn_list = preclude_dn_list
        self.do_up_right = self.up_right
        self.do_up_left = self._get_do_l_listF(self.up_left, self.up_right)
        self.do_dn_right = self.down_right
        self.do_dn_left = self._get_do_l_listF(self.down_left, self.down_right)
        self.do_list = self.do_up_left[0] + self.do_up_right + self.do_dn_left[0] + self.do_dn_right
        self.preclude_all_up_id = []
        self.preclude_all_dn_id = []
        self.preclude_all_up_id = [ i for i, n in enumerate(self.do_list) if n in self.preclude_up_list ]
        self.preclude_all_dn_id = [ i for i, n in enumerate(self.do_list) if n in self.preclude_dn_list ]
        self.preclude_up_id = [ i for i, n in enumerate(self.do_up_left[0] + self.do_up_right) if n in self.preclude_up_list ]
        self.preclude_dn_id = [ i for i, n in enumerate(self.do_dn_left[0] + self.do_dn_right) if n in self.preclude_dn_list ]
        self.applyF()

    def applyF(self):
        self._in_locF()
        if self.if_ctrl:
            self._ctrlF()
        if self.if_grp:
            self._loc_grpF()
        self._rigF()
        if self.combine_ctrl_loc_list1:
            self._main_ctrlF(list_=self.combine_ctrl_loc_list1, do_ctrl_list=self.do_ctrl_list, preclude_id=self.preclude_all_up_id + self.preclude_all_dn_id, p2=self.sys_grp)
        if self.combine_ctrl_loc_list2_1:
            self._main_ctrlF(self.combine_ctrl_loc_list2_1, self.do_up_ctrl_list, self.preclude_up_id, 'triangle', 6, self.sys_grp)
        if self.combine_ctrl_loc_list2_2:
            self._main_ctrlF(self.combine_ctrl_loc_list2_2, self.do_dn_ctrl_list, self.preclude_dn_id, 'triangle', 6, self.jaw_ctrl)
        cmds.select(self.jaw_ctrl, r=True)

    def _main_ctrlF(self, list_, do_ctrl_list, preclude_id, ctrl_style='hexagon', ctrl_color=22, p2=None):
        if do_ctrl_list:
            self.cto = THCtrlToObject(obj_list=list_, ctrl_color=ctrl_color, ctrl_method='None', if_use_obj_name=True, replace_str=self.replace_str, ctrl_axial=self.ctrl_axial, if_parent=False, if_create_main_grp=False, ctrl_style=ctrl_style)
            self.cto.create()
            new_ctrl_list = self.cto.new_ctrl_list
            new_ctrl_grp_list = self.cto.new_ctrl_grp_list
            ctrl_grp = cmds.group(new_ctrl_grp_list, n='main_mouth_ctrl_grp#')
            do_ctrl_list = [ n for i, n in enumerate(do_ctrl_list) if i not in preclude_id ]
            loc_list = ThDuplicateWithoutChildrenCon(thLocatorGrp(do_ctrl_list)).createConLocF()
            loc_grp = cmds.group(loc_list[1], n='mouth_main_loc_grp#')
            cmds.hide(loc_grp)
            joint_list = thWeightToCtrl(new_ctrl_list, loc_list[0])
            main_grp = cmds.group(em=True, n='main_mouth_sys_grp#')
            cmds.parent(main_grp, p2)
            cmds.parent([ctrl_grp, loc_grp], main_grp)
            ThCoordinateCreateMeshEx(list_=joint_list, aim='y', offset=0.1, ifLoop=False)

    def _get_do_l_listF(self, l_list, r_list):
        u"""回傳左邊列表"""
        if_split = None
        do_l_list = None
        if r_list[(-1)] in l_list:
            if_split = True
            do_l_list = l_list[:-1]
        else:
            if_split = False
            do_l_list = l_list
        return [
         do_l_list, if_split]

    def _in_locF(self):
        lo = cmds.spaceLocator(n='in_jaw_locator#')[0]
        lo_grp = cmds.group(lo, n='in_jaw_locator_grp#')
        head = cmds.spaceLocator(n='head_locator#')[0]
        head_grp = cmds.group(head, n='head_locator_grp#')
        jaw = cmds.spaceLocator(n='jaw_locator#')[0]
        jaw_grp = cmds.group(jaw, n='jaw_locator_grp#')
        self.loc_main_grp = cmds.group([lo_grp, head_grp, jaw_grp], n='mouthZipperLocator_grp#')
        cmds.hide(self.loc_main_grp)
        AdsorptionObj([lo_grp], self.jaw, 't')
        AdsorptionObj([head_grp], self.head, 't')
        AdsorptionObj([jaw_grp], self.jaw, 't')
        cmds.parentConstraint([self.jaw, lo], mo=True, weight=1)
        cmds.parentConstraint([self.head, head], mo=True, weight=1)
        cmds.parentConstraint([self.jaw, jaw], mo=True, weight=1)
        key_attr = [
         'tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        jaw_key_attr = [ lo + '.' + n for n in key_attr ]
        cmds.setDrivenKeyframe(jaw_key_attr, cd=lo + '.v', itt='linear', ott='linear')
        cmds.setAttr(lo + '.blendParent1', 0.5)
        self.in_jaw = [lo, head, jaw]

    def _do_ctrlF(self, color, list_):
        self.cto.obj_list = list_
        self.cto.ctrl_color = color
        self.cto.create()
        ctrl = self.cto.new_ctrl_list
        ctrl_grp = self.cto.new_ctrl_grp_list
        return [ctrl, ctrl_grp]

    def _ctrlF(self):
        self.cto = THCtrlToObject(obj_list=[], if_use_obj_name=True, replace_str=self.replace_str, ctrl_style=self.ctrl_style, ctrl_axial=self.ctrl_axial, if_parent=False, if_create_main_grp=False)
        self.do_up_left[0], do_up_left_grp = self._do_ctrlF(14, self.do_up_left[0])
        self.do_up_right, do_up_right_grp = self._do_ctrlF(14, self.do_up_right)
        self.do_dn_left[0], do_dn_left_grp = self._do_ctrlF(14, self.do_dn_left[0])
        self.do_dn_right, do_dn_right_grp = self._do_ctrlF(14, self.do_dn_right)
        self.do_up_ctrl_list = self.do_up_left[0] + self.do_up_right
        self.do_dn_ctrl_list = self.do_dn_left[0] + self.do_dn_right
        self.do_ctrl_list = self.do_up_left[0] + self.do_up_right + self.do_dn_left[0] + self.do_dn_right
        self.do_ctrl_list_grp = do_up_left_grp + do_up_right_grp + do_dn_left_grp + do_dn_right_grp
        ctrl_main_grp = do_up_right_grp + do_up_left_grp + do_dn_right_grp + do_dn_left_grp
        if self.mouth_corner:
            self.cto.obj_list = self.mouth_corner
            self.cto.ctrl_color = 6
            self.cto.create()
            self.mouth_corner = self.cto.new_ctrl_list
            ctrl_main_grp.extend(self.cto.new_ctrl_grp_list)
        self.ctrl_main_grp = cmds.group(ctrl_main_grp, n='mouthZipperCtrl_grp#')
        cmds.xform(self.ctrl_main_grp, cp=True)
        self.cto = THCtrlToObject(obj_list=[
         self.center_ref_loc if self.center_ref_loc else self.ctrl_main_grp], if_use_obj_name=False, name='mouth_main', ctrl_style='hexagon', ctrl_axial=self.ctrl_axial, if_parent=False, if_create_main_grp=False, ctrl_color=13, ctrl_method='constrain' if self.center_ref_loc else 'not')
        self.cto.create()
        self.main_rotate_ctrl = self.cto.new_ctrl_list[0]
        self.main_rotate_ctrl_grp = self.cto.new_ctrl_grp_list[0]
        cmds.parent(self.ctrl_main_grp, self.main_rotate_ctrl)
        self.cto = THCtrlToObject(obj_list=[
         self.jaw], if_use_obj_name=True, replace_str=self.replace_str, ctrl_color=13, ctrl_style='triangle', ctrl_axial=self.ctrl_axial, if_parent=False, if_create_main_grp=False)
        self.cto.create()
        self.jaw_ctrl = self.cto.new_ctrl_list[0]
        self.jaw_ctrl_grp = self.cto.new_ctrl_grp_list[0]
        self.sys_grp = cmds.group([self.loc_main_grp, self.main_rotate_ctrl_grp, self.jaw_ctrl_grp], n='mouthZipperSystem_grp#')
        if self.preclude_up_list and self.preclude_dn_list:
            grp = cmds.group(em=True, n='cheek_main_ctrl_grp#')
            cmds.parent(grp, self.main_rotate_ctrl_grp)
            p_up_ctrl_grp = [ n for i, n in enumerate(self.do_ctrl_list_grp) if i in self.preclude_all_up_id ]
            p_dn_ctrl_grp = [ n for i, n in enumerate(self.do_ctrl_list_grp) if i in self.preclude_all_dn_id ]
            cmds.parent(p_up_ctrl_grp + p_dn_ctrl_grp, grp)

    def _loc_grpF(self):
        self.do_up_left[0], up_left_loc_grp = ThDuplicateWithoutChildrenCon(thLocatorGrp(self.do_up_left[0])).createConLocF()
        self.do_up_right, up_right_loc_grp = ThDuplicateWithoutChildrenCon(thLocatorGrp(self.do_up_right)).createConLocF()
        self.do_dn_left[0], down_left_loc_grp = ThDuplicateWithoutChildrenCon(thLocatorGrp(self.do_dn_left[0])).createConLocF()
        self.do_dn_right, down_right_loc_grp = ThDuplicateWithoutChildrenCon(thLocatorGrp(self.do_dn_right)).createConLocF()
        loc_grp_list = up_left_loc_grp + up_right_loc_grp + down_left_loc_grp + down_right_loc_grp
        loc_main_grp = cmds.group(loc_grp_list, n='mouthConZipperLocator_grp#')
        cmds.parent(loc_main_grp, self.loc_main_grp)
        cmds.hide(loc_main_grp)
        if self.preclude_up_list and self.preclude_dn_list:
            grp = cmds.group(em=True, n='cheek_main_loc_grp#')
            cmds.parent(grp, self.main_rotate_ctrl_grp)
            cmds.hide(grp)
            p_up_loc_grp = [ n for i, n in enumerate(loc_grp_list) if i in self.preclude_all_up_id ]
            p_dn_loc_grp = [ n for i, n in enumerate(loc_grp_list) if i in self.preclude_all_dn_id ]
            cmds.parent(p_up_loc_grp + p_dn_loc_grp, grp)

    def _rigF(self):
        if not cmds.listAttr(self.jaw_ctrl, m=True, st='up_down'):
            cmds.addAttr(self.jaw_ctrl, ln='up_down', at='double', min=0, max=1, dv=0.5, k=True)
        cmds.connectAttr(self.jaw_ctrl + '.up_down', self.in_jaw[0] + '.blendParent1')
        if self.mouth_corner:
            for corner in self.mouth_corner:
                cmds.parentConstraint([self.in_jaw[0], corner], mo=True, w=1)

        TwoObjCtrl(self.in_jaw[0], self.in_jaw[1], self.do_up_left[0] + [self.do_up_right[(-1)]] if self.do_up_left[1] else self.do_up_left[0], self.jaw_ctrl, self.ctrl_mode, self.do_up_left[1], 'L_follow', 'L_offset')
        TwoObjCtrl(self.in_jaw[0], self.in_jaw[1], self.do_up_right, self.jaw_ctrl, self.ctrl_mode, False, 'R_follow', 'R_offset')
        TwoObjCtrl(self.in_jaw[0], self.in_jaw[2], self.do_dn_left[0] + [self.do_dn_right[(-1)]] if self.do_dn_left[1] else self.do_dn_left[0], self.jaw_ctrl, self.ctrl_mode, self.do_dn_left[1], 'L_follow', 'L_offset')
        TwoObjCtrl(self.in_jaw[0], self.in_jaw[2], self.do_dn_right, self.jaw_ctrl, self.ctrl_mode, False, 'R_follow', 'R_offset')
        if self.preclude_up_list and self.preclude_dn_list:
            loc_list = self.do_up_left[0] + self.do_up_right + self.do_dn_left[0] + self.do_dn_right
            p_up_loc = [ n for i, n in enumerate(loc_list) if i in self.preclude_all_up_id ]
            p_dn_loc = [ n for i, n in enumerate(loc_list) if i in self.preclude_all_dn_id ]
            p_all_loc = p_up_loc + p_dn_loc
            key_list = [ ('{}.{}').format(n, nn) for n in p_all_loc for nn in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'] ]
            cmds.setDrivenKeyframe(key_list, cd=('{}.v').format(self.sys_grp), itt='linear', ott='linear')
            cmds.addAttr(self.jaw_ctrl, ln='cheek_weight', at='double', min=0, max=1, dv=0.3, k=True)
            for n in p_all_loc:
                cmds.connectAttr(('{}.cheek_weight').format(self.jaw_ctrl), ('{}.blendParent1').format(n))


class ThTwoObjWeightBlend(object):

    def __init__(self, mainObjList, refObj, mainJointList, refJointList=None, om2=False, doPruneWeightsArgList=False):
        u"""拆分權重值"""
        self.refObj = refObj
        self.mainObjList = mainObjList
        self.refJointList = refJointList if refJointList else thFindSkinJoint([refObj])
        self.mainJointList = mainJointList
        self.om2 = om2
        self.doPruneWeightsArgList = doPruneWeightsArgList
        self.applyF()

    def applyF(self):
        progressBar = ThQProgressBar(1)
        progressBar.setStrat(0, '', len(self.mainObjList))
        for mainObj in self.mainObjList:
            progressBar.setFrame(0, mainObj)
            self.mainSkin = thFindSkinNode([mainObj])[0]
            cmds.skinCluster(self.mainSkin, e=True, fnw=True, normalizeWeights=1)
            cmds.setAttr(self.mainSkin + '.maintainMaxInfluences', 0)
            self._addJointF(mainObj)
            ThLockJointWeight([mainObj], 'nulock')
            self._copyRefF(mainObj)
            if self.om2:
                self._setWeightOm2F(mainObj)
                cmds.select(mainObj, r=True)
                if self.doPruneWeightsArgList:
                    mel.eval('doPruneSkinClusterWeightsArgList 1 {"0.0001"};')
            else:
                self._setWeightMelF()
            cmds.delete(self.refObjCopy)

        cmds.select(self.mainObjList, r=True)
        progressBar.deleteLater()

    def _setWeightMelF(self):
        for mainJoint in self.mainJointList:
            self._getF(mainJoint)
            self._setF(mainJoint)

    def _setWeightOm2F(self, mainObj):
        mainCwa = ThCopyWeightApi()
        mainCwa.getWeightDataF(mainObj)
        refCwa = ThCopyWeightApi()
        refCwa.getWeightDataF(self.refObjCopy)
        for mainJoint in self.mainJointList:
            cmds.select(cl=True)
            cmds.skinCluster(self.mainSkin, e=True, siv=mainJoint)
            self.mainVtxList = cmds.ls(sl=True, fl=True)
            if '.' not in ('').join(self.mainVtxList):
                continue
            idList = [ int(n.split('.')[1][4:-1]) for n in self.mainVtxList ]
            baseDataDict = copy.deepcopy(mainCwa.dataDict)
            refJointList = []
            ifMoveFinallyWeight = None
            if mainJoint in self.refJointList:
                refJointList = [ n for n in self.refJointList if n != mainJoint ]
                ifMoveFinallyWeight = False
            else:
                refJointList = self.refJointList[:-1]
                ifMoveFinallyWeight = True
            for refJoint in refJointList:
                idListData = []
                for id in idList:
                    idListData.append(refCwa.dataDict[refJoint][id] * baseDataDict[mainJoint][id])

                mainCwa.editWeightDataF(idList=idList, idListData=idListData, joint=refJoint, otherJointList=[mainJoint])

            if ifMoveFinallyWeight:
                mainCwa.editWeightDataF(idList=idList, idListData=[0] * len(idList), joint=mainJoint, otherJointList=[self.refJointList[(-1)]])
            mainCwa.setWeightDataF()

        return

    def _addJointF(self, mainObj):
        u"""添加 joint"""
        mainJointList = thFindSkinJoint([mainObj])
        for joint in self.refJointList:
            if joint not in mainJointList:
                cmds.skinCluster(self.mainSkin, e=True, lw=True, wt=0, ai=joint)

    def _copyRefF(self, mainObj):
        u"""複製新權重模型"""
        self.refObjCopy = cmds.duplicate(mainObj, rr=True, rc=True)[0]
        tcsaw = THCopySkinAndWeight([self.refObj], [self.refObjCopy])
        tcsaw.copy_skin()
        tcsaw.copy_weight()
        tcsaw.set_max_influences()
        self.copyMainSkin = thFindSkinNode([self.refObjCopy])[0]

    def _getF(self, mainJoint):
        cmds.select(cl=True)
        cmds.skinCluster(self.mainSkin, e=True, siv=mainJoint)
        self.mainVtxList = cmds.ls(sl=True, fl=True)
        self.mainWeightList = []
        for i, vtx in enumerate(self.mainVtxList):
            self.mainWeightList.append(cmds.skinPercent(self.mainSkin, vtx, t=mainJoint, q=True, v=True))

    def _setF(self, mainJoint):
        refVtxList = []
        for n in self.mainVtxList:
            refVtxList.append(('{}.{}').format(self.refObjCopy, n.split('.')[1]))

        refList0 = []
        for vtx in refVtxList:
            refList1 = []
            for joint in self.refJointList:
                refWeight = cmds.skinPercent(self.copyMainSkin, vtx, t=joint, q=True, v=True)
                if refWeight:
                    refList1.append([joint, refWeight])

            refList0.append(refList1)

        for i, vtx in enumerate(refVtxList):
            for ii, jointWeight in enumerate(refList0[i], 1):
                mainWeight = cmds.skinPercent(self.mainSkin, self.mainVtxList[i], t=mainJoint, q=True, v=True)
                mainWeightR = cmds.skinPercent(self.mainSkin, self.mainVtxList[i], t=jointWeight[0], q=True, v=True)
                jointData = None
                mainJointData = None
                if len(refList0[i]) != ii:
                    jointData = self.mainWeightList[i] * jointWeight[1]
                    mainJointData = mainWeight - jointData
                    jointData += mainWeightR
                else:
                    jointData = mainWeight + mainWeightR
                    mainJointData = 0
                cmds.skinPercent(self.mainSkin, self.mainVtxList[i], tv=[(jointWeight[0], jointData), (mainJoint, mainJointData)])

        return


class ChangeFilePath(object):

    def __init__(self):
        u"""更改貼圖路徑"""
        pass

    def change_path(self, new_path):
        if not cmds.objExists('file_path_system'):
            cmds.group(em=True, n='file_path_system')
            cmds.addAttr('file_path_system', sn='nts', ln='notes', dt='string')
            cmds.setAttr('file_path_system.notes', '{}', type='string')
            path_dict = {}
            file_list = cmds.ls(typ='file')
            for file in file_list:
                path = cmds.getAttr(file + '.fileTextureName')
                path_dict[file] = path
                new_path.replace('/', '\\')
                file_name = os.path.basename(path)
                cmds.setAttr(file + '.fileTextureName', new_path + '/' + file_name, type='string')

            cmds.setAttr('file_path_system.notes', path_dict, type='string')

    def reset_path(self):
        if cmds.objExists('file_path_system'):
            str_ = cmds.getAttr('file_path_system.notes')
            path_dict = eval(str_)
            for file in path_dict:
                cmds.setAttr(file + '.fileTextureName', path_dict[file], type='string')

            cmds.delete('file_path_system')


class AffectSystemList(object):
    ui = 'th_affectSystemList_{}_ui'

    def __init__(self):
        self.sys_dict = None
        self.create()
        return

    def create(self):
        if cmds.objExists('affectSystem_data'):
            if cmds.window(self.ui.format('main'), ex=True):
                cmds.deleteUI(self.ui.format('main'))
            p_win = cmds.window(self.ui.format('main'), title='List')
            cmds.formLayout(self.ui.format('form'), w=400)
            cmds.textScrollList(self.ui.format('list'), h=150, ams=True, sc=lambda *args: self._select_list_obj(), dcc=lambda *args: self._label_to_ui())
            cmds.button(self.ui.format('del'), h=20, l='delete', c=lambda *args: self._del())
            cmds.button(self.ui.format('start'), h=20, l='to start pose', c=lambda *args: self._to_pose('start'))
            cmds.button(self.ui.format('end'), h=20, l='to end pose', c=lambda *args: self._to_pose('end'))
            cmds.textScrollList(self.ui.format('objs'), h=150, ams=True, sc=lambda *args: self._select_list2_objs('objs'))
            cmds.textScrollList(self.ui.format('ctrl'), h=150, ams=True, sc=lambda *args: self._select_list2_objs('ctrl'))
            cmds.showWindow(self.ui.format('main'))
            self._set_main_form_eui()
            self._input()

    def _set_main_form_eui(self):
        ac_ = []
        an_ = []
        af_ = []
        ap_ = []
        af_.append([self.ui.format('list'), 'top', 2])
        ac_.append([self.ui.format('list'), 'bottom', 5,
         self.ui.format('del')])
        af_.append([self.ui.format('list'), 'left', 2])
        ap_.append([self.ui.format('list'), 'right', 2, 40])
        an_.append([self.ui.format('del'), 'top'])
        ac_.append([self.ui.format('del'), 'bottom', 5,
         self.ui.format('start')])
        af_.append([self.ui.format('del'), 'left', 2])
        ap_.append([self.ui.format('del'), 'right', 2, 40])
        an_.append([self.ui.format('start'), 'top'])
        af_.append([self.ui.format('start'), 'bottom', 2])
        af_.append([self.ui.format('start'), 'left', 2])
        ap_.append([self.ui.format('start'), 'right', 2, 20])
        an_.append([self.ui.format('end'), 'top'])
        af_.append([self.ui.format('end'), 'bottom', 2])
        ap_.append([self.ui.format('end'), 'left', 2, 20])
        ap_.append([self.ui.format('end'), 'right', 2, 40])
        af_.append([self.ui.format('objs'), 'top', 2])
        ap_.append([self.ui.format('objs'), 'bottom', 2, 50])
        ap_.append([self.ui.format('objs'), 'left', 2, 40])
        af_.append([self.ui.format('objs'), 'right', 2])
        ap_.append([self.ui.format('ctrl'), 'top', 2, 50])
        af_.append([self.ui.format('ctrl'), 'bottom', 2])
        ap_.append([self.ui.format('ctrl'), 'left', 2, 40])
        af_.append([self.ui.format('ctrl'), 'right', 2])
        cmds.formLayout(self.ui.format('form'), e=True, af=af_, ac=ac_, an=an_, ap=ap_)

    def _input(self):
        u"""寫入列表"""
        if cmds.objExists('affectSystem_data'):
            sys_str = cmds.getAttr('affectSystem_data.notes')
            self.sys_dict = eval(sys_str)
            cmds.textScrollList(self.ui.format('list'), e=True, ra=True)
            cmds.textScrollList(self.ui.format('objs'), e=True, ra=True)
            cmds.textScrollList(self.ui.format('ctrl'), e=True, ra=True)
            label = self.sys_dict['label'].keys()
            label.sort()
            for n in label:
                cmds.textScrollList(self.ui.format('list'), e=True, a=n)

        else:
            cmds.deleteUI(self.ui.format('main'))

    def _select_list_obj(self):
        u"""選擇列表物件"""
        label_list = cmds.textScrollList(self.ui.format('list'), q=True, si=True)
        label = label_list[0]
        ctrl_list = []
        for n in label_list:
            ctrl_list.extend(self.sys_dict['label'][n]['ctrl'])

        ctrl_list = list(set(ctrl_list))
        cmds.select(ctrl_list, r=True)
        cmds.textScrollList(self.ui.format('objs'), e=True, ra=True)
        for n in self.sys_dict['label'][label]['objs']:
            cmds.textScrollList(self.ui.format('objs'), e=True, a=n)

        cmds.textScrollList(self.ui.format('ctrl'), e=True, ra=True)
        for n in self.sys_dict['label'][label]['ctrl']:
            cmds.textScrollList(self.ui.format('ctrl'), e=True, a=n)

    def _select_list2_objs(self, ui):
        u"""選擇列表物件"""
        sel_list = cmds.textScrollList(self.ui.format(ui), q=True, si=True)
        cmds.select(sel_list, r=True)

    def _del(self):
        u"""刪除指定物件"""
        label = cmds.textScrollList(self.ui.format('list'), q=True, si=True)
        THAffectSystem().delete_attr(label)
        self._input()

    def _to_pose(self, mode):
        label = cmds.textScrollList(self.ui.format('list'), q=True, si=True)
        THAffectSystem().set_ctrl(mode, label)

    def _label_to_ui(self):
        label = cmds.textScrollList(self.ui.format('list'), q=True, si=True)[0]
        ui = 'th_rig_affectSystem_{}_ui'
        cmds.textField(ui.format('labelName'), e=True, tx=label)


class ThDrivenKeySystemList(object):
    ui = 'th_drivenKeySystemList_{}_ui'

    def __init__(self):
        self.sys_dict = None
        self.create()
        return

    def create(self):
        if cmds.objExists('drivenKeySystem_data'):
            if cmds.window(self.ui.format('main'), ex=True):
                cmds.deleteUI(self.ui.format('main'))
            p_win = cmds.window(self.ui.format('main'), title='List')
            cmds.formLayout(self.ui.format('form'), w=400)
            cmds.textScrollList(self.ui.format('list'), h=150, ams=True, sc=lambda *args: self._select_list_obj('obj'))
            cmds.textScrollList(self.ui.format('obj'), h=150, ams=True, sc=lambda *args: self._select_list2_objs('obj'))
            cmds.textScrollList(self.ui.format('grp'), h=150, ams=True, sc=lambda *args: self._select_list2_objs('grp'))
            cmds.button(self.ui.format('del'), h=20, l='delete', c=lambda *args: self._del())
            cmds.button(self.ui.format('selectGrp'), h=20, l='select grp', c=lambda *args: self._select_list_obj('grp'))
            cmds.showWindow(self.ui.format('main'))
            self._set_main_form_eui()
            self._input()

    def _set_main_form_eui(self):
        ac_ = []
        an_ = []
        af_ = []
        ap_ = []
        af_.append([self.ui.format('list'), 'top', 2])
        ac_.append([self.ui.format('list'), 'bottom', 5,
         self.ui.format('del')])
        af_.append([self.ui.format('list'), 'left', 2])
        ap_.append([self.ui.format('list'), 'right', 2, 45])
        an_.append([self.ui.format('del'), 'top'])
        ac_.append([self.ui.format('del'), 'bottom', 5,
         self.ui.format('selectGrp')])
        af_.append([self.ui.format('del'), 'left', 2])
        ap_.append([self.ui.format('del'), 'right', 2, 45])
        an_.append([self.ui.format('selectGrp'), 'top'])
        af_.append([self.ui.format('selectGrp'), 'bottom', 2])
        af_.append([self.ui.format('selectGrp'), 'left', 2])
        ap_.append([self.ui.format('selectGrp'), 'right', 2, 45])
        af_.append([self.ui.format('obj'), 'top', 2])
        ap_.append([self.ui.format('obj'), 'bottom', 2, 50])
        ap_.append([self.ui.format('obj'), 'left', 2, 45])
        af_.append([self.ui.format('obj'), 'right', 2])
        ap_.append([self.ui.format('grp'), 'top', 2, 50])
        af_.append([self.ui.format('grp'), 'bottom', 2])
        ap_.append([self.ui.format('grp'), 'left', 2, 45])
        af_.append([self.ui.format('grp'), 'right', 2])
        cmds.formLayout(self.ui.format('form'), e=True, af=af_, ac=ac_, an=an_, ap=ap_)

    def _input(self):
        u"""寫入列表"""
        if cmds.objExists('drivenKeySystem_data'):
            sys_str = cmds.getAttr('drivenKeySystem_data.notes')
            self.sys_dict = eval(sys_str)
            cmds.textScrollList(self.ui.format('list'), e=True, ra=True)
            cmds.textScrollList(self.ui.format('obj'), e=True, ra=True)
            cmds.textScrollList(self.ui.format('grp'), e=True, ra=True)
            ctrl_attr = self.sys_dict.keys()
            ctrl_attr.sort()
            for n in ctrl_attr:
                cmds.textScrollList(self.ui.format('list'), e=True, a=n)

        else:
            cmds.deleteUI(self.ui.format('main'))

    def _select_list_obj(self, type):
        u"""選擇列表物件"""
        ctrl_attr_list = cmds.textScrollList(self.ui.format('list'), q=True, si=True)
        ctrl_attr = ctrl_attr_list[0]
        cmds.textScrollList(self.ui.format('obj'), e=True, ra=True)
        for n in self.sys_dict[ctrl_attr]['obj']:
            cmds.textScrollList(self.ui.format('obj'), e=True, a=n)

        cmds.textScrollList(self.ui.format('grp'), e=True, ra=True)
        for n in self.sys_dict[ctrl_attr]['grp']:
            cmds.textScrollList(self.ui.format('grp'), e=True, a=n)

        obj_list = []
        for n in ctrl_attr_list:
            obj_list.extend(self.sys_dict[n][type])

        cmds.select(obj_list, r=True)

    def _select_list2_objs(self, ui):
        u"""選擇列表物件"""
        sel_list = cmds.textScrollList(self.ui.format(ui), q=True, si=True)
        cmds.select(sel_list, r=True)

    def _del(self):
        u"""刪除指定物件"""
        sel_list = cmds.textScrollList(self.ui.format('list'), q=True, si=True)
        obj_list = cmds.ls(sl=True)
        tdks_cls_del = THDrivenKeySystem()
        if obj_list:
            tdks_cls_del.delete(sel_list, obj_list)
        else:
            tdks_cls_del.delete(sel_list)
        self._input()


class THDrivenKeySystem(object):
    sys = 'drivenKeySystem_data'

    def __init__(self, ctrl_attr=None, objects=None, attr_list=None, if_grp=True, if_prefix=True):
        """Driven key system"""
        self.ctrl_attr = ctrl_attr
        self.objects = objects
        self.attr_list = attr_list
        self.if_grp = if_grp
        self.if_prefix = if_prefix

    def app(self):
        self._sys()
        self._grp()
        self._key()
        cmds.select(self.select_obj, r=True)

    def reDataF(self):
        u"""刷新數據"""
        data = eval(cmds.getAttr(self.sys + '.notes'))
        for k, v in data.items():
            objList = copy.copy(v['obj'])
            grpList = copy.copy(v['grp'])
            for g in v['grp']:
                if not cmds.objExists(g):
                    objList.pop(grpList.index(g))
                    grpList.remove(g)

            data[k]['obj'] = objList
            data[k]['grp'] = grpList

        cmds.setAttr(self.sys + '.notes', str(data), type='string')
        sys.stdout.write('更新完成!')

    def _sys(self):
        u"""創建紀錄用 grp"""
        if not cmds.objExists(self.sys):
            cmds.group(em=True, n=self.sys)
            cmds.addAttr(self.sys, sn='nts', ln='notes', dt='string')
            cmds.setAttr(self.sys + '.notes', '{}', type='string')
        self.sys_dict = eval(cmds.getAttr(self.sys + '.notes'))

    def _grp(self):
        u"""創建 group"""
        new_obj = self.objects
        new_grp = self.objects
        sys_obj = []
        sys_grp = []
        if self.ctrl_attr in self.sys_dict:
            new_obj = []
            new_grp = []
            sys_obj = self.sys_dict[self.ctrl_attr]['obj']
            sys_grp = self.sys_dict[self.ctrl_attr]['grp']
            for obj in self.objects:
                if obj not in sys_obj:
                    new_obj.append(obj)
                    new_grp.append(obj)

        if self.if_prefix and self.ctrl_attr:
            self.prefix = ('{}__').format(self.ctrl_attr.replace('.', '_'))
        if self.if_grp:
            new_grp = thLocatorGrp(new_grp)
            if self.if_prefix:
                new_grp = [ cmds.rename(n, self.prefix + n) for n in new_grp ]
        self.sys_dict[self.ctrl_attr] = {'obj': sys_obj + new_obj, 
           'grp': sys_grp + new_grp}
        cmds.setAttr(self.sys + '.notes', self.sys_dict, type='string')

    def _key(self):
        u"""設置 key"""
        self.select_obj = []
        for obj in self.objects:
            index = self.sys_dict[self.ctrl_attr]['obj'].index(obj)
            grp = self.sys_dict[self.ctrl_attr]['grp'][index]
            self.select_obj.append(grp)
            for attr in self.attr_list:
                try:
                    cmds.setDrivenKeyframe(grp + '.' + attr, cd=self.ctrl_attr, itt='linear', ott='linear')
                except:
                    pass

    def delete(self, ctrl_attrs, objs=None):
        self._sys()
        if objs:
            for ctrl_attr in ctrl_attrs:
                for obj in objs:
                    if obj in self.sys_dict[ctrl_attr]['obj']:
                        index = self.sys_dict[ctrl_attr]['obj'].index(obj)
                        try:
                            cmds.ungroup(self.sys_dict[ctrl_attr]['grp'][index])
                        except:
                            thDeleteDrivenKey([self.sys_dict[ctrl_attr]['grp'][index]])

                        self.sys_dict[ctrl_attr]['obj'].pop(index)
                        self.sys_dict[ctrl_attr]['grp'].pop(index)

                if not self.sys_dict[ctrl_attr]['obj']:
                    del self.sys_dict[ctrl_attr]

        else:
            for ctrl_attr in ctrl_attrs:
                try:
                    cmds.ungroup(self.sys_dict[ctrl_attr]['grp'])
                except:
                    thDeleteDrivenKey(self.sys_dict[ctrl_attr]['grp'])

                del self.sys_dict[ctrl_attr]

        if not self.sys_dict:
            cmds.delete(self.sys)
        else:
            sys_str = str(self.sys_dict)
            cmds.setAttr(self.sys + '.notes', sys_str, type='string')

    def delNotKey(self):
        if not cmds.objExists(self.sys):
            return
        groupList = []
        data = eval(cmds.getAttr(self.sys + '.notes'))
        valueList = data.values()
        for objGrp in valueList:
            groupList.extend(objGrp['grp'])

        cmds.delete(groupList, sc=True, uac=True)


class THAffectSystem(object):
    type_list = [
     'X', 'Y', 'Z']
    type_attr = ['tx', 'ty', 'tz']
    ctrl_attr = ['rx', 'ry', 'rz']

    def __init__(self, objs=None, name=None, aim='x', rotate_='object', offset=1, ctrl=None):
        u"""牽動系統.
        關於名稱
        - 把主要的 obj 名稱作為 dict 包存於 note
        - 再依據 obj 名稱產生其他分之名稱
        """
        self.objs = objs
        self.name = name
        self.aim = aim
        self.rotate_ = rotate_
        self.offset = offset
        self.ctrl = ctrl if ctrl else objs
        self.obj_sr_node = []
        self.locator = []
        self.all_node = []
        self.start_data = []
        self.end_data = []
        self.ctrl_start_data = []
        self.ctrl_end_data = []
        self.if_edit = False

    def create(self):
        self._note_init()
        self._get_sys_data()
        self._locator()
        self._create_node()
        self._note_save()
        cmds.select('affectSystem_data', r=True)

    def _note_init(self):
        u"""初始化"""
        if not cmds.objExists('affectSystem_data'):
            cmds.group(em=True, n='affectSystem_data')
            thLockHiddenAttr(['affectSystem_data'], [1, 1, 1, 1], 1)
            cmds.addAttr('affectSystem_data', sn='nts', ln='notes', dt='string')
            cmds.setAttr('affectSystem_data.notes', "{'label': {}, 'locator': {}}", type='string')

    def _get_sys_data(self):
        u"""讀取系統"""
        if cmds.listAttr('affectSystem_data', m=True, st=self.name):
            str_ = cmds.getAttr('affectSystem_data.notes')
            dict_ = eval(str_)
            self.objs = dict_['label'][self.name]['objs']
            self.ctrl = dict_['label'][self.name]['ctrl']
            try:
                self.start_data = dict_['label'][self.name]['pose']['start']
                self.end_data = dict_['label'][self.name]['pose']['end']
                self.ctrl_start_data = dict_['label'][self.name]['ctrl pose']['start']
                self.ctrl_end_data = dict_['label'][self.name]['ctrl pose']['end']
            except:
                pass

            self.if_edit = True
        else:
            self.if_edit = False

    def _locator(self):
        u"""創建定位器"""
        if not self.if_edit:
            for obj in self.objs:
                offset = '1' if self.offset > 0 else '0'
                name = ('{}_{}{}_affectSystem_').format(obj, self.rotate_, offset)
                if not cmds.objExists(name + 'LO'):
                    grp1 = cmds.group(em=True, n=name + 'RO_grp1')
                    grp2 = cmds.group(grp1, n=name + 'RO_grp2')
                    grp = cmds.group(grp2, n=name + 'LO_main_grp')
                    cmds.parent(grp, 'affectSystem_data')
                    lo = cmds.spaceLocator(n=name + 'LO')[0]
                    cmds.hide(lo)
                    lo_grp = cmds.group(lo, n=name + 'LO_grp')
                    cmds.parent(lo_grp, grp)
                    ro = 't' if self.rotate_ == 'world' else 'tr'
                    AdsorptionObj([grp], obj, ro)
                    cmds.setAttr(('{}.t{}').format(grp1, self.aim), self.offset)
                    cmds.setAttr(('{}.t{}').format(lo_grp, self.aim), self.offset)
                    cmds.orientConstraint([obj, grp2], mo=True, weight=1)
                    cmds.pointConstraint([grp1, lo], mo=True, weight=1)
                    father = cmds.listRelatives(obj, p=True)
                    if father:
                        cmds.parentConstraint([father[0], grp], mo=True, weight=1)

        offset = '1' if self.offset > 0 else '0'
        for obj in self.objs:
            self.locator.append(('{}_{}{}_affectSystem_LO').format(obj, self.rotate_, offset))

    def _create_node(self):
        u"""創建節點"""
        if not self.if_edit:
            cmds.addAttr('affectSystem_data', ln=self.name, at='double', k=True)
            cmds.addAttr('affectSystem_data', ln=self.name + '_switch', at='double', min=0, max=1, dv=1, k=True)
            all_sr_node = []
            for i, obj in enumerate(self.objs):
                node = cmds.createNode('setRange', n=('{}_{}_affectSystem_SR').format(self.name, obj))
                cmds.connectAttr(self.locator[i] + '.t', node + '.value')
                all_sr_node.append(node)
                self.all_node.append(node)

            formula = ''
            index = 1
            for n in all_sr_node:
                for type in self.type_list:
                    formula += ('{}.outValue{} * ').format(n, type)

            formula += ('affectSystem_data.{};').format(self.name + '_switch')
            formula = ('affectSystem_data.{} = {}').format(self.name, formula)
            self.all_node.append(cmds.expression(n=('{}_affectSystem_EX').format(self.name), s=formula))
        for obj in self.objs:
            self.obj_sr_node.append(('{}_{}_affectSystem_SR').format(self.name, obj))

    def _note_save(self):
        u"""保存數據 to notes"""
        str_ = cmds.getAttr('affectSystem_data.notes')
        dict_ = eval(str_)
        if not self.if_edit:
            dict_['label'][self.name] = {}
            dict_['label'][self.name]['objs'] = self.objs
            dict_['label'][self.name]['ctrl'] = self.ctrl
            dict_['label'][self.name]['del'] = self.all_node
            for lo in self.locator:
                dict_['locator'].setdefault(lo, [])
                if self.name not in dict_['locator'][lo]:
                    dict_['locator'][lo].append(self.name)

            cmds.setAttr('affectSystem_data.notes', dict_, type='string')

    def save_pose(self, mode):
        u"""保存位置.
        :type mode: str
            'start' | 'end'
        """
        save_data_0 = None
        ctrl_save_data_0 = None
        if mode == 'start':
            save_data_0 = self.start_data = []
            ctrl_save_data_0 = self.ctrl_start_data = []
        else:
            if mode == 'end':
                save_data_0 = self.end_data = []
                ctrl_save_data_0 = self.ctrl_end_data = []
            for i, obj in enumerate(self.objs):
                save_data_1 = []
                ctrl_save_data_1 = []
                for ii, type in enumerate(self.type_list):
                    data = cmds.getAttr(('{}.{}').format(self.locator[i], self.type_attr[ii]))
                    ctrl_data = cmds.getAttr(('{}.{}').format(self.ctrl[i], self.ctrl_attr[ii]))
                    save_data_1.append(round(data, 3))
                    ctrl_save_data_1.append(ctrl_data)

                save_data_0.append(save_data_1)
                ctrl_save_data_0.append(ctrl_save_data_1)

        return

    def set_data(self, use_value=1):
        u"""設定數據"""
        raw_dict_0 = {}
        app_dict_0 = {}
        max_dict_0 = {}
        for i, obj in enumerate(self.objs):
            raw_dict_1 = {}
            app_dict_1 = {}
            max_dict_1 = {}
            for ii, type in enumerate(self.type_list):
                min = max = old_min = old_max = None
                if self.start_data[i][ii] != self.end_data[i][ii]:
                    min, max = (0, 1)
                    old_min, old_max = self.start_data[i][ii], self.end_data[i][ii]
                    if old_min > old_max:
                        min, max = (1, 0)
                        old_min, old_max = old_max, old_min
                else:
                    min = max = old_max = 1
                    old_min = 0
                max_dict_1[type] = abs(old_min - old_max) - min * max
                attr_list = [
                 'min', 'max', 'oldMin', 'oldMax']
                raw_data_list = [1, 1, 0, 1]
                app_data_list = [min, max, old_min, old_max]
                raw_dict_2 = {}
                app_dict_2 = {}
                for iii, attr in enumerate(attr_list):
                    raw_dict_2[attr] = raw_data_list[iii]
                    app_dict_2[attr] = app_data_list[iii]

                raw_dict_1[type] = raw_dict_2
                app_dict_1[type] = app_dict_2

            raw_dict_0[self.obj_sr_node[i]] = raw_dict_1
            app_dict_0[self.obj_sr_node[i]] = app_dict_1
            max_dict_0[self.obj_sr_node[i]] = max_dict_1

        if use_value != 3:
            for node in max_dict_0:
                sort = sorted(max_dict_0[node].items(), reverse=True, key=lambda item: item[1])
                for type in sort[:use_value]:
                    raw_dict_0[node][type[0]] = app_dict_0[node][type[0]]

            app_dict_0 = raw_dict_0
        for node in app_dict_0:
            for type in app_dict_0[node]:
                for attr in app_dict_0[node][type]:
                    cmds.setAttr(node + '.' + attr + type, app_dict_0[node][type][attr])

        self._note_save_pose()
        return

    def _note_save_pose(self):
        u"""保存起始與結束位置"""
        str_ = cmds.getAttr('affectSystem_data.notes')
        dict_ = eval(str_)
        dict_['label'][self.name]['pose'] = {'start': self.start_data, 'end': self.end_data}
        dict_['label'][self.name]['ctrl pose'] = {'start': self.ctrl_start_data, 'end': self.ctrl_end_data}
        cmds.setAttr('affectSystem_data.notes', dict_, type='string')

    def set_ctrl(self, mode, name_list):
        u"""設定控制器起始與結束位置.
        :type mode: str
            'start' | 'end'
        """
        str_ = cmds.getAttr('affectSystem_data.notes')
        dict_ = eval(str_)
        for name in name_list:
            app_data = {'start': "dict_['label'][name]['ctrl pose']['start']", 
               'end': "dict_['label'][name]['ctrl pose']['end']"}
            for i, n in enumerate(dict_['label'][name]['ctrl']):
                for ii, attr in enumerate(['rx', 'ry', 'rz']):
                    cmds.setAttr(n + '.' + attr, eval(app_data[mode])[i][ii])

    def check_locator_rotate(self):
        u"""確認 locator 座標與軸向"""
        str_ = cmds.getAttr('affectSystem_data.notes')
        dict_ = eval(str_)
        transform = dict_['locator'].keys()
        if not cmds.getAttr(transform[0] + '.v'):
            cmds.showHidden(transform)
            for lo in transform:
                cmds.setAttr(lo + '.displayLocalAxis', 1)

        else:
            cmds.hide(transform)
            for lo in transform:
                cmds.setAttr(lo + '.displayLocalAxis', 0)

    def delete_attr(self, attr_list):
        u"""刪除屬性, EX, SR"""
        str_ = cmds.getAttr('affectSystem_data.notes')
        dict_ = eval(str_)
        for attr in attr_list:
            cmds.delete(dict_['label'][attr]['del'])
            cmds.deleteAttr('affectSystem_data', at=attr + '_switch')
            cmds.deleteAttr('affectSystem_data', at=attr)
            del dict_['label'][attr]
            lo_list = copy.copy(dict_['locator'])
            for lo in lo_list:
                if attr in dict_['locator'][lo]:
                    dict_['locator'][lo].remove(attr)
                if not dict_['locator'][lo]:
                    cmds.delete(lo + '_main_grp')
                    del dict_['locator'][lo]

            if not dict_['locator']:
                cmds.delete('affectSystem_data')
            else:
                cmds.setAttr('affectSystem_data.notes', dict_, type='string')


class THCheckInfluences(object):

    def __init__(self, mesh_list):
        u"""確認最大 skin influences"""
        self.mesh_list = mesh_list
        self.inf_dict = {}
        self.max_inf = None
        self.max_vtx = []
        self._get_max()
        self._max_inf()
        self._get_max_vtx()
        return

    def print_max_inf(self):
        u"""打印篩選最大 influences"""
        sys.stdout.write(('Max influences: {}, Vertex quantity: {}').format(self.max_inf, len(self.max_vtx)))

    def select_max_inf_vtx(self):
        u"""選擇最大 influences vtx"""
        cmds.select(self.max_vtx, r=True)

    def _get_max(self):
        u"""讀取每個頂點最大 influences"""
        for m in self.mesh_list:
            vertex_num = cmds.polyEvaluate(m, v=True)
            joint_list = thGetSkinJoint([m])
            skin_node = thFindSkinNode([m])[0]
            for vtx in range(vertex_num):
                mt = ('{}.vtx[{}]').format(m, vtx)
                weights = cmds.skinPercent(skin_node, mt, q=True, v=True)
                weights = [ w for w in weights if w > 0 ]
                self.inf_dict[mt] = len(weights)

    def _max_inf(self):
        u"""篩選最大 influences"""
        self._get_max()
        sort_weight = sorted(self.inf_dict.items(), reverse=True, key=lambda item: item[1])
        self.max_inf = sort_weight[0][1]

    def _get_max_vtx(self):
        u"""篩選最大 influences vtx"""
        for vtx in self.inf_dict:
            if self.inf_dict[vtx] == self.max_inf:
                self.max_vtx.append(vtx)


class THMoveSkinWeightOm2(object):

    def __init__(self, objs, old_joint_list, new_joint_list, opacity=1, ifRemoveInfluence=False):
        u"""移動 skin weight"""
        self.objs = objs
        self.old_joint_list = old_joint_list
        self.new_joint_list = new_joint_list
        self.opacity = opacity
        self.ifRemoveInfluence = ifRemoveInfluence
        self.idList = []
        self._add_joint()
        try:
            self._move()
        except RuntimeError:
            sys.stdout.write('對象與此方法不兼容!')

    def _add_joint(self):
        u"""判斷添加 joint"""
        self.meshs = self.objs
        if '.' in self.objs[0]:
            self.objs = cmds.polyListComponentConversion(self.objs, tv=True)
            self.objs = cmds.ls(self.objs, fl=True)
            self.meshs = [
             self.objs[0].split('.')[0]]
        add_joint_list = self.old_joint_list + self.new_joint_list
        for m in self.meshs:
            skin_joint_list = thFindSkinJoint([m])
            for j in add_joint_list:
                if j not in skin_joint_list:
                    cmds.skinCluster(m, e=True, wt=0, ai=j)

    def _move(self):
        u"""移動 weight"""
        app_joint_list = self.new_joint_list
        if len(self.new_joint_list) < len(self.old_joint_list):
            app_joint_list = [self.new_joint_list[0]] * len(self.old_joint_list)
        if '.' in self.objs[0]:
            self.idList = [ int(n.split('.')[1][4:-1]) for n in self.objs ]
        for m in self.meshs:
            cwa = ThCopyWeightApi()
            cwa.getWeightDataF(m)
            skin_node = thFindSkinNode([m])[0]
            for i, old_joint in enumerate(self.old_joint_list):
                if '.' not in self.objs[0]:
                    cmds.select(cl=True)
                    cmds.skinCluster(skin_node, e=True, siv=old_joint)
                    vtx_list = cmds.ls(sl=True, fl=True)
                    if '.' not in vtx_list[0]:
                        continue
                    self.idList = [ int(n.split('.')[1][4:-1]) for n in vtx_list ]
                cwa.editWeightDataF(idList=self.idList, idListData=[self.opacity] * len(self.idList), joint=app_joint_list[i], otherJointList=[old_joint])

            cwa.setWeightDataF()
            if self.ifRemoveInfluence:
                cmds.skinCluster(skin_node, e=True, ri=old_joint)


class THMoveSkinWeight(object):

    def __init__(self, objs, old_joint_list, new_joint_list, opacity=1):
        u"""移動 skin weight"""
        self.objs = objs
        self.old_joint_list = old_joint_list
        self.new_joint_list = new_joint_list
        self.opacity = opacity
        self.skin_nodes = []
        self.if_range = True
        self.app()

    def app(self):
        self._find_skin()
        for n in self.skin_nodes:
            cmds.skinCluster(n, e=True, fnw=True, normalizeWeights=1)
            cmds.setAttr(n + '.maintainMaxInfluences', 0)

        self._add_joint()
        self._move()

    def _find_skin(self):
        u"""判斷是否為 vtx 與 find skin node"""
        meshs = self.objs
        if '.' in self.objs[0]:
            self.objs = cmds.polyListComponentConversion(self.objs, tv=True)
            meshs = [ n.split('.')[0] for n in self.objs ]
            meshs = list(set(meshs))
            self.if_range = False
        self.skin_nodes = thFindSkinNode(meshs)

    def _add_joint(self):
        u"""判斷添加 joint"""
        joint_list = self.old_joint_list + self.new_joint_list
        for m in self.objs:
            skin_joints = thFindSkinJoint([m])
            for j in joint_list:
                if j not in skin_joints:
                    cmds.skinCluster(m, e=True, wt=0, ai=j)

    def _move(self):
        u"""移動 weight"""
        mesh = self.objs[0].split('.')[0] if self.if_range else self.objs[0]
        joint_list = thFindSkinJoint([mesh])
        for j in joint_list:
            cmds.setAttr(j + '.liw', 1)

        app_list = self.new_joint_list
        if len(self.new_joint_list) < len(self.old_joint_list):
            app_list = [
             self.new_joint_list[0]] * len(self.old_joint_list)
        progressBar = ThQProgressBar(3)
        progressBar.setStrat(0, 'Joint', len(self.old_joint_list))
        vtx_list = self.objs
        for i, j in enumerate(self.old_joint_list):
            progressBar.setFrame(0)
            if not self.skin_nodes:
                continue
            cmds.setAttr(app_list[i] + '.liw', 0)
            progressBar.setStrat(1, 'Skin node', len(self.skin_nodes))
            for s in self.skin_nodes:
                progressBar.setFrame(1)
                in_joints = cmds.skinCluster(s, q=True, wi=True)
                if j in in_joints:
                    if self.if_range:
                        cmds.select(cl=True)
                        cmds.skinCluster(s, e=True, siv=j)
                        vtx_list = cmds.ls(sl=True, fl=True)
                else:
                    continue
                progressBar.setStrat(2, 'Vertex', len(vtx_list))
                for vtx in vtx_list:
                    progressBar.setFrame(2)
                    old_weight = cmds.skinPercent(s, vtx, t=j, q=True)
                    if old_weight > 0:
                        new_weight = cmds.skinPercent(s, vtx, t=app_list[i], q=True)
                        set_weight = old_weight * self.opacity
                        cmds.skinPercent(s, vtx, tv=[j, old_weight - set_weight])

            cmds.setAttr(app_list[i] + '.liw', 1)

        progressBar.deleteLater()


class THHair(object):

    def __init__(self, cv, name, solver=None, follicle_mode='base', create_mode='ik'):
        """create hair rig
        :type follicle_mode: str
            'base' | 'tip' | 'both ends'
        """
        self.cv = cv
        self.name = name
        self.follicle_mode = follicle_mode
        self.create_mode = create_mode
        self.hair = None
        self.hair_shape = None
        self.nucleus = None
        self.follicle = None
        self.follicle_shape = None
        self.start_cv = None
        self.start_cv_grp = None
        self.dyn_cv = None
        self.dyn_cv_shape = None
        self.dyn_cv_grp = None
        return

    def app(self):
        if_app = True
        default_name = ['hairSystem1', 'nucleus1',
         'hairSystem1Follicles', 'hairSystem1OutputCurves']
        if if_app:
            self._create()
            self._rename()
            self._outliner()
            self._rig_ik()
            cmds.hide([self.start_cv_grp, self.dyn_cv_grp])
        else:
            cmds.select(error_name, r=True)
            sys.stdout.write(('{} Exists name: [ {} ] {}').format('-' * 50, (', ').join(error_name), '-' * 50))

    def _create(self):
        """create hair system"""
        self.start_cv = self.cv
        if self.create_mode == 'ik':
            self.start_cv = cmds.duplicate(self.cv, rr=True, rc=True)[0]
        if cmds.listRelatives(self.start_cv, p=True):
            cmds.parent(self.start_cv, w=True)
        cmds.select(self.start_cv, r=True)
        mel.eval('makeCurvesDynamic 2 {"1","0","1","1","0"}')

    def _rename(self):
        """rename"""
        self.hair = cmds.rename('hairSystem1', ('{}_hairSystem#').format(self.name))
        self.hair_shape = cmds.listRelatives(self.hair, s=True)[0]
        if cmds.objExists('nucleus1'):
            self.nucleus = cmds.rename('nucleus1', ('{}_nucleus#').format(self.name))
        self.follicle = cmds.listRelatives('hairSystem1Follicles', c=True)[0]
        self.follicle = cmds.rename(self.follicle, ('{}_follicle#').format(self.name))
        self.follicle_shape = cmds.listRelatives(self.follicle, s=True)[0]
        self.start_cv = cmds.rename(self.start_cv, ('{}_hairCv#').format(self.name))
        self.start_cv_grp = cmds.rename('hairSystem1Follicles', ('{}_hairSystem1Follicles#').format(self.name))
        self.dyn_cv = cmds.listRelatives('hairSystem1OutputCurves', c=True)[0]
        self.dyn_cv = cmds.rename(self.dyn_cv, ('{}_hairDynCv#').format(self.name))
        self.dyn_cv_shape = cmds.listRelatives(self.dyn_cv, s=True)[0]
        self.dyn_cv_grp = cmds.rename('hairSystem1OutputCurves', ('{}_hairSystem1OutputCurves#').format(self.name))

    def _outliner(self):
        u"""整理 outliner"""
        if not cmds.objExists('dyn'):
            cmds.group(em=True, n='dyn')
        if not cmds.objExists(self.name + '_dyn_grp'):
            cmds.group(em=True, n=self.name + '_dyn_grp')
            cmds.parent(self.name + '_dyn_grp', 'dyn')
        cmds.parent(self.hair, self.name + '_dyn_grp')
        if self.nucleus:
            if not cmds.objExists(self.name + '_dyn_nucleus_grp'):
                cmds.group(em=True, n=self.name + '_dyn_nucleus_grp')
                cmds.parent(self.name + '_dyn_nucleus_grp', self.name + '_dyn_grp')
            cmds.parent(self.nucleus, self.name + '_dyn_nucleus_grp')
        cmds.parent(self.start_cv_grp, self.name + '_dyn_grp')
        cmds.parent(self.dyn_cv_grp, self.name + '_dyn_grp')

    def _rig_ik(self):
        """rig ik spline"""
        follicle_point_lock = {'base': 1, 'tip': 2, 'both ends': 3}
        cmds.setAttr(self.follicle_shape + '.pointLock', follicle_point_lock[self.follicle_mode])
        blend = cmds.blendShape([self.dyn_cv, self.cv], n=self.name + '_hairSystem_blend_node#', frontOfChain=True)[0]
        cmds.setAttr(blend + '.w[0]', 1)
        skin_objs = thFindSkinJoint([self.cv])
        skin_objs.append(self.start_cv)
        cmds.skinCluster(skin_objs, n=self.name + '_hairSystem_skin_node#', mi=5, dr=4.0, tsb=True)
        skin = thFindSkinNode([self.cv])[0]
        cmds.expression(n=self.name + '_hairSystem_blend_EX#', s=('{}.envelope = 1 - {}.envelope;').format(blend, skin))
        cmds.setAttr(self.hair_shape + '.simulationMethod', 0)
        cmds.setAttr(skin + '.envelope', 1)
        cmds.setDrivenKeyframe(skin + '.envelope', cd=self.hair_shape + '.simulationMethod', itt='linear', ott='linear')
        cmds.setAttr(self.hair_shape + '.simulationMethod', 3)
        cmds.setAttr(skin + '.envelope', 0)
        cmds.setDrivenKeyframe(skin + '.envelope', cd=self.hair_shape + '.simulationMethod', itt='linear', ott='linear')


class THObjOffsetObjs(object):

    def __init__(self, list_, obj):
        u"""物件座標在物件列表上偏移
        :type list_: list
        :type obj: str
        """
        self.list_ = list_
        self.obj = obj
        self.con_node = None
        self.sys = None
        return

    def app(self):
        self._constrain()
        self._ctrl()
        self._key()

    def _constrain(self):
        u"""約束"""
        con = self.list_ + [self.obj]
        self.con_node = cmds.parentConstraint(con, weight=1)[0]

    def _ctrl(self):
        u"""創建控制器"""
        self.sys = cmds.group(em=True, n='objOffsetSystem')
        cmds.addAttr(self.sys, ln='offset', at='double', min=0, max=10, dv=0, k=True)

    def _key(self):
        u"""key 批次啟動"""
        key_list = []
        for i, n in enumerate(self.list_):
            key_list.append(('{}.{}W{}').format(self.con_node, n, i))

        set_ = 0
        add = 10.0 / (len(key_list) - 1)
        for i, n in enumerate(key_list):
            cmds.setAttr(self.sys + '.offset', set_)
            for nn in key_list:
                cmds.setAttr(nn, 0)

            cmds.setAttr(n, 1)
            cmds.setDrivenKeyframe(key_list, cd=self.sys + '.offset', itt='linear', ott='linear')
            if i < len(key_list) - 1:
                set_ += add
                if set_ > 10:
                    set_ = 10

    def delete(self):
        cmds.delete(self.con_node)
        cmds.delete(self.sys)


class THCreateFollowObjsJoint(object):

    def __init__(self, list_, quantity):
        u"""創建跟隨物件"""
        self.list_ = list_
        self.quantity = quantity
        self.joint = None
        self.new_joints = []
        return

    def app(self):
        cmds.select(cl=True)
        self.joint = cmds.joint()
        tooo_cls = THObjOffsetObjs(self.list_, self.joint)
        tooo_cls.app()
        set_ = 0
        add = 10.0 / (self.quantity - 1)
        for i in range(self.quantity):
            cmds.setAttr(tooo_cls.sys + '.offset', set_)
            cmds.select(cl=True)
            joint = cmds.joint()
            AdsorptionObj([joint], self.joint, 'tr')
            self.new_joints.append(joint)
            if i < self.quantity - 1:
                set_ += add
                if set_ > 10:
                    set_ = 10

        cmds.makeIdentity(self.new_joints, apply=True, t=True, r=True, s=True, n=False, pn=True)
        tooo_cls.delete()
        cmds.delete(self.joint)


class TWheelRig(object):

    def __init__(self, meshList, name='wheel', axial='x', axisObjList=None, ifConAxisObjList=True):
        u"""輪子 RIG"""
        self.meshList = meshList
        self.name = name
        self.axial = axial
        self.axisObjList = axisObjList
        self.ifConAxisObjList = ifConAxisObjList
        self.mainGrp = None
        self.axisList = []
        self.ctrlList = []
        if not cmds.objExists('def_wheel_main_grp'):
            cmds.group(em=True, n='def_wheel_main_grp')
        if not cmds.objExists('rig_wheel_main_grp'):
            cmds.group(em=True, n='rig_wheel_main_grp')
        self.mainGrp = cmds.group(em=True, n=('{}_wheel_main_grp').format(self.name))
        cmds.parent([self.mainGrp, 'def_wheel_main_grp'])
        cmds.hide(self.mainGrp)
        for i, mesh in enumerate(self.meshList):
            self.newName = ('{}{}').format(self.name, i + 1)
            self._disF(mesh)
            ctrlRus = self._ctrlF(self.axisObjList[i] if self.axisObjList else None)
            self._exF()
            if self.ifConAxisObjList:
                cmds.parentConstraint([self.axis, self.axisObjList[i]], mo=True, weight=1)

        cmds.select(self.ctrlList, r=True)
        return

    def _disF(self, mesh):
        u"""輪子大小測量"""
        self.tfvmd = TFindVtxMaxDis([mesh])
        self.loc1 = cmds.spaceLocator(n=('{}_wheel_loc1').format(self.newName))[0]
        cmds.move(self.tfvmd.hexagon[2][0], self.tfvmd.hexagon[2][1], self.tfvmd.hexagon[2][2], self.loc1)
        self.loc2 = cmds.spaceLocator(n=('{}_wheel_loc2').format(self.newName))[0]
        cmds.move(self.tfvmd.hexagon[3][0], self.tfvmd.hexagon[3][1], self.tfvmd.hexagon[3][2], self.loc2)
        self.locGrp = cmds.group(em=True, n=('{}_wheel_loc_grp').format(self.newName))
        cmds.parent([self.loc1, self.loc2, self.locGrp])
        cmds.parent([self.locGrp, self.mainGrp])
        self.dis = cmds.createNode('distanceBetween', n=('{}_wheel_loc_dis').format(self.newName))
        cmds.connectAttr(self.loc1 + '.t', self.dis + '.point1')
        cmds.connectAttr(self.loc2 + '.t', self.dis + '.point2')

    def _ctrlF(self, axisObj):
        u"""創建控制器"""
        self.axis = cmds.spaceLocator(n=('{}_wheel_axis').format(self.newName))[0]
        self.axisList.append(self.axis)
        if axisObj:
            AdsorptionObj([self.axis], axisObj, 'tr')
        else:
            cmds.move(self.tfvmd.center[0], self.tfvmd.center[1], self.tfvmd.center[2], self.axis)
        thcto = THCtrlToObject([
         self.axis], name=('{}_wheel').format(self.newName), ctrl_style='hexagon', ctrl_axial=self.axial, ctrl_method='parent', ctrl_color=18, grp_layout=2, if_create_main_grp=False, ctrl_size=2)
        thcto.create()
        self.ctrlList.append(thcto.new_ctrl_list[0])
        self.ctrl = thcto.new_ctrl_list[0]
        ctrlGrpEnd = thcto.new_ctrl_grp_list[(-1)]
        cmds.addAttr(self.ctrl, ln='auto', at='bool', k=True, dv=1)
        cmds.parentConstraint([self.ctrl, self.loc1], mo=True, skipRotate=['x', 'y', 'z'], weight=1)
        cmds.parentConstraint([self.ctrl, self.loc2], mo=True, skipRotate=['x', 'y', 'z'], weight=1)
        cmds.parent([ctrlGrpEnd, 'rig_wheel_main_grp'])

    def _exF(self):
        """expression"""
        app = {'x': 'z', 'z': 'x'}
        moveLoc = cmds.spaceLocator(n=('{}_wheel_move_loc').format(self.newName))[0]
        moveLocGrp = cmds.group(moveLoc, n=('{}_wheel_move_loc_grp').format(self.newName))
        cmds.pointConstraint([self.ctrl, moveLoc], mo=True, weight=1)
        cmds.orientConstraint([self.ctrl, moveLocGrp], mo=True, weight=1)
        cmds.addAttr(self.ctrl, ln='anim', at='double', dv=0, k=True)
        ex = '\nif ({ctrl}.auto == 1){{\n    {axis}.rx = (({moveLoc}.t{axial} + {ctrlAttr}) * 360) / ({dis}.distance * 3.14159);\n}} else {{\n    {axis}.rx = ({ctrlAttr} * 360) / ({dis}.distance * 3.14159);\n}}\n'
        ctrlAttr = ('{}.anim').format(self.ctrl)
        ex = ex.format(ctrl=self.ctrl, axis=self.axis, moveLoc=moveLoc, axial=app[self.axial], ctrlAttr=ctrlAttr, dis=self.dis)
        cmds.expression(n=('{}_wheel_EX').format(self.newName), s=ex)
        cmds.parent([moveLocGrp, self.mainGrp])


class TFindVtxMaxDis(object):

    def __init__(self, list_):
        u"""判斷頂點最大最小距離"""
        self.list_ = list_
        self.xyz_list = []
        self.vtx_list = []
        self.hexagon = []
        self.anise = []
        self.center = []
        if '.' in list_[0]:
            self.vtx_list = list_
        else:
            for n in list_:
                size = cmds.polyEvaluate(n, v=True)
                for i in range(size):
                    self.vtx_list.append(('{}.vtx[{}]').format(n, i))

            for n in self.vtx_list:
                self.xyz_list.append(cmds.xform(n, q=True, ws=True, t=True))

        x_dir = sorted([ i[0] for i in self.xyz_list ])
        y_dir = sorted([ i[1] for i in self.xyz_list ])
        z_dir = sorted([ i[2] for i in self.xyz_list ])
        x_list = [
         x_dir[0], (x_dir[0] - x_dir[(-1)]) / 2 + x_dir[(-1)], x_dir[(-1)]]
        y_list = [
         y_dir[0], (y_dir[0] - y_dir[(-1)]) / 2 + y_dir[(-1)], y_dir[(-1)]]
        z_list = [
         z_dir[0], (z_dir[0] - z_dir[(-1)]) / 2 + z_dir[(-1)], z_dir[(-1)]]
        self.hexagon = [
         [
          x_list[0], y_list[1], z_list[1]],
         [
          x_list[2], y_list[1], z_list[1]],
         [
          x_list[1], y_list[0], z_list[1]],
         [
          x_list[1], y_list[2], z_list[1]],
         [
          x_list[1], y_list[1], z_list[0]],
         [
          x_list[1], y_list[1], z_list[2]]]
        self.anise = [
         [
          x_list[0], y_list[0], z_list[2]],
         [
          x_list[0], y_list[0], z_list[0]],
         [
          x_list[0], y_list[2], z_list[2]],
         [
          x_list[0], y_list[2], z_list[0]],
         [
          x_list[2], y_list[0], z_list[2]],
         [
          x_list[2], y_list[0], z_list[0]],
         [
          x_list[2], y_list[2], z_list[2]],
         [
          x_list[2], y_list[2], z_list[0]]]
        self.center = [
         x_list[1], y_list[1], z_list[1]]

    def create(self, mode='hexagon'):
        """
        :type mode: str
            'anise' | 'hexagon'
        """
        app = {'hexagon': self.hexagon, 'anise': self.anise}
        new = []
        for i in app[mode]:
            cmds.select(cl=True)
            new.append(cmds.joint(p=i))

        cmds.select(new, r=True)


class TEditCvShape(object):

    def __init__(self, ctrl):
        u"""控制器移動, 旋轉, 縮放"""
        self.ctrl = ctrl
        self.cv_list = []
        if '.' in ctrl[0]:
            set_ = set([ n.split('.')[0] for n in ctrl ])
            self.ctrl = list(set_)
        for n in self.ctrl:
            shape = cmds.listRelatives(n, f=True, s=True)[0]
            cv_size = int(cmds.getAttr(shape + '.maxValue'))
            cv_degree = int(cmds.getAttr(shape + '.degree'))
            open = cmds.getAttr(shape + '.form')
            if open:
                cv_size -= 1
            elif cv_degree == 2:
                cv_size += 1
            elif cv_degree == 3:
                cv_size += 2
            self.cv_list.append(('{}.cv[{}:{}]').format(n, 0, cv_size))

    def move(self, axial, offset):
        u"""旋轉控制器造型.
        :type axial: str
            'x' | 'y' | 'z'
        :rotate offset: float
        """
        x_data, y_data, z_data = 0, 0, 0
        if axial == 'x':
            x_data, y_data, z_data = offset, 0, 0
        elif axial == 'y':
            x_data, y_data, z_data = 0, offset, 0
        elif axial == 'z':
            x_data, y_data, z_data = 0, 0, offset
        cmds.move(x_data, y_data, z_data, self.cv_list, r=True, os=True, wd=True)

    def rotate(self, rotate):
        u"""旋轉控制器造型.
        :rotate size: list
            [int, int, int]
        """
        cmds.rotate(rotate[0], rotate[1], rotate[2], self.cv_list, r=True)

    def scale(self, size):
        u"""縮放控制器造型大小.
        :type size: float
        """
        cmds.scale(size, size, size, self.cv_list, r=True)


class TRandSelect(object):

    def __init__(self, objs):
        u"""隨機選擇.
        :typ objs: list
        """
        self.objs = objs
        self.new_list = copy.copy(objs)
        self.filter_list = []

    def do(self, max, filter_=True):
        if len(self.new_list) > max:
            filter_list = []
            for i in range(max):
                index = random.randint(0, len(self.new_list) - 1)
                filter_list.append(self.new_list[index])
                if filter_:
                    self.filter_list.append(self.new_list[index])
                    self.new_list.remove(self.new_list[index])

            cmds.select(filter_list, r=True)
            return filter_list


class THCopySkinAndWeight(object):

    def __init__(self, ref_list, obj_list, mode='point'):
        u"""複製 skin 與 weight"""
        self.ref_list = ref_list
        self.obj_list = obj_list
        self.mode = mode
        self.ref_size = len(self.ref_list)
        self.obj_size = len(self.obj_list)

    def copy_skin(self):
        u"""複製 skin"""
        if self.ref_size > 1 and self.obj_size == 1 or self.ref_size == 1 and self.obj_size > 1:
            joints = thFindSkinJoint(self.ref_list)
            for i, obj in enumerate(self.obj_list):
                skin_node = thFindSkinNode([obj])
                if joints and not skin_node:
                    cmds.skinCluster(joints, obj, mi=5, dr=4.0, tsb=True)

        elif self.ref_size == self.obj_size:
            for i, ref in enumerate(self.ref_list):
                joints = thFindSkinJoint([ref])
                skin_node = thFindSkinNode([self.obj_list[i]])
                if joints and not skin_node:
                    cmds.skinCluster(joints, self.obj_list[i], mi=5, dr=4.0, tsb=True)

    def copy_weight(self):
        u"""複製 weight"""
        if self.mode == 'uv':
            ref_uv = cmds.polyUVSet(self.ref_list, q=True, cuv=True)
            obj_ui = cmds.polyUVSet(self.obj_list, q=True, cuv=True)
            if self.ref_size > 1 and self.obj_size == 1:
                sys.stdout.write(' 無法使用此模式 !')
                return
            if self.ref_size == self.obj_size:
                for i, obj in enumerate(self.obj_list):
                    cmds.copySkinWeights(self.ref_list[i], obj, uv=[ref_uv[i], obj_ui[i]], nm=True, sa='closestPoint', ia='closestJoint')

            elif self.ref_size == 1 and self.obj_size > 1:
                for i, obj in enumerate(self.obj_list):
                    cmds.copySkinWeights(self.ref_list[0], obj, uv=[ref_uv[0], obj_ui[i]], nm=True, sa='closestPoint', ia='closestJoint')

        elif self.mode == 'point':
            if self.ref_size > 1 and self.obj_size == 1:
                cmds.copySkinWeights(self.ref_list, self.obj_list[0], nm=True, sa='closestPoint', ia='closestJoint')
            elif self.ref_size == self.obj_size:
                for i, obj in enumerate(self.obj_list):
                    cmds.copySkinWeights(self.ref_list[i], obj, nm=True, sa='closestPoint', ia='closestJoint')

            elif self.ref_size == 1 and self.obj_size > 1:
                for obj in self.obj_list:
                    cmds.copySkinWeights(self.ref_list[0], obj, nm=True, sa='closestPoint', ia='closestJoint')

        elif self.mode == 'name':
            if self.ref_size > 1 and self.obj_size == 1:
                cmds.copySkinWeights(self.ref_list, self.obj_list[0], nm=True, sa='closestPoint', ia='name')
            elif self.ref_size == self.obj_size:
                for i, obj in enumerate(self.obj_list):
                    cmds.copySkinWeights(self.ref_list[i], obj, nm=True, sa='closestPoint', ia='name')

            elif self.ref_size == 1 and self.obj_size > 1:
                for obj in self.obj_list:
                    cmds.copySkinWeights(self.ref_list[0], obj, nm=True, sa='closestPoint', ia='name')

    def set_max_influences(self):
        skin_node = thFindSkinNode([self.ref_list[0]])[0]
        inf = cmds.getAttr(skin_node + '.maxInfluences')
        for obj in self.obj_list:
            obj_skin_node = thFindSkinNode([obj])[0]
            cmds.setAttr(obj_skin_node + '.maxInfluences', inf)


class THSelectPointIndex(object):

    def __init__(self, list_):
        u"""保存與選擇 index"""
        self.list_ = list_
        self.index = []

    def save(self):
        for i in self.list_:
            self.index.append(i.split('.')[1])

    def do_select(self, objs):
        objs_list = []
        for obj in objs:
            objs_list.extend([ obj + '.' + i for i in self.index ])

        cmds.select(objs_list, r=True)


class TwoObjCtrl(object):

    def __init__(self, obj1, obj2, obj_list, main_ctrl, mode, attr_ctrl, exclude_end=False, add_follow_name='follow', add_offset_name='offset'):
        u"""兩個物件約束批量物件並創建批次啟動控制器.
        :type obj2: str
        :type obj1: str
        :type obj_list: list
        :type main_ctrl: str
        :type mode: str ('connect', 'soft')
        :type exclude_end: bool 是否排除列表最後一個物件
        :rtype: list
        """
        self.obj1 = obj1
        self.obj2 = obj2
        self.obj_list = obj_list
        self.main_ctrl = main_ctrl
        self.mode = mode
        self.exclude_end = exclude_end
        self.add_follow_name = add_follow_name
        self.add_offset_name = add_offset_name
        self.attr_ctrl = attr_ctrl
        self.constrain_list = []
        self.create()

    def create(self):
        con_list = self.obj_list[:-1] if self.exclude_end else self.obj_list
        for i, n in enumerate(con_list):
            self.constrain_list.append(cmds.parentConstraint([self.obj2, self.obj1, n], mo=True, w=1)[0])

        self.do_attr_ctrl = self.attr_ctrl if self.attr_ctrl else self.main_ctrl
        if not cmds.listAttr(self.do_attr_ctrl, m=True, st=self.add_follow_name):
            cmds.addAttr(self.do_attr_ctrl, ln=self.add_follow_name, at='double', min=0, max=10, dv=0, k=True)
        if not cmds.listAttr(self.do_attr_ctrl, m=True, st=self.add_offset_name):
            cmds.addAttr(self.do_attr_ctrl, ln=self.add_offset_name, at='double', min=0, max=10, dv=0, k=True)
        app_dict = {'connect': 'self._mode_connect()', 
           'soft': 'self._mode_soft()'}
        eval(app_dict[self.mode])
        cmds.select(self.do_attr_ctrl)

    def _mode_connect(self):
        u"""connect 控制模式"""
        for n in self.constrain_list:
            thReverseConnect([n], [n, self.obj1 + 'W1'], self.obj2 + 'W0')

        thBatchEnable(self.do_attr_ctrl + '.' + self.add_follow_name, self.do_attr_ctrl + '.' + self.add_offset_name, self.constrain_list, self.obj1 + 'W1', len(self.obj_list))

    def _mode_soft(self):
        u"""soft 控制模式"""
        dsl_cls = ThDistanceSoftLocator(objs=self.obj_list, exclude_end=self.exclude_end)
        for i, con in enumerate(self.constrain_list):
            thReverseConnect([con], [con, self.obj1 + 'W1'], self.obj2 + 'W0')
            cmds.connectAttr(dsl_cls.locator_list[i] + '.ty', con + '.' + self.obj1 + 'W1')

        cmds.connectAttr(self.do_attr_ctrl + '.' + self.add_follow_name, dsl_cls.soft_node[0][1] + '.follow')
        cmds.connectAttr(self.do_attr_ctrl + '.' + self.add_offset_name, dsl_cls.soft_node[0][1] + '.offset')


class THRemoveDuplicateNames(object):

    def __init__(self, objs=None, findShape=True):
        u"""重命名重複名稱物件"""
        self.objs = objs if objs else cmds.ls(typ='transform')
        self.findShape = findShape
        if self.findShape:
            objsShape = cmds.listRelatives(self.objs, f=True, s=True)
            objsShape = cmds.ls(objsShape)
            if objsShape:
                self.objs += objsShape
        self.reObjs = []
        for obj in self.objs:
            if '|' in obj:
                self.reObjs.append(obj)

    def app(self):
        u"""重命名選擇物件"""
        if self.reObjs:
            cmds.sets(em=True, n='th_duplicate_names_main_sets')
            newSets = []
            for i, reObj in enumerate(self.reObjs):
                newSets.append(cmds.sets(reObj, n='th_duplicate_names_sets#'))
                cmds.sets(newSets[i], add='th_duplicate_names_main_sets')

            for s in newSets:
                reObj = cmds.sets(s, q=True)[0]
                if '|' in reObj:
                    reObjClear = reObj.split('|')[(-1)]
                    reObjClear = thRemoveStrNum(reObjClear, False)[0]
                    cmds.rename(reObj, reObjClear + '#')

            cmds.delete(newSets)

    def printMenuF(self, select=True):
        u"""打印與選擇重複名稱物件"""
        if select:
            cmds.select(self.reObjs, r=True)
        sys.stdout.write((' 重複名稱的物件共有: {}').format(len(self.reObjs)))


class THVtxLocator(object):
    """依據選擇物件創建 follow ctrl"""

    def __init__(self, objs=None, name='obj', if_vl=False, vl_aim='y', vl_size=1, control_vl_mode=None, control_obj=None, rotate_obj=None, ctrl_style=None, ctrl_axial='y', ctrl_size=1.0, ctrl_mode='not', ctrl_color=13, ctrl_grp_layrt=3):
        self.objs = objs
        self.name = name
        self.if_vl = if_vl
        self.vl_aim = vl_aim
        self.vl_size = vl_size
        self.control_vl_mode = control_vl_mode
        self.control_obj = control_obj
        self.rotate_obj = rotate_obj
        self.ctrl_style = ctrl_style
        self.ctrl_axial = ctrl_axial
        self.ctrl_size = ctrl_size
        self.ctrl_mode = ctrl_mode
        self.ctrl_color = ctrl_color
        self.ctrl_grp_layrt = ctrl_grp_layrt
        self.vl = None
        self.vl_vtx_list = []
        self.vl_vtx_sets_list = []
        self.follicle_list = []
        self.new_ctrl_list = []
        return

    def create_vl_and_follicle(self):
        if not self.objs:
            return
        else:
            smooth_node = None
            if self.if_vl:
                self._vl_for_sel()
                smooth_node = cmds.polySmooth(self.vl)[0]
                smooth_vtx_size = cmds.polyEvaluate(self.vl, v=True)
                range_ = range(smooth_vtx_size - len(self.objs), smooth_vtx_size)
                self.vl_vtx_list = [ ('{}.vtx[{}]').format(self.vl, i) for i in range_ ]
            else:
                self.vl_vtx_list = self.objs
            if '.' in self.vl_vtx_list[0]:
                self.follicle_list = ThVertexFollicle(self.vl_vtx_list, self.name, self.rotate_obj).apply()
            else:
                self.follicle_list = self.vl_vtx_list
            if self.ctrl_mode == 'ctrl' or self.ctrl_mode == 'ctrl follow':
                self._ctrl_mode()
                cmds.select(self.new_ctrl_list, r=True)
            if smooth_node:
                cmds.delete(smooth_node)
                self._control_vtx()
                cmds.select(self.follicle_list, r=True)
            return

    def create_vl(self):
        u"""創建定位用 polygons 三角形定位器"""
        poly = cmds.polyCreateFacet(ch=False, tx=1, s=1, n=self.name + '_vl#', p=[
         [
          0, 0.037021, 0.111063], [0, 0.037021, -0.111063], [0, -0.074042, 0]])[0]
        cmds.polyProjection(poly, ch=False, type='Planar', ibd=True, kir=True, md='y')
        if self.vl_aim == 'x':
            cmds.rotate(90, -90, 0, poly + '.vtx[0:2]', r=True)
        elif self.vl_aim == 'z':
            cmds.rotate(90, 0, 0, poly + '.vtx[0:2]', r=True)
        if self.vl_size != 1:
            cmds.scale(self.vl_size, self.vl_size, self.vl_size, poly + '.vtx[0:2]', r=True)
        return poly

    def test_create_vl(self):
        selectList = cmds.ls(sl=True)
        vl = self.create_vl()
        if selectList:
            try:
                AdsorptionObj([vl], selectList[0], 'tr')
            except:
                pass

    def _vl_for_sel(self):
        u"""依據物件創建 vl"""
        if not cmds.objExists('def'):
            cmds.group(em=True, n='def')
        if not cmds.objExists('vl_grp'):
            cmds.group(em=True, n='vl_grp')
            cmds.parent('vl_grp', 'def')
        adsorption_type = None
        if len(self.objs[0].split('.')) == 1:
            adsorption_type = 'tr'
        else:
            adsorption_type = 'vertex'
        vl_list = []
        for n in self.objs:
            vl = self.create_vl()
            vl_list.append(vl)
            AdsorptionObj([vl], n, adsorption_type)

        if self.control_obj:
            for vl in vl_list:
                node = cmds.normalConstraint([
                 self.control_obj, vl], weight=1, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])
                cmds.delete(node)

        if len(self.objs) > 1:
            self.vl = cmds.polyUnite(vl_list, ch=False, mergeUVSets=1)
            self.vl = cmds.rename(self.vl, self.name + '_vl#')
            cmds.polyMultiLayoutUV(self.vl, lm=1, sc=1, rbf=1, fr=1, ps=1, l=2, psc=0, su=1, sv=1, ou=0, ov=0)
        else:
            self.vl = vl
        cmds.parent(self.vl, 'vl_grp')
        return

    def _return_veryex_sets_list(self, vl):
        u"""回傳頂點集列表.
        :type vl: str
        """
        vertex_size = cmds.polyEvaluate(vl, v=True)
        list_ = []
        for i in range(vertex_size):
            list_.append(('{}.vtx[{}]').format(vl, i))
            if len(list_) == 3:
                self.vl_vtx_sets_list.append(list_)
                list_ = []

    def _return_veryex_list(self, vl):
        u"""回傳頂點列表.
        :type vl: str
        """
        vertex_size = cmds.polyEvaluate(vl, v=True)
        list_ = []
        for i in range(2, vertex_size, 3):
            list_.append(('{}.vtx[{}]').format(vl, i))

        return list_

    def _control_vtx(self):
        u"""控制 vtx locator"""
        if self.control_obj and self.control_vl_mode == 'skin':
            thObjForObjSkin(self.control_obj, self.vl)
            cmds.copySkinWeights(self.control_obj, self.vl, nm=True, sa='closestPoint', ia='closestJoint')
            self.unite_wight([self.vl])
        elif self.control_obj and self.control_vl_mode == 'wrap':
            cmds.select([self.vl, self.control_obj], r=True)
            mel.eval('doWrapArgList "7" {"1","0","1","2","0","1","0"}')

    def unite_wight(self, vl_list):
        u"""統一權重.
        :type vl: str
        """
        for vl in vl_list:
            self._return_veryex_sets_list(vl)
            for n in self.vl_vtx_sets_list:
                cmds.select(n[2], r=True)
                mel.eval('artAttrSkinWeightCopy')
                cmds.GrowPolygonSelectionRegion()
                mel.eval('artAttrSkinWeightPaste')

        cmds.select(cl=True)

    def _ctrl_mode(self):
        u"""創建控制器 模式"""
        locator_list = self.follicle_list if '.' in self.objs[0] else self.objs
        thcto_cls = THCtrlToObject(obj_list=locator_list, name=self.name + '_follow', ctrl_style=self.ctrl_style, ctrl_axial=self.ctrl_axial, ctrl_method='not', lock_hide_attr=[
         0, 0, 0, 1], ctrl_size=self.ctrl_size, ctrl_color=self.ctrl_color, grp_layout=self.ctrl_grp_layrt, if_create_main_grp=True)
        thcto_cls.create()
        self.new_ctrl_list = thcto_cls.new_ctrl_list
        con_obj_list = self.new_ctrl_list if self.ctrl_grp_layrt == 0 else [ n[0] for n in thcto_cls.grp_layout_list ]
        for i, follicle in enumerate(self.follicle_list):
            cmds.parentConstraint([follicle, con_obj_list[i]], mo=True, weight=1)

        if self.ctrl_mode == 'ctrl follow':
            for i, follicle in enumerate(self.follicle_list):
                md = cmds.createNode('multiplyDivide', n=self.name + '_follow_MD#')
                cmds.connectAttr(self.new_ctrl_list[i] + '.t', md + '.input1')
                cmds.setAttr(md + '.input2', -1, -1, -1)
                cmds.connectAttr(md + '.output', thcto_cls.grp_layout_list[i][2] + '.t')

    def reset_uv_pos(self, follicle_list, vl):
        vertex_list = self._return_veryex_list(vl)
        uv_pos_list = thGetPolyUvPos(vertex_list)[1]
        if len(vertex_list) != len(follicle_list):
            cmds.warning('程序未執行: 頂點與 follicle 數量不一致! ')
            return
        for i, follicle in enumerate(follicle_list):
            follicle_shape = cmds.listRelatives(follicle, f=True, s=True)[0]
            cmds.setAttr(follicle_shape + '.parameterU', uv_pos_list[i][0])
            cmds.setAttr(follicle_shape + '.parameterV', uv_pos_list[i][1])


class THAimCtrl(object):

    def __init__(self, locator, father=None, name='eye', ctrl_aim='z', ctrl_offset=5, ctrl_size=1):
        u"""創建 eye 控制器.
        :type locator: str
        :type father: str
        """
        self.locator = locator
        self.father = father
        self.name = name
        self.ctrl_aim = ctrl_aim
        self.ctrl_offset = ctrl_offset
        self.ctrl_size = ctrl_size
        self.def_main_grp = None
        self.ctrl_main_grp = None
        self.aim_main_grp = None
        self.aim_main_con_grp = None
        self.ik_joint = []
        self.ik = None
        self.ctrl = None
        self.fk_ctrl = None
        return

    def create(self):
        self._create_grp()
        self._create_joint()
        self.ik = cmds.ikHandle(n=self.name + '_aimSys_ik#', sj=self.ik_joint[0], ee=self.ik_joint[1], sol='ikSCsolver')
        cmds.hide(self.ik[0])
        self._create_ctrl()
        self._create_text_cv()
        self._if_constrain()
        cmds.select(self.ctrl)

    def _create_grp(self):
        u"""創建 grp"""
        if not cmds.objExists('def'):
            cmds.group(em=True, n='def')
        if not cmds.objExists('def_aimSys_grp'):
            cmds.group(em=True, n='def_aimSys_grp')
            cmds.parent('def_aimSys_grp', 'def')
        self.def_main_grp = cmds.group(em=True, n=self.name + '_def_aimSys_grp#')
        cmds.parent(self.def_main_grp, 'def_aimSys_grp')
        if not cmds.objExists('aimSys_ctrl_grp'):
            cmds.group(em=True, n='aimSys_ctrl_grp')
        self.ctrl_main_grp = cmds.group(em=True, n=self.name + '_aimSys_ctrl_grp#')
        cmds.parent(self.ctrl_main_grp, 'aimSys_ctrl_grp')

    def _create_joint(self):
        u"""創建 joint"""
        cmds.select(cl=True)
        self.ik_joint.append(cmds.joint(n=self.name + '_aimSys_ik_joint1_#'))
        self.ik_joint.append(cmds.joint(n=self.name + '_aimSys_ik_joint2_#'))
        AdsorptionObj([self.ik_joint[0]], self.locator)
        data = cmds.getAttr(self.ik_joint[1] + '.t' + self.ctrl_aim)
        cmds.setAttr(self.ik_joint[1] + '.t' + self.ctrl_aim, data + self.ctrl_offset)

    def _create_ctrl(self):
        u"""創建控制器"""
        thcto_cls = THCtrlToObject(obj_list=[
         self.ik[0]], name=self.name + '_aim', ctrl_style='ball', ctrl_method='parent', ctrl_size=self.ctrl_size / 2, ctrl_color=22, grp_layout=3, if_create_main_grp=False, lock_hide_attr=[
         0, 0, 1, 1])
        thcto_cls.create()
        self.ctrl = thcto_cls.new_ctrl_list[0]
        self.aim_main_grp = thcto_cls.new_ctrl_grp_list
        self.aim_main_con_grp = thcto_cls.grp_layout_list[0][1]
        cmds.parent(self.aim_main_grp, self.ctrl_main_grp)
        thcto_cls = THCtrlToObject(obj_list=[
         self.ik_joint[0]], name=self.name + '_fk', ctrl_style='circle', ctrl_method='not', ctrl_size=self.ctrl_size, ctrl_color=18, grp_layout=2, if_create_main_grp=False, ctrl_axial=self.ctrl_aim, lock_hide_attr=[
         0, 1, 0, 1])
        thcto_cls.create()
        self.fk_ctrl = thcto_cls.new_ctrl_list[0]
        TEditCvShape([self.fk_ctrl]).move(self.ctrl_aim, self.ctrl_offset / 3)
        cmds.parent(self.ik_joint[0], self.fk_ctrl)
        cmds.parent(thcto_cls.new_ctrl_grp_list[0], self.ctrl_main_grp)
        if self.father:
            cmds.parentConstraint([self.father, thcto_cls.grp_layout_list[0][1]], mo=True, w=1)

    def _create_text_cv(self):
        u"""創建參考線"""
        test_cv = thObjectCurve(self.ik_joint, False)
        test_cv = cmds.rename(test_cv, self.name + '_aimSys_test_cv#')
        cmds.parent(test_cv, self.def_main_grp)
        cmds.select(cl=True)
        joint1 = cmds.joint(n=self.name + '_aimSys_test_joint1_#')
        cmds.select(cl=True)
        joint2 = cmds.joint(n=self.name + '_aimSys_test_joint2_#')
        cmds.hide([joint1, joint2])
        AdsorptionObj([joint1], self.ik_joint[0])
        AdsorptionObj([joint2], self.ik_joint[1])
        cmds.parent(joint1, self.fk_ctrl)
        cmds.parent(joint2, self.ctrl)
        cmds.skinCluster([joint1, joint2, test_cv], mi=1, dr=2, tsb=True)
        cmds.setAttr(test_cv + '.template', 1)

    def _if_constrain(self):
        u"""是否受父物件約束"""
        if self.father:
            attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            con_attr = []
            for attr in attrs:
                con_attr.append(('{}.{}').format(self.aim_main_con_grp, attr))

            cmds.parentConstraint([
             self.father, self.aim_main_con_grp], mo=True, w=1)
            cmds.setDrivenKeyframe(con_attr, cd=self.aim_main_con_grp + '.v', itt='linear', ott='linear')
            cmds.addAttr(self.ctrl, k=True, ln='add_attr', at='enum', en='------:------:')
            cmds.setAttr(self.ctrl + '.add_attr', e=True, channelBox=True)
            cmds.addAttr(self.ctrl, min=0, max=1, dv=1, ln='follow', at='double', k=True)
            cmds.connectAttr(self.ctrl + '.follow', self.aim_main_con_grp + '.blendParent1')

    def combine_ctrl(self, objs, name, father):
        u"""合併控制器
        :type objs: list
        :type name: str
        :type father: str
        """
        objs_father = cmds.listRelatives(objs, p=True)
        ctrl = thMyController(name=name + '_ctrl', style='x', axial=self.ctrl_aim, scale=self.ctrl_size, color=13, lock_hide_attr=[
         0, 1, 1, 1])
        ctrl_grp1 = cmds.group(ctrl, n=ctrl + '_grp#')
        ctrl_grp2 = cmds.group(ctrl, n=ctrl + '_grp#')
        con_obj = copy.copy(objs)
        con_obj.append(ctrl_grp1)
        constrain_ = cmds.parentConstraint(con_obj, w=1)
        cmds.delete(constrain_)
        for obj in objs_father:
            cmds.connectAttr(ctrl + '.t', obj + '.t')

        if_follow_attr_ctrl = []
        for obj in objs:
            if cmds.listAttr(obj, m=True, st='follow'):
                if_follow_attr_ctrl.append(obj)

        if if_follow_attr_ctrl or father:
            cmds.addAttr(ctrl, k=True, ln='add_attr', at='enum', en='------:------:')
            cmds.setAttr(ctrl + '.add_attr', e=True, channelBox=True)
            cmds.addAttr(ctrl, min=0, max=1, dv=1, ln='follow', at='double', k=True)
        for follow_attr_ctrl in if_follow_attr_ctrl:
            cmds.connectAttr(ctrl + '.follow', follow_attr_ctrl + '.follow')
            cmds.setAttr(follow_attr_ctrl + '.add_attr', lock=True, keyable=False, channelBox=False)
            cmds.setAttr(follow_attr_ctrl + '.follow', lock=True, keyable=False, channelBox=False)

        if father:
            attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            con_attr = []
            for attr in attrs:
                con_attr.append(('{}.{}').format(ctrl_grp2, attr))

            cmds.parentConstraint([father, ctrl_grp2], mo=True, w=1)
            cmds.setDrivenKeyframe(con_attr, cd=ctrl_grp2 + '.v', itt='linear', ott='linear')
            cmds.connectAttr(ctrl + '.follow', ctrl_grp2 + '.blendParent1')
        cmds.parent(ctrl_grp1, 'aimSys_ctrl_grp')
        cmds.select(ctrl)


class THCtrlToObject(object):

    def __init__(self, obj_list=None, name='obj', ctrl_style='circle', ctrl_axial='y', ctrl_method='constrain', rig_TRS=[
 1, 1, 1], if_use_constrain_scale=False, lock_hide_attr=[
 0, 0, 0, 1], ctrl_size=1, ctrl_color=18, grp_layout=2, if_create_main_grp=True, adsorption_mode='tr', if_parent=False, if_use_obj_name=False, replace_str=None, suffix='_ctrl'):
        u"""依據選擇物件創建控制器.
        :type ctrl_axial: str
            'x' | 'y' | 'z'
        :type ctrl_method: str
            'None' | 'parent' | 'constrain' | 'connect'
        :type rig_TRS: list
            [bool, bool, bool]
        :type lock_hide_attr: list
            [bool, bool, bool, bool]
        :type adsorption_mode: str
            'tr' | 't' | 'r'
        """
        self.obj_list = obj_list
        self.name = name
        self.ctrl_style = ctrl_style
        self.ctrl_axial = ctrl_axial
        self.ctrl_method = ctrl_method
        self.rig_TRS = rig_TRS
        self.if_use_constrain_scale = if_use_constrain_scale
        self.lock_hide_attr = lock_hide_attr
        self.ctrl_size = ctrl_size
        self.ctrl_color = ctrl_color
        self.grp_layout = grp_layout
        self.if_create_main_grp = if_create_main_grp
        self.adsorption_mode = adsorption_mode
        self.if_parent = if_parent
        self.if_use_obj_name = if_use_obj_name
        self.replace_str = replace_str
        self.suffix = suffix
        self.new_name = None
        self.new_ctrl_list = None
        self.new_ctrl_grp_list = None
        self.main_grp = None
        self.grp_layout_list = []
        return

    def create(self, obj_list=None):
        if obj_list is not None:
            self.obj_list = obj_list
        self._name()
        self._ctrl()
        self._control()
        self._main_grp()
        if self.if_parent:
            self.ctrl_parent()
        return [
         self.new_ctrl_list, self.new_ctrl_grp_list]

    def batch_create(self):
        new_list = []
        obj_list = []
        for obj in self.obj_list:
            child_list = cmds.listRelatives(obj, ad=True)
            child_list.append(obj)
            new_list.append(child_list[::-1])
            obj_list.extend(child_list)

        new_ctrl_list = []
        name = self.name
        for i, obj_childs in enumerate(new_list):
            self.obj_list = obj_childs
            self.name = ('{}_{}').format(name, i + 1)
            self.create()
            new_ctrl_list.extend(self.new_ctrl_list)
            self.new_ctrl_list = []
            self.new_ctrl_grp_list = []
            self.grp_layout_list = []
            self.new_name = []

        self.new_ctrl_list = new_ctrl_list
        self.obj_list = obj_list

    def _name(self):
        u"""產生命名列表"""
        self.new_name = []
        if self.if_use_obj_name:
            if self.replace_str:
                for n in self.obj_list:
                    new_name = n.replace(self.replace_str, self.suffix)
                    new_name = n + self.suffix if new_name == n else new_name
                    self.new_name.append(new_name)

            else:
                for n in self.obj_list:
                    self.new_name.append(n + self.suffix)

        elif len(self.obj_list) == 1:
            self.new_name = [
             self.name + self.suffix] * len(self.obj_list)
        else:
            for i, n in enumerate(self.obj_list, 1):
                self.new_name.append(('{}{}{}').format(self.name, self.suffix, i))

    def _ctrl(self):
        self.new_ctrl_list = []
        self.new_ctrl_grp_list = []
        self.grp_layout_list = []
        for i, n in enumerate(self.obj_list):
            ctrl = thMyController(style=self.ctrl_style, axial=self.ctrl_axial, scale=self.ctrl_size, color=self.ctrl_color)
            if not cmds.objExists(self.new_name[i]):
                ctrl = cmds.rename(ctrl, self.new_name[i])
            else:
                ctrl = cmds.rename(ctrl, self.new_name[i] + '_#')
            ctrl_grp1 = None
            new_grp_list = []
            if self.grp_layout:
                for index in range(self.grp_layout):
                    new_grp_list.append(thLocatorGrp([ctrl])[0])

                ctrl_grp1 = new_grp_list[0]
            else:
                new_grp_list.append(ctrl)
                ctrl_grp1 = ctrl
            self.new_ctrl_list.append(ctrl)
            self.new_ctrl_grp_list.append(ctrl_grp1)
            self.grp_layout_list.append(new_grp_list)
            try:
                cmds.setAttr(ctrl + '.rotateOrder', cmds.getAttr(n + '.rotateOrder'))
            except:
                continue

            AdsorptionObj([ctrl_grp1], n, self.adsorption_mode)

        thLockHiddenAttr(self.new_ctrl_list, self.lock_hide_attr)
        return

    def _control(self):
        u"""控制物件"""
        tmc_cls = THMultipleControl(self.new_ctrl_list, self.obj_list)
        if self.ctrl_method == 'parent':
            tmc_cls.app_parent()
        elif self.ctrl_method == 'connect':
            tmc_cls.app_connect(self.rig_TRS)
        elif self.ctrl_method == 'constrain':
            for i, ctrl in enumerate(self.new_ctrl_list):
                if self.rig_TRS[0] and self.rig_TRS[1]:
                    cmds.parentConstraint([ctrl, self.obj_list[i]], mo=True, weight=1)
                elif self.rig_TRS[0]:
                    cmds.pointConstraint([ctrl, self.obj_list[i]], mo=True, weight=1)
                elif self.rig_TRS[1]:
                    cmds.orientConstraint([ctrl, self.obj_list[i]], offset=[0, 0, 0], weight=1)
                if self.rig_TRS[2]:
                    if self.if_use_constrain_scale:
                        cmds.scaleConstraint([ctrl, self.obj_list[i]], offset=[1, 1, 1], weight=1)
                    else:
                        cmds.connectAttr(ctrl + '.s', self.obj_list[i] + '.s')

    def _main_grp(self):
        u"""創件主要 grp"""
        if self.if_create_main_grp:
            name = thRemoveStrNum(self.new_name[0])[0]
            self.main_grp = cmds.group(n=name + '_main_grp#', em=True)
            cmds.parent(self.new_ctrl_grp_list, self.main_grp)

    def ctrl_parent(self):
        thGrpParent(self.new_ctrl_list, True, self.grp_layout)


class THMultipleControl(object):

    def __init__(self, ctrl_list, objs):
        u"""多個控制多個.
        :type ctrl_list: list
        :type objs: list
        """
        self.ctrl_list = ctrl_list
        self.objs = objs

    def app_parent(self):
        """parent"""
        for i, ctrl in enumerate(self.ctrl_list):
            cmds.parent(self.objs[i], ctrl)

    def app_connect(self, use_trs_bool):
        """connect.
        :type use_trs_bool: list
            [bool, bool, bool]
        """
        attr_list = []
        for i, attr in enumerate(['t', 'r', 's']):
            if use_trs_bool[i]:
                attr_list.append(attr)

        for i, ctrl in enumerate(self.ctrl_list):
            for attr in attr_list:
                cmds.connectAttr(ctrl + '.' + attr, self.objs[i] + '.' + attr)

    def app_constrain(self, use_trs_bool):
        """constrain.
        :type use_trs_bool: list
            [bool, bool, bool]
        """
        for i, ctrl in enumerate(self.ctrl_list):
            if use_trs_bool[0] and use_trs_bool[1]:
                cmds.parentConstraint([ctrl, self.objs[i]], mo=True, weight=1)
            elif use_trs_bool[0]:
                cmds.pointConstraint([ctrl, self.objs[i]], mo=True, weight=1)
            elif use_trs_bool[1]:
                cmds.orientConstraint([ctrl, self.objs[i]], offset=[0, 0, 0], weight=1)
            if use_trs_bool[2]:
                cmds.scaleConstraint([ctrl, self.objs[i]], offset=[1, 1, 1], weight=1)


class AnimKeyChangeType(object):

    def __init__(self, objs, main_ctrl_attr, key_attrs, strat_time, end_time):
        u"""動畫轉 driven key.
        :type objs: list
        :type main_ctrl_attr: str
        :type key_attrs: list
        :type strat_time: int
        :type end_time: int
        """
        self.objs = objs
        self.main_ctrl_attr = main_ctrl_attr
        self.key_attrs = key_attrs
        self.strat_time = strat_time
        self.end_time = end_time
        self.total_timr = None
        self.in_key_attr_dict = {}
        self.frame_data_dict = {}
        return

    def to_driven_key(self):
        cmds.delete(self.objs, sc=True, uac=False, hi=False, cp=False, s=False)
        self.total_timr = int(self.end_time - self.strat_time)
        anim_node_list = self._get_key_attrs()
        self._save_frame_data()
        cmds.delete(anim_node_list)
        self._set_key()
        cmds.select(self.main_ctrl_attr.split('.')[0])

    def _get_key_attrs(self):
        u"""找每個物件中有設置 key 的 attr
            {obj: [attr,...],...}
        """
        anim_node_list = []
        for obj in self.objs:
            attr_list = []
            if self.key_attrs:
                attr_list = self.key_attrs
            else:
                attr_list = cmds.listAttr(obj, k=True, u=True, m=True)
            attr_ = []
            for attr in attr_list:
                key_node = cmds.listConnections(obj + '.' + attr, c=False)
                if key_node:
                    type = cmds.nodeType(key_node[0])
                    if type == 'animCurveTA' or type == 'animCurveTL' or type == 'animCurveTU':
                        attr_.append(attr)
                        anim_node_list.append(key_node[0])

            if attr_:
                self.in_key_attr_dict[obj] = attr_

        return anim_node_list

    def _save_frame_data(self):
        u"""保存每個時間上的物件屬性數據.
            {frame: {obj: {attr: data, ...}, ...}, ...}
        """
        for frame in range(self.total_timr):
            offset = self.strat_time + frame
            cmds.currentTime(offset)
            obj_attr_data = {}
            for obj in self.in_key_attr_dict:
                attr_data = {}
                for attr in self.in_key_attr_dict[obj]:
                    attr_data[attr] = cmds.getAttr(obj + '.' + attr)

                obj_attr_data[obj] = attr_data

            self.frame_data_dict[offset] = obj_attr_data

    def _set_key(self):
        u"""設定 DrivenKey"""
        key_attr_list = []
        for obj in self.in_key_attr_dict:
            for attr in self.in_key_attr_dict[obj]:
                key_attr_list.append(obj + '.' + attr)

        for frame in self.frame_data_dict:
            cmds.setAttr(self.main_ctrl_attr, frame)
            for obj in self.frame_data_dict[frame]:
                for attr in self.frame_data_dict[frame][obj]:
                    cmds.setAttr(obj + '.' + attr, self.frame_data_dict[frame][obj][attr])

            cmds.setDrivenKeyframe(key_attr_list, cd=self.main_ctrl_attr, itt='linear', ott='linear')


class ThSaveObjsAttrData(object):

    def __init__(self, objs=None, attrList=None, data=None):
        u"""保存物件屬性及數據"""
        self.objs = objs
        self.attrList = attrList if attrList else []
        self.data = data if data else []
        if type(data) is dict:
            dataList = []
            for key, values in data.items():
                dataValue = []
                for attr, value in values.items():
                    dataValue.append([attr, value])

                dataList.append([key, dataValue])

            self.data = dataList

    def save(self):
        for obj in self.objs:
            doAttrList = self.attrList
            if not self.attrList:
                doAttrList = cmds.listAttr(obj, m=True, k=True, r=True, se=True, v=True, w=True, c=True, u=True)
            if not doAttrList:
                continue
            dataAttr = []
            for attr in doAttrList:
                try:
                    value = cmds.getAttr(('{}.{}').format(obj, attr))
                    dataAttr.append([attr, value])
                except:
                    continue

            dataAttr = dataAttr if dataAttr else None
            self.data.append([obj, dataAttr])

        return

    def redoSave(self):
        u"""回到保存數據"""
        for obj, attrValue in self.data:
            if attrValue is None:
                continue
            for attr, value in attrValue:
                try:
                    cmds.setAttr(('{}.{}').format(obj, attr), value)
                except RuntimeError:
                    continue

        return


class ThDistanceSoftLocator(object):

    def __init__(self, objs, name='th', create_soft=True, quantity_soft=1, mode_soft='zipper', default=0, conn_attr=None, exclude_end=False):
        u"""依據距離創建 soft locator.
        :type objs: list
        :type name: str
        :type create_soft: bool
        :type quantity_soft: int 
        :type mode_soft: str 
            'zipper' | 'pipe'
        :type default: int 
        :type conn_attr: list
            [attr] | None
        :type exclude_end: bool
            是否排除列表最後一個物件
        """
        self.objs = objs
        self.name = name
        self.create_soft = create_soft
        self.quantity_soft = quantity_soft
        self.mode_soft = mode_soft
        self.default = default
        self.conn_attr = conn_attr
        self.exclude_end = exclude_end
        self.xyz_list = []
        self.main_grp = None
        self.max_all = None
        self.curve = None
        self.curve_shape = None
        self.locator_list = []
        self.soft_node = []
        self.create()
        return

    def create(self):
        self._get_distance()
        self._create_curve()
        self._creatr_locator()
        if self.create_soft:
            self._create_soft()
        if self.conn_attr:
            self._connect()
        cmds.setAttr(self.curve + '.ty', self.default)

    def _get_distance(self):
        u"""測量每個物件之間的距離."""
        dds = cmds.createNode('distanceDimShape')
        dds_tr = cmds.listRelatives(dds, p=True, f=True)
        xyz = cmds.xform(self.objs[0], q=True, ws=True, t=True)
        cmds.setAttr(dds + '.startPoint', xyz[0], xyz[1], xyz[2])
        for i in range(1, len(self.objs)):
            xyz = cmds.xform(self.objs[i], q=True, ws=True, t=True)
            if i % 2:
                cmds.setAttr(dds + '.endPoint', xyz[0], xyz[1], xyz[2])
            else:
                cmds.setAttr(dds + '.startPoint', xyz[0], xyz[1], xyz[2])
            distance = cmds.getAttr(dds + '.distance')
            self.xyz_list.append(distance)

        cmds.delete(dds_tr)

    def _create_curve(self):
        u"""創建 curve"""
        if not cmds.objExists('def'):
            cmds.group(em=True, n='def')
        if not cmds.objExists('DSL_system_grp'):
            cmds.group(em=True, n='DSL_system_grp')
            cmds.parent('DSL_system_grp', 'def')
            cmds.hide('DSL_system_grp')
        self.main_grp = cmds.group(n=self.name + '_DSL_grp#', em=True)
        cmds.parent(self.main_grp, 'DSL_system_grp')
        max = 0
        for n in self.xyz_list:
            max += n

        self.xyz_list.insert(0, max)
        self.xyz_list.append(max)
        xyz_list_add = []
        data = 0
        for i in range(len(self.xyz_list)):
            xyz_list_add.append(self.xyz_list[i] + data)
            data = xyz_list_add[i]

        move_ = [ [n, 0, 0] for n in xyz_list_add ]
        move_.insert(0, [0, 0, 0])
        self.curve = cmds.curve(d=1, p=move_, n=self.name + '_DSL_curve#')
        self.curve_shape = cmds.listRelatives(self.curve, ad=True)[0]
        cmds.parent(self.curve, self.main_grp)
        self.max_all = max * 3

    def _creatr_locator(self):
        u"""創建 locator"""
        lo_grp = cmds.group(n=self.name + '_DSL_locator_grp#', em=True)
        cmds.parent(lo_grp, self.main_grp)
        app_len = len(self.objs) if self.exclude_end else len(self.objs) + 1
        for i in range(1, app_len):
            poci = cmds.createNode('pointOnCurveInfo', n=('{0}_pointOnCurveInfo{1}_#').format(self.name, i))
            cmds.setAttr(poci + '.parameter', i)
            cmds.connectAttr(self.curve_shape + '.worldSpace[0]', poci + '.inputCurve')
            lo = cmds.spaceLocator(n=('{0}_DSL_locator{1}_#').format(self.name, i))[0]
            self.locator_list.append(lo)
            cmds.connectAttr(poci + '.position', lo + '.translate')
            cmds.parent(lo, lo_grp)

    def _create_soft(self):
        u"""創建 soft"""
        for i in range(self.quantity_soft):
            self.soft_node.append(cmds.softMod(self.curve, n=self.name + '_DSL_soft#'))
            cmds.parent(self.soft_node[i][1], self.main_grp)
            cmds.setAttr(self.soft_node[i][1] + '.scalePivot', 0, 0, 0)
            cmds.setAttr(self.soft_node[i][1] + '.rotatePivot', 0, 0, 0)
            cmds.setAttr(self.soft_node[i][0] + '.falloffCenter', 0, 0, 0)
            cmds.setAttr(self.soft_node[i][1] + 'Shape.origin', 0, 0, 0)
            cmds.setAttr(self.soft_node[i][0] + '.falloffRadius', self.max_all)

        for i in range(self.quantity_soft):
            cmds.addAttr(self.soft_node[i][1], ln='follow', at='double', min=0, max=10, dv=0, k=True)
            cmds.addAttr(self.soft_node[i][1], ln='offset', at='double', min=0, max=10, dv=0, k=True)
            sr_follow = cmds.createNode('setRange', n=self.name + '_DSL_follow_SR#')
            sr_offset = cmds.createNode('setRange', n=self.name + '_DSL_offset_SR#')
            cmds.setAttr(sr_follow + '.minX', 0)
            cmds.setAttr(sr_follow + '.maxX', 0.7)
            cmds.setAttr(sr_follow + '.oldMinX', 0)
            cmds.setAttr(sr_follow + '.oldMaxX', 10)
            cmds.setAttr(sr_offset + '.minX', 0)
            cmds.setAttr(sr_offset + '.maxX', 0.29)
            cmds.setAttr(sr_offset + '.oldMinX', 0)
            cmds.setAttr(sr_offset + '.oldMaxX', 10)
            cmds.connectAttr(self.soft_node[i][1] + '.follow', sr_follow + '.valueX')
            cmds.connectAttr(self.soft_node[i][1] + '.offset', sr_offset + '.valueX')
            pma1 = cmds.createNode('plusMinusAverage', n=self.name + '_DSL_PMA1_#')
            cmds.connectAttr(sr_follow + '.outValueX', pma1 + '.input1D[0]')
            cmds.connectAttr(sr_offset + '.outValueX', pma1 + '.input1D[1]')
            pma2 = cmds.createNode('plusMinusAverage', n=self.name + '_DSL_PMA2_#')
            cmds.connectAttr(sr_follow + '.outValueX', pma2 + '.input1D[0]')
            cmds.setAttr(pma2 + '.input1D[1]', 0.3)
            cmds.connectAttr(pma1 + '.output1D', self.soft_node[i][0] + '.falloffCurve[0].falloffCurve_Position')
            cmds.connectAttr(pma2 + '.output1D', self.soft_node[i][0] + '.falloffCurve[1].falloffCurve_Position')
            cmds.setAttr(self.soft_node[i][1] + '.ty', 1)
            if self.mode_soft == 'pipe':
                formula = ('{} = ({}/2)+({}/2)').format(self.soft_node[i][0] + '.falloffCurve[2].falloffCurve_Position', pma1 + '.output1D', pma2 + '.output1D')
                cmds.expression(s=formula, n=self.name + '_DSL_EX#')
                cmds.setAttr(self.soft_node[i][0] + '.falloffCurve[2].falloffCurve_Interp', 2)
                cmds.setAttr(self.soft_node[i][0] + '.falloffCurve[0].falloffCurve_FloatValue', 0)
                cmds.setAttr(self.soft_node[i][0] + '.falloffCurve[2].falloffCurve_FloatValue', 1)

        cmds.select([ n[1] for n in self.soft_node ], r=True)

    def _connect(self):
        u"""與控制器連接"""
        for i, lo in enumerate(self.locator_list):
            for attr in self.conn_attr:
                cmds.connectAttr(lo + '.ty', self.objs[i] + '.' + attr)


class ThCurveCreateJoint(object):

    def __init__(self, curve, quantity, name='new', if_adsorption=False, if_parent=True, tangent_aim=[0, 1, 0]):
        u"""依據 curve create joint.
        :type curve: list
        :type name: str
        :type quantity: int
        :type if_adsorption: bool
        :type if_parent: bool
        :rtype: list
        """
        self.curve = curve
        self.quantity = quantity
        self.name = name
        self.if_adsorption = if_adsorption
        self.if_parent = if_parent
        self.tangent_aim = tangent_aim
        self.joint_list_all = []
        self.create()

    def create(self):
        for n in self.curve:
            self.joint_list_all.extend(self._ikh(n))

        cmds.select(self.joint_list_all, r=True)
        return self.joint_list_all

    def _ikh(self, curve):
        cmds.select(cl=True)
        ikh_joint1 = cmds.joint()
        ikh_joint2 = cmds.joint(p=[0.5, 0, 0])
        cmds.ikHandle(sol='ikSplineSolver', ccv=False, pcv=False, n='cc_ikSplineSolver', sj=ikh_joint1, ee=ikh_joint2, c=curve)
        open = cmds.getAttr(curve + '.form')
        open_close = 0 if open else 1
        max_vertex = cmds.getAttr(curve + '.maxValue')
        add_time = max_vertex / (self.quantity - open_close)
        time = 0
        joint_list = []
        for i in range(self.quantity):
            cmds.setAttr('cc_ikSplineSolver.offset', time)
            xyz = cmds.xform(ikh_joint1, q=True, ws=True, t=True)
            cmds.select(cl=True)
            new_joint = cmds.joint(n=self.name + '_joint#', p=xyz)
            time += add_time
            joint_list.append(new_joint)

        if self.if_adsorption:
            AdsorptionObj(objs=joint_list, main=curve, mode='tangent', ifFreeze=True, tangentAim=self.tangent_aim)
        if self.if_parent:
            thGrpParent(joint_list, False)
        cmds.delete(ikh_joint1)
        return joint_list


class THMModifyJointMove(object):

    def __init__(self, joints):
        u"""修改 joint 座標"""
        self.joints = joints
        self.new_joints = []
        if not cmds.objExists('th_modify_joint_old_sets'):
            cmds.sets(em=True, n='th_modify_joint_old_sets')
            cmds.sets(em=True, n='th_modify_joint_ref_sets')
            self.new_joints.extend(cmds.duplicate(joints, rr=True, n='th_modify_joint#', po=True))
            cmds.sets(joints, add='th_modify_joint_old_sets')
            cmds.sets(self.new_joints, add='th_modify_joint_ref_sets')
            cmds.select(self.new_joints, r=True)
            for j in self.new_joints:
                cmds.setAttr(j + '.displayLocalAxis', 1)


TH_TOOL_UPDATA_LIST = '- 適用 MAYA 版本: 2018 - 2020\n- 適用系統: window\n- 更新歷史:\n\n2021.10.20\n/控制器/ 工具集/\n    (新增: 創建 in between 屬性 功能)\n\n2021.10.19\n/通用/ 列表工具(單列表)\n    (新增: 創建 nonlinear)\n\n2021.10.15\n/骨骼/ 編輯骨骼/ 重建父子關係/\n    (優化: 存檔內容)\n/控制器/ IK spline/\n    (新增: 限制層級數 功能)\n    \n2021.10.14\n/骨骼/ 複製權重/ \n    (新增: "name" 模式)\n/通用/ 列表工具(雙列表)/ 工具集/\n    (新增: Skin 功能)\n\n2021.10.10\n/骨骼/ \n    (新增: 編輯指定骨骼權重 功能)\n/骨骼/ 複製權重/\n    (新增: 複製權重(方法三) 功能)\n\n2021.10.06\n/控制器/ 輪子控制器/\n    (新增: 控制參數)\n\n2021.10.05\n/動畫/ 動作錄製/\n    (新增: 創建 curve 功能)\n\n2021.09.26\n/控制器/ \n    (新增: 列表屬性值 0 到 1 循環 功能)\n\n2021.09.25\n/骨骼/ 編輯權重/\n    (優化: 導回權重效率)\n\n2021.09.21\n/骨骼/\n    (新增: 變形器轉換蒙皮權重 功能)\n\n2021.09.19\n/骨骼/ 工具集/\n    (新增: 依據子骨骼數量創建歸納群組 功能)\n\n2021.09.10\n/控制器/ IK spline/\n    (新增: 控制器數量等於骨骼數量 功能)\n\n2021.09.03\n/骨骼/ 工具集/\n    (新增: 移動權重到新骨骼 功能)\n\n2021.09.02\n/控制器/ 工具集/\n    (新增: 分割屬性權重 功能)\n\n2021.08.31\n/控制器/ 目標控制器/\n    (優化: 綁定架構)\n\n2021.08.29\n/骨骼/ 轉移 skin weight/\n    (優化: 執行方式並增加 "修剪權重參數列表" 功能)\n\n2021.07.20\n/控制器/ 工具集/\n    (新增: 清理層級下無作用的 group 功能)\n    \n2021.07.04\n/控制器/ Objects ctrl/\n    (修正: THVtxLocator class bug)\n\n2021.05.31\n/控制器/ IK spline/\n    (優化: elasticity 功能)\n\n2021.02.17\n/控制器/ 拉鍊嘴型/\n    (優化: 執行方式)\n\n2021.02.12\n/通用/ 列表工具(單列表)/ 批量設置關鍵偵/\n    (優化: 執行方式)\n\n2021.02.09\n/通用/ 通用工具集/ 工具集/\n    (新增: 篩選頂點數量, 顏色相同的 curve 功能)\n/骨骼/ 編輯權重/ 編輯局部權重/\n    (優化: 執行方式)\n\n2021.02.08\n/控制器/ 工具集/\n    (修正: 複製控制器並連接屬性 功能)\n\n2021.02.01\n/通用/ 重命名/ 篩選指定字符物件/\n    (新增: 模式 功能)\n/控制器/ 控制器工具集/ 工具集/\n    (優化: 複製控制器並連接屬性 功能)\n\n2021.01.29\n/控制器/ 拉鍊嘴型/\n    (新增: 創建表情控制器 功能)\n\n2021.01.28\n/控制器/ 控制器工具集/\n    (新增: 複製控制器並連接屬性 功能)\n    (新增: 物件變換屬性添加權重設定 功能)\n\n2021.01.26\n/控制器/ Driven key system/\n    (新增: 縮放值/ 列表 功能)\n\n2021.01.24\n/控制器/ 牽動系統/\n    (修正: 設定開始, 結束打印數據 BUG)\n\n2021.01.22\n/骨骼/ 骨骼工具集/\n    (優化: ThCoordinateCreateMeshEx 函數)\n/控制器/ 拉鍊嘴型/\n    (優化: 執行內容)\n\n2021.01.18\n/控制器/ Objects ctrl/\n    (優化: THVtxLocator 函數)\n\n2021.01.17\n/骨骼/ 工具集/\n    (優化: 切換開/ 關所有 skin 屬性)\n\n2021.01.11\n/控制器/ \n    (新增: 列表屬性驅動 0 到 1 屬性值 功能)\n\n2021.01.06\n/控制器/ Edit blend shape/\n    (新增: 匹配目標並連接屬性 功能)\n\n2020.12.29\n/通用/ 列表工具(單列表)/\n    (新增: 指定屬性移出動畫層 功能)\n\n2020.12.06\n/骨骼/ 編輯權重/\n    (新增: 編輯局部權重 功能)\n\n2020.11.27\n/通用/ 工具集/\n    (新增: 刪除多餘 shape 功能)\n\n2020.11.19\n/控制器/ 工具集/\n    (新增: 傳遞連接 功能)\n\n2020.11.08\n/控制器/ Edit blend shape/\n    (新增: 依據 skin 權重設定 blend 功能)\n\n2020.11.06\n/動畫/ 工具集/\n    (新增: 節點數值傳遞至控制器上 功能)\n\n2020.10.23\n/ 控制器/ 工具集/\n    (新增: 斷開/ 恢復 物件連接 功能)\n\n2020.10.10\n/ 控制器/ 工具集/\n    (新增: 關閉所有 blendShape 編輯狀態 功能)\n    \n2020.09.28\n/ 骨骼/ 工具集/\n    (新增: 設定 skin 節點屬性 功能)\n\n2020.09.25\n/ 通用/ 一般功能/ \n    (新增: 打印設定物件屬性值(移動))\n    (新增: 打印設定物件屬性值(旋轉))\n\n2020.08.21\n- 優化 QSS \n/ 通用/ 通用工具集/ 工具集/ \n    (新增: 批量 reference 功能)\n\n2020.08.20\n/ 動畫/ 對位並 KEY/ \n    (新增: 設定模式 功能)\n\n2020.08.18\n/ 動畫/ 對位並 KEY/\n    (新增: 選擇是否傳遞移動或旋轉 功能)\n/ 動畫/ Play blast/\n    (新增: get 當前時間範圍 功能)\n    \n2020.08.11\n/ 控制器/ Edit blend shape/ 依據 skin 權重拆分 blend/ \n    (新增: 復原權重 功能)\n    (新增: 附屬功能(smooth weight) 功能)\n\n2020.08.04\n/ 動畫/ 平滑動畫曲線/\n    (新增: 過濾 功能)\n\n2020.08.03\n/ 動畫/ 動畫工具集/\n    (新增: 對位並 KEY 功能)\n\n2020.07.25\n/ 通用/ 選擇自訂前綴名稱工具/\n    (新增: 替換 功能)\n\n2020.06.11\n/ 通用/ "列表工具/ 選擇集"/\n    (新增: 保存, 讀取, 刪除 功能)\n\n2020.06.07\n- "?" 提示功能優化\n\n2020.05.31\n/ 控制器/ Edit blend shape/ 依據 skin 權重拆分 blend/\n    (新增: 創建拆分工具 功能)\n\n2020.05.23\n/ 通用/ "列表工具/ 選擇集"/\n    (優化: 選擇到變換節點 功能)\n\n2020.05.21\n/ 動畫/ \n    (新增: 動作錄製 功能)\n\n2020.05.19\n/ 控制器/ Objects ctrl/\n    (優化: 操作模式)\n\n2020.05.17\n- 優化: "摺疊控件" 功能\n- 優化: 拉下式選單顯示風格\n/ 通用/ "列表工具/ 選擇集"/\n    (優化: 操作模式)\n\n2020.05.16\n/ 通用/ 工具集/ \n    (優化: 打印當前選擇物件 功能)\n    (優化: 打印設定物件屬性數值 功能)\n\n2020.05.12\n/ 骨骼/ 骨骼工具集/\n    (新增: 創建模式 功能選項)\n\n2020.05.11\n/ 骨骼/ Smooth weight/\n    (優化: 選擇複數模型執行)\n\n2020.05.05\n/ 通用/ 重命名/ 添加(前/ 後)綴/\n    (新增: 方向 功能選項)\n/ 控制器/ Ctrl objects/\n    (優化: 使用物件名稱做命名 判斷條件)\n\n2020.05.04\n/ 控制器/ 拉鍊嘴型/\n    (新增: 創建控制器 功能選項)\n\n2020.05.03\n/ 控制器/ 拉鍊嘴型/\n    (新增: 創建於層級上 功能選項)\n\n2020.05.02\n/ 骨骼/ 編輯骨骼/\n    (新增: 調整骨骼鍊段數 功能)\n\n2020.05.01\n- 更新 UI 介面風格\n\n2020.04.21\n/ 通用/ 選擇指定類別物件/\n    (新增: 選擇類別)\n/ 動畫/ 動畫工具集/ \n    (新增: 影格換算時間 功能)\n\n2020.04.20\n- 優化: om2 設定權重 功能\n    \n2020.04.19\n/ 骨骼/ 轉移 skin weight/ 拆分權重值/\n    (新增: 使用 om2 設定權重 功能)\n\n2020.04.03\n/ 動畫/ 動畫工具集/ 工具集/\n    (新增: 打印使用的解算器名稱)\n\n2020.04.02\n/ 動畫/ 動畫工具集/ 工具集/\n    (新增: 刪除未使用的解算器)\n\n2020.03.30\n/ 動畫/ 動畫工具集/ \n    (新增: Solver display 功能)\n\n2020.03.27\n/ 骨骼/ 轉移 skin weight/\n    (新增: 使用 om2 設定權重 功能)\n\n2020.03.26\n/ 骨骼/ 編輯權重/ Soft to skin weight/\n    (新增: 使用 om2 設定權重 功能)\n\n2020.03.23\n/ 通用/ 通用工具集/ 工具集/\n    (新增: (Undo)頂點數值傳遞 功能)\n\n2020.03.19\n/ 骨骼/ 編輯權重/ Soft to skin weight/\n    (新增: 批量設定子層級 功能)\n\n2020.03.16\n/ 骨骼/ 權重工具集/ \n    (新增: 依據選擇骨骼創建 mesh 功能)\n\n2020.03.14\n/ 骨骼/ 編輯權重/ 編輯權重/ \n    (優化: 自動關閉 maintainMaxInfluences 屬性)\n\n2020.03.11\n/ 骨骼/ 轉移 skin weight/\n    (優化: 執行判斷條件)\n/ 骨骼/ 權重規範/\n    (新增: 設置(all) influences 功能)\n    (新增: maintain max influences 功能)\n\n2020.03.10\n/ 通用/ 工具集/\n    (新增: 打印設定物件屬性值 功能)\n/ 通用/ 重命名/\n    (新增: 篩選指定字符物件)\n\n2020.03.09\n/ 控制器/ 少數控制多數/\n    (新增: 重新設定 UV 座標 功能)\n\n2020.03.03\n/ 控制器/ Help/\n    (新增: 控制參數)\n\n2020.03.02\n- QComboBox\n    (顯示介面優化)\n/ 骨骼/ 權重工具集/ 工具集/ \n    (新增: 座標創建 mesh 功能)\n/ 動畫/ 動畫工具集/\n    (新增: Play blast 功能)\n\n2020.03.01\n/ 控制器/ 控制器工具集/ 工具集/\n    (新增: 篩選有數值的 transform)\n\n2020.02.22\n/ 骨骼/ 權重工具集/\n    (優化: 操作介面)\n\n2020.02.15\n/ 控制器/ \n    (新增: 牽動系統)\n/ 骨骼/ 權重工具集/ 工具集/\n    (新增: (非循環)依據選擇物件之層級創建 mesh)\n    (新增: (循環)依據選擇物件之層級創建 mesh)\n\n2020.02.12\n/ 控制器/ Edit blend shape/ 添加 shape to node/ \n    (優化: 執行方式)\n\n2020.02.11\n/ 控制器/ \n    (新增: 骨骼肌肉系統 功能)\n\n2020.02.10\n/ 控制器/ Ctrl objects/\n    (修正: 無法創建 joint BUG)\n\n2020.02.09\n/ 骨骼/\n    (優化: 重新歸納工具群組名稱)\n/ 骨骼/ 轉移 skin weight/ "多對多/ 多對一"/\n    (修正: 選擇頂點傳遞時的 BUG)\n\n2020.02.07\n/ 通用/ 鏡像工具/\n    (新增: 選擇全部列表物件)\n/ 控制器/ Driven key system/\n    (新增: 快速設定控制器屬性值)\n/ 動畫/ \n    (新增: 擾亂場 功能)\n\n2020.02.03\n/ 骨骼/ 權重工具集/ Smooth weight/\n    (優化: 執行方式)\n\n2020.01.31\n/ 骨骼/ 轉移 skin weight/ 拆分權重值/ \n    (優化: 自動添加拆分用 joints)\n/ 控制器/ Objects ctrl/ \n    (優化: 創建模式的控制器生成軸向，對應至物件)\n\n2020.01.30\n/ 通用/ 通用工具集/\n    (優化: "交互切換顯示/ 隱藏")\n/ 骨骼/ 權重工具集/ \n    (新增: "Smooth weight" 功能)\n\n2020.01.21\n/ 骨骼/ "匯出/ 匯入蒙皮頂點的權重數據"/\n    (修正: 匯入權重總量超過 1 錯誤)\n\n2020.01.20\n/ 通用/ 通用工具集/ 工具集/\n    (優化: 依據功能歸納到相對應模塊中)\n    (優化: 取消展開列表時，隱藏同層級工具列功能)\n/ 控制器/ 工具集/ 創建 group/\n    (優化: 執行判斷條件)\n\n2020.01.19\n/ 通用/ 列表工具(雙列表)/ 其他/\n    (修正: data transfer(數值傳遞) BUG)\n\n2020.01.18\n/ 通用/ 創建控制器/\n    (優化: 功能移動至/ 控制器/ 控制器)\n\n2020.01.17\n/ 骨骼/ 編輯骨骼/ \n    (新增: 選擇子層級骨骼)\n\n2020.01.16\n/ 通用/ 通用工具集/ 重建父子關係/ \n    (優化: 增加一些防呆判斷條件)\n\n2020.01.15\n/ 骨骼/ 編輯骨骼/ \n    (新增: 顯示軸向, 設置末端骨骼軸向 功能)\n\n2020.01.06\n/ 骨骼/ "匯出/ 匯入蒙皮頂點的權重數據"/\n    (優化: 執行方式)\n/ 骨骼/ 權重工具集/ 選擇關聯物件/\n    (優化: 執行方式)\n/ 通用/ 重命名/\n    (新增: "清除指定長度", "交換名稱" 功能)\n    \n2019.12.17\n/ 通用/ 列表工具(單列表)/\n    (新增: Move 功能)\n/ 動畫/\n    (新增: 批量設置關鍵偵 功能)\n    \n2019.12.16\n- 更新安裝檔、資料夾架構\n    \n2019.12.02\n/ 控制器/ Edit blend shape/\n    (新增: 創建 blend shape)\n    \n2019.11.30\n- 增加 "logo show" 動畫 \n/ 控制器/ 序列控制器/ 單屬性控制序列(deform)\n    (修正: BUG)\n    \n2019.11.28\n- 可重複創建新 window\n    \n2019.11.25\n- 啟動程式自動加載 "微軟正黑體" 字型\n- 更新進度條樣式\n/ 控制器/ Edit blend shape/\n    (新增: 獲取沒有 deform 影響的 shape)\n    (新增: 從 skin weight 拆分 blend shape)\n    \n2019.11.16\n/ 控制器/\n    (新增: Edit blend shape 功能)\n    \n2019.11.12\n- 為了將來能開發更多樣化的工具，因此使用 PySide2 重寫了 UI 介面，\n新 UI 為中文化界面，專有名詞的部分則保持英文，\n標題列新增兩個按鈕\n    ("+" 複製工具列、"?" 顯示註解(有的話才顯示))\n/ 通用/ 通用工具集/ 工具集/ \n    (以往 Tools 的部分改為 "展開列表")\n    (直接在本框架中顯示，不會產出新視窗)\n'
RIG_NOTE = ''
TOP_STYLE_SHEET = '\n/********** QMainWindow **********/\nQMainWindow {\n    background-color: rgb(60,55,55);\n}\n\n/********** QScrollBar **********/\nQScrollBar {\n    background-color: rgb(50,50,50);\n    border-radius: 8px;\n}\nQScrollBar:horizontal {\n    height: 15px;\n    margin: -1px;\n}\nQScrollBar:vertical {\n    width: 15px;\n    margin: -1px;\n}\nQScrollBar::handle:horizontal, QScrollBar::handle:vertical {\n    background-color: rgb(90,90,90);\n    border: 1px solid rgb(50,50,50);\n    border-radius: 6px;\n    margin: 2px;\n    min-height: 30px;\n}\nQScrollBar::add-line, QScrollBar::sub-line {\n    width: 0px;\n    height: 0px;\n} \nQScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n     background: none;\n}\n\n/********** QProgressBar **********/\nQProgressBar {\n    max-height: 15px;\n    border: 1px solid rgb(100,100,100);\n    border-radius: 6px;\n    text-align: center;\n}\nQProgressBar::chunk {\n    background-color: rgb(165,53,53);\n    margin: 3px;\n}\n\n/********** QDialog **********/\nQDialog {\n    background-color: rgb(68,65,65);\n}\n\n/********** QWidget **********/\nQWidget#mainWidget1 {\n    background-color: rgb(68,65,65);\n}\nQWidget#mainWidget2 {\n    background-color: rgb(68,65,65);\n}\n\n/********** QScrollArea **********/\nQScrollArea {\n    border: none;\n    background-color: transparent;\n}\n\n/********** QSpinBox **********/\nQSpinBox {\n    border-radius: 4px;\n    min-width: 20px;\n    min-height: 20px;\n    border: 1px solid rgb(100,100,100);\n    background-color: rgb(40,40,40);\n}\n\n/********** QDoubleSpinBox **********/\nQDoubleSpinBox {\n    border-radius: 4px;\n    min-width: 20px;\n    min-height: 20px;\n    border: 1px solid rgb(100,100,100);\n    background-color: rgb(40,40,40);\n}\n\n/********** QCheckBox **********/\nQCheckBox {\n    min-height: 20px;\n}\nQCheckBox::indicator {\n    width: 8px;\n    height: 8px;\n    border: 1px solid rgb(100,100,100);\n    border-radius: 5px;\n}\nQCheckBox::indicator:unchecked {\n    border: 1px solid rgb(100,100,100);\n    background-color: rgb(30,30,30);\n}\nQCheckBox::indicator:checked {\n    border: 1px solid rgb(30,30,30);\n    background-color: rgb(100,160,170);\n}\nQCheckBox::indicator:hover {\n    border: 1px solid rgb(150,150,150);\n}\nQCheckBox:!enabled {\n    color: rgb(120,120,120);\n}\n\n/********** QRadioButton **********/\nQRadioButton {\n    min-height: 20px;\n}\nQRadioButton::indicator {\n    width: 8px;\n    height: 8px;\n    border: 1px solid rgb(100,100,100);\n    border-radius: 5px;\n}\nQRadioButton::indicator:unchecked {\n    border: 1px solid rgb(100,100,100);\n    background-color: rgb(30,30,30);\n}\nQRadioButton::indicator:checked {\n    border: 1px solid rgb(30,30,30);\n    background-color: rgb(100,160,170);\n}\nQRadioButton::indicator:hover {\n    border: 1px solid rgb(150,150,150);\n}\nQRadioButton:!enabled {\n    color: rgb(120,120,120);\n}\n\n/********** QComboBox **********/\nQComboBox {\n    min-width: 50px;\n    height: 20px;\n    border-radius: 4px;\n    border: 1px solid rgb(100,100,100);\n    background-color: rgb(40,40,40);\n}\nQComboBox:hover {\n    border: 1px solid rgb(150,150,150);\n}\nQComboBox:on {\n    background-color: rgb(90,40,40);\n}\nQComboBox::drop-down {\n    background-color: transparent;\n}\nQComboBox QAbstractItemView {\n    border-radius: 4px;\n    border: 2px solid rgb(150,150,150);\n}\nQComboBox QAbstractItemView::item {\n    min-height: 20px; \n}\nQListView {\n    font-size: 12px;\n    font-weight: bold;\n    font-family: Microsoft JhengHei;\n}\n\n/********** QFontComboBox **********/\nQFontComboBox::drop-down {\n    width: 20px;\n    background-color: rgb(100,100,100);\n    border-top-right-radius: 2px;\n    border-bottom-right-radius: 2px;\n}\n\n/********** QFrame **********/\nQFrame#frameGrp {\n    background-color: rgb(60,55,55);\n    border: 2px solid rgb(100,100,100);\n    border-radius: 6px;\n}\n\n/********** QGroupBox **********/\nQGroupBox {\n    background-color: rgb(60,55,55);\n    font-size: 12px;\n    font-weight: bold;\n    font-family: Microsoft JhengHei;\n    border: 2px solid rgb(100,100,100);\n    border-radius: 6px;\n    margin-top: 17px;\n}\nQGroupBox::title {\n    border-radius: 10px;\n    color: rgb(240,200,150);\n    subcontrol-origin: margin;\n    subcontrol-position: top center;\n}\n\n/********** QPushButton **********/\nQPushButton {\n    background-color: rgb(100,100,100);\n    border-radius: 4px;\n    padding: 3px;\n}\nQPushButton:hover {\n    background-color: rgb(80,125,135);\n}\nQPushButton#foldButton:hover {\n    background-color: rgb(80,80,80);\n}\nQPushButton#foldButton[check=true] {\n    background-color: rgb(50,50,50);\n}\nQPushButton#modeButton:hover {\n    background-color: rgb(90,40,40);\n}\nQPushButton#modeButton[check=true] {\n    background-color: rgb(210,100,50);\n}\n\n/********** QLineEdit **********/\nQLineEdit {\n    border-radius: 4px;\n    min-height: 20px;\n    border: 1px solid rgb(100,100,100);\n}\nQLineEdit:enabled {\n    background-color: rgb(40,40,40);\n}\nQLineEdit:!enabled {\n    background-color: rgb(70,70,70);\n}\n\n/********** QLabel **********/\nQLabel#annotation {\n    color: rgb(220,80,80);\n}\n\n/********** QListWidget **********/\nQListWidget {\n    background-color: rgb(40,40,40);\n    border: 1px solid rgb(100,100,100);\n    border-radius: 6px;\n}\n\n/********** QPlainTextEdit **********/\nQPlainTextEdit {\n    background-color: rgb(40,40,40);\n    border: 1px solid rgb(100,100,100);\n    border-radius: 6px;\n}\n\n/********** ALL text color **********/\nQPushButton, QLabel, QCheckBox, \nQRadioButton, QSpinBox, QComboBox, \nQPlainTextEdit, QDoubleSpinBox {\n    color: rgb(200,200,200);\n}\n\n/********** ALL font **********/\nQPushButton, QLabel, QCheckBox, \nQRadioButton, QSpinBox, QComboBox, \nQPlainTextEdit, QDoubleSpinBox {\n    font-size: 12px;\n    font-weight: bold;\n    font-family: Microsoft JhengHei;\n}\n\n/********** ALL selection-background-color **********/\nQComboBox QAbstractItemView, QDoubleSpinBox, QPlainTextEdit,\nQSpinBox, QScrollArea, QListWidget, QLineEdit {\n    selection-background-color: rgb(80,125,135);\n}\n\n/********** ToolBox **********/\nQPushButton#toolButton {\n    text-align: left;\n    color: rgb(255,160,100);\n    background-color: rgb(20,20,20);\n}\nQPushButton#toolButton:pressed {\n    background-color: rgb(0,0,0);\n}\nQPushButton#toolButton:hover {\n    background-color: rgb(0,0,0);\n}\nQPushButton#copyButton, QPushButton#helpButton {\n    min-width: 25px;\n    color: rgb(30,30,30);\n    background-color: transparent;\n}\nQPushButton#copyButton:hover {\n    color: rgb(200,200,200);\n    background-color: rgb(180,80,80);\n}\nQPushButton#helpButton[check=true] {\n    color: rgb(255,160,100);\n}\nQPushButton#helpButton:hover[check=true] {\n    color: rgb(200,200,200);\n    background-color: rgb(180,80,80);\n}\n'

def getMayaMainWindow():
    u"""獲取 maya 主要框架名稱"""
    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtWidgets.QMainWindow)


def thDoUndo(func):
    u"""裝飾器: 設置函數執行的開始與結束"""

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        ret = func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)
        return ret

    return wrapper


class ThCtrlStyleListData(object):
    ctrlStyleList = [
     [
      '圓環', 'circle'],
     [
      '球體', 'ball'],
     [
      '平方體', 'square'],
     [
      '立方體', 'cube'],
     [
      '三角形', 'triangle'],
     [
      '六角形', 'hexagon'],
     [
      '手柄', 'handles'],
     [
      '十字體', 'x'],
     [
      '菱形體', 'cones'],
     [
      '指向性(四向, 箭頭)', 'arrow'],
     [
      '指向性(四向, 三角形)', 'angle1'],
     [
      '指向性(四向, 梯形)', 'angle2'],
     [
      '指向性(四向, 正方形)', 'angle3'],
     [
      'Locator', 'locator'],
     [
      'Joint', 'joint']]


class ThQFrameGrp(QtWidgets.QFrame):

    def __init__(self):
        super(ThQFrameGrp, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setObjectName('frameGrp')


class ThQProgressBar(QtWidgets.QDialog):

    def __init__(self, size):
        global TOP_STYLE_SHEET
        super(ThQProgressBar, self).__init__(parent=getMayaMainWindow())
        self.setWindowTitle('Progress')
        width = 15
        for i in range(size):
            width += 20

        self.resize(500, width)
        self.setStyleSheet(TOP_STYLE_SHEET)
        self.layout1 = QtWidgets.QVBoxLayout()
        self.layout1.setMargin(10)
        self.layout1.setSpacing(2)
        self.setLayout(self.layout1)
        self.progressList = []
        self.addProgress(size)
        self.show()
        QtWidgets.QApplication.processEvents()

    def addProgress(self, size):
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(6)
        self.layout1.addLayout(layout2)
        for i in range(size):
            fIndex += 1
            label = QtWidgets.QLabel()
            layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
            progressBar = QtWidgets.QProgressBar()
            progressBar.setValue(0)
            layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, progressBar)
            self.progressList.append([label, progressBar])

    def setStrat(self, index, label, max):
        if label:
            self.progressList[index][0].setText(('{}: ').format(label))
        self.progressList[index][1].setMaximum(max)
        QtWidgets.QApplication.processEvents()

    def setFrame(self, index, label=None):
        if label:
            self.progressList[index][0].setText(('{}: ').format(label))
        value = self.progressList[index][1].value() + 1
        self.progressList[index][1].setValue(value)
        if value > self.progressList[index][1].maximum():
            if index != 0:
                self.progressList[index][1].setValue(1)
        QtWidgets.QApplication.processEvents()

    def deleteLater(self):
        time.sleep(0.2)
        super(ThQProgressBar, self).deleteLater()


class ThSeparationLine(QtWidgets.QFrame):
    """分隔線"""

    def __init__(self, mode, lineWidth=1, midLineWidth=0):
        super(ThSeparationLine, self).__init__()
        modeDict = {'V': QtWidgets.QFrame.VLine, 
           'H': QtWidgets.QFrame.HLine}
        self.setFrameShape(modeDict[mode])
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setLineWidth(lineWidth)
        self.setMidLineWidth(midLineWidth)
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor(100, 100, 100))
        self.setPalette(pal)


class ThQFontComboBox(QtWidgets.QFontComboBox):

    def __init__(self):
        super(ThQFontComboBox, self).__init__()

    def wheelEvent(self, event):
        event.ignore()


class ThQListWidget(QtWidgets.QListWidget):

    def __init__(self):
        super(ThQListWidget, self).__init__()

    def wheelEvent(self, event):
        event.ignore()


class ThQDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """Float Box"""

    def __init__(self, value_=None, min_=-999999, max_=999999, ecimals=2):
        super(ThQDoubleSpinBox, self).__init__()
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setRange(min_, max_)
        self.setDecimals(ecimals)
        if value_:
            self.setValue(value_)

    def wheelEvent(self, event):
        event.ignore()


class ThQSpinBox(QtWidgets.QSpinBox):
    """Int Box"""

    def __init__(self, value_=None, min_=-999999, max_=999999):
        super(ThQSpinBox, self).__init__()
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setRange(min_, max_)
        if value_:
            self.setValue(value_)

    def wheelEvent(self, event):
        event.ignore()


class ThQComboBox(QtWidgets.QComboBox):
    """菜單欄"""

    def __init__(self, maxVisibleItems=30):
        super(ThQComboBox, self).__init__()
        self.setMaxVisibleItems(maxVisibleItems)
        self.setView(QtWidgets.QListView())

    def setInputMaxWidth(self):
        width = self.minimumSizeHint().width()
        self.view().setMinimumWidth(width)

    def wheelEvent(self, event):
        event.ignore()


class ThQSlider(QtWidgets.QSlider):
    """拉霸"""

    def wheelEvent(self, event):
        event.ignore()


class ThQTimeRangeBox(QtWidgets.QWidget):
    """時間範圍"""

    def __init__(self):
        super(ThQTimeRangeBox, self).__init__()
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        self.stratTime = ThQSpinBox(value_=1)
        layout1.addWidget(self.stratTime)
        self.endTime = ThQSpinBox(value_=24)
        layout1.addWidget(self.endTime)
        line = ThSeparationLine('V')
        layout1.addWidget(line)
        self.inputButton = QtWidgets.QPushButton('<')
        self.inputButton.setStyleSheet('min-width: 20px;max-width: 20px;')
        self.inputButton.clicked.connect(self.setData)
        layout1.addWidget(self.inputButton)

    def setData(self):
        start = int(cmds.playbackOptions(q=True, min=True))
        end = int(cmds.playbackOptions(q=True, max=True))
        self.stratTime.setValue(start)
        self.endTime.setValue(end)

    def getData(self):
        start = self.stratTime.value()
        end = self.endTime.value()
        return [start, end]


class ThQLineBox(QtWidgets.QWidget):
    """物件部件"""

    def __init__(self, ifShowHideButton=True, ifEnabled=False, ifShowSelectButton=True):
        super(ThQLineBox, self).__init__()
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        self.dataList = []
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setStyleSheet('color: rgb(200,200,200);')
        self.lineEdit.setEnabled(ifEnabled)
        layout1.addWidget(self.lineEdit)
        if ifShowHideButton:
            line = ThSeparationLine('V')
            layout1.addWidget(line)
            button = QtWidgets.QPushButton('H')
            button.setStyleSheet('min-width: 20px;max-width: 20px;')
            button.clicked.connect(self.hideObject)
            layout1.addWidget(button)
            button = QtWidgets.QPushButton('S')
            button.setStyleSheet('min-width: 20px;max-width: 20px;')
            button.clicked.connect(self.showObject)
            layout1.addWidget(button)
        if ifShowSelectButton:
            line = ThSeparationLine('V')
            layout1.addWidget(line)
            button = QtWidgets.QPushButton('選')
            button.setStyleSheet('min-width: 20px;max-width: 20px;')
            button.clicked.connect(self.select)
            layout1.addWidget(button)
        line = ThSeparationLine('V')
        layout1.addWidget(line)
        self.inputButton = QtWidgets.QPushButton('<')
        self.inputButton.setStyleSheet('min-width: 20px;max-width: 20px;')
        self.inputButton.clicked.connect(lambda : self.setData())
        layout1.addWidget(self.inputButton)

    def setData(self, data=None):
        if data is None:
            selectList = cmds.ls(sl=True, fl=True)
            data = selectList[0] if selectList else ''
        self.lineEdit.setText(data)
        return

    def getData(self):
        return self.lineEdit.text()

    def select(self):
        cmds.select(self.lineEdit.text(), r=True)

    def showObject(self):
        cmds.showHidden(self.lineEdit.text())

    def hideObject(self):
        cmds.hide(self.lineEdit.text())


class ThQLineBoxList(ThQLineBox):
    """列表部件"""

    def __init__(self, ifShowHideButton=True, ifEnabled=False, ifShowSelectButton=True, flatten=False):
        super(ThQLineBoxList, self).__init__(ifShowHideButton, ifEnabled, ifShowSelectButton)
        self.flatten = flatten
        self.inputButton.setText('<<')

    def setData(self, data=None):
        appLs = {True: 'cmds.ls(sl=True, fl=True)', False: 'cmds.ls(sl=True)'}
        self.dataList = eval(appLs[self.flatten]) if data is None else data
        self.lineEdit.setText(str(len(self.dataList)))
        return

    def getData(self):
        return self.dataList

    def select(self):
        cmds.select(self.dataList, r=True)

    def showObject(self):
        cmds.showHidden(self.dataList)

    def hideObject(self):
        cmds.hide(self.dataList)


class ThQLineBoxAttr(ThQLineBox):
    """屬性"""

    def __init__(self, ifEnabled=True):
        super(ThQLineBoxAttr, self).__init__(ifShowHideButton=False, ifEnabled=ifEnabled, ifShowSelectButton=False)
        self.inputButton.setText(':')

    def setData(self, data=None):
        if data is None:
            attrs = cmds.channelBox('mainChannelBox', q=True, sma=True)
            data = attrs[0] if attrs else ''
        self.lineEdit.setText(data)
        return


class ThQLineBoxAttrList(ThQLineBox):
    """屬性列表"""

    def __init__(self, ifEnabled=True):
        super(ThQLineBoxAttrList, self).__init__(ifShowHideButton=False, ifEnabled=ifEnabled, ifShowSelectButton=False)
        self.inputButton.setText('::')

    def setData(self, data=None):
        if data is None:
            attrs = cmds.channelBox('mainChannelBox', q=True, sma=True)
            data = attrs if attrs else []
        self.lineEdit.setText((', ').join(data) if data else '')
        return

    def getData(self):
        return self.lineEdit.text().split(', ')


class ThQLineBoxObjAttr(ThQLineBox):
    """控制器與屬性"""

    def __init__(self, ifEnabled=False):
        super(ThQLineBoxObjAttr, self).__init__(ifShowHideButton=False, ifEnabled=ifEnabled)
        self.inputButton.setText('<:')

    def setData(self, data=None):
        if data:
            self.data = data
        else:
            selectList = cmds.ls(sl=True)
            attrs = cmds.channelBox('mainChannelBox', q=True, sma=True)
            if attrs and selectList:
                self.data = selectList[0] + '.' + attrs[0]
            else:
                self.data = ''
        self.lineEdit.setText(self.data)

    def select(self):
        if self.data:
            cmds.select(self.data.split('.')[0], r=True)


class ThQLineBoxObjAttrList(ThQLineBox):
    """控制器列表與屬性"""

    def __init__(self, ifEnabled=False):
        super(ThQLineBoxObjAttrList, self).__init__(ifShowHideButton=False, ifEnabled=ifEnabled)
        self.inputButton.setText('<<:')

    def setData(self, data=None):
        if data:
            self.dataList = data
        else:
            selectList = cmds.ls(sl=True)
            attrs = cmds.channelBox('mainChannelBox', q=True, sma=True)
            if attrs and selectList:
                self.dataList = [ ('{}.{}').format(n, attrs[0]) for n in selectList ]
                self.lineEdit.setText(str(len(self.dataList)))
            else:
                self.dataList = []
                self.lineEdit.setText('0')

    def select(self):
        if self.dataList:
            cmds.select([ n.split('.')[0] for n in self.dataList ], r=True)

    def getData(self):
        return self.dataList


class ThQCheckBox(QtWidgets.QWidget):
    """確認部件"""

    def __init__(self, labelList, isCheckList, layoutMode='V'):
        super(ThQCheckBox, self).__init__()
        layoutModeDict = {'V': QtWidgets.QVBoxLayout, 'H': QtWidgets.QHBoxLayout}
        layout1 = layoutModeDict[layoutMode]()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        self.checkBoxList = []
        for i, n in enumerate(labelList):
            checkBox = QtWidgets.QCheckBox(n)
            self.checkBoxList.append(checkBox)
            checkBox.setChecked(isCheckList[i])
            layout1.addWidget(checkBox)

    def isCheckedList(self):
        list_ = []
        for n in self.checkBoxList:
            list_.append(n.isChecked())

        return list_

    def isCheckedIdList(self):
        list_ = []
        for i, n in enumerate(self.checkBoxList):
            if n.isChecked():
                list_.append(i)

        return list_


class ThQRadioButtonBox(QtWidgets.QWidget):
    """選單部件"""

    def __init__(self, nameList, index, layoutMode='V'):
        super(ThQRadioButtonBox, self).__init__()
        layoutModeDict = {'V': QtWidgets.QVBoxLayout, 'H': QtWidgets.QHBoxLayout}
        layout1 = layoutModeDict[layoutMode]()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        self.radioButtonList = []
        self.bg = QtWidgets.QButtonGroup()
        for i, n in enumerate(nameList):
            radioButton = QtWidgets.QRadioButton(n)
            self.radioButtonList.append(radioButton)
            layout1.addWidget(radioButton)
            self.bg.addButton(radioButton, i)

        self.radioButtonList[index].setChecked(True)

    def isCheckedId(self):
        return self.bg.checkedId()


class ThQToolBoxTopBtn(QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):
        super(ThQToolBoxTopBtn, self).__init__(*args, **kwargs)
        self.setObjectName('toolButton')
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout1.addItem(spacerItem)
        self.copyWidgetButton = QtWidgets.QPushButton('+')
        self.copyWidgetButton.setObjectName('copyButton')
        layout1.addWidget(self.copyWidgetButton)
        self.helpCheck = False
        self.helpWidgetList = []
        self.help = QtWidgets.QPushButton('?')
        self.help.setObjectName('helpButton')
        self.help.setProperty('check', False)
        self.help.clicked.connect(self.setHiddenHelpText)
        layout1.addWidget(self.help)

    def copyUi(self, func, ifSpacerItem=True):
        self.copyWidgetButton.clicked.connect(lambda : QMainWindowInWidget(func, ifSpacerItem))

    def addHelpText(self, text):
        self.help.setProperty('check', True)
        self.helpWidgetList.append(text)
        text.hide()

    def setHiddenHelpText(self):
        if not self.helpWidgetList:
            return
        if self.helpCheck:
            for widget in self.helpWidgetList:
                widget.hide()

            self.helpCheck = False
        else:
            for widget in self.helpWidgetList:
                widget.show()

            self.helpCheck = True


class ThQWToolBox(QtWidgets.QWidget):
    """Tool box"""

    def __init__(self, label='', check=False):
        super(ThQWToolBox, self).__init__()
        self.check = check
        self.layout = None
        layoutMain = QtWidgets.QVBoxLayout()
        layoutMain.setMargin(0)
        layoutMain.setSpacing(0)
        self.setLayout(layoutMain)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(0)
        layoutMain.addLayout(layout1)
        self.topBotton = ThQToolBoxTopBtn(' ' + label)
        self.topBotton.setProperty('check', self.check)
        self.topBotton.clicked.connect(lambda : self.switchWidget())
        layout1.addWidget(self.topBotton)
        self.widget = QtWidgets.QWidget()
        layoutMain.addWidget(self.widget)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(2, 6, 2, 6)
        self.layout.setSpacing(6)
        self.widget.setLayout(self.layout)
        if not self.check:
            self.widget.hide()
        return

    def switchWidget(self, check=None):
        u"""切換控件收合狀態"""
        check = not check if check is not None else self.check
        if check:
            self.widget.hide()
            self.check = False
        else:
            self.widget.show()
            self.check = True
        return


class ThQWToolBoxSetClassAttr(ThQWToolBox):

    def __init__(self, parent=None, check=False, goCls=None, toCls=None, clsAttr=None, eFilename=None, label='', helpText=''):
        super(ThQWToolBoxSetClassAttr, self).__init__(label=label, check=check)
        self.goCls = goCls
        self.toCls = toCls
        self.clsAttr = clsAttr
        self.eFilename = eFilename
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        if helpText:
            label = QtWidgets.QLabel(helpText)
            label.setObjectName('annotation')
            self.topBotton.addHelpText(label)
            layout1.addWidget(label)
        self.textWidget = QtWidgets.QPlainTextEdit()
        self.textWidget.setReadOnly(False)
        layout1.addWidget(self.textWidget)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('回復到預設')
        button.clicked.connect(self.resetF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('回復到最後編輯')
        button.clicked.connect(self.reNowF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('讀檔')
        button.clicked.connect(self.openF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('存檔')
        button.clicked.connect(self.saveF)
        layout2.addWidget(button)
        self.buttonApp = QtWidgets.QPushButton('應用')
        self.buttonApp.clicked.connect(self.applyF)
        layout2.addWidget(self.buttonApp)
        self.reNowF()

    def reNowF(self):
        try:
            text = getattr(self.toCls, self.clsAttr)
            self.textWidget.setPlainText(pprint.pformat(text))
        except:
            cmds.warning('獲取資料發生錯誤!')

    def openF(self):
        fileList = cmds.fileDialog2(startingDirectory=cmds.file(q=True, sn=True) or 'D:/', fileFilter=('Mocap label (*.{})').format(self.eFilename), fm=1)
        if not fileList:
            return
        else:
            data = None
            with open(fileList[0], 'r') as (file):
                data = file.read()
            self.textWidget.setPlainText(data)
            sys.stdout.write('讀取完成，確認資料無誤，再執行應用!')
            return

    def saveF(self):
        data = self._getDataF()
        if data is None:
            return
        else:
            fileList = cmds.fileDialog2(startingDirectory=cmds.file(q=True, sn=True) or 'D:/', fileFilter=('Mocap label (*.{});;All Files (*.*)').format(self.eFilename), dialogStyle=2)
            if not fileList:
                return
            with open(fileList[0], 'w') as (file):
                file.write(pprint.pformat(data))
            sys.stdout.write('存檔完成!')
            return

    def _getDataF(self):
        data = None
        try:
            data = eval(self.textWidget.toPlainText())
        except:
            cmds.warning('語法錯誤!')

        return data

    def applyF(self):
        data = self._getDataF()
        if data is None:
            return
        else:
            setattr(self.toCls, self.clsAttr, data)
            sys.stdout.write('執行完成!')
            return

    def resetF(self):
        try:
            text = getattr(self.goCls, self.clsAttr)
            self.textWidget.setPlainText(pprint.pformat(text))
        except:
            cmds.warning('獲取資料發生錯誤!')


class ThCreateFaceCtrlDataE(ThQWToolBoxSetClassAttr):

    def __init__(self, parent=None, check=False):
        super(ThCreateFaceCtrlDataE, self).__init__(parent=parent, check=check, goCls=ThCreateFaceCtrlData, toCls=ThCreateFaceCtrl, clsAttr='data', eFilename='mayaFile', label='Edit face data', helpText=None)
        return


class ThRigToolsQtWin(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    """主要視窗"""

    def __init__(self, parent=None):
        super(ThRigToolsQtWin, self).__init__(parent)
        self.setMinimumSize(290, 500)
        self.commonWidgetList = []
        self.weightWidgetList = []
        self.ctrlWidgetList = []
        self.dynamicWidgetList = []
        self.setWindowTitle('TH RIG Tools')
        widget1 = QtWidgets.QWidget()
        widget1.setObjectName('mainWidget1')
        self.setCentralWidget(widget1)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        widget1.setLayout(layout1)
        self.topButtonF(layout1)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setObjectName('mainScrollArea')
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        layout1.addWidget(scrollArea)
        widget2 = QtWidgets.QWidget()
        widget2.setObjectName('mainWidget2')
        scrollArea.setWidget(widget2)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.setMargin(2)
        layout2.setSpacing(2)
        widget2.setLayout(layout2)
        self.commonModeF(layout2)
        self.skinModeF(layout2)
        self.ctrlModeF(layout2)
        self.dynamicModeF(layout2)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout2.addItem(spacerItem)
        self.allWidgetList = [
         self.commonWidgetList,
         self.weightWidgetList,
         self.ctrlWidgetList,
         self.dynamicWidgetList]
        self.isAllWidgetList = [ nn for n in self.allWidgetList for nn in n ]
        self.foldButtonDefDataF()
        self.startModeF(self.modeButtonList[0])
        self.setStyleSheet(TOP_STYLE_SHEET)
        self.setDockableParameters(width=300, dockable=True, area='right', allowedArea='right', floating=False)
        self.show()

    def showEvent(self, e):
        super(ThRigToolsQtWin, self).showEvent(e)

    def floatingChanged(self, isFloating):
        super(ThRigToolsQtWin, self).floatingChanged(isFloating)

    def topButtonF(self, layout):
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        layout.addLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.foldButtonSwitch = True
        self.foldButtonData = []
        self.foldButton = QtWidgets.QPushButton('切換控件')
        self.foldButton.setObjectName('foldButton')
        self.foldButton.clicked.connect(self.setFoldButtonSwitchF)
        layout2.addWidget(self.foldButton)
        self.foldButtonDef = QtWidgets.QPushButton('關閉控件')
        self.foldButtonDef.setObjectName('foldButton')
        self.foldButtonDef.clicked.connect(self.setFoldButtonDefF)
        layout2.addWidget(self.foldButtonDef)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.modeButtonList = []
        self.isModeButton = None
        nameList = ['通用', '骨骼', '控制器', '動畫']
        for n in nameList:
            button = QtWidgets.QPushButton(n)
            button.setObjectName('modeButton')
            button.clicked.connect(partial(self.switchModeF, button))
            self.modeButtonList.append(button)
            layout2.addWidget(button)

        return

    def foldButtonDefDataF(self):
        self.foldButtonDefData = []
        for n in self.isAllWidgetList:
            self.foldButtonDefData.append(n.check)

    def setFoldButtonDefF(self):
        for i, n in enumerate(self.isAllWidgetList):
            n.switchWidget(self.foldButtonDefData[i])

    def setFoldButtonSwitchF(self):
        u"""關閉控件"""
        if self.foldButtonSwitch:
            self.foldButton.setProperty('check', True)
            self.foldButton.setText('<< 切換控件 >>')
            self.foldButtonSwitch = False
            self.foldButtonData = []
            for n in self.isAllWidgetList:
                self.foldButtonData.append(n.check)
                n.switchWidget(False)

        else:
            self.foldButton.setProperty('check', False)
            self.foldButton.setText('切換控件')
            self.foldButtonSwitch = True
            for i, n in enumerate(self.isAllWidgetList):
                n.switchWidget(self.foldButtonData[i])

        self.foldButton.setStyle(self.foldButton.style())

    def startModeF(self, button):
        u"""初始化"""
        button.setProperty('check', True)
        button.setStyle(button.style())
        self.isModeButton = button
        for i, n in enumerate(self.modeButtonList):
            if n is button:
                for nn in self.allWidgetList[i]:
                    nn.show()

            else:
                for nn in self.allWidgetList[i]:
                    nn.hide()

    def switchModeF(self, button):
        u"""功能模組切換"""
        if self.isModeButton is button:
            return
        button.setProperty('check', True)
        button.setStyle(button.style())
        self.isModeButton.setProperty('check', False)
        self.isModeButton.setStyle(self.isModeButton.style())
        self.isModeButton = button
        for i, n in enumerate(self.modeButtonList):
            if n is button:
                for nn in self.allWidgetList[i]:
                    nn.show()

            else:
                for nn in self.allWidgetList[i]:
                    nn.hide()

    def commonModeF(self, layout):
        self.commonWidgetList.append(ThQWToolBoxAuthorInformation(layout, False))
        self.commonWidgetList.append(ThQWToolBoxCommonBox(layout, True))
        self.commonWidgetList.append(ThQWToolBoxSelectSet(layout, True))
        self.commonWidgetList.append(ThQWToolBoxSelectType(layout, False))
        self.commonWidgetList.append(ThQWToolBoxRename(layout, False))
        self.commonWidgetList.append(ThQWToolBoxNamespaceSelect(layout, False))
        self.commonWidgetList.append(ThQWToolBoxSelectIndex(layout, False))
        self.commonWidgetList.append(ThQWToolBoxMirrorTransform(layout, False))
        self.commonWidgetList.append(ThQWToolBoxListTool(layout, False))
        self.commonWidgetList.append(ThQWToolBoxListToList(layout, False))
        self.commonWidgetList.append(ThQWToolBoxRand(layout, False))
        self.commonWidgetList.append(ThQWToolBoxFilePath(layout, False))

    def skinModeF(self, layout):
        self.weightWidgetList.append(ThQWToolBoxCommonSkinTools(layout, True))
        self.weightWidgetList.append(ThQWToolBoxSkinJoint(layout, True))
        self.weightWidgetList.append(ThQWToolBoxCopyWeight(layout, True))
        self.weightWidgetList.append(ThQWToolBoxSkinWeight(layout, True))
        self.weightWidgetList.append(ThQWToolBoxSoftToSkinWeight(layout, False))
        self.weightWidgetList.append(ThQWToolBoxSmoothWeight(layout, False))
        self.weightWidgetList.append(ThQWToolBoxEditSelectJointSkinWeight(layout, False))
        self.weightWidgetList.append(ThQWToolBoxDefToSkin(layout, False))
        self.weightWidgetList.append(ThQWToolBoxExportSkinWeight(layout, False))
        self.weightWidgetList.append(ThQWToolBoxTransferSkinWeight(layout, False))
        self.weightWidgetList.append(ThQWToolBoxEditJoint(layout, False))
        self.weightWidgetList.append(ThQWToolBoxWeightSpecification(layout, False))

    def ctrlModeF(self, layout):
        self.ctrlWidgetList.append(ThQWToolBoxEditCtrl(layout, True))
        self.ctrlWidgetList.append(ThQWToolBoxRotateOrder(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxLimitInformation(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxCtrlToObject(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxObjToCtrl(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxIkElasticity(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxWeightToCtrl(layout, False))
        self.ctrlWidgetList.append(ThQWToolUiCtrl(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxHelpTxt(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxEditBlendShape(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxCtrlBlendShape(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxPtInpObjChangeEx(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxLoopValueRangeLimit(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxExtrudeJoint(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxAffectSystem(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxDrivenKeySys(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxAnimToDrivenKey(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxDefSoft(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxAimCtrl(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxSequentialStart(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxMouthRig(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxReelRig(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxObjectCurve(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxCurveJoint(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxFollowCvLoc(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxWheel(layout, False))
        self.ctrlWidgetList.append(ThQWToolBoxFollowOffset(layout, False))

    def dynamicModeF(self, layout):
        self.dynamicWidgetList.append(ThQWToolBoxDynCommon(layout, True))
        self.dynamicWidgetList.append(ThQWToolBoxAlignAndKey(layout, True))
        self.dynamicWidgetList.append(ThQWToolBoxTimeFrameConvert(layout, True))
        self.dynamicWidgetList.append(ThQWToolBoxSolverDisplay(layout, True))
        self.dynamicWidgetList.append(ThQWToolBoxFields(layout, False))
        self.dynamicWidgetList.append(ThQWToolBoxDynCtrl(layout, False))
        self.dynamicWidgetList.append(ThQWToolBoxDynamicsOutliner(layout, False))
        self.dynamicWidgetList.append(ThQWToolBoxSmoothAnimCv(layout, False))
        self.dynamicWidgetList.append(ThQWToolBoxShootAttrAnim(layout, False))


class QMainWindowInWidget(QtWidgets.QMainWindow):
    """顯示獨立小部件"""

    def __init__(self, toolBox, ifSpacerItem=True):
        super(QMainWindowInWidget, self).__init__(parent=getMayaMainWindow())
        self.toolBox = toolBox
        self.setWindowTitle('Window')
        self.setObjectName('mainWindow')
        self.setMinimumSize(290, 30)
        widget1 = QtWidgets.QWidget()
        self.setCentralWidget(widget1)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        widget1.setLayout(layout1)
        if ifSpacerItem:
            scrollArea = QtWidgets.QScrollArea()
            scrollArea.setObjectName('mainScrollArea')
            scrollArea.setWidgetResizable(True)
            scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            layout1.addWidget(scrollArea)
        self.widget2 = QtWidgets.QWidget()
        self.widget2.setObjectName('mainWidget2')
        if ifSpacerItem:
            scrollArea.setWidget(self.widget2)
        else:
            layout1.addWidget(self.widget2)
        self.layout2 = QtWidgets.QVBoxLayout()
        self.layout2.setMargin(2)
        self.layout2.setSpacing(2)
        self.widget2.setLayout(self.layout2)
        self.toolBox = toolBox(self.layout2, True)
        self.toolBox.topBotton.clicked.connect(self.setSize)
        if ifSpacerItem:
            spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.layout2.addItem(spacerItem)
        self.setStyleSheet(TOP_STYLE_SHEET)
        self.setSize()
        self.show()

    def setSize(self):
        heightData = self.widget2.sizeHint().height() + 4
        heightData = heightData if self.toolBox.check else 35
        screenShape = QtWidgets.QDesktopWidget().screenGeometry().height()
        minScreenShape = screenShape - 200
        heightData = minScreenShape if heightData > minScreenShape else heightData
        self.resize(290, heightData)


class ThQWToolBoxCommonBox(ThQWToolBox):

    def __init__(self, parent=None, check=True):
        super(ThQWToolBoxCommonBox, self).__init__(label='通用工具集', check=check)
        self.topBotton.copyUi(ThQWToolBoxCommonBox)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('對位')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('移動')
        layout1.addWidget(button)
        button.clicked.connect(lambda : self.adsorption('t'))
        button = QtWidgets.QPushButton('旋轉')
        layout1.addWidget(button)
        button.clicked.connect(lambda : self.adsorption('r'))
        button = QtWidgets.QPushButton('移動 + 旋轉')
        layout1.addWidget(button)
        button.clicked.connect(lambda : self.adsorption('tr'))
        button = QtWidgets.QPushButton('頂點')
        layout1.addWidget(button)
        button.clicked.connect(lambda : self.adsorption('vertex'))
        grpBox = QtWidgets.QGroupBox('編輯變換節點')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('center pivot')
        button.clicked.connect(self.centerPivot)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('freeze')
        button.clicked.connect(self.makeIdentity)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('delete history')
        button.clicked.connect(self.deleteHistory)
        layout2.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('顯示/ 隱藏物件軸向')
        button.clicked.connect(self.localRotationAxes)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('顯示/ 隱藏優先選擇手柄')
        button.clicked.connect(self.selectionHandles)
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('批量建立父子關係')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 層級數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.spinBox = ThQSpinBox()
        layout3.addWidget(self.spinBox)
        line = ThSeparationLine('V')
        layout3.addWidget(line)
        self.checkBoxReverseList = QtWidgets.QCheckBox('反向')
        self.checkBoxReverseList.setChecked(False)
        layout3.addWidget(self.checkBoxReverseList)
        line = ThSeparationLine('V')
        layout3.addWidget(line)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.parentList)
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('交互切換顯示/ 隱藏')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表一: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.listWidget1 = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.listWidget1)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表二: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.listWidget2 = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.listWidget2)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('顯示全部')
        button.clicked.connect(self.twoListShow)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('隱藏全部')
        button.clicked.connect(self.twoListHide)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('切換')
        button.clicked.connect(self.twoListSwitch)
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('工具集')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2, 70)
        self.funcList = []
        self.setFuncList()
        self.funcComboBox1 = ThQComboBox()
        self.funcComboBox1.activated.connect(self.setFuncListButton)
        for labelButtonFunc in self.funcList:
            self.funcComboBox1.addItem(labelButtonFunc[0])

        self.funcComboBox1.setInputMaxWidth()
        layout2.addWidget(self.funcComboBox1)
        self.funcComboBox2 = ThQComboBox()
        layout2.addWidget(self.funcComboBox2)
        self.setFuncListButton()
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.appFuncListOpen)
        layout1.addWidget(button, 15)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        line = ThSeparationLine('V')
        layout1.addWidget(line)
        self.funcListWidgetBool = False
        self.funcButton = QtWidgets.QPushButton('展開\n列表')
        layout1.addWidget(self.funcButton, 15)
        self.funcButton.setSizePolicy(sizePolicy)
        self.funcButton.clicked.connect(self.showFuncList)
        self.funcListWidget = QtWidgets.QWidget()
        self.layout.addWidget(self.funcListWidget)
        self.funcLayout = QtWidgets.QVBoxLayout()
        self.funcLayout.setMargin(0)
        self.funcLayout.setSpacing(6)
        self.funcListWidget.setLayout(self.funcLayout)
        line = ThSeparationLine('H')
        self.funcLayout.addWidget(line)
        self._setFuncListOpen()
        self.funcListWidget.hide()

    @thDoUndo
    def parentList(self):
        thGrpParent(cmds.ls(sl=True), self.checkBoxReverseList.isChecked(), self.spinBox.value())

    @thDoUndo
    def twoListShow(self):
        allList = self.listWidget1.getData() + self.listWidget2.getData()
        for n in allList:
            try:
                cmds.showHidden(n)
            except:
                pass

    @thDoUndo
    def twoListHide(self):
        allList = self.listWidget1.getData() + self.listWidget2.getData()
        for n in allList:
            try:
                cmds.hide(n)
            except:
                pass

    @thDoUndo
    def twoListSwitch(self):
        listData1 = cmds.getAttr(self.listWidget1.getData()[0] + '.v')
        for i in range(len(self.listWidget1.getData())):
            try:
                cmds.setAttr(self.listWidget1.getData()[i] + '.v', not listData1)
            except:
                pass

        for i in range(len(self.listWidget2.getData())):
            try:
                cmds.setAttr(self.listWidget2.getData()[i] + '.v', listData1)
            except:
                pass

    def _setFuncListOpen(self):
        for label in self.funcList:
            grpBox = QtWidgets.QGroupBox(label[0])
            self.funcLayout.addWidget(grpBox)
            layout1 = QtWidgets.QVBoxLayout()
            layout1.setMargin(2)
            layout1.setSpacing(2)
            grpBox.setLayout(layout1)
            for button in label[1]:
                foncButton = QtWidgets.QPushButton(' ' + button[0])
                foncButton.setStyleSheet('text-align: left;min-width: 200px;')
                layout1.addWidget(foncButton)
                foncButton.clicked.connect(thDoUndo(lambda s=button[1]: eval(s)))

    @thDoUndo
    def appFuncListOpen(self):
        index1 = self.funcComboBox1.currentIndex()
        index2 = self.funcComboBox2.currentIndex()
        eval(self.funcList[index1][1][index2][1])

    def showFuncList(self):
        if self.funcListWidgetBool:
            self.funcListWidget.hide()
            self.funcButton.setText('展開\n列表')
            self.funcListWidgetBool = False
        else:
            self.funcListWidget.show()
            self.funcButton.setText('收合\n列表')
            self.funcListWidgetBool = True

    @thDoUndo
    def adsorption(self, mode):
        selectList = cmds.ls(sl=True)
        AdsorptionObj(selectList[:-1], selectList[(-1)], mode)

    def centerPivot(self):
        cmds.xform(cp=True)

    def makeIdentity(self):
        cmds.makeIdentity(apply=1, t=1, r=1, s=1)

    def deleteHistory(self):
        cmds.delete(ch=True)

    def localRotationAxes(self):
        ThTransformDisplay(cmds.ls(sl=True), 'axes')

    def selectionHandles(self):
        ThTransformDisplay(cmds.ls(sl=True), 'handles')

    def setFuncList(self):
        self.funcList = [
         [
          '一般功能',
          [
           [
            '頂點數值傳遞 — (先選擇參考物件，後選擇要修改的物件)', 'ThSetMeshPoint().apply(cmds.ls(sl=True)[0],cmds.ls(sl=True)[1])'],
           [
            '(Undo)頂點數值傳遞 — (直接執行)', 'ThSetMeshPoint().resetCoordinate()'],
           [
            '關閉所有 blendShape 編輯狀態 — (直接執行)', 'ThEditBlendShape().offEditF()'],
           [
            '屬性數值傳遞 — (先選擇參考物件，後選擇要修改的物件)', 'ThSetListAttrDataToSelect()'],
           [
            '軸心至中 — (選擇物件執行)', 'thPivotToWorld(cmds.ls(sl=True))'],
           [
            '軸心吸附 — (最後加選參考物件)', 'thEditPivot(cmds.ls(sl=True)[:-1],cmds.ls(sl=True)[-1])'],
           [
            '軸心吸附並受約束 — (最後加選參考物件)', 'thAdsorptionAndConstrain(cmds.ls(sl=True))'],
           [
            '反轉選擇順序', 'cmds.select(cmds.ls(sl=True)[::-1])'],
           [
            '篩選頂點數量, 顏色相同的 curve — (最後加選參考物件)', 'ThSelectIsTypeCtrl(cmds.ls(sl=True)[:-1],cmds.ls(sl=True)[-1])'],
           [
            '篩選頂點數量相同的 mesh — (最後加選參考物件)', 'cmds.select(thFindVtxSame(cmds.ls(sl=True)),r=True)'],
           [
            '複製並對齊 — (最後加選參考物件)', 'thCopyAndAlign(cmds.ls(sl=True)[:-1],cmds.ls(sl=True)[-1])'],
           [
            '移除命名空間 — (直接執行)', 'thDelNamespace()'],
           [
            '刪除未知節點 — (直接執行)', 'thDelUnknown()'],
           [
            '打印當前選擇物件 — (選擇物件執行)', 'thFromPythonPrintSelect()'],
           [
            '打印設定物件屬性數值 — (選擇物件執行)', 'ThPrintSetAttrData(None)'],
           [
            '打印設定物件屬性數值(移動) — (選擇物件執行)', 'ThPrintSetAttrData(["tx","ty","tz"])'],
           [
            '打印設定物件屬性數值(旋轉) — (選擇物件執行)', 'ThPrintSetAttrData(["rx","ry","rz"])'],
           [
            '選擇面向攝影機的面 — (選擇物件執行)', 'thFaceToCam(cmds.ls(sl=True)[0])'],
           [
            '刪除多餘 shape — (選擇物件執行)', 'ThClearChShapeNode(cmds.ls(sl=True))'],
           [
            '刪除多餘 shape(type=shape) — (直接執行)', 'ThClearChShapeNode()'],
           [
            '批量 reference — (選擇檔案執行)', 'ThBatchReference()'],
           [
            '交換名稱 — (選擇兩個物件執行)', 'ThRenameExchange([cmds.ls(sl=True)[0]], [cmds.ls(sl=True)[1]])']]],
         [
          '開啟檔案路徑',
          [
           [
            '打開該檔路徑', 'thOpenPath("file")'],
           [
            '打開預設路徑', 'thOpenPath("default")'],
           [
            '打開當機時文件保存的路徑', 'thOpenPath("temp")']]],
         [
          '形狀節點',
          [
           [
            '開/ 關 visibility 屬性 — (選擇物件執行)', 'thSetShapeAttr(cmds.ls(sl=True), "visibility")'],
           [
            '開/ 關 template 屬性 — (選擇物件執行)', 'thSetShapeAttr(cmds.ls(sl=True), "template")']]],
         [
          '材質',
          [
           [
            '選擇到材質球 — (選擇物件執行)', 'cmds.select(thGetMaterial(cmds.ls(sl=True)), r=True)'],
           [
            '套用最後選擇模型之材質 — (最後加選參考物件)', 'thUseSelMaterial(cmds.ls(sl=True))'],
           [
            '套用 reference 材質後刪除本地材質 — (直接執行)', 'thDeleteRepeatMaterial(print_=True)']]],
         [
          '動畫',
          [
           [
            '將 Key 模式設定為 spline — (直接執行)', 'thKeyTangentMode("spline")'],
           [
            '將 Key 模式設定為 clamped — (直接執行)', 'thKeyTangentMode("clamped")'],
           [
            '將 Key 模式設定為 linear — (直接執行)', 'thKeyTangentMode("linear")']]],
         [
          'MAYA工具',
          [
           [
            'Set driven key', 'cmds.SetDrivenKeyOptions()'],
           [
            '動畫曲線編輯器', 'cmds.GraphEditor()'],
           [
            '元件編輯器', 'cmds.ComponentEditor()'],
           [
            'blend shape 編輯器', 'cmds.ShapeEditor()'],
           [
            '材質編輯器', 'cmds.HypershadeWindow()'],
           [
            '雕刻筆刷 — (舊)', 'mel.eval("artPuttyToolScript 3")'],
           [
            '命名空間編輯器', 'mel.eval("namespaceEditor")']]]]

    def setFuncListButton(self):
        self.funcComboBox2.clear()
        index = self.funcComboBox1.currentIndex()
        for button in self.funcList[index][1]:
            self.funcComboBox2.addItem(button[0])

        self.funcComboBox2.setInputMaxWidth()


class ThQWToolBoxSelectSet(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSelectSet, self).__init__(label='列表工具/ 選擇集', check=check)
        self.topBotton.copyUi(ThQWToolBoxSelectSet)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('列表工具')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.listSlider = ThQSlider(QtCore.Qt.Horizontal)
        self.listSlider.setMinimum(100)
        self.listSlider.setMaximum(800)
        self.listSlider.valueChanged[int].connect(self.listWidgetWidthF)
        layout1.addWidget(self.listSlider)
        self.listWidget = ThQListWidget()
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setMinimumWidth(50)
        self.listWidget.setMinimumHeight(100)
        self.listWidget.itemSelectionChanged.connect(self.selectListObjF)
        self.listWidget.clicked.connect(self.selectListObjF)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.listWidget.setSizePolicy(sizePolicy)
        layout1.addWidget(self.listWidget)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.list_ = []
        button = QtWidgets.QPushButton('>')
        button.clicked.connect(lambda : self.addToListWidgetF())
        layout2.addWidget(button, 13)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('H')
        button.clicked.connect(lambda : cmds.hide(self.list_))
        layout2.addWidget(button, 13)
        button = QtWidgets.QPushButton('S')
        button.clicked.connect(lambda : cmds.showHidden(self.list_))
        layout2.addWidget(button, 13)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('回歸初始值')
        button.clicked.connect(thDoUndo(lambda : thCtrlDefaultPose(self.list_)))
        layout2.addWidget(button, 31)
        button = QtWidgets.QPushButton('刷新列表')
        button.clicked.connect(self.resetListF)
        layout2.addWidget(button, 30)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('選擇')
        button.clicked.connect(lambda : cmds.select(self.list_, r=True))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('選擇(增加)')
        button.clicked.connect(lambda : cmds.select(self.list_, add=True))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('選擇(交換)')
        button.clicked.connect(lambda : cmds.select(self.list_, tgl=True))
        layout2.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('添加列表')
        button.clicked.connect(self.addListF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('移出列表')
        button.clicked.connect(self.removeListF)
        layout2.addWidget(button)
        self.listLineEdit = QtWidgets.QLineEdit()
        self.listLineEdit.setPlaceholderText('重命名 — (按下 Enter 執行)')
        self.listLineEdit.returnPressed.connect(self.listRenameF)
        layout1.addWidget(self.listLineEdit)
        grpBox = QtWidgets.QGroupBox('選擇集')
        self.layout.addWidget(grpBox)
        self.setLayout = QtWidgets.QVBoxLayout()
        self.setLayout.setMargin(2)
        self.setLayout.setSpacing(2)
        grpBox.setLayout(self.setLayout)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        self.setLayout.addLayout(layout2)
        self.setsSystemData = {}
        self.setWidgetList = []
        self.checkBox = QtWidgets.QCheckBox('紀錄位置')
        self.checkBox.setChecked(True)
        layout2.addWidget(self.checkBox, 28)
        button = QtWidgets.QPushButton('創建')
        button.clicked.connect(self.addItemF)
        layout2.addWidget(button, 18)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('保存')
        button.clicked.connect(self.saveSetsDataF)
        layout2.addWidget(button, 18)
        button = QtWidgets.QPushButton('讀取')
        button.clicked.connect(self.getSetsDataF)
        layout2.addWidget(button, 18)
        button = QtWidgets.QPushButton('刪除')
        button.clicked.connect(self.clearSetsWidgeAllF)
        layout2.addWidget(button, 18)
        line = ThSeparationLine('H')
        self.setLayout.addWidget(line)

    def clearSetsWidgeAllF(self):
        for ui in self.setWidgetList:
            ui.deleteLater()

        del self.setsSystemData
        del self.setWidgetList
        self.setsSystemData = {}
        self.setWidgetList = []

    def getSetsDataF(self):
        if not cmds.objExists('mySetsSystem_data'):
            return
        self.clearSetsWidgeAllF()
        self.setsSystemData = eval(cmds.getAttr('mySetsSystem_data.notes'))
        for id, uiData in self.setsSystemData.items():
            self.addItemWidgetF(id, uiData[0], uiData[1])

    @thDoUndo
    def saveSetsDataF(self):
        if not cmds.objExists('mySetsSystem_data'):
            cmds.group(em=True, n='mySetsSystem_data')
            cmds.addAttr('mySetsSystem_data', sn='nts', ln='notes', dt='string')
        cmds.setAttr('mySetsSystem_data.notes', self.setsSystemData, type='string')

    def _findSetIdF(self):
        key_ = self.setsSystemData.keys()
        len_ = len(key_)
        id = len_ + 1
        for i in range(1, len_ + 1):
            if i not in key_:
                id = i
                break

        return id

    @thDoUndo
    def listRenameF(self):
        index = self.listWidget.currentRow()
        if index < 0:
            return
        newName = self.listLineEdit.text()
        newName = cmds.rename(self.list_[index], newName)
        self.list_[index] = newName
        self.addToListWidgetF(self.list_)

    def selectListObjF(self):
        selectItemList = self.listWidget.selectedItems()
        if not selectItemList:
            return
        selectItemTextList = [ item.text() for item in selectItemList ]
        cmds.select(selectItemTextList, r=True)
        self.listLineEdit.setText(selectItemTextList[0])

    def removeListF(self):
        u"""移出列表工具"""
        sel = cmds.ls(sl=True, fl=True)
        list_ = list(set(self.list_) - set(sel))
        self.addToListWidgetF(list_)

    def addListF(self):
        u"""添加列表工具"""
        sel = cmds.ls(sl=True, fl=True)
        list_ = list(set(self.list_) | set(sel))
        self.addToListWidgetF(list_)

    def resetListF(self):
        u"""更新列表工具"""
        list_ = [ n for n in self.list_ if cmds.objExists(n) ]
        self.addToListWidgetF(list_)

    def addToListWidgetF(self, list_=None):
        u"""數據到列表工具"""
        self.list_ = list_ if list_ is not None else cmds.ls(sl=True, fl=True)
        self.listWidget.clear()
        for n in self.list_:
            self.listWidget.addItem(n)

        return

    def listWidgetWidthF(self):
        u"""調整 listWidget 高度"""
        pos = self.listSlider.value()
        self.listWidget.setMinimumHeight(pos)

    def addItemF(self):
        u"""添加選擇集控件"""
        selectList = cmds.ls(sl=True, fl=True)
        if not selectList:
            return
        else:
            data = []
            ifUndo = False if [ n for n in selectList if '.' in n ] else True
            if ifUndo and self.checkBox.isChecked():
                soad = ThSaveObjsAttrData(selectList)
                soad.save()
                data = soad.data
            else:
                data = [ [n, None] for n in selectList ]
            id = self._findSetIdF()
            text = (', ').join(selectList[:5] + ['...']) if len(selectList) > 5 else (', ').join(selectList)
            self.setsSystemData[id] = [data, text]
            self.addItemWidgetF(id, data, text)
            return

    def reLabelF(self, id, ui):
        u"""更新標籤名稱"""
        self.setsSystemData[id][1] = ui.text()

    def addItemWidgetF(self, id, saveData, text):
        key_ = saveData.keys() if type(saveData) is dict else [ n[0] for n in saveData ]
        widget = QtWidgets.QWidget()
        self.setLayout.addWidget(widget)
        self.setWidgetList.append(widget)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(2)
        widget.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        listButton = QtWidgets.QPushButton(str(len(key_)))
        listButton.setStyleSheet('min-width: 45px;')
        listButton.clicked.connect(lambda : self.addToListWidgetF(key_))
        layout2.addWidget(listButton)
        lineEdit = QtWidgets.QLineEdit(text)
        lineEdit.returnPressed.connect(lambda : self.reLabelF(id, lineEdit))
        lineEdit.editingFinished.connect(lambda : self.reLabelF(id, lineEdit))
        layout2.addWidget(lineEdit)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('選')
        button.setStyleSheet('min-width: 20px;')
        button.clicked.connect(lambda : cmds.select(key_, r=True))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('+ 選')
        button.setStyleSheet('min-width: 20px;')
        button.clicked.connect(lambda : cmds.select(key_, add=True))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('H')
        button.setStyleSheet('min-width: 20px;')
        button.clicked.connect(lambda : cmds.hide(key_))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('S')
        button.setStyleSheet('min-width: 20px;')
        button.clicked.connect(lambda : cmds.showHidden(key_))
        layout2.addWidget(button)
        defaultButton = QtWidgets.QPushButton('←')
        defaultButton.setStyleSheet('min-width: 20px;')
        layout2.addWidget(defaultButton)
        saveButton = QtWidgets.QPushButton('→')
        saveButton.setStyleSheet('min-width: 20px;')
        layout2.addWidget(saveButton)
        ifUndo = True
        for n in key_:
            if '.' in n:
                ifUndo = False
                break

        if ifUndo:
            defaultButton.clicked.connect(thDoUndo(lambda : thCtrlDefaultPose(key_)))
        else:
            defaultButton.setEnabled(False)
        value_ = saveData.values() if type(saveData) is dict else [ n[1] for n in saveData ]
        ifData = False
        for v in value_:
            if v is not None:
                ifData = True
                break

        if ifData:
            saveButton.clicked.connect(thDoUndo(lambda : ThSaveObjsAttrData(data=saveData).redoSave()))
        else:
            saveButton.setEnabled(False)
        button = QtWidgets.QPushButton('刪除')
        button.setStyleSheet('min-width: 20px;')
        button.clicked.connect(lambda : self.deleteItemWidgetF(widget, id))
        layout2.addWidget(button)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        return

    def deleteItemWidgetF(self, ui, id):
        ui.deleteLater()
        self.setsSystemData.pop(id)
        self.setWidgetList.remove(ui)


class ThQWToolBoxSelectType(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSelectType, self).__init__(label='選擇指定類別物件', check=check)
        self.topBotton.copyUi(ThQWToolBoxSelectType)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.selModeList = []
        self.setSelModeList()
        self.selMode = ThQRadioButtonBox([ n[0] for n in self.selModeList ], 2, 'V')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.selMode)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇類別: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.selTypeList = []
        self.setSelTypeList()
        self.selType = ThQComboBox()
        for label in self.selTypeList:
            self.selType.addItem(label[0])

        self.selType.setInputMaxWidth()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.selType)
        fIndex += 1
        label = QtWidgets.QLabel('* "其他" 輸入框若有輸入名稱\n將會取代 "選擇類別" 選項')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, label)
        fIndex += 1
        label = QtWidgets.QLabel(' 其他:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.customType = QtWidgets.QLineEdit()
        layout3.addWidget(self.customType)
        button = QtWidgets.QPushButton('<')
        button.setStyleSheet('min-width: 20px;max-width: 20px;')
        button.clicked.connect(self.getObjType)
        layout3.addWidget(button)
        fIndex += 1
        self.ifSelUp = QtWidgets.QCheckBox('選擇到變換節點')
        self.ifSelUp.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifSelUp)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('附屬功能')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('向上選擇')
        button.clicked.connect(lambda : cmds.pickWalk(d='up'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('向下選擇')
        button.clicked.connect(lambda : cmds.pickWalk(d='down'))
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        sel = cmds.ls(sl=True)
        appType = self.selTypeList[self.selType.currentIndex()][1]
        customTypeText = self.customType.text()
        if customTypeText.strip():
            appType = customTypeText
        sto = ThSelectTypeObject(objs=sel, mode=self.selModeList[self.selMode.isCheckedId()][1], type=appType, transform=self.ifSelUp.isChecked())
        sto.selectObjsF()

    def getObjType(self):
        sel = cmds.ls(sl=True)
        if not sel:
            self.customType.setText('')
        else:
            objTypeList = thType([sel[0]])
            self.customType.setText(objTypeList[0])

    def setSelTypeList(self):
        self.selTypeList = [
         [
          'mesh', 'mesh'],
         [
          'nurbsCurve', 'nurbsCurve'],
         [
          '-' * 30, ''],
         [
          'joint', 'joint'],
         [
          'skinCluster', 'skinCluster'],
         [
          'locator', 'locator'],
         [
          'ikHandle', 'ikHandle'],
         [
          '-' * 30, ''],
         [
          'parentConstraint', 'parentConstraint'],
         [
          'pointConstraint', 'pointConstraint'],
         [
          'orientConstraint', 'orientConstraint'],
         [
          'scaleConstraint', 'scaleConstraint'],
         [
          'aimConstraint', 'aimConstraint'],
         [
          '-' * 30, ''],
         [
          'blendShape', 'blendShape'],
         [
          'cluster', 'cluster'],
         [
          'lattice', 'lattice'],
         [
          'wire', 'wire'],
         [
          'blend', 'blend'],
         [
          'nonlinear', 'nonlinear'],
         [
          'sculpt', 'sculpt'],
         [
          'expression', 'expression'],
         [
          '-' * 30, ''],
         [
          'nucleus', 'nucleus'],
         [
          'nCloth', 'nCloth'],
         [
          'hairSystem', 'hairSystem'],
         [
          '-' * 30, ''],
         [
          'animLayer', 'animLayer']]

    def setSelModeList(self):
        self.selModeList = [
         [
          '層級以下的所有物件', 'father'],
         [
          '當前選擇的物件中做塞選', 'select'],
         [
          '搜索整個場景', 'scenes']]


class ThQWToolBoxCommonSkinTools(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxCommonSkinTools, self).__init__(label='骨骼工具集', check=check)
        self.topBotton.copyUi(ThQWToolBoxCommonSkinTools)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('依據選擇骨骼創建 mesh')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.createMeshList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.createMeshList)
        fIndex += 1
        label = QtWidgets.QLabel(' influences: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.createMeshInf = ThQSpinBox(5)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.createMeshInf)
        fIndex += 1
        label = QtWidgets.QLabel(' 創建模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.modeList = [
         [
          '依據選擇物件', 1], ['依據選擇物件(EX)', 2], ['包含子層級', 3]]
        self.mode = ThQRadioButtonBox([ n[0] for n in self.modeList ], 1, 'V')
        self.mode.bg.buttonClicked.connect(self.createMeshChShow)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mode)
        self.exWidget = ThQFrameGrp()
        layout1.addWidget(self.exWidget)
        layout1_1 = QtWidgets.QVBoxLayout()
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.exWidget.setLayout(layout1_1)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(0)
        layout2_1.setSpacing(2)
        layout1_1.addLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 偏移: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.exOffset = ThQDoubleSpinBox(value_=0.1)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.exOffset)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 方向: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.aimList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.aim = ThQRadioButtonBox([ n[0] for n in self.aimList ], 0, 'H')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.aim)
        fIndex_1 += 1
        line = ThSeparationLine('H')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex_1 += 1
        self.exLoop = QtWidgets.QCheckBox('成為循環體')
        self.exLoop.setChecked(True)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.exLoop)
        self.chWidget = ThQFrameGrp()
        layout1.addWidget(self.chWidget)
        layout1_1 = QtWidgets.QHBoxLayout()
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.chWidget.setLayout(layout1_1)
        self.createMeshLoop = QtWidgets.QCheckBox('成為循環體')
        self.createMeshLoop.setChecked(True)
        layout1_1.addWidget(self.createMeshLoop)
        line = ThSeparationLine('V')
        layout1_1.addWidget(line)
        self.createMeshSkin = QtWidgets.QCheckBox('自動蒙皮')
        self.createMeshSkin.setChecked(True)
        layout1_1.addWidget(self.createMeshSkin)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.createMeshApply)
        layout2.addWidget(button)
        self.createMeshSkinButton = QtWidgets.QPushButton('蒙皮')
        self.createMeshSkinButton.clicked.connect(self.createMeshSkinApply)
        layout2.addWidget(self.createMeshSkinButton)
        self.createMeshChShow()
        grpBox = QtWidgets.QGroupBox('工具集')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.funcComboBox = ThQComboBox()
        self.setFuncList()
        for label in self.funcList:
            self.funcComboBox.addItem(label[0])

        self.funcComboBox.setInputMaxWidth()
        layout1.addWidget(self.funcComboBox, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.appFuncListOpen)
        layout1.addWidget(button, 20)

    def createMeshSkinApply(self):
        if self.createMeshCls:
            newMesh = self.createMeshCls.newMesh
            cmds.delete(newMesh, ch=True)
            jointList = self.createMeshList.getData()
            cmds.skinCluster(jointList, newMesh, mi=self.createMeshInf.value(), dr=4.0, tsb=True)
            cmds.select(newMesh, r=True)

    def createMeshChShow(self):
        id = self.modeList[self.mode.isCheckedId()][1]
        self.createMeshSkinButton.setHidden(True if id != 1 else False)
        self.exWidget.setHidden(False if id == 2 else True)
        self.chWidget.setHidden(False if id == 3 else True)

    @thDoUndo
    def createMeshApply(self):
        selectList = self.createMeshList.getData()
        if not selectList:
            return
        id = self.modeList[self.mode.isCheckedId()][1]
        if id == 1:
            self.createMeshCls = ThCoordinateCreateMesh(selectList)
        elif id == 2:
            ThCoordinateCreateMeshEx(list_=selectList, inf=self.createMeshInf.value(), aim=self.aimList[self.aim.isCheckedId()][1], offset=self.exOffset.value(), ifLoop=self.exLoop.isChecked())
        elif id == 3:
            ThCreateChPoly(selectList, self.createMeshLoop.isChecked(), self.createMeshSkin.isChecked(), self.createMeshInf.value())

    @thDoUndo
    def appFuncListOpen(self):
        index = self.funcComboBox.currentIndex()
        eval(self.funcList[index][1])

    def setFuncList(self):
        self.funcList = [
         [
          '切換開/ 關所有 skin "envelope" 屬性 — (直接執行)', 'ThSwitchSkinAll("envelope")'],
         [
          '切換開/ 關所有 skin "skinningMethod" 屬性 — (直接執行)', 'ThSwitchSkinAll("skinningMethod")'],
         [
          '重新設定 skin bind pose — (選擇 root 骨骼執行)', 'thResetBindPose()'],
         [
          '在選擇的頂點上創建 joint — (選擇 vertex 執行)', 'thVtxJoint(cmds.ls(sl=True, fl=True))'],
         [
          '顯示/ 隱藏 — (選擇骨骼執行)', 'thJointDrawStyle(cmds.ls(sl=True))'],
         [
          '開關 joint segmentScaleCompensate 屬性 — (選擇骨骼執行)', 'thSwitchJointScaleAttr(cmds.ls(sl=True))'],
         [
          '選擇 skin node — (選擇模型執行)', 'cmds.select(thFindSkinNode([cmds.ls(sl=True)[0]]), r=True)'],
         [
          '調整末端骨骼的軸向對應至父層級 — (直接執行)', 'ThJointAxialToWorld()'],
         [
          '骨骼 -> 頂點 — (選擇模型與骨骼執行)', 'self.jointToVtx()'],
         [
          '骨骼 -> 模型 — (選擇骨骼執行)', 'self.jointToMesh()'],
         [
          '模型 -> 骨骼 — (選擇模型執行)', 'self.meshToJoint()'],
         [
          '選擇權重值不為 1 的頂點 — (選擇骨骼與模型執行)', 'self.selectWeightNotFull()'],
         [
          '移動權重到新骨骼 — (選擇骨骼執行)', 'ThMoveSkinWeightToNewJoint(cmds.ls(sl=True))'],
         [
          '依據子骨骼數量創建歸納群組 — (選擇骨骼列表執行)', 'ThJointLayoutGrp()']]

    @thDoUndo
    def selectWeightNotFull(self):
        ThSelectWeightVtx()

    @thDoUndo
    def meshToJoint(self):
        cmds.select(thFindSkinJoint(cmds.ls(sl=True)), r=True)

    @thDoUndo
    def jointToMesh(self):
        cmds.select(thFindJointConnectMesh(cmds.ls(sl=True)), r=True)

    @thDoUndo
    def jointToVtx(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        typeList = thType(selectList)
        meshList = [ selectList[i] for i, n in enumerate(typeList) if n == 'mesh' ]
        jointList = [ selectList[i] for i, n in enumerate(typeList) if n == 'joint' ]
        thSelectJointVtx(jointList, meshList[0])


class ThQWToolBoxSkinJoint(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSkinJoint, self).__init__(label='編輯骨骼', check=check)
        self.topBotton.copyUi(ThQWToolBoxSkinJoint)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('創建骨骼')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('骨骼鍊')
        button.clicked.connect(cmds.JointTool)
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('在世界中心')
        button.clicked.connect(self.createJoint)
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('在選擇物件中心')
        button.clicked.connect(self.createSelectJoint)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('調整骨骼鍊段數')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 段數: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.mjqQuantity = ThQSpinBox(value_=5)
        layout3.addWidget(self.mjqQuantity, 20)
        button = QtWidgets.QPushButton('選擇 "起始", "結束" 骨骼執行')
        button.clicked.connect(self.mjqApply)
        layout3.addWidget(button, 80)
        grpBox = QtWidgets.QGroupBox('編輯骨骼')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('顯示軸向')
        button.clicked.connect(self.displayJointAxialApply)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('設置軸向')
        button.clicked.connect(cmds.OrientJointOptions)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('設置末端骨骼軸向')
        button.clicked.connect(thDoUndo(lambda : ThJointAxialToWorld(cmds.ls(sl=True))))
        layout2.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('選擇子層級骨骼')
        button.clicked.connect(self.selectChJointApply)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('設置大小')
        button.clicked.connect(lambda : mel.eval('jdsWin()'))
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('重建父子關係')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('執行(選擇物件)')
        layout1.addWidget(button)
        button.clicked.connect(self.parentRedo)
        button = QtWidgets.QPushButton('選擇列表物件')
        layout1.addWidget(button)
        button.clicked.connect(self.parentRedoSelect)
        grpBox = QtWidgets.QGroupBox('鏡像骨骼')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 軸向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.mjAxialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.mjRadioButton = ThQRadioButtonBox([ n[0] for n in self.mjAxialList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mjRadioButton)
        fIndex += 1
        self.mirrorCheckBox = QtWidgets.QCheckBox('自動重命名左右邊')
        self.mirrorCheckBox.setChecked(True)
        self.mirrorCheckBox.stateChanged.connect(self.mirrorCheckBoxShow)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mirrorCheckBox)
        fIndex += 1
        self.mirrorWidget = QtWidgets.QWidget()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mirrorWidget)
        self.mirrorCheckBoxShow()
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        self.mirrorWidget.setLayout(layout2)
        self.mirrorLineEdit1 = QtWidgets.QLineEdit()
        self.mirrorLineEdit1.setPlaceholderText('Left_')
        layout2.addWidget(self.mirrorLineEdit1)
        label = QtWidgets.QLabel('>')
        layout2.addWidget(label)
        self.mirrorLineEdit2 = QtWidgets.QLineEdit()
        self.mirrorLineEdit2.setPlaceholderText('Right_')
        layout2.addWidget(self.mirrorLineEdit2)
        button = QtWidgets.QPushButton('選擇骨骼後執行')
        button.clicked.connect(self.mirrorJoint)
        layout1.addWidget(button)

    @thDoUndo
    def mjqApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList or len(selectList) != 2:
            return
        ThModifyJointQuantity(selectList[0], selectList[1], self.mjqQuantity.value())

    @thDoUndo
    def parentRedo(self):
        ThReconstructionParent(cmds.ls(sl=True)).apply()

    def parentRedoSelect(self):
        ThReconstructionParent().select()

    @thDoUndo
    def selectChJointApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        jointList = cmds.listRelatives(selectList, ad=True, f=True, type='joint')
        for n in selectList:
            if cmds.nodeType(n) == 'joint':
                jointList.append(n)

        cmds.select(jointList[::-1], r=True)

    @thDoUndo
    def displayJointAxialApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ThTransformDisplay(selectList=selectList, attr='axes', parent=True, type='joint')

    @thDoUndo
    def mirrorJoint(self):
        axialLndex = self.mjRadioButton.isCheckedId()
        thMirrorJoint(joints=cmds.ls(sl=True), axial=self.mjAxialList[axialLndex][1], rename_name=[
         self.mirrorLineEdit1.text(), self.mirrorLineEdit2.text()], automatic_re=self.mirrorCheckBox.isChecked())

    @thDoUndo
    def createJoint(self):
        cmds.select(cl=True)
        cmds.joint()

    @thDoUndo
    def createSelectJoint(self):
        thSelCreateJoint(cmds.ls(sl=True, fl=True))

    def mirrorCheckBoxShow(self):
        if self.mirrorCheckBox.isChecked():
            self.mirrorWidget.hide()
        else:
            self.mirrorWidget.show()


class ThQWToolBoxCopyWeight(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxCopyWeight, self).__init__(label='複製權重', check=check)
        self.topBotton.copyUi(ThQWToolBoxCopyWeight)
        parenr.addWidget(self)
        grpBox = QtWidgets.QGroupBox('複製權重(方法一)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 內建自動蒙皮')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        button = QtWidgets.QPushButton('交換列表位置')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        button.clicked.connect(self.exchangeCopyWeightList)
        layout1.addWidget(button)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.copyWeightList1 = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.copyWeightList1)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.copyWeightList2 = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.copyWeightList2)
        fIndex += 1
        label = QtWidgets.QLabel(' 模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.cwCopyModeList = [
         [
          'Point', 'point'], ['UV', 'uv'], ['Name', 'name']]
        self.cwRadioButton = ThQRadioButtonBox([ n[0] for n in self.cwCopyModeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.cwRadioButton)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.copyWeight1)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('複製權重(方法二)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.autoSkinCheckBox = QtWidgets.QCheckBox('自動\n蒙皮')
        self.autoSkinCheckBox.setChecked(True)
        layout2.addWidget(self.autoSkinCheckBox, 20)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        self.copyWeightCheckBox = QtWidgets.QCheckBox('複製\n權重')
        self.copyWeightCheckBox.setChecked(True)
        layout2.addWidget(self.copyWeightCheckBox, 20)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('執行\n(加選來源)')
        button.clicked.connect(self.copyWeight2)
        layout2.addWidget(button, 30)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('交互複製\n(加選來源)')
        button.clicked.connect(self.copyWeight2_1)
        layout2.addWidget(button, 30)
        grpBox = QtWidgets.QGroupBox('複製權重(方法三: om2 傳遞頂點權重數據)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('執行(加選來源)')
        button.clicked.connect(self.copyWeight3)
        layout1.addWidget(button)

    @thDoUndo
    def copyWeight3(self):
        selectList = cmds.ls(sl=True)
        if len(selectList) > 1:
            ThCopyWeightApi().copyWeightF(selectList[1], selectList[0])

    @thDoUndo
    def copyWeight2_1(self):
        sel = cmds.ls(sl=True)
        if len(sel) != 2:
            cmds.warning('請選擇: [來源, 目標] 執行!')
        csaw = THCopySkinAndWeight([sel[1]], [sel[0]])
        csaw.copy_skin()
        csaw.copy_weight()
        csaw = THCopySkinAndWeight([sel[0]], [sel[1]])
        csaw.copy_weight()
        csaw.set_max_influences()
        cmds.select(sel[1], r=True)

    @thDoUndo
    def copyWeight2(self):
        sel = cmds.ls(sl=True)
        csaw = THCopySkinAndWeight([sel[(-1)]], sel[:-1])
        if self.autoSkinCheckBox.isChecked():
            csaw.copy_skin()
        if self.copyWeightCheckBox.isChecked():
            csaw.copy_weight()
        csaw.set_max_influences()
        cmds.select(sel[0], r=True)
        sys.stdout.write('執行完成!')

    @thDoUndo
    def copyWeight1(self):
        modeIndex = self.cwRadioButton.isCheckedId()
        csaw = THCopySkinAndWeight(self.copyWeightList1.getData(), self.copyWeightList2.getData(), self.cwCopyModeList[modeIndex][1])
        csaw.copy_skin()
        csaw.copy_weight()
        csaw.set_max_influences()
        sys.stdout.write('執行完成!')

    def exchangeCopyWeightList(self):
        list1 = self.copyWeightList1.getData()
        list2 = self.copyWeightList2.getData()
        self.copyWeightList1.setData(list2)
        self.copyWeightList2.setData(list1)


class ThQWToolBoxSkinWeight(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSkinWeight, self).__init__(label='編輯權重', check=check)
        self.topBotton.copyUi(ThQWToolBoxSkinWeight)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('編輯局部權重(導回功能將無法undo)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2, 70)
        button = QtWidgets.QPushButton('擷取局部(選擇面執行)')
        button.clicked.connect(self.spdsAppF1)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('導回權重(直接執行)')
        button.clicked.connect(self.spdsAppF2)
        layout2.addWidget(button)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2, 30)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.addLayout(layout3)
        button = QtWidgets.QPushButton('H')
        button.clicked.connect(lambda : self.spdsHSF('hide'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('S')
        button.clicked.connect(lambda : self.spdsHSF('show'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('刪除紀錄')
        button.clicked.connect(self.spdsAppF3)
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('編輯權重')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.toVtxCheckBox = QtWidgets.QCheckBox('轉換為頂點')
        self.toVtxCheckBox.setChecked(True)
        layout2.addWidget(self.toVtxCheckBox)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('權重筆刷')
        button.clicked.connect(self.paintWeight)
        layout2.addWidget(button)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('鏡像權重')
        button.clicked.connect(cmds.MirrorSkinWeightsOptions)
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('編輯骨架權重鎖定狀態')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ejList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ejList)
        label = QtWidgets.QLabel('* 選擇骨骼執行;\n* 加選模型執行會自動導入列表')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('獨開')
        button.clicked.connect(lambda : self.lockWeightJoint('lock'))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('獨關')
        button.clicked.connect(lambda : self.lockWeightJoint('nulock'))
        layout2.addWidget(button)

    def spdsHSF(self, mode):
        ThSimplifyPolyDoSkin().hiddenF(mode)

    @thDoUndo
    def spdsAppF3(self):
        ThSimplifyPolyDoSkin().deleteF()

    @thDoUndo
    def spdsAppF2(self):
        ThSimplifyPolyDoSkin().copyWeightF()

    @thDoUndo
    def spdsAppF1(self):
        selectList = cmds.ls(sl=True)
        self.spds = ThSimplifyPolyDoSkin(selectList)
        self.spds.simplifyF()

    @thDoUndo
    def lockWeightJoint(self, mode):
        u"""鎖定指定 joint weight"""
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        typeList = thType(selectList)
        selectMeshList = []
        for i, type in enumerate(typeList):
            if type == 'mesh':
                selectMeshList.append(selectList[i])

        uiMesh = self.ejList.getData()
        if uiMesh or selectMeshList:
            if selectMeshList:
                ThLockJointWeight(selectList, mode)
            else:
                ThLockJointWeight(selectList + uiMesh, mode)
        if selectMeshList:
            self.ejList.setData(selectMeshList)

    @thDoUndo
    def paintWeight(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        if '.' not in selectList[0]:
            typeList = thType(selectList)
            if 'mesh' not in typeList:
                return
            if 'joint' in typeList:
                ThLockJointWeight(selectList, 'lock')
        if self.toVtxCheckBox.isChecked():
            cmds.select(cmds.polyListComponentConversion(selectList, tv=True), r=True)
        thSetPaintWeightFree(selectList)
        cmds.ArtPaintSkinWeightsToolOptions()


class ThQWToolBoxSmoothWeight(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxSmoothWeight, self).__init__(label='Smooth weight', check=check)
        self.topBotton.copyUi(ThQWToolBoxSmoothWeight)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標骨骼:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.smoothJointList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.smoothJointList)
        fIndex += 1
        label = QtWidgets.QLabel(' value/ loop: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.smoothWeight = ThQDoubleSpinBox(value_=1)
        layout3.addWidget(self.smoothWeight)
        self.smoothQuantity = ThQSpinBox(1)
        layout3.addWidget(self.smoothQuantity)
        fIndex += 1
        self.smoothRang = QtWidgets.QCheckBox('使用目前權重範圍')
        self.smoothRang.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.smoothRang)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.smoothApply)
        layout1.addWidget(button)

    @thDoUndo
    def smoothApply(self):
        ThEditSkinWeightSmooth(cmds.ls(sl=True), self.smoothQuantity.value(), self.smoothJointList.getData(), self.smoothWeight.value(), self.smoothRang.isChecked())


class ThQWToolBoxSoftToSkinWeight(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxSoftToSkinWeight, self).__init__(label='Soft to skin weight', check=check)
        self.topBotton.copyUi(ThQWToolBoxSoftToSkinWeight)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 接收權重的骨骼: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.stkJoint = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.stkJoint)
        fIndex += 1
        self.stkIsCh = QtWidgets.QCheckBox('批量設定子層級')
        self.stkIsCh.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.stkIsCh)
        fIndex += 1
        self.stkUseOm2 = QtWidgets.QCheckBox('使用 om2 設定權重')
        self.stkUseOm2.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.stkUseOm2)
        button = QtWidgets.QPushButton('選擇頂點後執行')
        button.clicked.connect(self.softToSkin)
        layout1.addWidget(button)

    @thDoUndo
    def softToSkin(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        mel.eval('reflectionSetMode none')
        if self.stkIsCh.isChecked():
            sts = SoftToSkin(self.stkJoint.getData(), selectList, self.stkUseOm2.isChecked())
            sts.batchApply()
        else:
            sts = SoftToSkin(self.stkJoint.getData(), selectList, self.stkUseOm2.isChecked())
            sts.apply()


class ThQWToolBoxExportSkinWeight(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxExportSkinWeight, self).__init__(label='匯出/ 匯入蒙皮頂點的權重數據', check=check)
        self.topBotton.copyUi(ThQWToolBoxExportSkinWeight)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 匯出需選擇模型執行，匯入則否')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('匯出')
        button.clicked.connect(thDoUndo(self.expottFile))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('匯入')
        button.clicked.connect(thDoUndo(self.importFile))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('打開路徑')
        button.clicked.connect(lambda : thOpenPath('file'))
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('附屬功能')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('選擇到連接骨骼的模型\n(選擇根骨骼執行)')
        button.clicked.connect(thDoUndo(self.selectConnectMesh))
        layout1.addWidget(button)

    @thDoUndo
    def selectConnectMesh(self):
        selectList = cmds.ls(sl=True, l=True)
        if not selectList:
            return
        jointList = [
         selectList[0]]
        childJointList = cmds.listRelatives(selectList, ad=True, f=True, type='joint')
        if childJointList:
            selectList.extend(childJointList)
        cmds.select(thFindJointConnectMesh(selectList), r=True)

    @thDoUndo
    def expottFile(self):
        ThCopyWeightApi().exportWeightFileF(cmds.ls(sl=True))

    @thDoUndo
    def importFile(self):
        ThCopyWeightApi().importWeightFileF()


class ThQWToolBoxAuthorInformation(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        global TH_TOOL_UPDATA_LIST
        super(ThQWToolBoxAuthorInformation, self).__init__(label='< 關於本工具 >', check=check)
        self.topBotton.copyUi(ThQWToolBoxAuthorInformation, False)
        parent.addWidget(self)
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.layout.addWidget(self.splitter)
        grpBox = QtWidgets.QGroupBox('作者簡介')
        self.splitter.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.myText = None
        self.setMyText()
        self.textWidget1 = QtWidgets.QPlainTextEdit()
        self.textWidget1.setReadOnly(True)
        self.textWidget1.setPlainText(self.myText)
        layout1.addWidget(self.textWidget1)
        grpBox = QtWidgets.QGroupBox('權責說明')
        self.splitter.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.toolText = None
        self.setToolText()
        self.textWidget2 = QtWidgets.QPlainTextEdit()
        self.textWidget2.setReadOnly(True)
        self.textWidget2.setPlainText(self.myText)
        layout1.addWidget(self.textWidget2)
        grpBox = QtWidgets.QGroupBox('程序說明')
        self.splitter.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.toolText = None
        self.setToolText()
        self.textWidget3 = QtWidgets.QPlainTextEdit()
        self.textWidget3.setReadOnly(True)
        self.textWidget3.setPlainText(TH_TOOL_UPDATA_LIST)
        layout1.addWidget(self.textWidget3)
        self.setStretchFactorF()
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        self.layout.addLayout(layout1)
        button = QtWidgets.QPushButton('官方網站')
        button.clicked.connect(lambda : webbrowser.open('https://thrigtools.weebly.com/'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('教學頻道(YouTube)')
        button.clicked.connect(lambda : webbrowser.open('https://www.youtube.com/watch?v=e8jekQkfwm8&list=PLz897MlhexVC7lhNAo2JFZKby1dSriFX8'))
        layout1.addWidget(button)
        return

    def setToolText(self):
        self.myText = '本程式為免費工具，請勿隨意串改內容圖利，若想分享本工具，請附上作者簡介，感謝您!!\n'

    def setMyText(self):
        self.myText = '- 作者: 劉庭豪(Tony)\n- 信箱: sx785878@gmail.com\n- 工具簡介: \nTh Rig Tools 是基於 MAYA 軟體開發的 RIG Script，可以處理大量的循環事件，內容主要包括： 建立控制器，Skin Weight 等功能。'

    def setStretchFactorF(self):
        u"""設定分割窗口比例"""
        textList = [
         self.textWidget1, self.textWidget2, self.textWidget3]
        textLenList = []
        for text in textList:
            textLenList.append(len(text.toPlainText()))

        textLenWeightList = [25, 25, 50]
        for i, text in enumerate(textList):
            self.splitter.setStretchFactor(i, textLenWeightList[i])


class ThQWToolBoxEditJoint(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxEditJoint, self).__init__(label='編輯骨骼位置', check=check)
        self.topBotton.copyUi(ThQWToolBoxEditJoint)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 選擇骨骼執行啟用編輯\n會自動將骨骼導入下列相對應列表中\n* 若已經有自定義定位用骨骼\n可以忽略編輯按鈕，自行導入列表操作')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('啟用編輯')
        button.clicked.connect(self.editMode)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('解除編輯狀態')
        button.clicked.connect(self.delEditMode)
        layout2.addWidget(button)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 定位用的骨骼: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.refJoint = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.refJoint)
        fIndex += 1
        label = QtWidgets.QLabel(' 被編輯的骨骼: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.editJoint = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.editJoint)
        fIndex += 1
        self.ifDelRef = QtWidgets.QCheckBox('執行後刪除 "定位用的骨骼"')
        self.ifDelRef.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifDelRef)
        fIndex += 1
        self.ifFreeze = QtWidgets.QCheckBox('執行凍結變換')
        self.ifFreeze.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifFreeze)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('附屬功能')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('選擇層級下的所有骨骼')
        button.clicked.connect(self.selectHierarchyJoint)
        layout1.addWidget(button)

    @thDoUndo
    def selectHierarchyJoint(self):
        syo = ThSelectTypeObject(objs=cmds.ls(sl=True), mode='father', type='joint')
        syo.selectObjsF()

    @thDoUndo
    def editMode(self):
        self.mjm = THMModifyJointMove(cmds.ls(sl=True))
        cmds.hide(self.mjm.joints)
        self.refJoint.setData(self.mjm.new_joints)
        self.editJoint.setData(self.mjm.joints)

    @thDoUndo
    def delEditMode(self):
        if cmds.objExists('th_modify_joint_old_sets'):
            cmds.showHidden(cmds.sets('th_modify_joint_old_sets', q=True))
            cmds.delete('th_modify_joint_old_sets')
        if cmds.objExists('th_modify_joint_ref_sets'):
            cmds.delete(cmds.sets('th_modify_joint_ref_sets', q=True))

    @thDoUndo
    def apply(self):
        thReplaceJoint(self.editJoint.getData(), self.refJoint.getData(), self.ifDelRef.isChecked(), self.ifFreeze.isChecked())
        self.delEditMode()


class ThQWToolBoxRename(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxRename, self).__init__(label='重命名', check=check)
        self.topBotton.copyUi(ThQWToolBoxRename)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('去除重複名稱')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.clearIfSelect = QtWidgets.QCheckBox('選擇到物件')
        self.clearIfSelect.setChecked(True)
        layout2.addWidget(self.clearIfSelect, 30)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('搜尋場景中的重複名稱')
        button.clicked.connect(self.findRepeatRename)
        layout2.addWidget(button, 70)
        label = QtWidgets.QLabel('* 若選擇物件執行，只會更改選擇的物件\n* 若無選擇物件執行，將更改場景中所有物件')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        button = QtWidgets.QPushButton('重命名重複名稱物件\n(選擇/ 不選擇物件執行)')
        button.clicked.connect(self.clearRepeatRename)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('批量重命名')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.renameText = QtWidgets.QLineEdit()
        self.renameText.setPlaceholderText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.renameText)
        fIndex += 1
        self.renameIfChange = QtWidgets.QCheckBox('重命名子層級物件')
        self.renameIfChange.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.renameIfChange)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.rename)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('添加(前/ 後)綴')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.prefixText = QtWidgets.QLineEdit()
        self.prefixText.setPlaceholderText('prefix_')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.prefixText)
        fIndex += 1
        label = QtWidgets.QLabel(' 方向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.prefixModeList = [
         [
          '前', 'front'], ['後', 'back']]
        self.prefixMode = ThQRadioButtonBox([ n[0] for n in self.prefixModeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.prefixMode)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.addPrefix)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('去除指定字符')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 字符: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.replaceText = QtWidgets.QLineEdit()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.replaceText)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.replaceName)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('清除指定長度')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 長度: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        grpBox.setLayout(layout3)
        self.rclQuantity = ThQSpinBox(value_=1)
        layout3.addWidget(self.rclQuantity, 40)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.relApply)
        layout3.addWidget(button, 60)
        grpBox = QtWidgets.QGroupBox('交換名稱')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.switchList1 = ThQLineBoxList(flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.switchList1)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.switchList2 = ThQLineBoxList(flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.switchList2)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.exchangeApply)
        layout1.addWidget(button)

    @thDoUndo
    def exchangeApply(self):
        ThRenameExchange(self.switchList1.getData(), self.switchList2.getData())

    @thDoUndo
    def relApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ThRenameClearLen(selectList, self.rclQuantity.value())

    @thDoUndo
    def replaceName(self):
        replace = self.replaceText.text()
        thClearStr(cmds.ls(sl=True), replace)

    @thDoUndo
    def addPrefix(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        prefix = self.prefixText.text()
        mode = self.prefixModeList[self.prefixMode.isCheckedId()][1]
        if mode == 'front':
            for obj in selectList:
                cmds.rename(obj, prefix + obj)

        elif mode == 'back':
            for obj in selectList:
                cmds.rename(obj, obj + prefix)

    @thDoUndo
    def rename(self):
        sel = cmds.ls(sl=True)
        trdn_cls = THRemoveDuplicateNames(sel)
        trdn_cls.app()
        thBatchRename(sel, self.renameText.text(), self.renameIfChange.isChecked())

    @thDoUndo
    def clearRepeatRename(self):
        trdn_cls = THRemoveDuplicateNames(cmds.ls(sl=True))
        trdn_cls.app()

    @thDoUndo
    def findRepeatRename(self):
        rdn = THRemoveDuplicateNames(cmds.ls(sl=True))
        rdn.printMenuF(self.clearIfSelect.isChecked())


class ThQWToolBoxMirrorTransform(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxMirrorTransform, self).__init__(label='鏡像工具', check=check)
        self.topBotton.copyUi(ThQWToolBoxMirrorTransform)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* "列表一" 與 "列表二" 的物件數量要相同\n且，物件的排序也要是相對應的')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表一: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list1 = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list1)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表二: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list2 = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list2)
        fIndex += 1
        button = QtWidgets.QPushButton('選擇全部列表物件')
        button.clicked.connect(self.selectAllApply)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 軸向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.axialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.axial = ThQRadioButtonBox([ n[0] for n in self.axialList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.axial)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 使用的屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tAttrList = [
         [
          'tx', 'tx'], ['ty', 'ty'], ['tz', 'tz']]
        self.tAttr = ThQCheckBox([ n[0] for n in self.tAttrList ], [True, True, True], 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tAttr)
        fIndex += 1
        self.rAttrList = [['rx', 'rx'], ['ry', 'ry'], ['rz', 'rz']]
        self.rAttr = ThQCheckBox([ n[0] for n in self.rAttrList ], [True, True, True], 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.rAttr)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        self.ifCustomAttr = QtWidgets.QCheckBox('鏡像自訂屬性')
        self.ifCustomAttr.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifCustomAttr)
        fIndex += 1
        self.ifReverse = QtWidgets.QCheckBox('反轉鏡像')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifReverse)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(thDoUndo(self.apply))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 保存列表數據 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 本功能用於保存 "列表一"、"列表二" 數據\n* 本功能會在場景中創建名為\n"customCtrlMirror_data" 的物件\n目的為保存數據，請勿將其刪除!')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        self.saveListSlider = ThQSlider(QtCore.Qt.Horizontal)
        self.saveListSlider.setMinimum(100)
        self.saveListSlider.setMaximum(800)
        self.saveListSlider.valueChanged[int].connect(self.listWidgetWidth)
        layout1.addWidget(self.saveListSlider)
        self.saveList = ThQListWidget()
        self.saveList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.saveList.setMinimumWidth(50)
        self.saveList.setMinimumHeight(100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.saveList.setSizePolicy(sizePolicy)
        layout1.addWidget(self.saveList)
        label = QtWidgets.QLabel('* 數據導回列表功能只能選擇其一\n刪除則可以複選')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('讀取\n存檔')
        button.clicked.connect(self.getSystem)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('將選擇的數據導回\n"列表一"、"列表二"')
        button.clicked.connect(thDoUndo(self.setSystemToBox))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('刪除選擇\n的數據列表')
        button.clicked.connect(thDoUndo(self.deleyeSystemList))
        layout2.addWidget(button)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 新列表名稱: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.saveLabel = QtWidgets.QLineEdit()
        self.saveLabel.setText('object_01')
        layout3.addWidget(self.saveLabel)
        button = QtWidgets.QPushButton('<')
        button.setStyleSheet('min-width: 20px;max-width: 20px;')
        button.clicked.connect(self.inputSystemLabel)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('保存 "列表一"、"列表二" 數據')
        button.clicked.connect(thDoUndo(self.saveSystrm))
        layout1.addWidget(button)

    def selectAllApply(self):
        list1 = self.list1.getData()
        list2 = self.list2.getData()
        cmds.select(list1 + list2, r=True)

    @thDoUndo
    def deleyeSystemList(self):
        selectItemList = self.saveList.selectedItems()
        if not selectItemList:
            return
        selectItemTextList = [ item.text() for item in selectItemList ]
        data = eval(cmds.getAttr('customCtrlMirror_data.notes'))
        for selectItemText in selectItemTextList:
            del data[selectItemText]

        if data:
            cmds.setAttr('customCtrlMirror_data.notes', data, type='string')
        else:
            cmds.delete('customCtrlMirror_data')
        self.getSystem()

    def inputSystemLabel(self):
        selectItemList = self.saveList.selectedItems()
        if not selectItemList:
            return
        self.saveLabel.setText(selectItemList[0].text())

    def setSystemToBox(self):
        selectItemList = self.saveList.selectedItems()
        if not selectItemList:
            return
        data = eval(cmds.getAttr('customCtrlMirror_data.notes'))
        self.list1.setData(data[selectItemList[0].text()]['L'])
        self.list2.setData(data[selectItemList[0].text()]['R'])

    def saveSystrm(self):
        label = self.saveLabel.text()
        if not label:
            return
        list1 = self.list1.getData()
        list2 = self.list2.getData()
        cmd = THCtrlMirrorData(label)
        cmd.add_list(list1, 'L')
        cmd.add_list(list2, 'R')
        self.getSystem()

    def getSystem(self):
        self.saveList.clear()
        if cmds.objExists('customCtrlMirror_data'):
            data = eval(cmds.getAttr('customCtrlMirror_data.notes'))
            for label in data:
                self.saveList.addItem(label)

    @thDoUndo
    def apply(self):
        sel = cmds.ls(sl=True)
        tAttrList = [ self.tAttrList[i][1] for i in self.tAttr.isCheckedIdList() ]
        rAttrList = [ self.rAttrList[i][1] for i in self.rAttr.isCheckedIdList() ]
        useAttrList = tAttrList + rAttrList
        THMirrorData(self.list1.getData(), self.list2.getData(), self.axialList[self.axial.isCheckedId()][1], useAttrList, self.ifReverse.isChecked(), self.ifCustomAttr.isChecked())
        cmds.select(sel, r=True)

    def listWidgetWidth(self):
        u"""調整 listWidget 高度"""
        pos = self.saveListSlider.value()
        self.saveList.setMinimumHeight(pos)


class ThQWToolBoxListTool(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxListTool, self).__init__(label='列表工具(單列表)', check=check)
        self.topBotton.copyUi(ThQWToolBoxListTool)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('主要操作列表')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 在此欄位導入要操作之物件後\n可使用下方附屬功能')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list1 = ThQLineBoxList(flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list1)
        grpBox = QtWidgets.QGroupBox('Connect')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.attrList = ThQLineBoxAttrList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.attrList)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器與屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlAttr = ThQLineBoxObjAttr(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlAttr)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.connApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('Constrain')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.conMain = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.conMain)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('point')
        layout2.addWidget(button)
        button.clicked.connect(lambda : self.conApply('point'))
        button = QtWidgets.QPushButton('orient')
        layout2.addWidget(button)
        button.clicked.connect(lambda : self.conApply('orient'))
        button = QtWidgets.QPushButton('scale')
        layout2.addWidget(button)
        button.clicked.connect(lambda : self.conApply('scale'))
        button = QtWidgets.QPushButton('parent')
        layout2.addWidget(button)
        button.clicked.connect(lambda : self.conApply('parent'))
        button = QtWidgets.QPushButton('normal')
        layout2.addWidget(button)
        button.clicked.connect(self.conNormalApply)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        label = QtWidgets.QLabel(' 軸向: ')
        layout2.addWidget(label, 15)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        self.conAxialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.conAxial = ThQRadioButtonBox([ n[0] for n in self.conAxialList ], 0, 'H')
        layout2.addWidget(self.conAxial, 50)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('tangent')
        layout2.addWidget(button, 35)
        button.clicked.connect(self.conCurveApply)
        grpBox = QtWidgets.QGroupBox('Set attrs')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.saAttrList = ThQLineBoxAttrList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.saAttrList)
        fIndex += 1
        label = QtWidgets.QLabel(' 偏移: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.mvValue = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mvValue)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.saApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('批量設置關鍵偵')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inpAttr = ThQLineBoxAttr(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inpAttr)
        fIndex += 1
        label = QtWidgets.QLabel(' 值/ 初始時間/ 添加時間: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.stOffset = ThQDoubleSpinBox(value_=1)
        layout3.addWidget(self.stOffset)
        self.stFrame = ThQSpinBox(value_=1)
        layout3.addWidget(self.stFrame)
        self.stAddFrame = ThQSpinBox(value_=1)
        layout3.addWidget(self.stAddFrame)
        button = QtWidgets.QPushButton('選擇物件列表執行')
        button.clicked.connect(self.stApplyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('創建 nonlinear')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.nonlinearList = [
         'bend', 'flare', 'sine', 'squash', 'twist', 'wave']
        self.nonlinear = ThQComboBox()
        for label in self.nonlinearList:
            self.nonlinear.addItem(label)

        self.nonlinear.setInputMaxWidth()
        layout1.addWidget(self.nonlinear, 70)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.nonlinearApplyF)
        layout1.addWidget(button, 30)

    @thDoUndo
    def nonlinearApplyF(self):
        selectList = self.list1.getData()
        if not selectList:
            return
        thSelCreateNonlinearF(selectList, self.nonlinearList[self.nonlinear.currentIndex()])

    @thDoUndo
    def stApplyF(self):
        selectList = self.list1.getData()
        if not selectList:
            return
        attr = self.inpAttr.getData()
        if not attr:
            return
        thBatchSetKey(selectList, attr, self.stOffset.value(), self.stFrame.value(), self.stAddFrame.value())

    @thDoUndo
    def saApply(self):
        attrList = self.saAttrList.getData()
        offset = self.mvValue.value()
        start = 0
        for n in self.list1.getData():
            for attr in attrList:
                cmds.setAttr(('{}.{}').format(n, attr), start)
                start += offset

    @thDoUndo
    def conCurveApply(self):
        main = self.conMain.getData()
        axial = self.conAxialList[self.conAxial.isCheckedId()][1]
        app = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}
        for n in self.list1.getData():
            cmds.tangentConstraint([main, n], worldUpType='vector', aimVector=app[axial], upVector=app[axial], worldUpVector=app[axial])

    @thDoUndo
    def conNormalApply(self):
        main = self.conMain.getData()
        for n in self.list1.getData():
            cmds.normalConstraint([main, n], weight=1, aimVector=[1, 0, 0], upVector=[
             0, 1, 0], worldUpType='vector', worldUpVector=[0, 1, 0])

    @thDoUndo
    def conApply(self, mode='point'):
        appDict = {'point': 'cmds.pointConstraint({})', 
           'orient': 'cmds.orientConstraint({})', 
           'scale': 'cmds.scaleConstraint({})', 
           'parent': 'cmds.parentConstraint({})'}
        main = self.conMain.getData()
        for n in self.list1.getData():
            eval(appDict[mode].format('[main,n], mo=True, weight=1'))

    @thDoUndo
    def connApply(self):
        ctrlAttr = self.ctrlAttr.getData()
        if not ctrlAttr:
            return
        for n in self.list1.getData():
            for attr in self.attrList.getData():
                cmds.connectAttr(ctrlAttr, n + '.' + attr, f=True)


class ThQWToolBoxListToList(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxListToList, self).__init__(label='列表工具(雙列表)', check=check)
        self.topBotton.copyUi(ThQWToolBoxListToList)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('主要操作列表')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 在此欄位導入要操作之物件後\n可使用下方附屬功能')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        button = QtWidgets.QPushButton('交換列表位置')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        button.clicked.connect(self.exchangeList)
        layout1.addWidget(button)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list1 = ThQLineBoxList(flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list1)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list2 = ThQLineBoxList(flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list2)
        grpBox = QtWidgets.QGroupBox('Connect')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源屬性列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.attrList1 = ThQLineBoxAttrList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.attrList1)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.attrList2 = ThQLineBoxAttrList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.attrList2)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.connApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('Constrain')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('point')
        button.clicked.connect(lambda : self.conApply('point'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('orient')
        button.clicked.connect(lambda : self.conApply('orient'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('scale')
        button.clicked.connect(lambda : self.conApply('scale'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('parent')
        button.clicked.connect(lambda : self.conApply('parent'))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('工具集')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.otherList = []
        self.setOtherList()
        self.other = ThQComboBox()
        for label in self.otherList:
            self.other.addItem(label[0])

        self.other.setInputMaxWidth()
        layout1.addWidget(self.other, 70)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.otherApply)
        layout1.addWidget(button, 30)

    @thDoUndo
    def otherApply(self):
        list1 = self.list1.getData()
        list2 = self.list2.getData()
        ThTwoListTools(list1, list2, self.otherList[self.other.currentIndex()][1])

    @thDoUndo
    def conApply(self, mode='point'):
        appDict = {'point': 'cmds.pointConstraint({})', 
           'orient': 'cmds.orientConstraint({})', 
           'scale': 'cmds.scaleConstraint({})', 
           'parent': 'cmds.parentConstraint({})'}
        list1 = self.list1.getData()
        list2 = self.list2.getData()
        for i in range(len(list1)):
            eval(appDict[mode].format('[list1[i],list2[i]], mo=True, weight=1'))

    @thDoUndo
    def connApply(self):
        list1 = self.list1.getData()
        list2 = self.list2.getData()
        attrList1 = self.attrList1.getData()
        attrList2 = self.attrList2.getData()
        for i in range(len(list1)):
            for ii in range(len(attrList1)):
                cmds.connectAttr(list1[i] + '.' + attrList1[ii], list2[i] + '.' + attrList2[ii], f=True)

    def exchangeList(self):
        list1 = self.list1.getData()
        list2 = self.list2.getData()
        self.list1.setData(list2)
        self.list2.setData(list1)

    def setOtherList(self):
        self.otherList = [
         [
          'Parent 到來源', 'parent'],
         [
          'Skin(選擇的骨骼)', 'skin select'],
         [
          'Skin', 'skin'],
         [
          'BlendShape', 'blendShape'],
         [
          'Wire', 'wire'],
         [
          'Wrap', 'wrap'],
         [
          '使用 constrain 功能做位置吸附', 'adsorption'],
         [
          'Transform 數值傳遞(來源屬性回到預設)', 'data transfer'],
         [
          'Transform 數值傳遞(不更動來源)', 'data transfer not'],
         [
          '頂點數值傳遞', 'vtx transfer'],
         [
          '軸心吸附到目標', 'axis adsorption']]


class ThQWToolBoxSelectIndex(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSelectIndex, self).__init__(label='選擇相對的頂點', check=check)
        self.topBotton.copyUi(ThQWToolBoxSelectIndex)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 頂點列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.spi = None
        self.vertexList = ThQLineBoxList(flatten=True)
        self.vertexList.inputButton.clicked.connect(self.inputData)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.vertexList)
        button = QtWidgets.QPushButton('選擇模型執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        return

    def apply(self):
        if self.spi:
            self.spi.do_select(cmds.ls(sl=True))

    def inputData(self):
        self.spi = THSelectPointIndex(cmds.ls(sl=True, fl=True))
        self.spi.save()


class ThQWToolBoxNamespaceSelect(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxNamespaceSelect, self).__init__(label='選擇定義名稱物件', check=check)
        self.topBotton.copyUi(ThQWToolBoxNamespaceSelect)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list1 = ThQLineBoxList(flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list1)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 去除: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.clearText = QtWidgets.QLineEdit()
        layout3.addWidget(self.clearText, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.clearApplyF)
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' 添加: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.addText = QtWidgets.QLineEdit()
        layout3.addWidget(self.addText, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.addApplyF)
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' 替換: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.rep1 = QtWidgets.QLineEdit()
        layout3.addWidget(self.rep1, 38)
        label = QtWidgets.QLabel('>')
        layout3.addWidget(label, 4)
        self.rep2 = QtWidgets.QLineEdit()
        layout3.addWidget(self.rep2, 38)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.repApplyF)
        layout3.addWidget(button, 20)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 篩選: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.yesNoList = [
         [
          '包含', 'yes'], ['排除', 'no']]
        self.yesNo = ThQRadioButtonBox([ n[0] for n in self.yesNoList ], 0, 'H')
        layout3.addWidget(self.yesNo, 45)
        self.filterText = QtWidgets.QLineEdit()
        layout3.addWidget(self.filterText, 35)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.filterApplyF)
        layout3.addWidget(button, 20)

    @thDoUndo
    def filterApplyF(self):
        str_ = self.filterText.text()
        if not str_:
            return
        selectList = self.list1.getData()
        if not selectList:
            return
        newList = thFilterNameList(selectList, str_, self.yesNoList[self.yesNo.isCheckedId()][1])
        cmds.select(newList, r=True)

    def repApplyF(self):
        newList = []
        noList = []
        for n in self.list1.getData():
            name = n.replace(self.rep1.text(), self.rep2.text())
            if not cmds.objExists(name):
                noList.append(name)
            else:
                newList.append(name)

        if noList:
            cmds.warning((' 找不到: {}').format((', ').join(noList)))
        cmds.select(newList, r=True)

    def clearApplyF(self):
        newList = []
        str_ = self.clearText.text()
        noList = []
        for n in self.list1.getData():
            name = n.replace(str_, '')
            if not cmds.objExists(name):
                noList.append(name)
            else:
                newList.append(name)

        cmds.select(newList, r=True)
        if noList:
            cmds.warning((' 找不到: {}').format((', ').join(noList)))

    def addApplyF(self):
        newList = []
        str_ = self.addText.text()
        noList = []
        for n in self.list1.getData():
            name = ('{}{}').format(str_, n)
            if not cmds.objExists(name):
                noList.append(name)
            else:
                newList.append(name)

        cmds.select(newList, r=True)
        if noList:
            cmds.warning((' 找不到: {}').format((', ').join(noList)))


class ThQWToolBoxFilePath(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxFilePath, self).__init__(label='更改貼圖檔案路徑', check=check)
        self.topBotton.copyUi(ThQWToolBoxFilePath)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('替換代號')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 代號: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.code = QtWidgets.QLineEdit()
        self.code.setText('D')
        layout3.addWidget(self.code, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.codeApp)
        layout3.addWidget(button, 20)
        grpBox = QtWidgets.QGroupBox('替換路徑')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 新路徑: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.newPath = QtWidgets.QLineEdit()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.newPath)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('更改')
        button.clicked.connect(self.changeApply)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('還原')
        button.clicked.connect(self.changeReset)
        layout2.addWidget(button)

    @thDoUndo
    def changeApply(self):
        ChangeFilePath().change_path(self.newPath.text())

    @thDoUndo
    def changeReset(self):
        ChangeFilePath().reset_path()

    @thDoUndo
    def codeApp(self):
        code = self.code.text()
        fileNode = cmds.ls(typ='file')
        for n in fileNode:
            path = cmds.getAttr(n + '.fileTextureName')
            fileNode = code + path[1:]
            cmds.setAttr(n + '.fileTextureName', fileNode, type='string')


class ThQWToolBoxTransferSkinWeight(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxTransferSkinWeight, self).__init__(label='轉移 skin weight', check=check)
        self.topBotton.copyUi(ThQWToolBoxTransferSkinWeight)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('多對多/ 多對一')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ltlMeshList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ltlMeshList)
        fIndex += 1
        button = QtWidgets.QPushButton('交換列表位置')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        button.clicked.connect(self.exchangeList)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, button)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源骨骼列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ltlOutput = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ltlOutput)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標骨骼列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ltlInput = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ltlInput)
        fIndex += 1
        label = QtWidgets.QLabel(' 傳遞權重值: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ltlWeight = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ltlWeight)
        fIndex += 1
        self.ltlUseOm2 = QtWidgets.QCheckBox('使用 om2 設定權重')
        self.ltlUseOm2.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ltlUseOm2)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.ltlApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('拆分權重值')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源模型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.disOutputMesh = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.disOutputMesh)
        self.disOutputMesh.inputButton.clicked.connect(self.disInputJoint)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源骨頭列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.disOutputJointList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.disOutputJointList)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.disInputMesh = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.disInputMesh)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標骨頭列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.disInputJointList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.disInputJointList)
        fIndex += 1
        self.doPruneWeightsArgList = QtWidgets.QCheckBox('修剪權重參數列表')
        self.doPruneWeightsArgList.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.doPruneWeightsArgList)
        fIndex += 1
        self.disUseOm2 = QtWidgets.QCheckBox('使用 om2 設定權重')
        self.disUseOm2.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.disUseOm2)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('拆分')
        button.clicked.connect(self.disApply)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('返回')
        button.clicked.connect(self.disApplyBack)
        layout2.addWidget(button)

    @thDoUndo
    def disApplyBack(self):
        THMoveSkinWeightOm2(objs=self.disInputMesh.getData(), old_joint_list=self.disOutputJointList.getData(), new_joint_list=self.disInputJointList.getData(), opacity=1)

    @thDoUndo
    def disApply(self):
        ThTwoObjWeightBlend(refObj=self.disOutputMesh.getData(), mainObjList=self.disInputMesh.getData(), refJointList=self.disOutputJointList.getData(), mainJointList=self.disInputJointList.getData(), om2=self.disUseOm2.isChecked(), doPruneWeightsArgList=self.doPruneWeightsArgList.isChecked())

    def disInputJoint(self):
        sel = cmds.ls(sl=True)
        jointList = thFindSkinJoint(sel)
        self.disOutputJointList.setData(jointList)

    @thDoUndo
    def ltlApply(self):
        if self.ltlUseOm2.isChecked():
            THMoveSkinWeightOm2(objs=self.ltlMeshList.getData(), old_joint_list=self.ltlOutput.getData(), new_joint_list=self.ltlInput.getData(), opacity=self.ltlWeight.value())
        else:
            THMoveSkinWeight(objs=self.ltlMeshList.getData(), old_joint_list=self.ltlOutput.getData(), new_joint_list=self.ltlInput.getData(), opacity=self.ltlWeight.value())

    def exchangeList(self):
        list1 = self.ltlOutput.getData()
        list2 = self.ltlInput.getData()
        self.ltlOutput.setData(list2)
        self.ltlInput.setData(list1)


class ThQWToolBoxWeightSpecification(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxWeightSpecification, self).__init__(label='權重規範', check=check)
        self.topBotton.copyUi(ThQWToolBoxWeightSpecification)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('四捨五入')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 小數點位數: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.point = ThQSpinBox(value_=6)
        layout3.addWidget(self.point, 40)
        button = QtWidgets.QPushButton('選擇模型執行')
        button.clicked.connect(self.roundingApply)
        layout3.addWidget(button, 60)
        grpBox = QtWidgets.QGroupBox('Influences')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 讀取: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        button = QtWidgets.QPushButton('打印當前值')
        button.clicked.connect(thPrintMaxInfluencesData)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        button = QtWidgets.QPushButton('打印實際需要值')
        button.clicked.connect(self.printMax)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 計算並設置: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.influences = ThQSpinBox(value_=30)
        layout3.addWidget(self.influences, 40)
        button = QtWidgets.QPushButton('選擇模型執行')
        button.clicked.connect(self.setApply)
        layout3.addWidget(button, 60)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 設置全部節點屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.influencesAll = ThQSpinBox(value_=30)
        layout3.addWidget(self.influencesAll, 40)
        button = QtWidgets.QPushButton('直接執行')
        button.clicked.connect(self.influencesAllApply)
        layout3.addWidget(button, 60)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        label = QtWidgets.QLabel(' maintain max influences: ')
        layout1.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('啟用')
        button.clicked.connect(lambda : self.maintainInfluencesApply(1))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('關閉')
        button.clicked.connect(lambda : self.maintainInfluencesApply(0))
        layout2.addWidget(button)

    @thDoUndo
    def maintainInfluencesApply(self, data):
        nodeList = cmds.ls(type='skinCluster')
        for node in nodeList:
            cmds.setAttr(node + '.maintainMaxInfluences', data)

    @thDoUndo
    def influencesAllApply(self):
        data = self.influencesAll.value()
        nodeList = cmds.ls(type='skinCluster')
        for node in nodeList:
            cmds.setAttr(node + '.maxInfluences', data)

    @thDoUndo
    def roundingApply(self):
        thDoRoundSkinWeight(cmds.ls(sl=True), self.point.value())

    @thDoUndo
    def printMax(self):
        cif = THCheckInfluences(cmds.ls(sl=True))
        cif.print_max_inf()
        cif.select_max_inf_vtx()
        self.influences.setValue(cif.max_inf)

    @thDoUndo
    def setApply(self):
        thSetSkinWeightInfluences(cmds.ls(sl=True), self.influences.value())


class ThEditCtrlColorData(object):
    colorDataList = [
     [
      (100, 100, 100), 0], [(0, 0, 0), 1], [(255, 0, 0), 13],
     [
      (155, 0, 40), 4], [(63, 34, 31), 11], [(138, 72, 51), 10],
     [
      (228, 172, 121), 21], [(255, 255, 102), 22], [(105, 161, 48), 26], [(0, 70, 25), 7],
     [
      (0, 153, 84), 23], [(0, 255, 0), 14], [(0, 4, 96), 5],
     [
      (0, 65, 153), 15], [(48, 103, 161), 29], [(48, 161, 161), 28],
     [
      (0, 0, 255), 6], [(102, 230, 255), 18], [(111, 48, 161), 30], [(161, 48, 106), 31]]


class ThQWToolBoxEditCtrl(ThQWToolBox, ThEditCtrlColorData, ThCtrlStyleListData):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxEditCtrl, self).__init__(label='控制器工具集', check=check)
        self.topBotton.copyUi(ThQWToolBoxEditCtrl)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('創建控制器')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.ctrlComboBox = ThQComboBox()
        for label in self.ctrlStyleList:
            self.ctrlComboBox.addItem(label[0])

        self.ctrlComboBox.setInputMaxWidth()
        layout1.addWidget(self.ctrlComboBox, 70)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.createCtrl)
        layout1.addWidget(button, 30)
        grpBox = QtWidgets.QGroupBox('編輯控制器')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.outputList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.outputList)
        fIndex += 1
        label = QtWidgets.QLabel(' translate: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.move = ThQDoubleSpinBox(value_=2)
        layout3.addWidget(self.move, 31)
        button = QtWidgets.QPushButton('X')
        button.clicked.connect(lambda : self.moveApply('x'))
        layout3.addWidget(button, 23)
        button = QtWidgets.QPushButton('Y')
        button.clicked.connect(lambda : self.moveApply('y'))
        layout3.addWidget(button, 23)
        button = QtWidgets.QPushButton('Z')
        button.clicked.connect(lambda : self.moveApply('z'))
        layout3.addWidget(button, 23)
        fIndex += 1
        label = QtWidgets.QLabel(' rotate: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.rotate = ThQDoubleSpinBox(value_=45)
        layout3.addWidget(self.rotate, 31)
        button = QtWidgets.QPushButton('X')
        button.clicked.connect(lambda : self.rotateApply('x'))
        layout3.addWidget(button, 23)
        button = QtWidgets.QPushButton('Y')
        button.clicked.connect(lambda : self.rotateApply('y'))
        layout3.addWidget(button, 23)
        button = QtWidgets.QPushButton('Z')
        button.clicked.connect(lambda : self.rotateApply('z'))
        layout3.addWidget(button, 23)
        fIndex += 1
        label = QtWidgets.QLabel(' scale: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.scale = ThQDoubleSpinBox(value_=2)
        layout3.addWidget(self.scale, 60)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.scaleApply)
        layout3.addWidget(button, 40)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.colorList1 = self.colorDataList[:10]
        for n in self.colorList1:
            button = QtWidgets.QPushButton()
            button.setStyleSheet(('min-width: 5px;background-color: rgb{};').format(n[0]))
            button.clicked.connect(partial(self.setColor, n[1]))
            layout2.addWidget(button)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.colorList2 = self.colorDataList[10:]
        for n in self.colorList2:
            button = QtWidgets.QPushButton()
            button.setStyleSheet(('min-width: 5px;background-color: rgb{};').format(n[0]))
            button.clicked.connect(partial(self.setColor, n[1]))
            layout2.addWidget(button)

        grpBox = QtWidgets.QGroupBox('工具集')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.funcComboBox = ThQComboBox()
        self.setFuncList()
        for label in self.funcList:
            self.funcComboBox.addItem(label[0])

        self.funcComboBox.setInputMaxWidth()
        layout1.addWidget(self.funcComboBox, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.appFuncListOpen)
        layout1.addWidget(button, 20)

    @thDoUndo
    def appFuncListOpen(self):
        index = self.funcComboBox.currentIndex()
        eval(self.funcList[index][1])

    def setFuncList(self):
        self.funcList = [
         [
          '刪除約束 — (選擇物件執行)', 'thDeleteConstrainNode(cmds.ls(sl=True))'],
         [
          '斷開/ 恢復 物件連接1 — (選擇物件執行)', 'ThDisconnectConnect("disconnectAttr_data1").switchF(cmds.ls(sl=True))'],
         [
          '斷開/ 恢復 物件連接2 — (選擇物件執行)', 'ThDisconnectConnect("disconnectAttr_data2").switchF(cmds.ls(sl=True))'],
         [
          '傳遞連接 — (先選擇主要物件後加選物件列表)', 'ThDisconnectConnect().transferF(cmds.ls(sl=True)[0],cmds.ls(sl=True)[1:])'],
         [
          '創建 group — (選擇物件執行)', 'cmds.select(thLocatorGrp(cmds.ls(sl=True)), r=True)'],
         [
          '清理層級下無作用的 group — (選擇主要父物件執行)', 'ThDelNoneConGrp(cmds.ls(sl=True))'],
         [
          '連接 locator — (選擇 group 執行)', 'ThDuplicateWithoutChildrenCon(cmds.ls(sl=True)).createConLocF(False)'],
         [
          '連接 locator(層級) — (選擇 group 執行)', 'ThDuplicateWithoutChildrenCon(cmds.ls(sl=True)).createConLocF(True)'],
         [
          'Soft to cluster — (選擇頂點執行)', 'thSoftToCluster()'],
         [
          '頂點創建毛囊 — (選擇頂點執行)', 'ThVertexFollicle(cmds.ls(sl=True,fl=True)).apply()'],
         [
          '頂點創建定位器 — (選擇頂點執行)', 'thVertexCreateLoc(cmds.ls(sl=True, fl=True))'],
         [
          '回歸初始值 — (選擇物件執行)', 'thCtrlDefaultPose(cmds.ls(sl=True))'],
         [
          '替換控制器造型 — (最後加選參考物件)', 'thReplaceCurveShape(cmds.ls(sl=True))'],
         [
          '設置為不能移動 — (選擇物件執行)', 'thSetNoAni(cmds.ls(sl=True))'],
         [
          '在物件周圍創建 joint (樣式1) — (直接執行)', 'TFindVtxMaxDis(cmds.ls(sl=True,fl=True)).create("anise")'],
         [
          '在物件周圍創建 joint (樣式2) — (直接執行)', 'TFindVtxMaxDis(cmds.ls(sl=True,fl=True)).create()'],
         [
          '篩選有數值的 transform — (選擇物件執行)', 'thFilterTransformMove()'],
         [
          '複製控制器並連接屬性(連接) — (選擇物件執行)', 'ThDuplicateWithoutChildrenCon(cmds.ls(sl=True)).createConCtrlF(True,False)'],
         [
          '複製控制器並連接屬性(連接, 連動) — (選擇物件執行)', 'ThDuplicateWithoutChildrenCon(cmds.ls(sl=True)).createConCtrlF(True,True)'],
         [
          '物件變換屬性添加權重設定 — (選擇物件執行，物件需要有父、子層級)', 'ThDuplicateObjConGrpWeight(cmds.ls(sl=True))'],
         [
          '分割屬性權重1 — (選擇物件與屬性執行)', 'ThSplitAttrData(sysId=1).createF()'],
         [
          '分割屬性權重2 — (選擇物件與屬性執行)', 'ThSplitAttrData(sysId=2).createF()'],
         [
          '創建 in between 屬性 — (選擇物件與屬性執行)', 'ThCreateInBetweenAttr()']]

    def createCtrl(self):
        index = self.ctrlComboBox.currentIndex()
        thMyController(style=self.ctrlStyleList[index][1])

    @thDoUndo
    def moveApply(self, xyz='x'):
        appList = cmds.ls(sl=True)
        if not appList:
            appList = self.outputList.getData()
        if not appList:
            return
        TEditCvShape(appList).move(xyz, self.move.value())

    @thDoUndo
    def rotateApply(self, xyz='x'):
        appList = cmds.ls(sl=True)
        if not appList:
            appList = self.outputList.getData()
        if not appList:
            return
        data = self.rotate.value()
        app_dict = {'x': [data, 0, 0], 'y': [0, data, 0], 'z': [0, 0, data]}
        TEditCvShape(appList).rotate(app_dict[xyz])

    @thDoUndo
    def scaleApply(self):
        appList = cmds.ls(sl=True)
        if not appList:
            appList = self.outputList.getData()
        if not appList:
            return
        TEditCvShape(appList).scale(self.scale.value())

    @thDoUndo
    def setColor(self, colorData):
        appList = cmds.ls(sl=True)
        if not appList:
            appList = self.outputList.getData()
        if not appList:
            return
        thSetCtrlColor(appList, colorData)


class ThQWToolBoxRotateOrder(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxRotateOrder, self).__init__(label='Rotate order', check=check)
        self.topBotton.copyUi(ThQWToolBoxRotateOrder)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.list_ = [
         [
          'xyz', 0], ['yzx', 1], ['zxy', 2],
         [
          'xzy', 3], ['yxz', 4], ['zyx', 5]]
        self.labelList = ThQComboBox()
        for label in self.list_:
            self.labelList.addItem(label[0])

        self.labelList.setInputMaxWidth()
        layout1.addWidget(self.labelList, 40)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button, 60)

    def apply(self):
        sel = cmds.ls(sl=True)
        index = self.labelList.currentIndex()
        for n in sel:
            cmds.setAttr(n + '.rotateOrder', self.list_[index][1])


class ThQWToolBoxLimitInformation(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxLimitInformation, self).__init__(label='Limit information', check=check)
        self.topBotton.copyUi(ThQWToolBoxLimitInformation)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('Translate')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' X: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataTx = ThQDoubleSpinBox(value_=-1)
        self.minDataTx.setEnabled(False)
        layout3.addWidget(self.minDataTx, 30)
        self.minCheckTx = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckTx, 10)
        self.maxCheckTx = QtWidgets.QCheckBox()
        self.maxCheckTx.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckTx, 10)
        self.maxDataTx = ThQDoubleSpinBox(value_=1)
        self.maxDataTx.setEnabled(False)
        layout3.addWidget(self.maxDataTx, 30)
        self.minCheckTx.stateChanged.connect(self.minDataTx.setEnabled)
        self.maxCheckTx.stateChanged.connect(self.maxDataTx.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('tx'))
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' Y: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataTy = ThQDoubleSpinBox(value_=-1)
        self.minDataTy.setEnabled(False)
        layout3.addWidget(self.minDataTy, 30)
        self.minCheckTy = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckTy, 10)
        self.maxCheckTy = QtWidgets.QCheckBox()
        self.maxCheckTy.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckTy, 10)
        self.maxDataTy = ThQDoubleSpinBox(value_=1)
        self.maxDataTy.setEnabled(False)
        layout3.addWidget(self.maxDataTy, 30)
        self.minCheckTy.stateChanged.connect(self.minDataTy.setEnabled)
        self.maxCheckTy.stateChanged.connect(self.maxDataTy.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('ty'))
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' Z: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataTz = ThQDoubleSpinBox(value_=-1)
        self.minDataTz.setEnabled(False)
        layout3.addWidget(self.minDataTz, 30)
        self.minCheckTz = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckTz, 10)
        self.maxCheckTz = QtWidgets.QCheckBox()
        self.maxCheckTz.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckTz, 10)
        self.maxDataTz = ThQDoubleSpinBox(value_=1)
        self.maxDataTz.setEnabled(False)
        layout3.addWidget(self.maxDataTz, 30)
        self.minCheckTz.stateChanged.connect(self.minDataTz.setEnabled)
        self.maxCheckTz.stateChanged.connect(self.maxDataTz.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('tz'))
        layout3.addWidget(button, 20)
        grpBox = QtWidgets.QGroupBox('Rotate')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' X: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataRx = ThQDoubleSpinBox(value_=-45)
        self.minDataRx.setEnabled(False)
        layout3.addWidget(self.minDataRx, 30)
        self.minCheckRx = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckRx, 10)
        self.maxCheckRx = QtWidgets.QCheckBox()
        self.maxCheckRx.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckRx, 10)
        self.maxDataRx = ThQDoubleSpinBox(value_=45)
        self.maxDataRx.setEnabled(False)
        layout3.addWidget(self.maxDataRx, 30)
        self.minCheckRx.stateChanged.connect(self.minDataRx.setEnabled)
        self.maxCheckRx.stateChanged.connect(self.maxDataRx.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('rx'))
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' Y: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataRy = ThQDoubleSpinBox(value_=-45)
        self.minDataRy.setEnabled(False)
        layout3.addWidget(self.minDataRy, 30)
        self.minCheckRy = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckRy, 10)
        self.maxCheckRy = QtWidgets.QCheckBox()
        self.maxCheckRy.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckRy, 10)
        self.maxDataRy = ThQDoubleSpinBox(value_=45)
        self.maxDataRy.setEnabled(False)
        layout3.addWidget(self.maxDataRy, 30)
        self.minCheckRy.stateChanged.connect(self.minDataRy.setEnabled)
        self.maxCheckRy.stateChanged.connect(self.maxDataRy.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('ry'))
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' Z: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataRz = ThQDoubleSpinBox(value_=-45)
        self.minDataRz.setEnabled(False)
        layout3.addWidget(self.minDataRz, 30)
        self.minCheckRz = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckRz, 10)
        self.maxCheckRz = QtWidgets.QCheckBox()
        self.maxCheckRz.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckRz, 10)
        self.maxDataRz = ThQDoubleSpinBox(value_=45)
        self.maxDataRz.setEnabled(False)
        layout3.addWidget(self.maxDataRz, 30)
        self.minCheckRz.stateChanged.connect(self.minDataRz.setEnabled)
        self.maxCheckRz.stateChanged.connect(self.maxDataRz.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('rz'))
        layout3.addWidget(button, 20)
        grpBox = QtWidgets.QGroupBox('Scale')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' X: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataSx = ThQDoubleSpinBox(value_=-1)
        self.minDataSx.setEnabled(False)
        layout3.addWidget(self.minDataSx, 30)
        self.minCheckSx = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckSx, 10)
        self.maxCheckSx = QtWidgets.QCheckBox()
        self.maxCheckSx.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckSx, 10)
        self.maxDataSx = ThQDoubleSpinBox(value_=1)
        self.maxDataSx.setEnabled(False)
        layout3.addWidget(self.maxDataSx, 30)
        self.minCheckSx.stateChanged.connect(self.minDataSx.setEnabled)
        self.maxCheckSx.stateChanged.connect(self.maxDataSx.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('sx'))
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' Y: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataSy = ThQDoubleSpinBox(value_=-1)
        self.minDataSy.setEnabled(False)
        layout3.addWidget(self.minDataSy, 30)
        self.minCheckSy = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckSy, 10)
        self.maxCheckSy = QtWidgets.QCheckBox()
        self.maxCheckSy.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckSy, 10)
        self.maxDataSy = ThQDoubleSpinBox(value_=1)
        self.maxDataSy.setEnabled(False)
        layout3.addWidget(self.maxDataSy, 30)
        self.minCheckSy.stateChanged.connect(self.minDataSy.setEnabled)
        self.maxCheckSy.stateChanged.connect(self.maxDataSy.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('sy'))
        layout3.addWidget(button, 20)
        fIndex += 1
        label = QtWidgets.QLabel(' Z: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.minDataSz = ThQDoubleSpinBox(value_=-1)
        self.minDataSz.setEnabled(False)
        layout3.addWidget(self.minDataSz, 30)
        self.minCheckSz = QtWidgets.QCheckBox()
        layout3.addWidget(self.minCheckSz, 10)
        self.maxCheckSz = QtWidgets.QCheckBox()
        self.maxCheckSz.setLayoutDirection(QtCore.Qt.RightToLeft)
        layout3.addWidget(self.maxCheckSz, 10)
        self.maxDataSz = ThQDoubleSpinBox(value_=1)
        self.maxDataSz.setEnabled(False)
        layout3.addWidget(self.maxDataSz, 30)
        self.minCheckSz.stateChanged.connect(self.minDataSz.setEnabled)
        self.maxCheckSz.stateChanged.connect(self.maxDataSz.setEnabled)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(lambda : self.apply('sz'))
        layout3.addWidget(button, 20)

    @thDoUndo
    def apply(self, attr):
        appDict = {'tx': {'MinData': self.minDataTx, 
                  'MaxData': self.maxDataTx, 
                  'IfMin': self.minCheckTx, 
                  'IfMax': self.maxCheckTx}, 
           'ty': {'MinData': self.minDataTy, 
                  'MaxData': self.maxDataTy, 
                  'IfMin': self.minCheckTy, 
                  'IfMax': self.maxCheckTy}, 
           'tz': {'MinData': self.minDataTz, 
                  'MaxData': self.maxDataTz, 
                  'IfMin': self.minCheckTz, 
                  'IfMax': self.maxCheckTz}, 
           'rx': {'MinData': self.minDataRx, 
                  'MaxData': self.maxDataRx, 
                  'IfMin': self.minCheckRx, 
                  'IfMax': self.maxCheckRx}, 
           'ry': {'MinData': self.minDataRy, 
                  'MaxData': self.maxDataRy, 
                  'IfMin': self.minCheckRy, 
                  'IfMax': self.maxCheckRy}, 
           'rz': {'MinData': self.minDataRz, 
                  'MaxData': self.maxDataRz, 
                  'IfMin': self.minCheckRz, 
                  'IfMax': self.maxCheckRz}, 
           'sx': {'MinData': self.minDataSx, 
                  'MaxData': self.maxDataSx, 
                  'IfMin': self.minCheckSx, 
                  'IfMax': self.maxCheckSx}, 
           'sy': {'MinData': self.minDataSy, 
                  'MaxData': self.maxDataSy, 
                  'IfMin': self.minCheckSy, 
                  'IfMax': self.maxCheckSy}, 
           'sz': {'MinData': self.minDataSz, 
                  'MaxData': self.maxDataSz, 
                  'IfMin': self.minCheckSz, 
                  'IfMax': self.maxCheckSz}}
        THLimitInformation(cmds.ls(sl=True), attr, [
         appDict[attr]['MinData'].value(),
         appDict[attr]['MaxData'].value()], [
         appDict[attr]['IfMin'].isChecked(),
         appDict[attr]['IfMax'].isChecked()])


class ThQWToolUiCtrl(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolUiCtrl, self).__init__(label='手柄控制器', check=check)
        self.topBotton.copyUi(ThQWToolUiCtrl)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2, 85)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.lebel = QtWidgets.QLineEdit()
        self.lebel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.lebel)
        fIndex += 1
        label = QtWidgets.QLabel(' 造型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.styleList = [
         [
          '十字型', 'nine'],
         [
          '六角形(上)', 'six up'], ['六角形(下)', 'six dn'],
         [
          '六角形(左)', 'six left'], ['六角形(右)', 'six right'],
         [
          '上下', 'up dn'], ['左右', 'left right'],
         [
          '上', 'up'], ['下', 'dn'], ['左', 'left'], ['右', 'right']]
        self.style = ThQComboBox()
        for n in self.styleList:
            self.style.addItem(n[0])

        self.style.setInputMaxWidth()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.style)
        button = QtWidgets.QPushButton('執行')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        button.clicked.connect(self.apply)
        layout1.addWidget(button, 15)

    @thDoUndo
    def apply(self):
        ThRigCreateCtrl(self.lebel.text(), self.styleList[self.style.currentIndex()][1])


class ThQWToolBoxHelpTxt(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxHelpTxt, self).__init__(label='Help', check=check)
        self.topBotton.copyUi(ThQWToolBoxHelpTxt)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.lebel = QtWidgets.QLineEdit()
        self.lebel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.lebel)
        fIndex += 1
        label = QtWidgets.QLabel(' 大小: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.size = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.size)
        fIndex += 1
        label = QtWidgets.QLabel(' 旋轉: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.rotateX = ThQDoubleSpinBox(value_=-90)
        layout3.addWidget(self.rotateX)
        self.rotateY = ThQDoubleSpinBox(value_=0)
        layout3.addWidget(self.rotateY)
        self.rotateZ = ThQDoubleSpinBox(value_=0)
        layout3.addWidget(self.rotateZ)
        fIndex += 1
        label = QtWidgets.QLabel(' 字形: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.fontComboBox = ThQFontComboBox()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.fontComboBox)
        fIndex += 1
        self.centerPivot = QtWidgets.QCheckBox('center pivot')
        self.centerPivot.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.centerPivot)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        thCreateTxt(txt=self.lebel.text(), objs=cmds.ls(sl=True), size=self.size.value(), font=self.fontComboBox.currentFont().family(), isCenterPivot=self.centerPivot.isChecked(), rotate=[
         self.rotateX.value(), self.rotateY.value(), self.rotateZ.value()])


class ThQWToolBoxCtrlBlendShape(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxCtrlBlendShape, self).__init__(label='Edit blend shape ctrl', check=check)
        self.topBotton.copyUi(ThQWToolBoxCtrlBlendShape)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標模型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inputMesh = ThQLineBox(False)
        self.inputMesh.inputButton.clicked.connect(self.sbsInBsNode)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inputMesh)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標節點: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inputNode = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inputNode)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.getAttrModeList = [
         [
          'add shape', 'addShape'], ['from shape editor', 'fromAttr']]
        self.getAttrMode = ThQRadioButtonBox([ n[0] for n in self.getAttrModeList ], 1, 'V')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.getAttrMode)
        fIndex += 1
        self.inputAttr = ThQLineBox(ifShowHideButton=False, ifShowSelectButton=False)
        self.inputAttr.setData = self.setData
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inputAttr)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        label = QtWidgets.QLabel('* 選擇控制器執行')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('上左')
        button.clicked.connect(lambda : self.apply('upLeft'))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('上')
        button.clicked.connect(lambda : self.apply('up'))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('上右')
        button.clicked.connect(lambda : self.apply('upRight'))
        layout2.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('左')
        button.clicked.connect(lambda : self.apply('left'))
        layout2.addWidget(button)
        widget = QtWidgets.QWidget()
        layout2.addWidget(widget)
        button = QtWidgets.QPushButton('右')
        button.clicked.connect(lambda : self.apply('right'))
        layout2.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('下左')
        button.clicked.connect(lambda : self.apply('dnLeft'))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('下')
        button.clicked.connect(lambda : self.apply('dn'))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('下右')
        button.clicked.connect(lambda : self.apply('dnRight'))
        layout2.addWidget(button)

    def sbsInBsNode(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        nodeList = thFindBlendShapeNode(selectList[0])
        if not nodeList:
            return
        self.inputNode.setData(nodeList[0])

    def setData(self):
        mode = self.getAttrModeList[self.getAttrMode.isCheckedId()][1]
        sel = None
        if mode == 'addShape':
            selectList = cmds.ls(sl=True)
            if not selectList:
                return
            sel = selectList[0]
        else:
            sel = ThEditBlendShape().findSelectListIdAttrOneF()
            if not sel:
                return
        self.inputAttr.lineEdit.setText(sel)
        return

    @thDoUndo
    def apply(self, mode):
        sel = cmds.ls(sl=True)
        if not sel:
            return
        ThEditBlendShape().ctrlF(self.inputNode.getData(), self.inputMesh.getData(), self.inputAttr.lineEdit.text(), sel[0], mode, self.getAttrModeList[self.getAttrMode.isCheckedId()][1])


class ThCtrlColorQWidget(QtWidgets.QWidget, ThEditCtrlColorData):

    def __init__(self, ui):
        super(ThCtrlColorQWidget, self).__init__()
        self.ui = ui
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.colorList1 = self.colorDataList[:10]
        for n in self.colorList1:
            button = QtWidgets.QPushButton()
            button.setStyleSheet(('min-width: 5px;background-color: rgb{};').format(n[0]))
            button.clicked.connect(partial(self.setColor, n[1]))
            layout2.addWidget(button)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.colorList2 = self.colorDataList[10:]
        for n in self.colorList2:
            button = QtWidgets.QPushButton()
            button.setStyleSheet(('min-width: 5px;background-color: rgb{};').format(n[0]))
            button.clicked.connect(partial(self.setColor, n[1]))
            layout2.addWidget(button)

    def setColor(self, data):
        self.ui.setValue(data)


class ThQWToolBoxCtrlToObject(ThQWToolBox, ThCtrlStyleListData):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxCtrlToObject, self).__init__(label='Ctrl objects', check=check)
        self.topBotton.copyUi(ThQWToolBoxCtrlToObject)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 後綴: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.suffix = QtWidgets.QLineEdit()
        self.suffix.setText('_ctrl')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.suffix)
        fIndex += 1
        self.ifUseObjectName = QtWidgets.QCheckBox('使用物件名稱做命名')
        self.ifUseObjectName.setChecked(False)
        self.ifUseObjectName.stateChanged.connect(self.setUseObjectNameUi)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifUseObjectName)
        fIndex += 1
        label = QtWidgets.QLabel(' 替換字符: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.replaceStr = QtWidgets.QLineEdit()
        self.replaceStr.setEnabled(False)
        self.replaceStr.setText('_joint')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.replaceStr)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器造型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlStyle = ThQComboBox()
        for label in self.ctrlStyleList:
            self.ctrlStyle.addItem(label[0])

        self.ctrlStyle.setInputMaxWidth()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlStyle)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器方向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlAxialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.ctrlAxial = ThQRadioButtonBox([ n[0] for n in self.ctrlAxialList ], 1, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlAxial)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.conModeList = [
         [
          'constrain', 'constrain'], ['connect', 'connect'],
         [
          'parent', 'parent'], ['not', 'not']]
        self.conMode = ThQComboBox()
        for label in self.conModeList:
            self.conMode.addItem(label[0])

        self.conMode.setInputMaxWidth()
        self.conMode.activated.connect(self.setConModeUi)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.conMode)
        fIndex += 1
        self.conModeWidgetList = []
        label = QtWidgets.QLabel(' 控制屬性: ')
        self.conModeWidgetList.append(label)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.conAttr = ThQCheckBox([
         'translate', 'rotate', 'scale'], [
         True, True, True], 'V')
        self.conModeWidgetList.append(self.conAttr)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.conAttr)
        fIndex += 1
        self.ifConScaleAttr = QtWidgets.QCheckBox('constrain scale attr')
        self.conModeWidgetList.append(self.ifConScaleAttr)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifConScaleAttr)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 鎖定屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.lockAttr = ThQCheckBox([
         'translate', 'rotate', 'scale', 'visibility'], [
         False, False, False, True], 'V')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.lockAttr)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        self.ifMainGrp = QtWidgets.QCheckBox('創建主要 group')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifMainGrp)
        fIndex += 1
        self.ifCtrlFollowObj = QtWidgets.QCheckBox('控制器軸向與物件對齊')
        self.ifCtrlFollowObj.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifCtrlFollowObj)
        fIndex += 1
        self.ifParent = QtWidgets.QCheckBox('建立 parent')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifParent)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器大小: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlSize = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlSize)
        fIndex += 1
        label = QtWidgets.QLabel(' 新增群組數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlGrp = ThQSpinBox(value_=3)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlGrp)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器顏色: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.ctrlColor = ThQSpinBox(value_=18)
        layout3.addWidget(self.ctrlColor, 40)
        self.ctrlColorButton = QtWidgets.QPushButton('顏色選擇器')
        layout3.addWidget(self.ctrlColorButton, 60)
        fIndex += 1
        self.colorWidget = ThCtrlColorQWidget(self.ctrlColor)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, self.colorWidget)
        self.ctrlColorButton.clicked.connect(self.setCtrlColorButton)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        button = QtWidgets.QPushButton('創建於選擇物件')
        button.clicked.connect(lambda : self.apply(1))
        layout1.addWidget(button)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        button = QtWidgets.QPushButton('創建於選擇物件的層級以下')
        button.clicked.connect(lambda : self.apply(2))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 編輯當前創建內容 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇到: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('物件')
        button.clicked.connect(self.selectObj)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('控制器')
        button.clicked.connect(self.selectCtrl)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('轉換為頂點')
        button.clicked.connect(self.toVtx)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('建立 parent(直接執行)')
        button.clicked.connect(self.parentCtrl)
        layout1.addWidget(button)

    def toVtx(self):
        mel.eval('selectCurveCV("all")')

    @thDoUndo
    def selectObj(self):
        cmds.select(self.tcto.obj_list, r=True)

    @thDoUndo
    def selectCtrl(self):
        cmds.select(self.tcto.new_ctrl_list, r=True)

    @thDoUndo
    def parentCtrl(self):
        self.tcto.ctrl_parent()

    @thDoUndo
    def apply(self, mode):
        self.tcto = THCtrlToObject(obj_list=cmds.ls(sl=True), name=self.addLabel.text(), ctrl_style=self.ctrlStyleList[self.ctrlStyle.currentIndex()][1], ctrl_axial=self.ctrlAxialList[self.ctrlAxial.isCheckedId()][1], ctrl_method=self.conModeList[self.conMode.currentIndex()][1], rig_TRS=self.conAttr.isCheckedList(), if_use_constrain_scale=self.ifConScaleAttr.isChecked(), lock_hide_attr=self.lockAttr.isCheckedList(), ctrl_size=self.ctrlSize.value(), ctrl_color=self.ctrlColor.value(), grp_layout=self.ctrlGrp.value(), if_create_main_grp=self.ifMainGrp.isChecked(), adsorption_mode='tr' if self.ifCtrlFollowObj.isChecked() else 't', if_parent=self.ifParent.isChecked(), if_use_obj_name=self.ifUseObjectName.isChecked(), replace_str=self.replaceStr.text().strip(), suffix=self.suffix.text())
        app = self.tcto.create if mode == 1 else self.tcto.batch_create
        app()
        cmds.select(self.tcto.new_ctrl_list, r=True)

    def setCtrlColorButton(self):
        self.colorWidget.setHidden(not self.colorWidget.isHidden())

    def setConModeUi(self):
        conMode = self.conModeList[self.conMode.currentIndex()][1]
        if conMode == 'constrain':
            self.ifConScaleAttr.setEnabled(True)
        else:
            if conMode == 'connect':
                self.ifConScaleAttr.setEnabled(False)
                self.ifConScaleAttr.setChecked(False)
            if conMode == 'constrain' or conMode == 'connect':
                for n in self.conModeWidgetList:
                    n.show()

            else:
                for n in self.conModeWidgetList:
                    n.hide()

    def setUseObjectNameUi(self):
        app = self.ifUseObjectName.isChecked()
        self.replaceStr.setEnabled(app)
        self.addLabel.setEnabled(not app)


class ThQWToolBoxObjToCtrl(ThQWToolBox, ThCtrlStyleListData):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxObjToCtrl, self).__init__(label='Objects ctrl', check=check)
        self.topBotton.copyUi(ThQWToolBoxObjToCtrl)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 定位器: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.locator = ThQLineBoxList(ifShowHideButton=False, flatten=True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.locator)
        fIndex += 1
        label = QtWidgets.QLabel(' 旋轉控制器:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.rotateCtrl = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.rotateCtrl)
        fIndex += 1
        label = QtWidgets.QLabel(' 創建模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.createModeList = [
         [
          '控制器', 'ctrl'], ['鎖定位移的控制器', 'ctrl follow'], ['只有定位器', 'not']]
        self.createMode = ThQComboBox()
        for label in self.createModeList:
            self.createMode.addItem(label[0])

        self.createMode.setInputMaxWidth()
        self.createMode.activated.connect(self.setCreateModeUi)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.createMode)
        fIndex += 1
        self.createModeWidgets = ThQFrameGrp()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, self.createModeWidgets)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.createModeWidgets.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器造型: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlStyle = ThQComboBox()
        for label in self.ctrlStyleList:
            self.ctrlStyle.addItem(label[0])

        self.ctrlStyle.setInputMaxWidth()
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.ctrlStyle)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器方向: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlAxialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.ctrlAxial = ThQRadioButtonBox([ n[0] for n in self.ctrlAxialList ], 2, 'H')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.ctrlAxial)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器大小: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlSize = ThQDoubleSpinBox(value_=1)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.ctrlSize)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器層級數: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlGrpLayrt = ThQSpinBox(value_=3)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.ctrlGrpLayrt)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器顏色: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        layout3_1 = QtWidgets.QHBoxLayout()
        layout3_1.setMargin(0)
        layout3_1.setSpacing(2)
        layout2_1.setLayout(fIndex_1, QtWidgets.QFormLayout.FieldRole, layout3_1)
        self.ctrlColor = ThQSpinBox(value_=18)
        layout3_1.addWidget(self.ctrlColor, 40)
        self.ctrlColorButton = QtWidgets.QPushButton('顏色選擇器')
        layout3_1.addWidget(self.ctrlColorButton, 60)
        fIndex_1 += 1
        self.colorWidget = ThCtrlColorQWidget(self.ctrlColor)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.SpanningRole, self.colorWidget)
        self.ctrlColorButton.clicked.connect(self.setCtrlColorButton)
        fIndex += 1
        self.ifMeshLoc = QtWidgets.QCheckBox('創建三角模型定位器')
        self.ifMeshLoc.setChecked(True)
        self.ifMeshLoc.stateChanged.connect(lambda n: self.ifMeshLocWidgets.setHidden(not n))
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifMeshLoc)
        self.ifMeshLocWidgets = ThQFrameGrp()
        layout1.addWidget(self.ifMeshLocWidgets)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.ifMeshLocWidgets.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制模式: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.meshLocConModeList = [
         [
          'skin', 'skin'], ['wrap', 'wrap'], ['not', 'not']]
        self.meshLocConMode = ThQComboBox()
        for label in self.meshLocConModeList:
            self.meshLocConMode.addItem(label[0])

        self.meshLocConMode.setInputMaxWidth()
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.meshLocConMode)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制來源:* ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.meshLocFollowOut = ThQLineBox(False)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.meshLocFollowOut)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 定位器方向: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.meshLocAxialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.meshLocAxial = ThQRadioButtonBox([ n[0] for n in self.meshLocAxialList ], 1, 'H')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.meshLocAxial)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 定位器大小: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.meshLocSize = ThQDoubleSpinBox(value_=1)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.meshLocSize)
        fIndex_1 += 1
        button = QtWidgets.QPushButton('測試定位器大小')
        button.clicked.connect(thDoUndo(lambda : THVtxLocator().test_create_vl()))
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, button)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 編輯當前創建內容 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇到: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('follicle')
        button.clicked.connect(self.selectFollicle)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('控制器')
        button.clicked.connect(self.selectCtrl)
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 統一權重 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('選擇三角定位器執行')
        button.clicked.connect(thDoUndo(lambda : THVtxLocator().unite_wight(cmds.ls(sl=True))))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 重新設定 UV 座標 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' follicle list: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.rePosFollicleList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.rePosFollicleList)
        button = QtWidgets.QPushButton('選擇三角定位器執行')
        button.clicked.connect(self.rePosApply)
        layout1.addWidget(button)

    @thDoUndo
    def rePosApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        THVtxLocator().reset_uv_pos(self.rePosFollicleList.getData(), selectList[0])

    def selectFollicle(self):
        cmds.select(self.vl.follicle_list, r=True)

    def selectCtrl(self):
        cmds.select(self.vl.new_ctrl_list, r=True)

    @thDoUndo
    def apply(self):
        self.vl = THVtxLocator(objs=self.locator.getData(), name=self.addLabel.text(), if_vl=self.ifMeshLoc.isChecked(), vl_aim=self.meshLocAxialList[self.meshLocAxial.isCheckedId()][1], vl_size=self.meshLocSize.value(), control_vl_mode=self.meshLocConModeList[self.meshLocConMode.currentIndex()][1], control_obj=self.meshLocFollowOut.getData(), rotate_obj=self.rotateCtrl.getData(), ctrl_style=self.ctrlStyleList[self.ctrlStyle.currentIndex()][1], ctrl_axial=self.ctrlAxialList[self.ctrlAxial.isCheckedId()][1], ctrl_size=self.ctrlSize.value(), ctrl_mode=self.createModeList[self.createMode.currentIndex()][1], ctrl_color=self.ctrlColor.value(), ctrl_grp_layrt=self.ctrlGrpLayrt.value())
        self.vl.create_vl_and_follicle()

    def setCreateModeUi(self):
        mode = self.createModeList[self.createMode.currentIndex()][1]
        ifHide = True if mode == 'not' or mode == 'loc joint' else False
        self.createModeWidgets.setHidden(ifHide)

    def setCtrlColorButton(self):
        self.colorWidget.setHidden(not self.colorWidget.isHidden())


class ThQWToolBoxDrivenKeySys(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxDrivenKeySys, self).__init__(label='Driven key system', check=check)
        self.topBotton.copyUi(ThQWToolBoxDrivenKeySys)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器與屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlAttr = ThQLineBoxObjAttr()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlAttr)
        fIndex += 1
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('-1')
        button.clicked.connect(lambda : self.setAttrApplyF(-1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('0')
        button.clicked.connect(lambda : self.setAttrApplyF(0))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('1')
        button.clicked.connect(lambda : self.setAttrApplyF(1))
        layout3.addWidget(button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inpList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inpList)
        fIndex += 1
        button = QtWidgets.QPushButton('讀取存檔')
        button.clicked.connect(self.getSysF)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.attrList = ThQLineBoxAttrList(False)
        self.attrList.setData(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.attrList)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        self.ifGrp = QtWidgets.QCheckBox('創建 group')
        self.ifGrp.setChecked(True)
        self.ifGrp.stateChanged.connect(self.setIfReGrpF)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifGrp)
        fIndex += 1
        self.ifReGrp = QtWidgets.QCheckBox('以控制器名稱做前綴')
        self.ifReGrp.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifReGrp)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.applyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 編輯系統 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇到: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        button = QtWidgets.QPushButton('目標列表的 group')
        button.clicked.connect(self.selGrpF)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('全部 ctrl')
        button.clicked.connect(self.selCtrlAllF)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('全部 group')
        button.clicked.connect(self.selGrpAllF)
        layout3.addWidget(button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 縮放值/ 列表:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.scaleValue = ThQDoubleSpinBox(value_=0.5)
        layout3.addWidget(self.scaleValue)
        self.scaleList = ThQLineBoxList(False)
        layout3.addWidget(self.scaleList)
        fIndex += 1
        label = QtWidgets.QLabel(' 編輯 KEY: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.editTime = ThQSpinBox(value_=10)
        layout3.addWidget(self.editTime, 20)
        button = QtWidgets.QPushButton('to frame')
        button.clicked.connect(self.toCtrlF)
        layout3.addWidget(button, 40)
        line = ThSeparationLine('V')
        layout3.addWidget(line)
        button = QtWidgets.QPushButton('to group')
        button.clicked.connect(self.toGrpF)
        layout3.addWidget(button, 40)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 重命名控制器: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.editRename = QtWidgets.QLineEdit()
        layout3.addWidget(self.editRename, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.renameF)
        layout3.addWidget(button, 20)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 刪除: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.deleteF)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('選擇本系統節點')
        button.clicked.connect(self.selSysF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('刪除工具')
        button.clicked.connect(lambda : ThDrivenKeySystemList())
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('更新數據')
        button.clicked.connect(lambda : THDrivenKeySystem().reDataF())
        layout2.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('優先選擇\n手柄工具')
        button.clicked.connect(self.handlesF)
        layout2.addWidget(button, 30)
        button = QtWidgets.QPushButton('動畫曲線\n編輯器')
        button.clicked.connect(cmds.GraphEditor)
        layout2.addWidget(button, 30)
        button = QtWidgets.QPushButton('刪除\n靜態的 KEY')
        button.clicked.connect(self.delUnitlessF)
        layout2.addWidget(button, 40)

    @thDoUndo
    def setAttrApplyF(self, value):
        ctrlAttr = self.ctrlAttr.getData()
        cmds.setAttr(ctrlAttr, value)

    @thDoUndo
    def delUnitlessF(self):
        THDrivenKeySystem().delNotKey()

    @thDoUndo
    def handlesF(self):
        ThTransformDisplay(self.getCtrlGrpListF()[1], 'handles')

    def selSysF(self):
        cmds.select('drivenKeySystem_data', r=True)

    @thDoUndo
    def deleteF(self):
        sel = cmds.ls(sl=True)
        ctrlAttr = self.ctrlAttr.getData()
        dks = THDrivenKeySystem()
        if sel:
            dks.delete([ctrlAttr], sel)
        else:
            dks.delete([ctrlAttr])

    @thDoUndo
    def renameF(self):
        ctrlAttr = self.ctrlAttr.getData()
        newName = self.editRename.text()
        data = eval(cmds.getAttr('drivenKeySystem_data.notes'))
        name = ctrlAttr.split('.')
        if cmds.objExists(name[0]):
            newName = cmds.rename(name[0], newName + '#')
        for key in data.keys():
            dataName = key.split('.')
            if dataName[0] == name[0]:
                newKey = ('{}.{}').format(newName, dataName[1])
                newDict = {newKey: data.pop(key)}
                data.update(newDict)

        cmds.setAttr('drivenKeySystem_data.notes', data, type='string')
        self.ctrlAttr.setData(('{}.{}').format(newName, name[1]))

    @thDoUndo
    def selGrpF(self):
        cmds.select(self.getCtrlGrpListF()[1], r=True)

    @thDoUndo
    def selCtrlAllF(self):
        data = eval(cmds.getAttr('drivenKeySystem_data.notes'))
        ctrlAttr = self.ctrlAttr.getData()
        cmds.select(data[ctrlAttr]['obj'], r=True)

    @thDoUndo
    def selGrpAllF(self):
        data = eval(cmds.getAttr('drivenKeySystem_data.notes'))
        ctrlAttr = self.ctrlAttr.getData()
        cmds.select(data[ctrlAttr]['grp'], r=True)

    def getCtrlGrpListF(self):
        u"""獲取 sys ctrl grp 列表"""
        data = eval(cmds.getAttr('drivenKeySystem_data.notes'))
        ctrlAttr = self.ctrlAttr.getData()
        sysObjList = data[ctrlAttr]['obj']
        sysGrpList = data[ctrlAttr]['grp']
        inpList = self.inpList.getData()
        grpList = [ sysGrpList[sysObjList.index(n)] for n in inpList ]
        return [inpList, grpList]

    @thDoUndo
    def toGrpF(self):
        ctrlGrpList = self.getCtrlGrpListF()
        thDataTransfer(refList=ctrlGrpList[0], newList=ctrlGrpList[1], clean=False, scaleList=self.scaleList.getData(), scaleValue=self.scaleValue.value())
        self.applyF()

    @thDoUndo
    def toCtrlF(self):
        if not cmds.objExists('drivenKeySystem_data'):
            return
        ctrlGrpList = self.getCtrlGrpListF()
        thCtrlDefaultPose(ctrlGrpList[0])
        cmds.setKeyframe(ctrlGrpList[0], breakdown=0, hierarchy='none', controlPoints=0, shape=0, t=1)
        thDataTransfer(refList=ctrlGrpList[1], newList=ctrlGrpList[0], clean=False, addUp=True)
        cmds.setKeyframe(ctrlGrpList[0], breakdown=0, hierarchy='none', controlPoints=0, shape=0, t=self.editTime.value())

    @thDoUndo
    def applyF(self):
        tdks = THDrivenKeySystem(ctrl_attr=self.ctrlAttr.getData(), objects=self.inpList.getData(), attr_list=self.attrList.getData(), if_prefix=self.ifReGrp.isChecked(), if_grp=self.ifGrp.isChecked())
        tdks.app()

    def getSysF(self):
        u"""讀取系統"""
        if not cmds.objExists('drivenKeySystem_data'):
            return
        ctrlAttr = self.ctrlAttr.getData()
        if not ctrlAttr:
            return
        data = eval(cmds.getAttr('drivenKeySystem_data.notes'))
        if ctrlAttr in data:
            self.inpList.setData(data[ctrlAttr]['obj'])
        else:
            self.inpList.setData([])

    def setIfReGrpF(self):
        ifGrp = self.ifGrp.isChecked()
        if not ifGrp:
            self.ifReGrp.setChecked(False)
            self.ifReGrp.setEnabled(False)
        else:
            self.ifReGrp.setEnabled(True)


class ThQWToolBoxAnimToDrivenKey(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxAnimToDrivenKey, self).__init__(label='Animation to driven key', check=check)
        self.topBotton.copyUi(ThQWToolBoxAnimToDrivenKey)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器與屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlAttr = ThQLineBoxObjAttr()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlAttr)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.objList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.objList)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性列表:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.objAttrList = ThQLineBoxAttrList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.objAttrList)
        fIndex += 1
        self.ifMyRange = QtWidgets.QCheckBox('自訂時間範圍')
        self.ifMyRange.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifMyRange)
        fIndex += 1
        self.timeRange = ThQTimeRangeBox()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.timeRange)
        self.ifMyRange.stateChanged.connect(lambda n: self.timeRange.setHidden(not n))
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        start = int(cmds.playbackOptions(q=True, min=True))
        end = int(cmds.playbackOptions(q=True, max=True))
        if self.ifMyRange.isChecked():
            start, end = self.timeRange.getData()
        akct = AnimKeyChangeType(objs=self.objList.getData(), main_ctrl_attr=self.ctrlAttr.getData(), strat_time=start, end_time=end, key_attrs=self.objAttrList.getData())
        akct.to_driven_key()


class ThQWToolBoxIkElasticity(ThQWToolBox, ThCtrlStyleListData):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxIkElasticity, self).__init__(label='IK spline', check=check)
        self.topBotton.copyUi(ThQWToolBoxIkElasticity)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 骨骼鍊: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.jointList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.jointList)
        fIndex += 1
        button = QtWidgets.QPushButton('導入骨骼鍊')
        button.clicked.connect(self.inpJoints)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' curve:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.curve = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.curve)
        fIndex += 1
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('創建 curve')
        button.clicked.connect(self.createCurve)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('編輯 curve')
        button.clicked.connect(cmds.RebuildCurveOptions)
        layout3.addWidget(button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 主要控制器:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.mainCtrl = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mainCtrl)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器大小: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlSize = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlSize)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlQuantity = ThQSpinBox(value_=3)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlQuantity)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器顏色: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.ctrlColor = ThQSpinBox(value_=4)
        layout3.addWidget(self.ctrlColor, 40)
        self.ctrlColorButton = QtWidgets.QPushButton('顏色選擇器')
        layout3.addWidget(self.ctrlColorButton, 60)
        fIndex += 1
        self.colorWidget = ThCtrlColorQWidget(self.ctrlColor)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, self.colorWidget)
        self.ctrlColorButton.clicked.connect(self.setCtrlColorButton)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        self.ifJointLenIsCtrl = QtWidgets.QCheckBox('控制器數量等於骨骼數量')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifJointLenIsCtrl)
        fIndex += 1
        self.ifConObjs = QtWidgets.QCheckBox('constrain objects')
        self.ifConObjs.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifConObjs)
        fIndex += 1
        self.ifTwistAttr = QtWidgets.QCheckBox('use twist attr')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifTwistAttr)
        fIndex += 1
        self.ifTwistCtrl = QtWidgets.QCheckBox('create twist ctrl')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifTwistCtrl)
        fIndex += 1
        self.ifElasticity = QtWidgets.QCheckBox('create elasticity')
        self.ifElasticity.stateChanged.connect(self.setIfElasticity)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifElasticity)
        fIndex += 1
        self.ifScale = QtWidgets.QCheckBox('create scale')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifScale)
        fIndex += 1
        self.ifIkFk = QtWidgets.QCheckBox('create IK/ FK')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifIkFk)
        fIndex += 1
        self.ifParent = QtWidgets.QCheckBox('parent')
        self.ifParent.setChecked(True)
        self.ifParent.stateChanged.connect(self.setIfParent)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifParent)
        fIndex += 1
        self.ifParentCtrl = QtWidgets.QCheckBox('parent + ctrl')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifParentCtrl)
        fIndex += 1
        self.ifHair = QtWidgets.QCheckBox('hair system')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifHair)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        self.setIfElasticity()
        self.setIfParent()
        grpBox = QtWidgets.QGroupBox('{ 編輯當前創建內容 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('骨骼鍊')
        button.clicked.connect(lambda : cmds.select(self.ike.joints, r=True))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('控制器')
        button.clicked.connect(lambda : cmds.select(self.ike.ik_ctrl, r=True))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('轉換為頂點')
        button.clicked.connect(lambda : mel.eval('selectCurveCV("all")'))
        layout3.addWidget(button)
        fIndex += 1
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('ik joint')
        button.clicked.connect(lambda : cmds.select(self.ike.ik_joint, r=True))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('ik node')
        button.clicked.connect(lambda : cmds.select(self.ike.ik_handle[0], r=True))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('ik curve')
        button.clicked.connect(lambda : cmds.select(self.ike.curve, r=True))
        layout3.addWidget(button)
        fIndex += 1
        label = QtWidgets.QLabel(' parent: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.bakeIfParent = QtWidgets.QCheckBox('create ctrl')
        layout3.addWidget(self.bakeIfParent)
        line = ThSeparationLine('V')
        layout3.addWidget(line)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.parentCtrl)
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 創建於選擇骨骼列表 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        label = QtWidgets.QLabel('* 本功能依據以上設定\n但排除"骨骼鍊"、"curve"屬性')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 限制層級數: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.layerLen = ThQSpinBox(value_=0)
        layout3.addWidget(self.layerLen, 30)
        line = ThSeparationLine('V')
        layout3.addWidget(line)
        button = QtWidgets.QPushButton('選擇根骨骼列表執行')
        button.clicked.connect(self.selectHierarchy)
        layout3.addWidget(button, 70)
        grpBox = QtWidgets.QGroupBox('{ hair system }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' ik curve: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.hairCurve = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.hairCurve)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.applyHair)
        layout1.addWidget(button)

    @thDoUndo
    def selectHierarchy(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        for j in selectList:
            childList = cmds.listRelatives(j, ad=True)
            childList.append(j)
            childList.reverse()
            layerLen = self.layerLen.value()
            doChildList = childList
            if layerLen > 1:
                doChildList = childList[:layerLen]
            self.apply(doChildList, False, False)

    @thDoUndo
    def applyHair(self):
        hair = THHair(cv=self.hairCurve.getData(), name=self.addLabel.text())
        hair.app()

    @thDoUndo
    def parentCtrl(self):
        self.ike_cls.ctrl_parent(self.bakeIfParent.isChecked())

    @thDoUndo
    def apply(self, list_=None, ifCurve=True, ifSetHairCurve=True):
        list_ = list_ if list_ else self.jointList.getData()
        curve = self.curve.getData() if ifCurve else None
        self.ike = ThIKElasticity(joints=list_, name=self.addLabel.text(), curve=curve, main_ctrl=self.mainCtrl.getData(), size=self.ctrlSize.value(), ctrl_quantity=self.ctrlQuantity.value(), color=self.ctrlColor.value(), use_twist_attr=self.ifTwistAttr.isChecked(), create_twist_ctrl=self.ifTwistCtrl.isChecked(), create_elasticity=self.ifElasticity.isChecked(), create_fk_ik=self.ifIkFk.isChecked(), create_scale=self.ifScale.isChecked(), constrain_objects=self.ifConObjs.isChecked(), parent_ctrl=self.ifParent.isChecked(), parent_ctrl_other=self.ifParentCtrl.isChecked(), hair_system=self.ifHair.isChecked(), joint_len_is_ctrl=self.ifJointLenIsCtrl.isChecked())
        self.ike.create()
        if ifSetHairCurve:
            self.hairCurve.setData(self.ike.curve)
        return

    @thDoUndo
    def createCurve(self):
        curve = thObjectCurve(self.jointList.getData())
        self.curve.setData(curve)

    def inpJoints(self):
        cmds.select(hierarchy=True)
        self.jointList.setData(cmds.ls(sl=True))

    def setIfParent(self):
        ifParent = self.ifParent.isChecked()
        if not ifParent:
            self.ifParentCtrl.setChecked(False)
            self.ifParentCtrl.setEnabled(False)
        else:
            self.ifParentCtrl.setEnabled(True)

    def setIfElasticity(self):
        ifElasticity = self.ifElasticity.isChecked()
        if not ifElasticity:
            self.ifScale.setChecked(False)
            self.ifScale.setEnabled(False)
        else:
            self.ifScale.setEnabled(True)

    def setCtrlColorButton(self):
        self.colorWidget.setHidden(not self.colorWidget.isHidden())


class ThQWToolBoxDefSoft(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxDefSoft, self).__init__(label='Soft ctrl', check=check)
        self.topBotton.copyUi(ThQWToolBoxDefSoft)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 定位器: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.locator = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.locator)
        fIndex += 1
        self.ifCtrl = QtWidgets.QCheckBox('創建控制器')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifCtrl)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        THDefSoftCtrl(cmds.ls(sl=True), self.locator.getData(), self.addLabel.text(), self.ifCtrl.isChecked())


class ThQWToolBoxAimCtrl(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxAimCtrl, self).__init__(label='目標控制器', check=check)
        self.topBotton.copyUi(ThQWToolBoxAimCtrl)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 軸向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.axialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.axial = ThQRadioButtonBox([ n[0] for n in self.axialList ], 2, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.axial)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標物距離: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.offset = ThQDoubleSpinBox(value_=5)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.offset)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器大小: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlSize = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlSize)
        fIndex += 1
        label = QtWidgets.QLabel(' 父物件:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.father = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.father)
        button = QtWidgets.QPushButton('選擇中心物件執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 合併目標控制器 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addMainLabel = QtWidgets.QLineEdit()
        self.addMainLabel.setText('object_main')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addMainLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 父物件:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.mainFather = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mainFather)
        self.father.inputButton.clicked.connect(self.mainFather.setData)
        button = QtWidgets.QPushButton('選擇控制器執行')
        button.clicked.connect(self.applyMain)
        layout1.addWidget(button)

    @thDoUndo
    def applyMain(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        self.ac.combine_ctrl(selectList, self.addMainLabel.text(), self.mainFather.getData())

    @thDoUndo
    def apply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        self.ac = THAimCtrl(locator=selectList[0], father=self.father.getData(), name=self.addLabel.text(), ctrl_aim=self.axialList[self.axial.isCheckedId()][1], ctrl_offset=self.offset.value(), ctrl_size=self.ctrlSize.value())
        self.ac.create()


class ThQWToolBoxSequentialStart(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSequentialStart, self).__init__(label='序列控制器', check=check)
        self.topBotton.copyUi(ThQWToolBoxSequentialStart)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('單屬性控制序列(connect/ key)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器與屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.aCtrlAttr = ThQLineBoxObjAttr()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.aCtrlAttr)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.aInpAttr = ThQLineBoxAttr(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.aInpAttr)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.aConModeList = [
         [
          'connect', 'node'], ['key', 'key']]
        self.aConMode = ThQRadioButtonBox([ n[0] for n in self.aConModeList ], 0, 'H')
        self.aConMode.bg.buttonClicked.connect(self.setAConMode)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.aConMode)
        self.aConnWidget = ThQFrameGrp()
        layout1.addWidget(self.aConnWidget)
        layout1_1 = QtWidgets.QVBoxLayout()
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.aConnWidget.setLayout(layout1_1)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(0)
        layout2_1.setSpacing(2)
        layout1_1.addLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 過度屬性: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.aConnOffsetAttr = ThQLineBoxObjAttr()
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.aConnOffsetAttr)
        self.aKeyWidget = ThQFrameGrp()
        layout1.addWidget(self.aKeyWidget)
        layout1_1 = QtWidgets.QHBoxLayout()
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.aKeyWidget.setLayout(layout1_1)
        self.aKeyOn = QtWidgets.QCheckBox('順序開啟')
        self.aKeyOn.setChecked(True)
        layout1_1.addWidget(self.aKeyOn)
        line = ThSeparationLine('V')
        layout1_1.addWidget(line)
        self.aKeyReverse = QtWidgets.QCheckBox('反轉列表')
        layout1_1.addWidget(self.aKeyReverse)
        self.setAConMode()
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.aApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('單屬性控制序列(deform)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.softAddLabel = QtWidgets.QLineEdit()
        self.softAddLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.softAddLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.softInpAttr = ThQLineBoxAttrList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.softInpAttr)
        fIndex += 1
        self.softIfSoft = QtWidgets.QCheckBox('create soft')
        self.softIfSoft.setChecked(True)
        self.softIfSoft.stateChanged.connect(self.setSoftWidget)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.softIfSoft)
        self.softWidget = ThQFrameGrp()
        layout1.addWidget(self.softWidget)
        layout1_1 = QtWidgets.QHBoxLayout()
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.softWidget.setLayout(layout1_1)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(0)
        layout2_1.setSpacing(2)
        layout1_1.addLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制風格: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.softConModeList = [
         [
          '拉鍊', 'zipper'], ['氣泡', 'pipe']]
        self.softConMode = ThQRadioButtonBox([ n[0] for n in self.softConModeList ], 0, 'H')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.softConMode)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器數量: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.softQuantity = ThQSpinBox(value_=1)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.softQuantity)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 初始值: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.softDefault = ThQSpinBox(value_=1)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.softDefault)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.softApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('雙物件控制序列(constrain)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.toInpList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.toInpList)
        fIndex += 1
        button = QtWidgets.QPushButton('交換控制器位置')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        button.clicked.connect(self.toExchangeList)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, button)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器一: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.toCtrl1 = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.toCtrl1)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器二: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.toCtrl2 = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.toCtrl2)
        fIndex += 1
        label = QtWidgets.QLabel(' 屬性控制器:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.toCombineCtrl = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.toCombineCtrl)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.toCtrlModeList = [
         [
          'soft', 'soft'], ['connect', 'connect']]
        self.toCtrlMode = ThQRadioButtonBox([ n[0] for n in self.toCtrlModeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.toCtrlMode)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.toApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('雙列表控制序列(constrain)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tlInpList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tlInpList)
        fIndex += 1
        button = QtWidgets.QPushButton('交換控制器位置')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        button.setSizePolicy(sizePolicy)
        button.clicked.connect(self.tlExchangeList)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, button)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器列表一: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tlOutList1 = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tlOutList1)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器列表二: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tlOutList2 = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tlOutList2)
        fIndex += 1
        label = QtWidgets.QLabel(' 屬性控制器:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tlCombineCtrl = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tlCombineCtrl)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制風格: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tlCtrlModeList = [
         [
          '拉鍊', 'zipper'], ['氣泡', 'pipe']]
        self.tlCtrlMode = ThQRadioButtonBox([ n[0] for n in self.tlCtrlModeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tlCtrlMode)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制方法: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tlConModeList = [
         [
          'soft', 'soft'], ['key', 'key']]
        self.tlConMode = ThQRadioButtonBox([ n[0] for n in self.tlConModeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tlConMode)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.tlApply)
        layout1.addWidget(button)

    @thDoUndo
    def tlApply(self):
        TwoListSequential(self.tlInpList.getData(), self.tlOutList1.getData(), self.tlOutList2.getData(), self.tlCombineCtrl.getData(), self.tlCtrlModeList[self.tlCtrlMode.isCheckedId()][1], self.tlConModeList[self.tlConMode.isCheckedId()][1])

    def tlExchangeList(self):
        list1 = self.tlOutList1.getData()
        list2 = self.tlOutList2.getData()
        self.tlOutList1.setData(list2)
        self.tlOutList2.setData(list1)

    @thDoUndo
    def toApply(self):
        TwoObjCtrl(self.toCtrl1.getData(), self.toCtrl2.getData(), self.toInpList.getData(), self.toCtrl1.getData(), self.toCtrlModeList[self.toCtrlMode.isCheckedId()][1], self.toCombineCtrl.getData())

    def toExchangeList(self):
        list1 = self.toCtrl1.getData()
        list2 = self.toCtrl2.getData()
        self.toCtrl1.setData(list2)
        self.toCtrl2.setData(list1)

    @thDoUndo
    def softApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ThDistanceSoftLocator(objs=selectList, name=self.softAddLabel.text(), create_soft=self.softIfSoft.isChecked(), quantity_soft=self.softQuantity.value(), mode_soft=self.softConModeList[self.softConMode.isCheckedId()][1], default=self.softDefault.value(), conn_attr=self.softInpAttr.getData(), exclude_end=False)

    def setSoftWidget(self):
        self.softWidget.setHidden(not self.softIfSoft.isChecked())

    @thDoUndo
    def aApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        mode = self.aConModeList[self.aConMode.isCheckedId()][1]
        if mode == 'node':
            thBatchEnable(obj_follow=self.aCtrlAttr.getData(), obj_offset=self.aConnOffsetAttr.getData(), obj_list=selectList, con_attr=self.aInpAttr.getData())
        else:
            thBatchOffset(obj_list=selectList, con_attr=self.aInpAttr.getData(), obj_follow=self.aCtrlAttr.getData(), on_off=self.aKeyOn.isChecked(), reverse=self.aKeyReverse.isChecked())
        cmds.select(cl=True)

    def setAConMode(self):
        mode = self.aConModeList[self.aConMode.isCheckedId()][1]
        hidden = True if mode == 'node' else False
        self.aConnWidget.setHidden(not hidden)
        self.aKeyWidget.setHidden(hidden)


class ThQWToolBoxMouthRig(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxMouthRig, self).__init__(label='拉鍊嘴型', check=check)
        self.topBotton.copyUi(ThQWToolBoxMouthRig)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        helpText = '* "嘴角" 是處於中間部位，若無則不用讀入UI\n* 讀入順序是從嘴角選到中間部位\n(若左右公用一個中間，則重複讀入)\n(確保左右數量一致)'
        label = QtWidgets.QLabel(helpText)
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout1.addWidget(label)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 左/ 右標籤:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.labelL = QtWidgets.QLineEdit('L_')
        layout3.addWidget(self.labelL)
        self.labelR = QtWidgets.QLineEdit('R_')
        layout3.addWidget(self.labelR)
        fIndex += 1
        label = QtWidgets.QLabel(' 左上: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.upLeft = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.upLeft)
        fIndex += 1
        label = QtWidgets.QLabel(' 右上: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.upRight = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.upRight)
        fIndex += 1
        label = QtWidgets.QLabel(' 左下: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.dnLeft = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.dnLeft)
        fIndex += 1
        label = QtWidgets.QLabel(' 右下: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.dnRight = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.dnRight)
        self.upLeft.inputButton.clicked.connect(lambda : self._reLRF(self.upLeft, self.upRight, [self.labelL, self.labelR]))
        self.upRight.inputButton.clicked.connect(lambda : self._reLRF(self.upRight, self.upLeft, [self.labelR, self.labelL]))
        self.dnLeft.inputButton.clicked.connect(lambda : self._reLRF(self.dnLeft, self.dnRight, [self.labelL, self.labelR]))
        self.dnRight.inputButton.clicked.connect(lambda : self._reLRF(self.dnRight, self.dnLeft, [self.labelR, self.labelL]))
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        helpText = '* 包含左右'
        label = QtWidgets.QLabel(helpText)
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, label)
        fIndex += 1
        label = QtWidgets.QLabel(' 嘴角:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.corner = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.corner)
        fIndex += 1
        label = QtWidgets.QLabel(' 臉頰(上):* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.precludeUpList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.precludeUpList)
        fIndex += 1
        label = QtWidgets.QLabel(' 臉頰(下):* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.precludeDnList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.precludeDnList)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 下顎: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.jaw = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.jaw)
        fIndex += 1
        label = QtWidgets.QLabel(' 下顎父層級: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.head = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.head)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.conModeList = [
         [
          'connect', 'connect'], ['soft', 'soft']]
        self.conMode = ThQRadioButtonBox([ n[0] for n in self.conModeList ], 1, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.conMode)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        self.ifLocator = QtWidgets.QCheckBox('創建於父層級')
        self.ifLocator.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifLocator)
        fIndex += 1
        self.ifCtrl = QtWidgets.QCheckBox('創建控制器')
        self.ifCtrl.setChecked(True)
        self.ifCtrl.stateChanged.connect(self.setIfCtrlWidget)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifCtrl)
        self.ifCtrlWidget1 = ThQFrameGrp()
        layout1.addWidget(self.ifCtrlWidget1)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.ifCtrlWidget1.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 控制器: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrl = ThQLineBox(False)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.ctrl)
        self.ifCtrlWidget = ThQFrameGrp()
        layout1.addWidget(self.ifCtrlWidget)
        self.setIfCtrlWidget()
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.ifCtrlWidget.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 替換字符:* ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.reJoint = QtWidgets.QLineEdit()
        self.reJoint.setText('_joint')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.reJoint)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 嘴唇軸心:* ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.centerRefLoc = ThQLineBox(False)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.centerRefLoc)
        fIndex_1 += 1
        helpText = '* 導入左至右序列定位器'
        label = QtWidgets.QLabel(helpText)
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.SpanningRole, label)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 群組定位器1:* ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.mainRotateCtrlList1 = ThQLineBoxList(False)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.mainRotateCtrlList1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 群組定位器2(上排):* ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.mainRotateCtrlList21 = ThQLineBoxList(False)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.mainRotateCtrlList21)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 群組定位器2(下排):* ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.mainRotateCtrlList22 = ThQLineBoxList(False)
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.mainRotateCtrlList22)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.applyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 創建表情控制器 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('執行創建')
        button.clicked.connect(self.fcApplyF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('編輯設定檔')
        button.clicked.connect(self.fcEditDataF)
        layout2.addWidget(button)

    def _reLRF(self, inp_, out_, reLR):
        outData = out_.getData()
        if outData:
            return
        inpData = inp_.getData()
        newData = []
        for n in inpData:
            new = n.replace(reLR[0].text(), reLR[1].text())
            if cmds.objExists(new):
                newData.append(new)

        out_.setData(newData)

    @thDoUndo
    def fcApplyF(self):
        ThCreateFaceCtrl()

    def fcEditDataF(self):
        QMainWindowInWidget(ThCreateFaceCtrlDataE, ifSpacerItem=False)

    def setIfCtrlWidget(self):
        self.ifCtrlWidget.setHidden(not self.ifCtrl.isChecked())
        self.ifCtrlWidget1.setHidden(self.ifCtrl.isChecked())

    @thDoUndo
    def applyF(self):
        checkList1 = self.upLeft.getData() + self.upRight.getData() + self.dnLeft.getData() + self.dnRight.getData()
        checkList2 = self.precludeUpList.getData() + self.precludeDnList.getData()
        for n in checkList2:
            if n not in checkList1:
                cmds.warning('臉頰(上, 下)物件不存在於定義(左上, 左下...)列表中')
                return

        rm = ThRigMouth(up_left=self.upLeft.getData(), up_right=self.upRight.getData(), down_left=self.dnLeft.getData(), down_right=self.dnRight.getData(), head=self.head.getData(), jaw=self.jaw.getData(), jaw_ctrl=self.ctrl.getData(), ctrl_mode=self.conModeList[self.conMode.isCheckedId()][1], mouth_corner=self.corner.getData(), if_grp=self.ifLocator.isChecked(), if_ctrl=self.ifCtrl.isChecked(), ctrl_style='hexagon', ctrl_axial='z', center_ref_loc=self.centerRefLoc.getData(), replace_str=self.reJoint.text(), combine_ctrl_loc_list1=self.mainRotateCtrlList1.getData(), combine_ctrl_loc_list2_1=self.mainRotateCtrlList21.getData(), combine_ctrl_loc_list2_2=self.mainRotateCtrlList22.getData(), preclude_up_list=self.precludeUpList.getData(), preclude_dn_list=self.precludeDnList.getData())


class ThQWToolBoxReelRig(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxReelRig, self).__init__(label='卷軸', check=check)
        self.topBotton.copyUi(ThQWToolBoxReelRig)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.objList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.objList)
        fIndex += 1
        label = QtWidgets.QLabel(' 方向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.axialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.axial = ThQRadioButtonBox([ n[0] for n in self.axialList ], 2, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.axial)
        fIndex += 1
        label = QtWidgets.QLabel(' 模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.modeList = [
         [
          '單向', 'one'], ['雙向', 'two']]
        self.mode = ThQRadioButtonBox([ n[0] for n in self.modeList ], 1, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mode)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        line = ThSeparationLine('H')
        layout1.addWidget(line)
        button = QtWidgets.QPushButton('連接到控制器(加選控制器執行)')
        button.clicked.connect(self.connectCtrlApply)
        layout1.addWidget(button)

    @thDoUndo
    def connectCtrlApply(self):
        selelctList = cmds.ls(sl=True)
        if not selelctList:
            return
        THReelRig().con_ctrl(selelctList[0], selelctList[1])

    @thDoUndo
    def apply(self):
        THReelRig().app(self.objList.getData(), self.axialList[self.axial.isCheckedId()][1], self.modeList[self.mode.isCheckedId()][1])


class ThQWToolBoxObjectCurve(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxObjectCurve, self).__init__(label='依據選擇物件創建 curve', check=check)
        self.topBotton.copyUi(ThQWToolBoxObjectCurve)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.ifRebuild = QtWidgets.QCheckBox('重建曲線')
        self.ifRebuild.setChecked(True)
        self.ifRebuild.stateChanged.connect(lambda n: self.ifCoordinate.setHidden(not n))
        layout2.addWidget(self.ifRebuild)
        self.ifCoordinate = QtWidgets.QCheckBox('捕捉座標')
        self.ifCoordinate.setChecked(True)
        layout2.addWidget(self.ifCoordinate)
        self.ifDelete = QtWidgets.QCheckBox('刪除物件')
        self.ifDelete.setChecked(False)
        layout2.addWidget(self.ifDelete)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('附屬功能')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('rebuild curve options')
        button.clicked.connect(cmds.RebuildCurveOptions)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        selectList = cmds.ls(sl=True, fl=True)
        if not selectList:
            return
        thObjectCurve(selectList, self.ifRebuild.isChecked(), self.ifDelete.isChecked(), self.ifCoordinate.isChecked())


class ThQWToolBoxCurveJoint(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxCurveJoint, self).__init__(label='依據選擇 curve 創建 joint', check=check)
        self.topBotton.copyUi(ThQWToolBoxCurveJoint)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.quantity = ThQSpinBox(value_=5)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.quantity)
        fIndex += 1
        self.ifParent = QtWidgets.QCheckBox('建立 parent')
        self.ifParent.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifParent)
        fIndex += 1
        self.ifAdsorption = QtWidgets.QCheckBox('對齊法線')
        self.ifAdsorption.setChecked(True)
        self.ifAdsorption.stateChanged.connect(self.setIfAdsorptionWidgets)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifAdsorption)
        self.ifAdsorptionWidgets = ThQFrameGrp()
        layout1.addWidget(self.ifAdsorptionWidgets)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.ifAdsorptionWidgets.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 軸向: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        self.axialList = [
         [
          'yup', 'yup'], ['zup', 'zup']]
        self.axial = ThQRadioButtonBox([ n[0] for n in self.axialList ], 1, 'H')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.FieldRole, self.axial)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('附屬功能')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('polygon edges to curve')
        button.clicked.connect(self.polygonEdgesToCurve)
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('reverse curve')
        button.clicked.connect(self.reverseCurve)
        layout1.addWidget(button)

    @thDoUndo
    def reverseCurve(self):
        sel = cmds.ls(sl=True)
        for n in sel:
            cmds.reverseCurve(n, rpo=1)

        cmds.select(sel, r=True)

    @thDoUndo
    def polygonEdgesToCurve(self):
        cmds.polyToCurve(form=2, degree=3)
        cmds.CenterPivot()
        cmds.delete(ch=True)

    @thDoUndo
    def apply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        axial = [
         0, 1, 0]
        if self.axialList[self.axial.isCheckedId()][1] == 'zup':
            axial = [
             0, 0, 1]
        ThCurveCreateJoint(curve=selectList, quantity=self.quantity.value(), name=self.addLabel.text(), if_adsorption=self.ifAdsorption.isChecked(), if_parent=self.ifParent.isChecked(), tangent_aim=axial)

    def setIfAdsorptionWidgets(self):
        self.ifAdsorptionWidgets.setHidden(not self.ifAdsorption.isChecked())


class ThQWToolBoxFollowCvLoc(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxFollowCvLoc, self).__init__(label='創建跟隨 curve 的 locator', check=check)
        self.topBotton.copyUi(ThQWToolBoxFollowCvLoc)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLebal = QtWidgets.QLineEdit()
        self.addLebal.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLebal)
        fIndex += 1
        label = QtWidgets.QLabel(' 定位器數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.locQuantity = ThQSpinBox(value_=5)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.locQuantity)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        thCvToFollowLoc(selectList, self.locQuantity.value(), self.addLebal.text())


class ThQWToolBoxWeightToCtrl(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxWeightToCtrl, self).__init__(label='少數控制多數', check=check)
        self.topBotton.copyUi(ThQWToolBoxWeightToCtrl)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.outList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.outList)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inpList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inpList)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.vlSize = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.vlSize)
        fIndex += 1
        button = QtWidgets.QPushButton('測試定位器大小')
        button.clicked.connect(thDoUndo(lambda : THVtxLocator().test_create_vl()))
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 統一權重 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('選擇定位器列表執行')
        button.clicked.connect(thDoUndo(lambda : THVtxLocator().unite_wight(cmds.ls(sl=True))))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 重新設定 UV 座標 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' follicle list: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.rePosFollicleList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.rePosFollicleList)
        button = QtWidgets.QPushButton('選擇三角定位器執行')
        button.clicked.connect(self.rePosApply)
        layout1.addWidget(button)

    @thDoUndo
    def rePosApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        THVtxLocator().reset_uv_pos(self.rePosFollicleList.getData(), selectList[0])

    @thDoUndo
    def apply(self):
        thWeightToCtrl(main_obj=self.outList.getData(), obj=self.inpList.getData(), vl_size=self.vlSize.value())


class ThQWToolBoxWheel(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxWheel, self).__init__(label='輪子控制器', check=check)
        self.topBotton.copyUi(ThQWToolBoxWheel)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('wheel')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.meshList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.meshList)
        fIndex += 1
        label = QtWidgets.QLabel(' 定位器: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.locatorList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.locatorList)
        fIndex += 1
        label = QtWidgets.QLabel(' 軸向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.axialList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.axial = ThQRadioButtonBox([ n[0] for n in self.axialList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.axial)
        fIndex += 1
        self.ifCon = QtWidgets.QCheckBox('控制到定位器')
        self.ifCon.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifCon)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        TWheelRig(meshList=self.meshList.getData(), name=self.addLabel.text(), axial=self.axialList[self.axial.isCheckedId()][1], axisObjList=self.locatorList.getData(), ifConAxisObjList=self.ifCon.isChecked())


class ThQWToolBoxFollowOffset(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxFollowOffset, self).__init__(label='物件跟隨序列並偏移', check=check)
        self.topBotton.copyUi(ThQWToolBoxFollowOffset)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源物件: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inputObj = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inputObj)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.outList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.outList)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        THObjOffsetObjs(self.outList.getData(), self.inputObj.getData()).app()


class ThQWToolBoxDynamicsOutliner(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxDynamicsOutliner, self).__init__(label='Dynamics outliner', check=check)
        self.topBotton.copyUi(ThQWToolBoxDynamicsOutliner)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 標籤列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.labelListSlider = ThQSlider(QtCore.Qt.Horizontal)
        self.labelListSlider.setMinimum(100)
        self.labelListSlider.setMaximum(800)
        self.labelListSlider.valueChanged[int].connect(self.setLabelListSlider)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.labelListSlider)
        fIndex += 1
        self.labelList = ThQListWidget()
        self.labelList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.labelList.setMinimumWidth(50)
        self.labelList.setMinimumHeight(100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.labelList.setSizePolicy(sizePolicy)
        self.labelList.itemSelectionChanged.connect(self.getLabel)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.labelList)
        fIndex += 1
        button = QtWidgets.QPushButton('讀取存檔')
        button.clicked.connect(self.getSystem)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 新標籤: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLebel = QtWidgets.QLineEdit()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLebel)
        fIndex += 1
        self.ifRename = QtWidgets.QCheckBox('重命名選擇物件')
        self.ifRename.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifRename)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    def getLabel(self):
        selectItemList = self.labelList.selectedItems()
        if not selectItemList:
            return
        selectItemText = selectItemList[0].text()
        label = selectItemText.replace('_dyn_grp', '')
        self.addLebel.setText(label)

    def getSystem(self):
        if cmds.objExists('dyn'):
            self.labelList.clear()
            grps = cmds.listRelatives('dyn', c=True)
            for grp in grps:
                self.labelList.addItem(grp)

    @thDoUndo
    def apply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        thDynOutliner(objs=selectList, main=self.addLebel.text(), rename=self.ifRename.isChecked())
        self.getSystem()

    def setLabelListSlider(self):
        pos = self.labelListSlider.value()
        self.labelList.setMinimumHeight(pos)


class ThQWToolBoxDynCtrl(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxDynCtrl, self).__init__(label='Dynamics ctrl', check=check)
        self.topBotton.copyUi(ThQWToolBoxDynCtrl)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('創建控制器')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 類別: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.objTypeList = [
         [
          'cloth', 'cloth'], ['hair', 'hair'], ['nucleus', 'nucleus']]
        self.objType = ThQRadioButtonBox([ n[0] for n in self.objTypeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.objType)
        fIndex += 1
        label = QtWidgets.QLabel(' 數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.quantity = ThQSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.quantity)
        fIndex += 1
        label = QtWidgets.QLabel(' 字形: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.fontComboBox = ThQFontComboBox()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.fontComboBox)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 選擇層級下指定類別 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('nCloth')
        button.clicked.connect(lambda : self.selTypApply('nCloth'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('hairSys')
        button.clicked.connect(lambda : self.selTypApply('hairSystem'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('nucleus')
        button.clicked.connect(lambda : self.selTypApply('nucleus'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('nRigid')
        button.clicked.connect(lambda : self.selTypApply('nRigid'))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 連接物件 }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('最後加選控制器執行')
        button.clicked.connect(self.connectApply)
        layout1.addWidget(button)

    @thDoUndo
    def selTypApply(self, type):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        list_ = cmds.listRelatives(selectList, ad=True, typ=type, f=True)
        cmds.select(list_, r=True)

    @thDoUndo
    def connectApply(self):
        ThConnDynNode(cmds.ls(sl=True))

    @thDoUndo
    def apply(self):
        dynCtrl = THDynamicsCtrl(self.objTypeList[self.objType.isCheckedId()][1], self.fontComboBox.currentFont().family())
        dynCtrl.ctrl()
        dynCtrl.children_ctrl(self.quantity.value())


class ThQWToolBoxRand(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxRand, self).__init__(label='隨機工具集', check=check)
        self.topBotton.copyUi(ThQWToolBoxRand)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('隨機選擇')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sInputList = ThQLineBoxList(ifShowHideButton=False, flatten=True)
        self.sInputList.inputButton.clicked.connect(self.sSetSystem)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sInputList)
        fIndex += 1
        label = QtWidgets.QLabel(' 篩選數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sQuantity = ThQSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sQuantity)
        fIndex += 1
        self.sIfBakeSelect = QtWidgets.QCheckBox('排除選擇過的')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sIfBakeSelect)
        fIndex += 1
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.sApply)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('目前\n選擇的')
        button.clicked.connect(self.sFilter)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('未\n選擇過的')
        button.clicked.connect(self.sNew)
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('已經\n選擇過的')
        button.clicked.connect(self.sAdd)
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('隨機值設定')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.aInputList = ThQLineBoxList(False)
        self.aInputList.inputButton.clicked.connect(self.sSetSystem)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.aInputList)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.aAttrList = ThQLineBoxAttrList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.aAttrList)
        fIndex += 1
        label = QtWidgets.QLabel(' 最大/ 最小值: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.aMin = ThQDoubleSpinBox(value_=0)
        layout3.addWidget(self.aMin)
        self.aMax = ThQDoubleSpinBox(value_=10)
        layout3.addWidget(self.aMax)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.aApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('隨機篩選-合併兩個列表')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表一: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.combineInputList1 = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.combineInputList1)
        fIndex += 1
        label = QtWidgets.QLabel(' 列表二: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.combineInputList2 = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.combineInputList2)
        fIndex += 1
        label = QtWidgets.QLabel(' 篩選數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.combineQuantity = ThQSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.combineQuantity)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.combineApply)
        layout1.addWidget(button)

    @thDoUndo
    def combineApply(self):
        thIntegrationList(self.combineInputList1.getData(), self.combineInputList2.getData(), self.combineQuantity.value())

    @thDoUndo
    def aApply(self):
        thRandData(self.aInputList.getData(), self.aAttrList.getData(), self.aMin.value(), self.aMax.value())

    @thDoUndo
    def sFilter(self):
        cmds.select(self.sList, r=True)

    @thDoUndo
    def sNew(self):
        cmds.select(self.trs.new_list, r=True)

    @thDoUndo
    def sAdd(self):
        cmds.select(self.trs.filter_list, r=True)

    @thDoUndo
    def sSetSystem(self):
        self.trs = TRandSelect(cmds.ls(sl=True, fl=True))

    @thDoUndo
    def sApply(self):
        self.sList = self.trs.do(self.sQuantity.value(), self.sIfBakeSelect.isChecked())


class ThQWToolBoxEditBlendShape(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxEditBlendShape, self).__init__(label='Edit blend shape', check=check)
        self.topBotton.copyUi(ThQWToolBoxEditBlendShape)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('獲取沒有 deform 影響的模型')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('選擇模型執行')
        button.clicked.connect(self.ndApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('重建')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('選擇模型執行')
        button.clicked.connect(self.reApplyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('創建')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.crIfDelHis = QtWidgets.QCheckBox('刪除歷史紀錄')
        layout2.addWidget(self.crIfDelHis, 40)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('選擇添加模型執行')
        button.clicked.connect(self.createBlendShape)
        layout2.addWidget(button, 60)
        grpBox = QtWidgets.QGroupBox('添加')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標模型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addInputMesh = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addInputMesh)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標節點: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addInputNode = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addInputNode)
        self.addInputMesh.inputButton.clicked.connect(lambda : self.sbsInBsNode(self.addInputNode))
        button = QtWidgets.QPushButton('選擇要添加的物件執行')
        button.clicked.connect(self.addApply)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('減去')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.difIfCopy = QtWidgets.QCheckBox('複製新模型')
        layout2.addWidget(self.difIfCopy, 40)
        line = ThSeparationLine('V')
        layout2.addWidget(line)
        button = QtWidgets.QPushButton('依序選擇\n[base, strat, end]執行')
        button.clicked.connect(self.differenceApply)
        layout2.addWidget(button, 60)
        grpBox = QtWidgets.QGroupBox('匹配目標並連接屬性')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標模型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.wrapInputMesh = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.wrapInputMesh)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標節點: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.wrapInputNode = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.wrapInputNode)
        self.wrapInputMesh.inputButton.clicked.connect(lambda : self.sbsInBsNode(self.wrapInputNode))
        fIndex += 1
        label = QtWidgets.QLabel(' wrap 模型:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.wrapInputWrap = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.wrapInputWrap)
        button = QtWidgets.QPushButton('選擇要被匹配的物件執行')
        button.clicked.connect(self.wrapApplyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('依據 skin 權重設定 blend')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標模型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sbwMesh = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sbwMesh)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標節點: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sbwNode = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sbwNode)
        self.sbwMesh.inputButton.clicked.connect(lambda : self.sbsInBsNode(self.sbwNode))
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('創建 joint')
        button.clicked.connect(self.sbwJointApplyF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('執行設定')
        button.clicked.connect(self.sbwApplyF)
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('依據 skin 權重拆分模型')
        self.layout.addWidget(grpBox)
        self.sbsLayout1 = QtWidgets.QVBoxLayout()
        self.sbsLayout1.setMargin(2)
        self.sbsLayout1.setSpacing(2)
        grpBox.setLayout(self.sbsLayout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        self.sbsLayout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel('* Step1: 複製一個基礎模型\n* Step2: 創建拆分工具')
        label.setObjectName('annotation')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, label)
        fIndex += 1
        label = QtWidgets.QLabel(' 分割數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sbsSplitPlaneQuantityList = [
         [
          '2', 2], ['4', 4]]
        self.sbsSplitPlaneQuantity = ThQRadioButtonBox([ n[0] for n in self.sbsSplitPlaneQuantityList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sbsSplitPlaneQuantity)
        fIndex += 1
        button = QtWidgets.QPushButton('選擇 "複製模型" 執行')
        button.clicked.connect(self.sbsSplitPlaneApply)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel('* Step3: 將 "複製模型" skin 到拆分工具上')
        label.setObjectName('annotation')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, label)
        fIndex += 1
        button = QtWidgets.QPushButton('選擇 "複製模型" 與 "拆分工具模型" 執行')
        button.clicked.connect(self.sbsCopyWeight)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, button)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel('* Step4: 要拆分的模型 blend 到基礎模型上')
        label.setObjectName('annotation')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, label)
        fIndex += 1
        label = QtWidgets.QLabel(' mesh: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sbsMesh = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sbsMesh)
        fIndex += 1
        label = QtWidgets.QLabel(' blend node: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sbsNode = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sbsNode)
        self.sbsMesh.inputButton.clicked.connect(lambda : self.sbsInBsNode(self.sbsNode))
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        self.sbsLayout1.addLayout(layout2)
        button = QtWidgets.QPushButton('創建工具按鈕')
        button.clicked.connect(self.sbsApply)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('復原權重')
        button.clicked.connect(self.sbsReApply)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('拆解並複製')
        button.clicked.connect(self.sbsSplitApply)
        layout2.addWidget(button)
        line = ThSeparationLine('H')
        self.sbsLayout1.addWidget(line)
        self.sbsWidget = None
        grpBox = QtWidgets.QGroupBox('{ smooth weight }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' value/ loop: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.smoothWeight = ThQDoubleSpinBox(value_=1)
        layout3.addWidget(self.smoothWeight)
        self.smoothQuantity = ThQSpinBox(1)
        layout3.addWidget(self.smoothQuantity)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.smoothApply)
        layout1.addWidget(button)
        return

    @thDoUndo
    def reApplyF(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        for n in selectList:
            ThEditBlendShape().resetBlendShapeF(n)

        cmds.select(selectList, r=True)

    @thDoUndo
    def wrapApplyF(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ebs = ThEditBlendShape()
        ebs.wrapF(self.wrapInputMesh.getData(), selectList[0], self.wrapInputNode.getData(), self.wrapInputWrap.getData())

    @thDoUndo
    def sbwJointApplyF(self):
        ebs = ThEditBlendShape()
        ebs.isSkinWeightCreateJointF(mesh=self.sbwMesh.getData(), node=self.sbwNode.getData())

    @thDoUndo
    def sbwApplyF(self):
        ebs = ThEditBlendShape()
        ebs.isSkinWeightF(mesh=self.sbwMesh.getData(), node=self.sbwNode.getData())

    @thDoUndo
    def sbsReApply(self):
        spbs = ThSkinSplitBlendShape(self.sbsMesh.getData(), self.sbsNode.getData())
        spbs.reWeight()

    @thDoUndo
    def smoothApply(self):
        ThEditSkinWeightSmooth(list_=cmds.ls(sl=True), quantity=self.smoothQuantity.value(), value=self.smoothWeight.value())

    @thDoUndo
    def sbsCopyWeight(self):
        sel = cmds.ls(sl=True)
        csaw = THCopySkinAndWeight([sel[(-1)]], sel[:-1])
        csaw.copy_skin()
        csaw.copy_weight()
        csaw.set_max_influences()

    @thDoUndo
    def sbsSplitPlaneApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        smtb = ThSplitMeshPlane(selectList[0], self.sbsSplitPlaneQuantityList[self.sbsSplitPlaneQuantity.isCheckedId()][1])
        smtb.createPlane()

    def sbsInBsNode(self, ui):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        nodeList = thFindBlendShapeNode(selectList[0])
        if not nodeList:
            return
        ui.setData(nodeList[0])

    @thDoUndo
    def createBlendShape(self):
        ThEditBlendShape().createBlendShapeF(delHis=self.crIfDelHis.isChecked())

    @thDoUndo
    def sbsSplitApply(self):
        spbs = ThSkinSplitBlendShape(self.sbsMesh.getData(), self.sbsNode.getData())
        spbs.splitCopy()

    @thDoUndo
    def ndApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        newMeshList = ThEditBlendShape().baseShapeF(selectList)
        cmds.select(newMeshList, r=True)

    def sbsApply(self):
        spbs = ThSkinSplitBlendShape(self.sbsMesh.getData(), self.sbsNode.getData())
        if self.sbsWidget:
            self.sbsWidget.deleteLater()
            self.sbsWidget = None
        self.sbsWidget = ThQFrameGrp()
        self.sbsLayout1.addWidget(self.sbsWidget)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        self.sbsWidget.setLayout(layout1)
        for i, n in enumerate(spbs.data[0]):
            button = QtWidgets.QPushButton(n)
            button.clicked.connect(thDoUndo(lambda i=i: spbs.setWeight(i)))
            layout1.addWidget(button)

        return

    @thDoUndo
    def addApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ebs = ThEditBlendShape()
        ebs.addF(self.addInputNode.getData(), self.addInputMesh.getData(), selectList)

    @thDoUndo
    def differenceApply(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ebs = ThEditBlendShape()
        ebs.differenceF(selectList[0], selectList[1], selectList[2], self.difIfCopy.isChecked())


class ThQWToolBoxDynCommon(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxDynCommon, self).__init__(label='動畫工具集', check=check)
        self.topBotton.copyUi(ThQWToolBoxDynCommon)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('Play blast')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 起始/ 結束: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.playStart = ThQSpinBox(value_=0)
        layout3.addWidget(self.playStart, 30)
        self.playEnd = ThQSpinBox(value_=80)
        layout3.addWidget(self.playEnd, 30)
        button = QtWidgets.QPushButton('get')
        button.clicked.connect(self.playBlastGet)
        layout3.addWidget(button, 20)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.playBlastApply)
        layout3.addWidget(button, 20)
        grpBox = QtWidgets.QGroupBox('工具集')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        self.funcComboBox = ThQComboBox()
        self.setFuncList()
        for label in self.funcList:
            self.funcComboBox.addItem(label[0])

        self.funcComboBox.setInputMaxWidth()
        layout1.addWidget(self.funcComboBox, 80)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.appFuncListOpen)
        layout1.addWidget(button, 20)

    def playBlastGet(self):
        staet = int(cmds.playbackOptions(q=True, min=True))
        end = int(cmds.playbackOptions(q=True, max=True))
        self.playStart.setValue(staet)
        self.playEnd.setValue(end)

    @thDoUndo
    def playBlastApply(self):
        thPlayBlast(self.playStart.value(), self.playEnd.value())

    @thDoUndo
    def appFuncListOpen(self):
        index = self.funcComboBox.currentIndex()
        eval(self.funcList[index][1])

    def setFuncList(self):
        self.funcList = [
         [
          '交互式撥放工具 — (直接執行)', 'cmds.InteractivePlayback()'],
         [
          '將選擇的力學節點斷開解算器連接 — (選擇 hairSystem 執行)', 'thDisconnectHairNucleus(cmds.ls(sl=True))'],
         [
          '批量創建解算器 — (選擇力學節點執行)', 'thAssignNSolverF(cmds.ls(sl=True))'],
         [
          '刪除未使用的解算器 — (直接執行)', 'thDeleteNotNucleus()'],
         [
          '打印使用的解算器名稱 — (直接執行)', 'thPrintUseNucleus()'],
         [
          '設置 HIK IK 屬性 — (直接執行)', 'ThSetHIKAttr.setArmIkF()'],
         [
          '批量 KEY 屬性到 Frame — (選擇物件與屬性執行)', 'thBatchSetKeyToFrameF()'],
         [
          '指定屬性移出動畫層 — (選擇物件屬性列表執行)', 'reAnimAttrAppF()']]


class ThQWToolBoxFields(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxFields, self).__init__(label='擾亂場', check=check)
        self.topBotton.copyUi(ThQWToolBoxFields)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 命名: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addLabel = QtWidgets.QLineEdit()
        self.addLabel.setText('object')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addLabel)
        fIndex += 1
        label = QtWidgets.QLabel(' 力學節點: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.dynNode = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.dynNode)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrl = ThQLineBox(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrl)
        button = QtWidgets.QPushButton('選擇模型執行')
        button.clicked.connect(self.apply)
        layout1.addWidget(button)

    @thDoUndo
    def apply(self):
        thFieldTurbulence(cmds.ls(sl=True), self.ctrl.getData(), self.dynNode.getData(), self.addLabel.text())


class ThQWToolBoxExtrudeJoint(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxExtrudeJoint, self).__init__(label='骨骼肌肉系統', check=check)
        self.topBotton.copyUi(ThQWToolBoxExtrudeJoint)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('步驟 1: 創建骨骼')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標骨骼: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inpJoint = ThQLineBox(False)
        self.inpJoint.inputButton.clicked.connect(self._inJoint)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inpJoint)
        fIndex += 1
        self.quantityWidget = ThQFrameGrp()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, self.quantityWidget)
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.quantityWidget.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 數量:* ')
        layout2_1.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.quantityList = [
         [
          '1', 1], ['2', 2]]
        self.quantity = ThQRadioButtonBox([ n[0] for n in self.quantityList ], 0, 'H')
        self.quantity.bg.buttonClicked.connect(self._setIsParent)
        layout2_1.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.quantity)
        fIndex += 1
        self.toFather = QtWidgets.QCheckBox('1 parent to father')
        self.toFather.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.toFather)
        fIndex += 1
        label = QtWidgets.QLabel(' 新骨骼列表:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.newJointList = ThQLineBoxList(False)
        self.newJointList.inputButton.clicked.connect(self._inJointList)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.newJointList)
        fIndex += 1
        self.button1 = QtWidgets.QPushButton('執行: ')
        self.button1.clicked.connect(self.apply1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, self.button1)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇到: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('all')
        button.clicked.connect(lambda : self.selectJointMode('all'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('1')
        button.clicked.connect(lambda : self.selectJointMode('1'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('2')
        button.clicked.connect(lambda : self.selectJointMode('2'))
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('步驟 2: 創建控制器')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.meshList = ThQLineBoxList(False)
        self.meshList.inputButton.clicked.connect(self.setInputMeshList)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.meshList)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器大小: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlSize = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlSize)
        fIndex += 1
        self.button2 = QtWidgets.QPushButton('執行: ')
        self.button2.clicked.connect(self.apply2)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, self.button2)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        label = QtWidgets.QLabel(' 選擇到: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        button = QtWidgets.QPushButton('ctrl')
        button.clicked.connect(lambda : self.selectJointMode('ctrl'))
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, button)
        grpBox = QtWidgets.QGroupBox('步驟 3: 編輯權重')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 骨骼列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.weightJointList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.weightJointList)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.weightMeshList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.weightMeshList)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        self.editWeightWidget = None
        button = QtWidgets.QPushButton('創建編輯列表')
        button.clicked.connect(partial(self.setEditWeightButton, layout1))
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('執行 soft to weight')
        button.clicked.connect(self.softToWeight)
        layout2.addWidget(button)
        grpBox = QtWidgets.QGroupBox('附屬功能')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('paint\ntool')
        button.clicked.connect(self.paint)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('mirror\njoint')
        button.clicked.connect(self.mirrorJoint)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('mirror\nweight')
        button.clicked.connect(cmds.MirrorSkinWeightsOptions)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('reset system data')
        button.clicked.connect(lambda : ThExtrudeJoint().reset_sys_data())
        layout1.addWidget(button)
        return

    @thDoUndo
    def mirrorJoint(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        ThReconstructionParent(selectList).apply()
        newJoint = thMirrorJoint(joints=selectList, axial='x')
        thDeleteConstrainNode(newJoint)
        ThReconstructionParent().apply()

    @thDoUndo
    def paint(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        cmds.select(cmds.polyListComponentConversion(selectList, tv=True), r=True)
        cmds.ArtPaintSkinWeightsToolOptions()

    @thDoUndo
    def softToWeight(self):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        meshList = self.weightMeshList.getData()
        jointList = self.weightJointList.getData()
        dict_ = eval(cmds.getAttr('extrude_data.notes'))
        for j in jointList:
            father = dict_[j]
            ThLockJointWeight(meshList + [j, father], 'lock')
            cmds.select(selectList, r=True)
            SoftToSkin(j, selectList).apply()

    def setEditWeightButton(self, layout1):
        if self.editWeightWidget:
            self.editWeightWidget.deleteLater()
        self.editWeightWidget = ThQFrameGrp()
        layout1.addWidget(self.editWeightWidget)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.setMargin(2)
        layout2.setSpacing(2)
        self.editWeightWidget.setLayout(layout2)
        meshList = self.weightMeshList.getData()
        jointList = self.weightJointList.getData()
        dict_ = eval(cmds.getAttr('extrude_data.notes'))
        for j in jointList:
            father = dict_[j]
            layout3 = QtWidgets.QHBoxLayout()
            layout3.setMargin(0)
            layout3.setSpacing(2)
            layout2.addLayout(layout3)
            button = QtWidgets.QPushButton(j)
            button.clicked.connect(partial(self._lockJointWeightF, meshList + [j, father], 'lock'))
            layout3.addWidget(button)
            button = QtWidgets.QPushButton('soft')
            button.clicked.connect(partial(self._SoftToSkinF, j))
            layout3.addWidget(button)

    def _lockJointWeightF(self, list_, mode):
        ThLockJointWeight(list_, mode)

    def _SoftToSkinF(self, joint):
        SoftToSkin(joint, cmds.ls(sl=True)).apply()

    def setInputMeshList(self):
        selectList = cmds.ls(sl=True)
        self.weightMeshList.setData(selectList)

    @thDoUndo
    def apply2(self):
        self.ej_cls.rig(self.ctrlSize.value(), self.meshList.getData())
        self.button2.setText(('執行: {}').format(self.inpJoint.getData()))

    @thDoUndo
    def selectJointMode(self, mode):
        applyDict = {'all': 'self.ej_cls.new_joint', 
           '1': 'self.ej_cls.new_joint[0]', 
           '2': 'self.ej_cls.new_joint[1]', 
           'ctrl': 'self.ej_cls.ctrl_list'}
        cmds.select(eval(applyDict[mode]), r=True)

    @thDoUndo
    def apply1(self):
        inpJoint = self.inpJoint.getData()
        self.ej_cls = ThExtrudeJoint(inpJoint, self.quantityList[self.quantity.isCheckedId()][1], self.newJointList.getData(), self.toFather.isChecked())
        self.ej_cls.create_joint()
        self.button1.setText(('執行: {}').format(inpJoint))
        self.newJointList.setData(self.ej_cls.new_joint)
        self.weightJointList.setData(self.ej_cls.new_joint)
        self._inJointList()

    def _setIsParent(self):
        hidden = False if self.quantityList[self.quantity.isCheckedId()][1] == 1 else True
        self.toFather.setHidden(hidden)

    def _inJointList(self):
        newJointList = self.newJointList.getData()
        if not newJointList:
            return
        self.quantityWidget.hide()
        if len(newJointList) == 1:
            self.toFather.show()
        else:
            self.toFather.hide()

    def _inJoint(self):
        u"""Input 目標骨骼"""
        self.newJointList.setData([])
        self._reset()

    def _reset(self):
        u"""重置參數"""
        self._showWidget()
        self._clearButtonText()

    def _showWidget(self):
        u"""顯示小部件"""
        self.quantityWidget.show()
        self._setIsParent()

    def _clearButtonText(self):
        u"""清理 button text"""
        self.button1.setText('執行: ')
        self.button2.setText('執行: ')


class ThQWToolBoxAffectSystem(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxAffectSystem, self).__init__(label='牽動系統', check=check)
        self.topBotton.copyUi(ThQWToolBoxAffectSystem)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('步驟 1: 設置屬性名稱')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 名稱: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.label = QtWidgets.QLineEdit()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.label)
        fIndex += 1
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('select <')
        button.clicked.connect(lambda : self.inputLabel('select'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('attr <')
        button.clicked.connect(lambda : self.inputLabel('attr'))
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('步驟 2: 創建 locator')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 空間: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.axialList = [
         [
          'world', 'world'], ['object', 'object']]
        self.axial = ThQRadioButtonBox([ n[0] for n in self.axialList ], 1, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.axial)
        fIndex += 1
        label = QtWidgets.QLabel(' 軸向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.aimList = [
         [
          'X', 'x'], ['Y', 'y'], ['Z', 'z']]
        self.aim = ThQRadioButtonBox([ n[0] for n in self.aimList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.aim)
        fIndex += 1
        label = QtWidgets.QLabel(' 方向: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.directionList = [
         [
          '+', '+'], ['-', '-']]
        self.direction = ThQRadioButtonBox([ n[0] for n in self.directionList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.direction)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.refList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.refList)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制來源列表:* ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlRefList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlRefList)
        self.button2 = QtWidgets.QPushButton('執行')
        self.button2.clicked.connect(self.apply2)
        layout1.addWidget(self.button2)
        grpBox = QtWidgets.QGroupBox('步驟 3: 設定開始與結束')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QHBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('開始')
        button.clicked.connect(lambda : self.apply3('start'))
        layout1.addWidget(button)
        button = QtWidgets.QPushButton('結束')
        button.clicked.connect(lambda : self.apply3('end'))
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('步驟 4: 設置系統使用數據')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 使用數量: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.useQuantityList = [
         [
          '1', 1], ['2', 2], ['3', 3]]
        self.useQuantity = ThQRadioButtonBox([ n[0] for n in self.useQuantityList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.useQuantity)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.apply4)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 編輯 pose }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 依據: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.editAccordingList = [
         [
          '名稱', 'label'], ['attr', 'box']]
        self.editAccording = ThQRadioButtonBox([ n[0] for n in self.editAccordingList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.editAccording)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout1.addLayout(layout3)
        button = QtWidgets.QPushButton('to start pose')
        button.clicked.connect(lambda : self.toPose('start'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('to end pose')
        button.clicked.connect(lambda : self.toPose('end'))
        layout3.addWidget(button)
        grpBox = QtWidgets.QGroupBox('{ 編輯 system }')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('select system')
        button.clicked.connect(self.selectSys)
        layout1.addWidget(button)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('delete tool')
        button.clicked.connect(lambda : AffectSystemList())
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('check locator')
        button.clicked.connect(lambda : THAffectSystem().check_locator_rotate())
        layout2.addWidget(button)

    def selectSys(self):
        if cmds.objExists('affectSystem_data'):
            cmds.select('affectSystem_data', r=True)

    @thDoUndo
    def toPose(self, mode):
        attrList = [
         self.label.text()]
        if self.editAccordingList[self.editAccording.isCheckedId()][1] == 'box':
            attrList = cmds.channelBox('mainChannelBox', q=True, sma=True)
        THAffectSystem().set_ctrl(mode, attrList)

    def apply4(self):
        self.asCls.set_data(self.useQuantityList[self.useQuantity.isCheckedId()][1])
        sys.stdout.write(' Apply ok!\\n')

    def apply3(self, mode):
        self.asCls.save_pose(mode)
        appDict = {'start': self.asCls.start_data, 
           'end': self.asCls.end_data}
        sys.stdout.write((' {}: {}\\n').format(mode, appDict[mode]))

    @thDoUndo
    def apply2(self):
        attr = self.label.text()
        offset = self.directionList[self.direction.isCheckedId()][1]
        offsetInt = 1 if offset == '+' else -1
        self.asCls = THAffectSystem(self.refList.getData(), attr, self.aimList[self.aim.isCheckedId()][1], self.axialList[self.axial.isCheckedId()][1], offsetInt, self.ctrlRefList.getData())
        self.asCls.create()
        if self.asCls.if_edit:
            self.refList.setData(self.asCls.objs)
            self.ctrlRefList.setData(self.asCls.ctrl)
            self.button2.setText(('編輯: {}').format(attr))
        else:
            self.button2.setText(('創建: {}').format(attr))
        cmds.select(self.asCls.ctrl, r=True)

    def inputLabel(self, mode):
        if mode == 'select':
            selectList = cmds.ls(sl=True)
            self.label.setText(selectList[0] if selectList else '')
        else:
            attrList = cmds.channelBox('mainChannelBox', q=True, sma=True)
            self.label.setText(attrList[0] if attrList else '')


class ThQWToolBoxSmoothAnimCv(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxSmoothAnimCv, self).__init__(label='編輯動畫曲線', check=check)
        self.topBotton.copyUi(ThQWToolBoxSmoothAnimCv)
        parent.addWidget(self)
        grpBox = QtWidgets.QGroupBox('平滑')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 時間範圍: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sacTimeRangeList = [
         [
          '選擇範圍', 'select'], ['動畫總長', 'play']]
        self.sacTimeRange = ThQRadioButtonBox([ n[0] for n in self.sacTimeRangeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sacTimeRange)
        fIndex += 1
        label = QtWidgets.QLabel(' 循環次數: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sacStrength = ThQSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sacStrength)
        fIndex += 1
        label = QtWidgets.QLabel(' 設定值乘數: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sacKeep = ThQDoubleSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sacKeep)
        button = QtWidgets.QPushButton('選擇動畫曲線執行')
        button.clicked.connect(self.sacApplyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('過濾')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 時間範圍: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.filterTimeRangeList = [
         [
          '選擇範圍', 'select'], ['動畫總長', 'play']]
        self.filterTimeRange = ThQRadioButtonBox([ n[0] for n in self.filterTimeRangeList ], 0, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.filterTimeRange)
        fIndex += 1
        label = QtWidgets.QLabel(' time tolerance: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sacTimeTolerance = ThQDoubleSpinBox(value_=0.06)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sacTimeTolerance)
        button = QtWidgets.QPushButton('選擇動畫曲線執行')
        button.clicked.connect(self.filterApplyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('重整動畫曲線(限制旋轉值於360度之內)')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 時間範圍: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.reCustomTimeRangeList = [
         [
          '自訂', True], ['動畫總長', False]]
        self.reCustomTimeRange = ThQRadioButtonBox([ n[0] for n in self.reCustomTimeRangeList ], 1, 'H')
        self.reCustomTimeRange.bg.buttonClicked.connect(self.reSetReTimeRangeF)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.reCustomTimeRange)
        self.reCustomTimeRangeWidgets = ThQFrameGrp()
        layout1.addWidget(self.reCustomTimeRangeWidgets)
        self.reSetReTimeRangeF()
        fIndex_1 = -1
        layout2_1 = QtWidgets.QFormLayout()
        layout2_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2_1.setMargin(2)
        layout2_1.setSpacing(2)
        self.reCustomTimeRangeWidgets.setLayout(layout2_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 起始/ 結束: ')
        layout2_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2_1.setLayout(fIndex_1, QtWidgets.QFormLayout.FieldRole, layout3)
        self.rePlayStart = ThQSpinBox(value_=1)
        layout3.addWidget(self.rePlayStart)
        self.rePlayEnd = ThQSpinBox(value_=80)
        layout3.addWidget(self.rePlayEnd)
        button = QtWidgets.QPushButton('選擇物件執行')
        button.clicked.connect(self.reApplyF)
        layout1.addWidget(button)

    @thDoUndo
    def filterApplyF(self):
        sac = ThSmoothAnimCv(self.filterTimeRangeList[self.filterTimeRange.isCheckedId()][1])
        sac.filterCurveF(timeTolerance=self.sacTimeTolerance.value())

    @thDoUndo
    def sacApplyF(self):
        sac = ThSmoothAnimCv(self.sacTimeRangeList[self.sacTimeRange.isCheckedId()][1])
        sac.smoothF(strongValue=self.sacStrength.value(), keepValue=self.sacKeep.value())

    def reSetReTimeRangeF(self):
        result = self.reCustomTimeRangeList[self.reCustomTimeRange.isCheckedId()][1]
        self.reCustomTimeRangeWidgets.setHidden(not result)

    @thDoUndo
    def reApplyF(self):
        selectList = cmds.ls(sl=True)
        timeRange = None
        if self.reCustomTimeRangeList[self.reCustomTimeRange.isCheckedId()][1]:
            timeRange = [
             self.rePlayStart.value(), self.rePlayEnd.value()]
        if selectList:
            ThBackMocapRotate(selectList, timeRange)
        return


class ThQWToolBoxShootAttrAnim(ThQWToolBox):

    def __init__(self, parent=None, check=False):
        super(ThQWToolBoxShootAttrAnim, self).__init__(label='動作錄製', check=check)
        self.topBotton.copyUi(ThQWToolBoxShootAttrAnim)
        parent.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.attrList = ThQLineBoxAttrList(False)
        self.attrList.setData(['tx', 'ty', 'tz'])
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.attrList)
        fIndex += 1
        label = QtWidgets.QLabel(' fps: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.fps = ThQSpinBox(value_=24)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.fps)
        fIndex += 1
        label = QtWidgets.QLabel(' 初始影格: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.startFrame = ThQSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.startFrame)
        fIndex += 1
        self.ifClear = QtWidgets.QCheckBox('清理頭尾空白數據')
        self.ifClear.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifClear)
        self.saa = ThShootAttrAnim()
        self.appButton = QtWidgets.QPushButton('開始錄製(選擇物件執行)')
        self.appButton.clicked.connect(self.applyF)
        layout1.addWidget(self.appButton)
        grpBox = QtWidgets.QGroupBox('KEY')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        button = QtWidgets.QPushButton('設置到時間軸')
        button.clicked.connect(self.keyF)
        layout1.addWidget(button)
        grpBox = QtWidgets.QGroupBox('創建 curve')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' degree: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.degreeCv = ThQSpinBox(value_=3)
        layout3.addWidget(self.degreeCv)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.createCvF)
        layout3.addWidget(button)

    @thDoUndo
    def createCvF(self):
        if self.saa.ifApp:
            self._endF()
        if self.saa.data:
            self.saa.createCvF(degree=self.degreeCv.value())

    @thDoUndo
    def keyF(self):
        if self.saa.ifApp:
            self._endF()
        if self.saa.data:
            self.saa.keyF(startFrame=self.startFrame.value())
            sys.stdout.write('\n設置完成!')

    def _endF(self):
        self.saa.endF(ifClearData=self.ifClear.isChecked())
        self.appButton.setText('開始錄製(選擇物件執行)')
        sys.stdout.write('\n結束錄製!')

    def applyF(self):
        if self.saa.ifApp:
            self._endF()
        else:
            selectList = cmds.ls(sl=True)
            if not selectList:
                cmds.warning('請選擇一個物件後再執行本功能!')
                return
            self.saa.startF(obj=selectList[0], attr=self.attrList.getData(), fps=self.fps.value())
            self.appButton.setText('結束錄製')
            sys.stdout.write('\n開始錄製!')


class ThQWToolBoxPtInpObjChangeEx(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxPtInpObjChangeEx, self).__init__(label='列表屬性驅動 0 到 1 屬性值', check=check)
        self.topBotton.copyUi(ThQWToolBoxPtInpObjChangeEx)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標物件與屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.objAttr = ThQLineBoxObjAttr(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.objAttr)
        fIndex += 1
        label = QtWidgets.QLabel(' 來源列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.inpObjList = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.inpObjList)
        self.inpObjList.inputButton.clicked.connect(self.doClassF)
        fIndex += 1
        label = QtWidgets.QLabel(' 定義動作變化: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('起始')
        button.clicked.connect(lambda : self.getDataF('start'))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('結束')
        button.clicked.connect(lambda : self.getDataF('end'))
        layout3.addWidget(button)
        fIndex += 1
        self.ifExpression = QtWidgets.QCheckBox('創建 expression')
        self.ifExpression.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifExpression)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.appPrintF)
        layout1.addWidget(button)
        self.pioce = None
        return

    def doClassF(self):
        self.pioce = ThPtInpObjChangeEx(self.inpObjList.getData())

    @thDoUndo
    def appPrintF(self):
        errorText = None
        if not self.pioce:
            errorText = '請先設定來源列表!'
        elif not self.pioce.startData:
            errorText = '請先定義起始動作!'
        elif not self.pioce.endData:
            errorText = '請先定義結束動作!'
        if errorText:
            cmds.warning(errorText)
            return
        else:
            self.pioce.printF(self.objAttr.getData(), self.ifExpression.isChecked())
            return

    @thDoUndo
    def getDataF(self, mode):
        if not self.pioce:
            errorText = '請先設定來源列表!'
            cmds.warning(errorText)
            return
        self.pioce.getDataF(mode)


class ThQWToolBoxDefToSkin(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxDefToSkin, self).__init__(label='變形器轉換蒙皮權重', check=check)
        self.topBotton.copyUi(ThQWToolBoxDefToSkin)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.meshList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.meshList)
        fIndex += 1
        label = QtWidgets.QLabel(' 骨骼列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.jointList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.jointList)
        fIndex += 1
        label = QtWidgets.QLabel('* 本功能是將每根骨骼移動一段距離\n獲取頂點位置差異轉換為權重數據')
        label.setObjectName('annotation')
        self.topBotton.addHelpText(label)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, label)
        fIndex += 1
        label = QtWidgets.QLabel(' 權重模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.dirList = [
         [
          'x', 'x'], ['y', 'y'], ['z', 'z']]
        self.dir = ThQRadioButtonBox([ n[0] for n in self.dirList ], 1, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.dir)
        fIndex += 1
        label = QtWidgets.QLabel(' 計算距離: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.offset = ThQSpinBox(value_=1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.offset)
        fIndex += 1
        self.ifNewMesh = QtWidgets.QCheckBox('複製出新模型(權重無法undo)')
        self.ifNewMesh.setChecked(True)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifNewMesh)
        fIndex += 1
        line = ThSeparationLine('H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.SpanningRole, line)
        fIndex += 1
        self.ifDelLattice = QtWidgets.QCheckBox('刪除 lattice')
        self.ifDelLattice.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifDelLattice)
        fIndex += 1
        self.ifDelDeltaMush = QtWidgets.QCheckBox('刪除 deltaMush')
        self.ifDelDeltaMush.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifDelDeltaMush)
        fIndex += 1
        self.ifDelTension = QtWidgets.QCheckBox('刪除 tension')
        self.ifDelTension.setChecked(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ifDelTension)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.applyF)
        layout1.addWidget(button)

    @thDoUndo
    def applyF(self):
        ThDefToSkin().applyF(self.meshList.getData(), self.jointList.getData(), self.offset.value(), self.ifNewMesh.isChecked(), self.ifDelLattice.isChecked(), self.ifDelDeltaMush.isChecked(), self.ifDelTension.isChecked(), self.dirList[self.dir.isCheckedId()][1])


class ThQWToolBoxLoopValueRangeLimit(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxLoopValueRangeLimit, self).__init__(label='列表屬性值 0 到 1 循環', check=check)
        self.topBotton.copyUi(ThQWToolBoxLoopValueRangeLimit)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.list_ = ThQLineBoxList(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.list_)
        fIndex += 1
        label = QtWidgets.QLabel(' 目標屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.attr = ThQLineBoxAttr(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.attr)
        fIndex += 1
        label = QtWidgets.QLabel(' 控制器與屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.ctrlAttr = ThQLineBoxObjAttr(False)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.ctrlAttr)
        fIndex += 1
        label = QtWidgets.QLabel(' 速度: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.sleep = ThQDoubleSpinBox(value_=0.1)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.sleep)
        button = QtWidgets.QPushButton('執行')
        button.clicked.connect(self.applyF)
        layout1.addWidget(button)

    def applyF(self):
        ThLoopValueRangeLimit(list_=self.list_.getData(), ctrlAttr=self.ctrlAttr.getData(), attr=self.attr.getData(), speed=self.sleep.value())


class ThQWToolBoxTimeFrameConvert(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxTimeFrameConvert, self).__init__(label='時間/ 影格換算', check=check)
        self.topBotton.copyUi(ThQWToolBoxTimeFrameConvert)
        parenr.addWidget(self)
        grpBox = QtWidgets.QGroupBox('影格 -> 時間')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 影格數/ FPS: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.ffFrame = ThQSpinBox(value_=0)
        layout3.addWidget(self.ffFrame, 40)
        self.ffFps = ThQSpinBox(value_=30)
        layout3.addWidget(self.ffFps, 25)
        button = QtWidgets.QPushButton('打印結果')
        button.clicked.connect(self.ffApplyF)
        layout3.addWidget(button, 35)
        grpBox = QtWidgets.QGroupBox('時間 -> 影格')
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 時/ 分/ 秒/ 格: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.tfHour = ThQSpinBox(value_=0)
        layout3.addWidget(self.tfHour)
        self.tfMinute = ThQSpinBox(value_=0)
        layout3.addWidget(self.tfMinute)
        self.tfSecond = ThQSpinBox(value_=0)
        layout3.addWidget(self.tfSecond)
        self.tfFrame = ThQSpinBox(value_=0)
        layout3.addWidget(self.tfFrame)
        fIndex += 1
        label = QtWidgets.QLabel(' FPS: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.tfFps = ThQSpinBox(value_=30)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.tfFps)
        fIndex += 1
        label = QtWidgets.QLabel(' 添加(格): ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.addFrame = ThQSpinBox(value_=0)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.addFrame)
        button = QtWidgets.QPushButton('打印結果')
        button.clicked.connect(self.tfApplyF)
        layout1.addWidget(button)

    def tfApplyF(self):
        thTimeToFrameF(self.tfHour.value(), self.tfMinute.value(), self.tfSecond.value(), self.tfFrame.value(), self.tfFps.value(), self.addFrame.value())

    def ffApplyF(self):
        ThFrameToTime().toTime(self.ffFrame.value(), self.ffFps.value())


class ThQWToolBoxAlignAndKey(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxAlignAndKey, self).__init__(label='對位並 KEY', check=check)
        self.topBotton.copyUi(ThQWToolBoxAlignAndKey)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 套用屬性: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        self.foT = QtWidgets.QCheckBox('translate')
        self.foT.setChecked(True)
        layout3.addWidget(self.foT)
        self.foR = QtWidgets.QCheckBox('rotate')
        self.foR.setChecked(True)
        layout3.addWidget(self.foR)
        fIndex += 1
        label = QtWidgets.QLabel(' 設定模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.foSetModeList = [
         [
          '逐格', 'frame'], ['自訂範圍', 'range']]
        self.foSetMode = ThQRadioButtonBox([ n[0] for n in self.foSetModeList ], 0, 'H')
        self.foSetMode.bg.buttonClicked.connect(self.foSetModeF)
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.foSetMode)
        self.foFrameW = ThQFrameGrp()
        layout1.addWidget(self.foFrameW)
        layout1_1 = QtWidgets.QHBoxLayout()
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.foFrameW.setLayout(layout1_1)
        button = QtWidgets.QPushButton('往前')
        button.clicked.connect(lambda : self.foApplyF('previous'))
        layout1_1.addWidget(button)
        button = QtWidgets.QPushButton('往後')
        button.clicked.connect(lambda : self.foApplyF('next'))
        layout1_1.addWidget(button)
        self.foRangeW = ThQFrameGrp()
        layout1.addWidget(self.foRangeW)
        fIndex_1 = -1
        layout1_1 = QtWidgets.QFormLayout()
        layout1_1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout1_1.setMargin(2)
        layout1_1.setSpacing(2)
        self.foRangeW.setLayout(layout1_1)
        fIndex_1 += 1
        label = QtWidgets.QLabel(' 起始/ 結束: ')
        layout1_1.setWidget(fIndex_1, QtWidgets.QFormLayout.LabelRole, label)
        layout1_2 = QtWidgets.QHBoxLayout()
        layout1_2.setMargin(0)
        layout1_2.setSpacing(2)
        layout1_1.setLayout(fIndex_1, QtWidgets.QFormLayout.FieldRole, layout1_2)
        self.foStart = ThQSpinBox(value_=0)
        layout1_2.addWidget(self.foStart)
        self.foEnd = ThQSpinBox(value_=10)
        layout1_2.addWidget(self.foEnd)
        button = QtWidgets.QPushButton('apply')
        button.clicked.connect(lambda : self.foApplyF('next'))
        layout1_2.addWidget(button)
        self.foSetModeF()

    def foSetModeF(self):
        data = self.foSetModeList[self.foSetMode.isCheckedId()][1]
        setData = True if data == 'frame' else False
        self.foFrameW.setHidden(not setData)
        self.foRangeW.setHidden(setData)

    @thDoUndo
    def foApplyF(self, mode):
        selectList = cmds.ls(sl=True)
        if len(selectList) != 2:
            return
        else:
            strat = None
            end = None
            if self.foSetModeList[self.foSetMode.isCheckedId()][1] == 'range':
                strat = self.foStart.value()
                end = self.foEnd.value()
            thFollowObjAnimF(selectList[0], selectList[1], mode, self.foT.isChecked(), self.foR.isChecked(), strat, end)
            return


class ThQWToolBoxSolverDisplay(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxSolverDisplay, self).__init__(label='Solver display', check=check)
        self.topBotton.copyUi(ThQWToolBoxSolverDisplay)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' cloth: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('on')
        button.clicked.connect(lambda : self.solverDisplayApply('nCloth', 1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('off')
        button.clicked.connect(lambda : self.solverDisplayApply('nCloth', 0))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('on(all)')
        button.clicked.connect(lambda : self.solverDisplayApplyAll('nCloth', 1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('off(all)')
        button.clicked.connect(lambda : self.solverDisplayApplyAll('nCloth', 0))
        layout3.addWidget(button)
        fIndex += 1
        label = QtWidgets.QLabel(' hair: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('on')
        button.clicked.connect(lambda : self.solverDisplayApply('hairSystem', 1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('off')
        button.clicked.connect(lambda : self.solverDisplayApply('hairSystem', 0))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('on(all)')
        button.clicked.connect(lambda : self.solverDisplayApplyAll('hairSystem', 1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('off(all)')
        button.clicked.connect(lambda : self.solverDisplayApplyAll('hairSystem', 0))
        layout3.addWidget(button)
        fIndex += 1
        label = QtWidgets.QLabel(' rigid: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        layout3 = QtWidgets.QHBoxLayout()
        layout3.setMargin(0)
        layout3.setSpacing(2)
        layout2.setLayout(fIndex, QtWidgets.QFormLayout.FieldRole, layout3)
        button = QtWidgets.QPushButton('on')
        button.clicked.connect(lambda : self.solverDisplayApply('nRigid', 1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('off')
        button.clicked.connect(lambda : self.solverDisplayApply('nRigid', 0))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('on(all)')
        button.clicked.connect(lambda : self.solverDisplayApplyAll('nRigid', 1))
        layout3.addWidget(button)
        button = QtWidgets.QPushButton('off(all)')
        button.clicked.connect(lambda : self.solverDisplayApplyAll('nRigid', 0))
        layout3.addWidget(button)

    @thDoUndo
    def solverDisplayApplyAll(self, isType, envelope):
        selectList = cmds.ls(type=isType)
        if not selectList:
            return
        for n in selectList:
            cmds.setAttr(n + '.solverDisplay', envelope)
            if envelope and isType == 'nRigid':
                cmds.setAttr(n + '.displayColor', 1, 0, 0, type='double3')

        hidden = {1: 'cmds.showHidden({}, a=True)', 0: 'cmds.hide({})'}
        eval(hidden[envelope].format(selectList))

    @thDoUndo
    def solverDisplayApply(self, isType, envelope):
        selectList = cmds.ls(sl=True)
        if not selectList:
            return
        else:
            typeList = thType(selectList)
            fatherList = [ selectList[i] for i, n in enumerate(typeList) if n == 'transform' ]
            meshList = [ selectList[i] for i, n in enumerate(typeList) if n == 'mesh' ]
            isTypeList = [ selectList[i] for i, n in enumerate(typeList) if n == isType ]
            if fatherList:
                fatherList = cmds.listRelatives(fatherList, ad=True, typ=isType, f=True) or []
            if meshList:
                meshList = [ cmds.listConnections(n + '.worldMesh', s=False, type=isType) for n in meshList ]
                meshList = [ n[0] for n in meshList if n is not None ]
            doList = fatherList + meshList + isTypeList
            for n in doList:
                cmds.setAttr(n + '.solverDisplay', envelope)
                if envelope and isType == 'nRigid':
                    cmds.setAttr(n + '.displayColor', 1, 0, 0, type='double3')

            hidden = {1: 'cmds.showHidden({}, a=True)', 0: 'cmds.hide({})'}
            eval(hidden[envelope].format(doList))
            cmds.select(selectList, r=True)
            return


class ThQWToolBoxEditSelectJointSkinWeight(ThQWToolBox):

    def __init__(self, parenr=None, check=False):
        super(ThQWToolBoxEditSelectJointSkinWeight, self).__init__(label='編輯指定骨骼權重', check=check)
        self.topBotton.copyUi(ThQWToolBoxEditSelectJointSkinWeight)
        parenr.addWidget(self)
        grpBox = ThQFrameGrp()
        self.layout.addWidget(grpBox)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        grpBox.setLayout(layout1)
        fIndex = -1
        layout2 = QtWidgets.QFormLayout()
        layout2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        fIndex += 1
        label = QtWidgets.QLabel(' 模型: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.mesh = ThQLineBox()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.mesh)
        fIndex += 1
        label = QtWidgets.QLabel(' 骨骼列表: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.jointList = ThQLineBoxList()
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.jointList)
        fIndex += 1
        label = QtWidgets.QLabel(' 權重模式: ')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.LabelRole, label)
        self.weightModeList = [
         [
          'copy', 'copy'], ['skin', 'skin'], ['none', None]]
        self.weightMode = ThQRadioButtonBox([ n[0] for n in self.weightModeList ], 1, 'H')
        layout2.setWidget(fIndex, QtWidgets.QFormLayout.FieldRole, self.weightMode)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(2)
        layout1.addLayout(layout2)
        button = QtWidgets.QPushButton('開始編輯')
        button.clicked.connect(self.editF)
        layout2.addWidget(button)
        button = QtWidgets.QPushButton('導回權重')
        button.clicked.connect(self.modifyF)
        layout2.addWidget(button)
        return

    @thDoUndo
    def modifyF(self):
        ThEditSelectJointSkinWeight().modifyF()

    @thDoUndo
    def editF(self):
        ThEditSelectJointSkinWeight().editF(self.mesh.getData(), self.jointList.getData(), self.weightModeList[self.weightMode.isCheckedId()][1])


if __name__ == '__main__':
    if 'thRigToolsWin' in globals():
        thRigToolsWin.close()
        del thRigToolsWin
    thRigToolsWin = ThRigToolsQtWin()
RIG_NOTE = "\n- MAYA 重新拓樸(MEL):\n    polyRemesh -rft 1;\n    polyRetopo;\n\n\n- 表情 RIG 注意事項:\n    - 嘴巴:\n        - 做嘴巴整體權重:\n            - 拆分上下權重\n                - 創建 low 模型並 bind 到骨架上\n                - 複製 low 並 smooth\n                - 將 low 權重 copy 到 smooth\n                - 處理 smooth 權重(20次)\n                - 使用 blend 展開 Smooth weight(1.展開呈扇形, 2.調整為平面)\n                - 使用 smooth 之模型去拆分嘴唇之主要權重\n        - 嘴邊周圍肌肉:\n            - 要做兩層(也就是要有起始與結束端，模擬肌肉拉伸)\n            - 注意有分為上顎與下顎之權重\n        - 拉鍊嘴型:\n            - 嘴角上下偏移屬性，需要做 driven key(初始為0，往上驅動微笑、往下反之)\n        - Main ctrl:\n            - smooth mesh(3次), smooth weight(4次)(排除邊界 vertex)\n    - 眼睛:\n        - Joint:\n            - 整體 joint_1(移動 eye)\n            - 整體 joint_2(閉眼)\n            - 細節\n        - 權重處理:\n            - 處理整體位移權重\n            - 處理閉眼整體權重\n            - 複製一個模型並切出細節(做閉眼)\n            - 分割閉眼細節模型權重:\n                - smooth mesh(3次), smooth weight(6次)(整體 vertex)\n    - 眉毛:\n        - 分割細節模型權重:\n            - joint 數量(5), smooth mesh(2次), smooth weight(8次)(排除邊界 vertex)\n    - Driven key:\n        - 帶旋轉的要先 key\n    - 修 blend shape:\n        - 先修左或右邊在鏡像與合併\n\n- 其他:\n    - group 層級堆疊控制方法是，能旋轉的一定要在最接近起始層\n\n\n————————————————————————————————————————————————————————————————————————————————\n# 統一 mesh id\nlistObj1 = [\n    'AL_V2_exp01:ZBrushPolyMesh3D.vtx[34522]', \n    'AL_V2_exp01:ZBrushPolyMesh3D.vtx[1308]', \n    'AL_V2_exp01:ZBrushPolyMesh3D.vtx[30602]']\n#\nlistObj2 = cmds.ls(sl=True)\nlistVtx2 = ['.vtx[60822]', '.vtx[2642]', '.vtx[47217]']\n#\nfor i, n in enumerate(listObj2):\n    print(u'set: ', n)\n    #cmds.select([n+listVtx2[0], n+listVtx2[1], n+listVtx2[2]], add=True)\n    cmds.meshRemap(\n        listObj1[0], listObj1[1], listObj1[2], \n        n+listVtx2[0], n+listVtx2[1], n+listVtx2[2])\n\n————————————————————————————————————————————————————————————————————————————————\n# 數值轉換到限制範圍\nold_value = 10000\nold_min = .0\nold_max = 16000\nnew_min = .0\nnew_max = 1\n\nold_range = (old_max - old_min)\nnew_range = (new_max - new_min)\nnew_value = (((old_value - old_min) * new_range) / old_range) + new_min\nprint(new_value)\n\n————————————————————————————————————————————————————————————————————————————————\n# 保留 Function\nthDefSineSwirlRig  # Sine 變形器設定漩渦 rig effects\nthFindLayerObj  # 返回 animLayer 中的物件\nthGetMouseCoordinates  # 讀取滑鼠座標\n\n————————————————————————————————————————————————————————————————————————————————\n# 修改 blens shape 方法\n- 創建 blend shape node\n- 連上驅動控制器\n- 調整 pose，傳遞回修改 shape\n- 回到 bind pose，段開控制器連接\n- 打開數值，複製模型，拆分模型\n- 導回左右邊\n\n————————————————————————————————————————————————————————————————————————————————\n# dynamic blend shape 研究\n- 變數總量公式 = (總變數) + (個別變數*個別變數)\n8 + (4 * 4)\n16 + (8 * 8)\n\n————————————————————————————————————————————————————————————————————————————————\n# 獲取當前計算機語言\nQtCore.QLocale.system().name()\n"