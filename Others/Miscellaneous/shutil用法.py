# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-05-10 16:03
# Description:

# import shutil
#
# shutil.copyfileobj(open(r'C:\\Users\\yinyufei\\Desktop\\skin.json', 'r'),
#                    open(r'C:\\Users\\yinyufei\\Desktop\\cs.cs', 'w'))

# shutil.copyfile(r'C:\Users\yinyufei\Desktop\skin.json',
#                 r'C:\Users\yinyufei\Desktop\skin02.json')
# !/usr/bin/env python
# encoding=utf-8
import os
import sys
if __name__ == '__main__':

    dirname = "E:\\TO yinyufei\\yyf\\gongju\JunCmds\\blendShapeManage\\blendShapeManage"

    os.system('uncompyle6 -o %s.py %s.pyc'%(dirname,dirname))
