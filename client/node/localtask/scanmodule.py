# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
启用的扫描组件
可选值:lint,cc,dup,cloc(分别代表代码检查、圈复杂度、重复代码、代码统计这4个检查组件),多项可用英文逗号(,)分隔
"""

import logging

from util.textutil import StringMgr

logger = logging.getLogger(__name__)


class ScanModule(object):
    """
    管理启用的扫描组件
    """
    @staticmethod
    def get_module_setting(scan_module_str):
        """
        获取扫描组件配置
        :param scan_module_str: 可选值-lint,cc,dup,cloc(分别代表代码检查、圈复杂度、重复代码、代码统计这4个检查组件),多项用英文逗号(,)分隔
        :return:
        """
        # 初始化默认配置,默认只启用代码检查组件
        module_setting = {
            "lint": True,
            "cc": False,
            "dup": False,
            "cloc": False
        }
        if scan_module_str:
            enable_module_list = StringMgr.str_to_list(scan_module_str)
            for name, value in module_setting.items():
                if name in enable_module_list:
                    module_setting[name] = True
                else:
                    module_setting[name] = False
        return module_setting
