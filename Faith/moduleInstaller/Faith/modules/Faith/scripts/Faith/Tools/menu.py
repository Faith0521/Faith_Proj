# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yin Yu Fei
# Github: https://github.com/
# CreatDate: 2022-07-21 16:09
# Description:
from functools import partial
import Faith.menu
import pymel.core as pm


def install_tool():
    """
    Install some useful small tools
    @return:
    """
    commands = (
        ("SDK_Tool", str_show_sdk, ""),
        ("BlendShape_Tool", str_bs_show, ""),
        ("CCS(for maya 2022)", str_ccs, ""),
        ("Rename_Tool", str_rename_show, ""),
        ("Rivet_Tool", str_rivet_show, ""),
    )
    Faith.menu.install("Tools", commands, image="")


def install_skin():
    """

    @return:
    """
    commands = (
        ("Copy Skin", str_show_skin, ""),
        ("Export Skin Weight", str_exp_skin, ""),
        ("Import Skin Weight", str_imp_skin, ""),
        ("Export Deformer Weight", str_exp_deform, ""),
        ("Import Deformer Weight", str_imp_deform, ""),
    )
    Faith.menu.install("Skin And Weights", commands, image="")


str_show_sdk = """
import Faith.Tools.SDK_Manager.UI.ui_manager as ui
ui.show_guide_component_manager()
"""
str_bs_show = """

"""
str_ccs = """

"""
str_rename_show = """

"""
str_rivet_show = """

"""


str_show_skin = """

"""
str_exp_skin = """

"""
str_imp_skin = """

"""
str_exp_deform = """

"""
str_imp_deform = """

"""