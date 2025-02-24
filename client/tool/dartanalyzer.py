# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
dartanalyzer: dart语言静态分析工具
"""

import os
import sys
import yaml
import shlex

from shutil import copyfile

from task.scmmgr import SCMMgr
from task.codelintmodel import CodeLintModel
from util.pathfilter import FilterPathUtil
from util.subprocc import SubProcController
from util.logutil import LogPrinter


class DartAnalyzer(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"dartanalyzer": "Tool", "Dartanalyzer": "Tool"}

    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        enabl_rules = params.rules
        incr_scan = params["incr_scan"]
        error_output = os.path.join(work_dir, "dartanalyzer_result.txt")
        envs = os.environ
        dart_home = envs.get("DART_HOME")

        config_file = self.config(params)

        scan_cmd = ["dartanalyzer", "--options", config_file, "--dart-sdk", dart_home]

        # --packages 指向.packeges文件，指明了pub的路径
        if "DARTANALYZER_OPTION_PARAMS" in envs:
            scan_cmd.extend(shlex.split(envs["DARTANALYZER_OPTION_PARAMS"]))

        # 扫描指定文件，存在问题。
        # 指定扫描目录或者文件，支持增量
        want_suffix = [".dart"]
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path)
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
            relpos = len(source_dir) + 1
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
            toscans = [path[relpos:].replace(os.sep, "/") for path in toscans]

            # windows下增量文件路径总长度超长，改为扫描整个soucedir，否则会执行异常
            # 因为 windows 下执行subprocess.Popen方法且shell=False的情况下，命令长度限制为32768字节
            # 这里文件路径长度限制为32500，因为前面还要预留cppcheck命令的长度
            if sys.platform == "win32" and len(" ".join(toscans)) > 32500:
                toscans = ["."]
        else:
            toscans = ["."]

        if not toscans:
            LogPrinter.debug("To-be-scanned files is empty ")
            return []
        scan_cmd.extend(toscans)

        self.print_log("scan_cmd: %s" % " ".join(scan_cmd))
        SubProcController(
            scan_cmd,
            cwd=source_dir,
            stdout_filepath=error_output,
            stdout_line_callback=self.print_log,
            stderr_line_callback=self.print_log,
        ).wait()
        # 异常处理

        # data handle
        issues = list()
        f = open(error_output)
        # 处理问题跨行的情况
        tmp_line = ""
        for line in f.readlines():
            line = line.strip()
            if not line.startswith(("error", "lint", "hint", "warning", "info")):
                if not tmp_line:
                    continue
            else:
                tmp_line = ""

            tmp_line = ("%s\n%s" % (tmp_line, line)).strip()
            infos = tmp_line.split("•")
            infos = [info.strip() for info in infos]

            if len(infos) != 4:
                continue
            else:
                tmp_line = ""
            msg = infos[1]
            location = infos[2].split(":")
            path = location[0]
            line_num = int(location[1])
            column_num = int(location[2])
            rule = infos[3]
            if rule not in enabl_rules:
                continue
            issues.append({"path": path, "rule": rule, "msg": msg, "line": line_num, "column": column_num})
        f.close()

        return issues

    def config(self, params):
        """
        配置dartanalyzer配置文件
        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        path_exclude = params.path_filters.get("exclusion", [])
        enabl_rules = params.rules
        envs = os.environ

        # 支持指定代码库下的配置文件
        if "DARTANALYZER_CONFIG" in envs:
            return os.path.join(source_dir, envs["DARTANALYZER_CONFIG"])

        config_file = os.path.join(work_dir, "analysis_options.yml")
        if os.path.exists(config_file):
            os.remove(config_file)
        copyfile(os.path.join(envs.get("DART_HOME"), "analysis_options.yaml"), config_file)
        f = open(config_file)
        config = yaml.safe_load(f)
        f.close()

        # 设置过滤
        if path_exclude:
            config["analyzer"]["exclude"] = [path.replace("*", "**") for path in path_exclude]

        # 设置开关规则
        analyzer_rules = config["analyzer"]["errors"]
        for rule in analyzer_rules:
            if rule not in enabl_rules:
                continue
            analyzer_rules[rule] = "warning"

        linter_rules = config["linter"]["rules"]
        for rule in linter_rules:
            if rule not in enabl_rules:
                continue
            linter_rules[rule] = True

        # 设置其他配置，include/strong-mode

        f = open(config_file, "w")
        yaml.dump(config, f, default_flow_style=False)
        f.close()

        return config_file


tool = DartAnalyzer

if __name__ == "__main__":
    pass
