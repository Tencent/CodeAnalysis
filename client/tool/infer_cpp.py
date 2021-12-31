#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from tool.util.infer import Infer
from task.codelintmodel import CodeLintModel

VERSION = "1.1"


class InferCPP(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"inferCPP": "Tool"}

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        params.lang = __name__.split("_")[1]
        self.print_log("inferCPP compile start.")
        return Infer(self.sensitive).compile(params)

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        params.lang = __name__.split("_")[1]
        self.print_log("inferCPP analyze start.")
        return Infer(self.sensitive).analyze(params)


tool = InferCPP

if __name__ == "__main__":
    pass
