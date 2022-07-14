# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-27 20:03:35
# @Last Modified by:   Admin
# @Last Modified time: 2022-04-30 22:03:41

import string
import re
import pymel.core as pm

# default fields/tokens
NAMING_SPECIFICATE_TOKENS = ["guide",
                      "side",
                      "index",
                      "description",
                      "extension"]
DEFAULT_NAMING_SPECIFICATE = r"{guide}_{side}{index}_{description}_{extension}"
DEFAULT_SIDE_L_NAME = "L"
DEFAULT_SIDE_R_NAME = "R"
DEFAULT_SIDE_C_NAME = "M"
DEFAULT_JOINT_SIDE_L_NAME = "L"
DEFAULT_JOINT_SIDE_R_NAME = "R"
DEFAULT_JOINT_SIDE_C_NAME = "M"
DEFAULT_CTL_EXT_NAME = "ctrl"
DEFAULT_JOINT_EXT_NAME = "jnt"


def normalize_name_Specificate(text):
    """规范化命名规范模板替换无效字符

    :param text string: A text to normalize.
    :return text: Normalized text

    """
    text = str(text)

    if re.match("^[0-9]", text):
        text = "_" + text

    return re.sub("[^A-Za-z0-9_{}]", "", str(text))


def name_Specificate_validator(Specificate, valid_tokens, log=True):
    """
    检查命名规则
    :param Specificate: 名称规则
    :param valid_tokens: 指定的有效字符
    :param log: 打印log日志
    :return:
    """

    invalid_tokens = []
    for token in string.Formatter().parse(Specificate):

        if token[1] and token[1] in valid_tokens:
            continue
        # compare to None to avoid errors with empty token
        elif token[1] is None and token[0]:
            continue
        else:
            invalid_tokens.append(token[1])

    if invalid_tokens:
        if log:
            pm.displayWarning(
                "{} not valid token".format(invalid_tokens))
            pm.displayInfo("Valid tokens are: {}".format(NAMING_SPECIFICATE_TOKENS))
        return
    else:
        return True


def name_solve(Specificate, values, validate=True):
    """
    解包字典赋值给命名规则的表达式中
    :param Specificate: 指定名称
    :param values: 字典数据
    :param validate: 检查字典中的数据是否规范
    :return:
    """

    # index padding
    values["index"] = str.zfill(values["index"], values["padding"])
    included_val = dict()
    if validate and not name_Specificate_validator(Specificate, NAMING_SPECIFICATE_TOKENS):
        return
    for token in string.Formatter().parse(Specificate):
        if token[1]:
            try:
                included_val[token[1]] = values[token[1]]
            except KeyError:
                continue
        elif token[0]:
            continue
        else:
            return

    return Specificate.format(**included_val)


def letter_case_solve(name, letter_case=0):
    """
    修改大小写
    :param name: 名称
    :param letter_case:
            0 = will not change the leter casing
            1 = will convert all letters to upper case
            2 = will convert all letters to lower case
            3 = will capitalize the first letter of the name
    :return: TYPE: Description
    """

    if letter_case == 1:
        name = name.upper()
    elif letter_case == 2:
        name = name.lower()
    elif letter_case == 3:
        name = name.capitalize()
    return name


def get_component_and_relative_name(guide_name):
    """
    获取组件名称和相对的本地名称
    ie. "arm_C0_root" return "arm_C0"
    :param guide_name: guide 名称
    :return: TYPE: Description
    """

    guide_name_split = guide_name.split("_")
    # chains are the only component that have 2 parts at the end
    if guide_name.endswith("_loc"):
        n = 2
    else:
        n = 1
    comp_name = "_".join(guide_name_split[:-n])
    local_relative_name = "_".join(guide_name_split[-n:])

    return comp_name, local_relative_name
