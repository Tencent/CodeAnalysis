# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - core
"""
# 项目内
from .basemgr import *
from .rulemgr import *
from .toollibmgr import *
from .toolmgr import *
from .pkgmgr import *
from .profilemgr import *


def add_checkrules_to_checkpackage(checkpackage, checkrules, user=None):
    """
    批量添加规则到规则包
    """
    CheckPackageManager.add_rules(checkpackage, checkrules, user)
