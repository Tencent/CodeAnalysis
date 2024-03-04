# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
tscan 扫描任务
"""

from distutils.log import Log
import os
import stat

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.basic.common import subprocc_log
from task.codelintmodel import CodeLintModel
from util.logutil import LogPrinter
from util.pathlib import PathMgr
from task.scmmgr import SCMMgr
from util.subprocc import SubProcController
from util.exceptions import AnalyzeTaskError

class Tscan(CodeLintModel):
    def analyze(self, params, tc_home, bin_name, want_suffix):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :param tc_home: tscan所在目录
        :param bin_name: 二进制文件名称如tscancode, tsclua
        :param want_syffix: 扫描的文件后缀
        :return:
        """
        source_dir = params["source_dir"]
        self.relpos = len(source_dir) + 1
        self.work_dir = os.getcwd()
        output_file = os.path.join(self.work_dir, "result.xml")
        self.rules = params["rules"]
        toscans = [source_dir]
        inc = params["incr_scan"]
        if inc:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [diff.path.replace(os.sep, "/") for diff in diffs if diff.path.endswith(tuple(want_suffix))]
            toscans = PathMgr().format_cmd_arg_list(toscans)
        os.chmod(os.path.join(tc_home, bin_name), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        cmd_args = [bin_name, "--xml", f"2>{output_file}"]
        CMD_ARG_MAX = PathMgr().get_cmd_arg_max()
        cmd_args_list = PathMgr().get_cmd_args_list(cmd_args, toscans, CMD_ARG_MAX)
        issues = []
        for cmd in cmd_args_list:
            LogPrinter.info(f"cmd: {cmd}")
            sp = SubProcController(
                command=cmd,
                cwd=tc_home,
                stdout_line_callback=subprocc_log,
            )
            sp.wait()
            if os.path.exists(output_file) and os.stat(output_file).st_size != 0:
                issues.extend(self._format_issue(output_file))
        return issues

    def _format_issue(self, output_file):
        issues = []
        try:
            result_tree = ET.parse(output_file)
        except ET.ParseError:
            raise AnalyzeTaskError("源文件编码格式错误，建议启用WrongEncoding规则检测源文件编码格式")
        root = result_tree.getroot()
        for error in root:
            error_attr = error.attrib
            path = error_attr["file"]
            if not path:
                continue
            rule = error_attr["subid"]
            if not rule or rule not in self.rules:
                continue
            issues.append(
                {
                    "path": path[self.relpos :],
                    "rule": rule,
                    "line": int(error_attr.get("line", "0")),
                    "column": "1",
                    "msg": error_attr.get("msg", ""),
                }
            )
        return issues


if __name__ == "__main__":
    pass
