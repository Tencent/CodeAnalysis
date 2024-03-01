#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from tool.util.infer import Infer
from task.codelintmodel import CodeLintModel
from tool.util.xcodeswitch import XcodeSwitch

VERSION = "1.1"


class InferOC(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"inferOC": "Tool"}

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        # 根据项目环境变量选择合适的xcode版本
        XcodeSwitch.set_xcodebuild_version()

        params.lang = __name__.split("_")[1]
        self.print_log("inferOC compile start.")
        return Infer(self.sensitive).compile(params)

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        params.lang = __name__.split("_")[1]
        self.print_log("inferOC analyze start.")
        return Infer(self.sensitive).analyze(params)


tool = InferOC

if __name__ == "__main__":
    pass
