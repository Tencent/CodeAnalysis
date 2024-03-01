# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
dart_code_metrics: dart语言圈复杂度检测工具
"""

import logging
import os
import re
import json

from task.codemetricmodel import CodeMetricModel
from util.subprocc import SubProcController
from util.textutil import CodecClient
from util.textutil import CommentsManager
from util.pathlib import PathMgr
from util.logutil import LogPrinter


class DartCodeMetrics(CodeMetricModel):
    def __init__(self, params):
        CodeMetricModel.__init__(self, params)
        self.cmd_output = []
        self.sensitive_word_maps = {
            "DartCodeMetrics": "Tool",
            "dartcodemetrics": "Tool",
            "dart-code-metrics": "Tool"
        }

    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        # source_dir = params.source_dir
        # work_dir = params.work_dir
        # incr_scan = params["incr_scan"]
        # path_include = params.path_filters.get("wildcard_inclusion", [])
        # path_exclude = params.path_filters.get("wildcard_exclusion", [])
        # error_output = os.path.join(work_dir, "dartcodemetrics_result.txt")
        # envs = os.environ
        # dart_home = envs.get("DART_HOME")
        issues = list()
        return issues

    def scan(self, params, dart_home, report_type, report_path, options=None, source_dir=None):
        """
        dart_code_metrics工具扫描的封装方法
        :param params:
        :param report_type:
        :param report_path:
        :param options:
        :param source_dir:
        :return: None或者结果文件绝对路径
        """
        source_dir = source_dir if source_dir else params.source_dir
        path_exclude = params.path_filters.get("wildcard_exclusion", [])

        scan_cmd = [
            "dart",
            os.path.join(dart_home, "bin", "metrics.dart"),
            source_dir,
            "--root-folder=%s" % (source_dir),
            "--reporter=%s" % (report_type),
        ]

        # options=["--cyclomatic-complexity=5"]
        if options:
            scan_cmd.extend(options)

        # 设置路径过滤
        if path_exclude:
            scan_cmd.append(
                '--ignore-files="{/**.g.dart,%s}"' % (",".join([path.replace("*", "**") for path in path_exclude]))
            )

        # scan_cmd = PathMgr().format_cmd_arg_list(scan_cmd)
        self.print_log("scan cmd: %s" % " ".join(scan_cmd))
        subProC = SubProcController(
            scan_cmd,
            cwd=source_dir,
            # stdout_line_callback=subprocc_log,
            # stderr_line_callback=self.__collect_result_callback__
            stdout_line_callback=self.__collect_result_callback__
        )
        subProC.wait()

        # 异常处理
        rt = subProC.returncode
        if rt != 0:
            LogPrinter.error("工具分析异常，返回码为%d" % rt)

        # 结果存入report_path
        with open(report_path, 'w') as f:
            json.dump(self.cmd_output, f)

    def __collect_result_callback__(self, line):
        """单行输出回调,收集结果"""
        self.print_log(line)
        # 提取圈复杂度结果
        if line.startswith('[{'):
            new_line = json.loads(line)
            self.cmd_output = new_line

    def get_ccn_infos(self, params, output, source_dir=None):
        """
        处理圈复杂度结果
        :param params:
        :param output:
        :return:
        """
        source_dir = source_dir if source_dir else params.source_dir
        fopen = open(output, 'r')
        f = json.loads(fopen.read())
        reader = []
        for issue in f:
            if not issue["check_name"] == "cyclomaticComplexity":
                continue
            path = os.path.join(source_dir, issue["location"]["path"])
            start_line = issue["location"]["lines"]["begin"]
            end_line = issue["location"]["lines"]["end"]
            description = issue["description"]
            func_name = re.findall(r"Function `(.*)` has", description)[0]
            long_name = func_name
            ccn = re.findall(r"Cyclomatic Complexity of ([0-9]*) ", description)[0]
            line_num = end_line - start_line + 1

            # 需要支持去掉空行和注释
            temp_f = open(path, "rb")
            lines = CodecClient().decode(temp_f.read()).splitlines()
            temp_f.close()
            code_line_num = len(
                CommentsManager(path, "\n".join(lines[start_line - 1 : end_line - 1])).get_codes()
            )
            fieldvalues = {
                "ccn": ccn,
                "code_line_num": code_line_num,
                "func_param_num": -1,
                "line_num": line_num,
                "path": path,
                "func_name": func_name,
                "long_name": long_name,
                "start_line": start_line,
                "end_line": end_line,
            }
            reader.append(fieldvalues)

        for row in reader:
            row["token"] = -1
            yield row
        fopen.close()


tool = DartCodeMetrics

if __name__ == "__main__":
    pass
