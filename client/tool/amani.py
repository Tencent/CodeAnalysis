#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys

from tool.util.amani import Amani as Tool
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from node.app import settings


class Amani(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Amani": "Tool", "amani": "Tool"}

    def analyze(self, params):
        """
        :param params: 
        :return:
        """
        issues = list()
        amani = Tool(params=params)
        output = amani.check()
        if output and os.path.exists(output):
            # 处理结果
            for issue in amani.get_issue(output):
                issues.append(issue)

        return issues

    def check_tool_usable(self, tool_params):
        if settings.PLATFORMS[sys.platform] == "mac":
            return []
        cmds = Tool().get_cmd(["--version"])
        if SubProcController(cmds).wait() != 0:
            return []
        return ["analyze"]


tool = Amani

if __name__ == "__main__":
    pass
