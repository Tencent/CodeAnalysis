# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import json
import os
import sys

from task.codelintmodel import CodeLintModel
from util.exceptions import AnalyzeTaskError
from util.logutil import LogPrinter
from node.app import settings
from task.authcheck.check_license import __lu__
from tool.util.compass import Compass as Tool

logger = LogPrinter


class Compass(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)

    def analyze(self, params):
        source_dir = params["source_dir"]
        self.relpos = len(source_dir) + 1
        result_path = Tool(params).scan()
        if not os.path.exists(result_path):
            logger.info("没有生成结果文件")
            raise AnalyzeTaskError("工具执行错误")
        with open(result_path, "r") as result_reader:
            issues = json.load(result_reader)
            if not issues:
                return []
            issues = self._format_issue(issues)
        return issues

    def check_tool_usable(self, tool_params):
        if settings.PLATFORMS[sys.platform] == "mac":
            return []
        return ["analyze"]

    def _format_issue(self, lint_result):
        issues = []
        for i in lint_result:
            issues.append(
                {
                    "column": i["column"],
                    "line": i["line"],
                    "msg": i["msg"],
                    "rule": i["rule"],
                    "path": i["path"][self.relpos :],
                    "refs": [],
                }
            )
        return issues


tool = Compass

if __name__ == "__main__":
    pass
