# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2025 Tencent
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
tscan 扫描任务
"""

import os


from tool.util.tscan import Tscan


class TscanLua(Tscan):
    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        want_suffix = ["lua", "wlua", "glua", "gluaw", "mlua", "clua", "lua.txt"]
        envs = os.environ
        tc_home = envs.get("TSCANLUA_HOME", None)
        bin_name = "tsclua"
        issues = []
        issues = super().analyze(params, tc_home, bin_name, want_suffix)
        return issues


tool = TscanLua

if __name__ == "__main__":
    pass
