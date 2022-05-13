# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import json
import os
import sys

from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.envset import EnvSet
from util.exceptions import AnalyzeTaskError
from util.logutil import LogPrinter
from node.app import settings
from task.authcheck.check_license import __lu__

logger = LogPrinter


class Compass(CodeLintModel):

    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.tool_home = os.environ.get("COMPASS_HOME")
        self.tool_name = self.__class__.__name__
        
    def analyze(self, params):
        source_dir = params["source_dir"]
        self.relpos = len(source_dir) + 1
        task_dir = os.path.dirname(os.getcwd())
        os.environ["SOURCE_DIR"] = source_dir
        request_file = os.path.abspath(os.path.join(task_dir, "task_request.json"))
        os.environ["TASK_REQUEST"] = request_file
        tool_cmd = self.get_cmd(["--TOKEN"])
        work_dir = os.getcwd()

        sp = SubProcController(
            command=tool_cmd,
            cwd=work_dir,
            stdout_line_callback=self.print_log,
            stderr_line_callback=self.print_log,
            env = EnvSet().get_origin_env()
        )
        sp.wait()
        result_path = os.path.join(work_dir, "result.json")
        if not os.path.exists(result_path):
            logger.info("没有生成结果文件")
            raise AnalyzeTaskError("工具执行错误")
        with open(result_path, 'r') as result_reader:
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
                    "path": i["path"][self.relpos:],
                    "refs": [],
                }
            )
        return issues

    def get_cmd(self, args):
        tool_path = os.path.join(self.tool_home, "bin", settings.PLATFORMS[sys.platform], self.tool_name)
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return __lu__().format_cmd(tool_path, args)

tool = Compass

if __name__ == "__main__":
    pass
