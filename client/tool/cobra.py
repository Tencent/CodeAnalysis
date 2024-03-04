#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
cobra: Cobra是一款源代码安全审计工具，支持检测多种开发语言源代码中的大部分显著的安全问题和漏洞。
"""

import json
import os
import shutil

from task.scmmgr import SCMMgr
from util.logutil import LogPrinter
from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from tool.util.toolenvset import ToolEnvSet
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from task.basic.common import subprocc_log
from util.exceptions import AnalyzeTaskError


class Cobra(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Cobra": "Tool", "cobra": "Tool"}
        self.install_steps = (
            "1. 执行<Client安装位置>/data/tools/cobra-v2.0.0-alpha.5/install.sh安装依赖;\n"
            "2. cd <Client安装位置>/data/tools/cobra-v2.0.0-alpha.5; pip3 install -r requirements.txt\n"
            "3. 检验: python3 cobra.py --help"
        )

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        incr_scan = params["incr_scan"]
        rules = params["rules"]
        path_filter = FilterPathUtil(params)

        error_output = os.path.join(work_dir, "result.json")
        COBRA_HOME = os.environ.get("COBRA_HOME")

        # 增量扫描和过滤
        relpos = len(source_dir) + 1
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [os.path.join(source_dir, diff.path) for diff in diffs if diff.state != "del"]
        else:
            toscans = [path for path in PathMgr().get_dir_files(source_dir)]

        toscans = path_filter.get_include_files(toscans, relpos)
        toscans = [path[relpos:].replace(os.sep, "/") for path in toscans]

        LogPrinter.info(f"待分析文件数是: {len(toscans)}")
        toscan_dir = os.path.join(work_dir, "toscan_dir")
        for path in toscans:
            file_path = os.path.join(toscan_dir, path)
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            shutil.copyfile(os.path.join(params.source_dir, path), file_path)

        ToolEnvSet.auto_set_py_env(version=3)

        scan_cmd = [
            "python3",
            "cobra.py",
            "-t",
            toscan_dir,
            "-f",
            "json",
            "-o",
            error_output,
            "-d",
        ]
        if rules:
            scan_cmd.extend(["-r", ",".join(rules)])

        LogPrinter.info("scan_cmd: %s" % " ".join(scan_cmd))
        scan_cmd = PathMgr().format_cmd_arg_list(scan_cmd)
        SubProcController(
            scan_cmd, cwd=COBRA_HOME, stdout_line_callback=self.analyze_callback, stderr_line_callback=self.print_log
        ).wait()

        # 分析完成之后，删除拷贝的代码
        PathMgr().rmpath(toscan_dir)

        if not os.path.exists(error_output):
            LogPrinter.error(f"分析结果不存在，请确认cobra是否安装成功:\n{self.install_steps}")
            return []
        with open(error_output, "r") as f:
            raw_warning_json = json.loads(f.read())
        issues = []
        column = 0
        for (_, value) in raw_warning_json.items():
            vulns = value["vulnerabilities"]
            for vuln in vulns:
                path = vuln["file_path"]
                if path_filter.should_filter_path(path):
                    continue
                line = int(vuln["line_number"])
                rule = "CVI-" + vuln["id"]
                if rule.startswith("CVI-999"):
                    rule = "CVI-999XXX"

                msg = vuln["solution"] + "\n" + vuln["analysis"]
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})

        return issues

    def analyze_callback(self, line):
        """
        输出回调处理
        :param line:
        :return:
        """
        subprocc_log(line)
        if (
            line.find("brew install findutils pleases!") != -1
            or line.find("ModuleNotFoundError: No module named") != -1
        ):
            raise AnalyzeTaskError(f"请确认cobra是否安装成功:\n{self.install_steps}")

    def check_tool_usable(self, tool_params):
        """
        这里判断机器上是否可以正常执行cobra脚本，不行的话便把任务发布给其他公线机器执行
        :return:
        """
        ToolEnvSet.auto_set_py_env(version=3)
        if SubProcController(["python3", "--version"]).wait() != 0:
            return []
        if SubProcController(["python3", "cobra.py", "--help"], cwd=os.environ.get("COBRA_HOME")).wait() != 0:
            LogPrinter.error(f"cobra不可用，建议:\n{self.install_steps}")
            return []
        return ["analyze"]


tool = Cobra

if __name__ == "__main__":
    pass
