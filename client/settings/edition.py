# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""版本相关的配置信息
"""

from enum import Enum


# ========================
# 版本可选值
# ========================
class Edition(Enum):
    OpenSource = 1


# ========================
# 版本声明
# ========================
EDITION = Edition.OpenSource


# ========================
# 版本号
# ========================
# puppy版本号,格式：浮点数，整数部分为8位日期，小数部分为编号(从1开始)
VERSION = 20240716.1
