#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
flow: A STATIC TYPE CHECKER FOR JAVASCRIPT.
"""

import json
import os
from shutil import copyfile

from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.logutil import LogPrinter


class Flow(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "Flow": "Tool",
            "flow": "Tool"
        }

    def analyze(self, params):
        source_dir = params.source_dir
        work_dir = os.getcwd()
        rules = params["rules"]

        error_output = os.path.join(work_dir, "flow_result.json")
        config_file = os.path.join(source_dir, ".flowconfig")
        user_config_file = os.path.join(work_dir, "user_flowconfig")
        default_rule = "type-error"

        # 分析
        # 如果项目中已有.flowconfig配置文件，需要保存起来，后面要恢复现场
        if os.path.exists(config_file):
            copyfile(config_file, user_config_file)
            os.remove(config_file)
        SubProcController(["flow", "init", "--lints", "all=error"], cwd=source_dir).wait()
        scan_cmd = [
            "flow",
            "check",
            "--all",
            "--json",
            "--show-all-errors",
            "--include-warnings",
            "--strip-root",
            "--temp-dir",
            work_dir,
        ]
        self.print_log("scan_cmd: %s" % " ".join(scan_cmd))
        SubProcController(scan_cmd, cwd=source_dir, stdout_filepath=error_output).wait()
        SubProcController(["flow", "stop"], cwd=source_dir).wait()

        # 删除flow生成的配置文件，并将客户代码库自身的配置文件拷贝会代码库中，恢复现场
        if os.path.exists(config_file):
            os.remove(config_file)
        if os.path.exists(user_config_file):
            copyfile(user_config_file, config_file)

        # 结果解析
        with open(error_output, "r") as f:
            error_json = json.loads(f.read())["errors"]
        issues = []
        for error in error_json:
            msg = []
            refs = []
            kind = error["kind"]
            for message in error["message"]:
                if message["type"] != "Comment":
                    ref_line = message["line"]
                    ref_msg = message["descr"]
                    msg.append(ref_msg)
                    ref_tag = message["type"]
                    ref_path = message["path"]
                    refs.append({"line": ref_line, "msg": ref_msg, "tag": ref_tag, "path": ref_path})
                else:
                    msg.append(message["descr"])
            path = refs[0].get("path")
            line = refs[0].get("line")

            if kind == "lint":
                rule = msg[0].split(":")[0]
            else:
                rule = default_rule
            if rule not in rules:
                continue
            issues.append({"path": path, "rule": rule, "msg": " - ".join(msg), "line": line, "refs": refs})

        LogPrinter.debug(issues)
        return issues


tool = Flow

if __name__ == "__main__":
    pass
