#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
HtmlCS: Html style static analyzer
"""

import os
from shutil import copyfile

from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.pathfilter import FilterPathUtil
from util.textutil import CodecClient
from util.logutil import LogPrinter


class Htmlcs(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "htmlcs": "Tool",
            "Htmlcs": "Tool"
        }

    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        source_dir = params.source_dir
        work_dir = os.getcwd()
        rules = params.rules
        envs = os.environ
        incr_scan = params["incr_scan"]
        config_file = os.path.join(work_dir, ".htmlcsrc")

        scan_cmd = ["htmlcs", "hint"]

        # 指向项目中的配置文件，填写路径
        if "HTMLCS_CONFIG" in envs:
            scan_cmd.extend(["--config", envs.get("HTMLCS_CONFIG")])
        else:
            copyfile(os.path.join(os.environ.get("NODE_HOME"), "htmlcsrc"), config_file)
            scan_cmd.extend(["--config", config_file])

        want_suffix = [".html", ".htm"]
        if "HTMLCS_EXT" in envs:
            # 后缀名，以逗号分隔
            want_suffix = envs.get("HTMLCS_EXT").split(",")

        # htmlcs默认检索后缀是.html，如果指定的是目录，便会遍历下面.html文件。也没有过滤设置，后缀指定设置
        # 故这里修改为指定具体文件的方式来扫描
        relpos = len(source_dir) + 1
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path)
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
        else:
            toscans = [path for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))]

        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
        toscans = [path[relpos:].replace(os.sep, "/") for path in toscans]

        LogPrinter.info(f"待扫描文件数是: {len(toscans)}")
        # 获取命令行最长限制
        cmd_arg_max = PathMgr().get_cmd_arg_max()
        LogPrinter.info("命令行长度限制：%d" % cmd_arg_max)
        cmd_args_list = PathMgr().get_cmd_args_list(scan_cmd, toscans, cmd_arg_max)
        issues = []
        for i in range(len(cmd_args_list)):
            error_output = os.path.join(work_dir, f"htmlcs-output-{i}.txt")
            self.print_log("scan_cmd: %s" % " ".join(cmd_args_list[i]))
            SubProcController(cmd_args_list[i], cwd=source_dir, stdout_filepath=error_output).wait()

            if not os.path.exists(error_output) or os.stat(error_output).st_size == 0:
                LogPrinter.info(f"{error_output} is empty")
                continue

            error_file = open(error_output, "rb")
            content = CodecClient().decode(error_file.read()).splitlines()
            error_file.close()
            for error in content:
                # 文件路径
                if not error.startswith("[WARN]"):
                    path = error[:-1]
                else:
                    tmp = error.split()
                    line = int(tmp[2][:-1])
                    column = int(tmp[4][:-1])
                    msg = error.split(":")[1]
                    rule = tmp[-2][1:-1]
                    if rule not in rules:
                        continue
                    issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})
        LogPrinter.debug(issues)

        return issues


tool = Htmlcs

if __name__ == "__main__":
    pass
