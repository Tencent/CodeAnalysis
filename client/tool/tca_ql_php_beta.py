#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
from util.logutil import LogPrinter
from tool.util.tca_ql_beta import TcaQlBeta


logger = LogPrinter()


class TcaQlPHPBeta(TcaQlBeta):
    def __init__(self, params):
        super().__init__(params)

    def compile(self, params):
        """
        编译执行函数
        :param params: 编译所需要的资源 1.项目地址 2. 编译命令 3. 环境变量参数 4.编译结果生成地址
        :return:
        """
        lang = "php"
        super().compile(params, lang)

    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        lang = "php"
        issues = super().analyze(params, lang)
        return issues

tool = TcaQlPHPBeta

if __name__ == "__main__":
    pass