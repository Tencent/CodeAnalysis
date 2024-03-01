#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from util.logutil import LogPrinter
from tool.util.tca_ql import TcaQl


logger = LogPrinter()


class TcaQlPython(TcaQl):
    def __init__(self, params):
        super().__init__(params)

    def compile(self, params):
        lang = "python"
        super().compile(params, lang)

    def analyze(self, params):
        lang = "python"
        issues = super().analyze(params, lang)
        return issues

tool = TcaQlPython

if __name__ == "__main__":
    pass