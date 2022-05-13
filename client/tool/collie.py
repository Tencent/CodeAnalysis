#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys

from tool.util.collie import Collie as Tool
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from node.app import settings


class Collie(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Collie": "Tool", "collie": "Tool"}

    def analyze(self, params):
        issues = list()
        collie = Tool(params=params)
        func_output = collie.check()
        if func_output and os.path.exists(os.path.join(func_output, "check.csv")):
            for issue in collie.get_issue(os.path.join(func_output, "check.csv")):
                issues.append(issue)

        return issues

    def check_tool_usable(self, tool_params):
        cmds = Tool().get_cmd(["-v"])
        if settings.PLATFORMS[sys.platform] == "mac":
            return []
        elif SubProcController(
                cmds,             
                # stdout_line_callback=print,
                # stderr_line_callback=print,
            ).wait() != 0:
            return []
        return ["analyze"]


tool = Collie

if __name__ == "__main__":
    pass
