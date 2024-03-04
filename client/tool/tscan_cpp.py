# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
tscan 扫描任务
"""

import os


from tool.util.tscan import Tscan


class TscanCode(Tscan):
    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        want_suffix = ["cpp", "c", "C", "cc", "cxx", "h", "hxx", "hpp"]
        envs = os.environ
        tc_home = envs.get("TSCANCPP_HOME", None)
        bin_name = "tscancode"
        issues = []
        issues = super().analyze(params, tc_home, bin_name, want_suffix)
        return issues


tool = TscanCode

if __name__ == "__main__":
    pass
