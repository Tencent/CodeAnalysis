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


class TcaQlCpp(TcaQl):
    def __init__(self, params):
        super().__init__(params)

    def compile(self, params):
        lang = "cpp"
        super().compile(params, lang)

    def analyze(self, params):
        lang = "cpp"
        issues = super().analyze(params, lang)
        return issues

tool = TcaQlCpp

if __name__ == "__main__":
    pass