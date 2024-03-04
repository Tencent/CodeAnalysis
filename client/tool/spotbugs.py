# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
spotbugs java漏洞扫描工具
"""

import os

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from tool.util.compile import BasicCompile
from util.exceptions import CompileTaskError
from tool.findbugs import RulesToVisitors, ClassToFilename, Findbugs
from util.logutil import LogPrinter


class Spotbugs(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "Spotbugs": "Tool",
            "spotbugs": "Tool"
        }

    def compile(self, params):
        """
        编译执行函数
        :param params: 编译所需要的资源 1.项目地址 2. 编译命令 3. 环境变量参数 4.编译结果生成地址
        :return:
        """
        LogPrinter.info("Tool compile start.")
        build_cmd = params.get("build_cmd")
        if not build_cmd:
            raise CompileTaskError("编译语言项目执行静态分析需要输入编译命令，请填入编译命令后重试！")
        BasicCompile(params, sensitive=self.sensitive, sensitive_word_maps=self.sensitive_word_maps,
                     build_cmd=BasicCompile.generate_shell_file(build_cmd)).compile()
        LogPrinter.info("Tool compile done.")
        return True

    def analyze(self, params):

        source_dir = params["source_dir"]
        enabled_rules = params["rules"]
        error_output = os.path.join(os.path.curdir, "spotbugs_result.xml")

        # analyze step
        tool_name = "spotbugs"
        visitors = RulesToVisitors(tool_name).get_needed_visitors(enabled_rules)
        scan_cmd = [
            "java",
            "-jar",
            os.path.join(os.environ["SPOTBUGS_HOME"], "lib", "spotbugs.jar"),
            "-textui",
            "-low",
            "-exitcode",
            "-nested:false",
            "-xml:withMessages",
        ]
        if visitors:
            scan_cmd.append("-visitors")
            scan_cmd.append(",".join(visitors))
        scan_cmd.extend(["-output", error_output, source_dir])
        self.print_log(" ".join(scan_cmd))
        SubProcController(scan_cmd).wait()

        # format step
        ctf = ClassToFilename(source_dir)
        items = Findbugs.data_handle(error_output, enabled_rules, ctf)
        return items


tool = Spotbugs

if __name__ == "__main__":
    pass
