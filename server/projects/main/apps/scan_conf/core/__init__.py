# -*- coding: utf-8 -*-
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
    # TODO：注意：使用此方法需兼容不同平台，对于规则权限有不同的判断
    CheckPackageManager.add_rules(checkpackage, checkrules, user)
