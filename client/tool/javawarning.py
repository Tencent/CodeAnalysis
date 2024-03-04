# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
javawarning, 获取java编译警告信息
Error Prone，增强java的类型分析
"""

import os

from task.codelintmodel import CodeLintModel
from tool.util.compile import BasicCompile
from util.exceptions import CompileTaskError


class JavaWarning(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        work_dir = params.work_dir
        build_log_path = os.path.join(work_dir, "build.log")
        # build_err_path = os.path.join(work_dir, "build.err")
        # 如果指定了编译log文件，则直接跳过编译
        if "JAVAWARNING_BUILD_LOG" in os.environ:
            return True
        # 1. javac -Xlint:all
        build_cmd = params.get("build_cmd")
        if not build_cmd:
            raise CompileTaskError("编译语言项目执行静态分析需要输入编译命令，请填入编译命令后重试！")
        BasicCompile(
            params,
            sensitive=self.sensitive,
            sensitive_word_maps=self.sensitive_word_maps,
            build_cmd=BasicCompile.generate_shell_file(build_cmd),
        ).compile(build_out=build_log_path, build_err=build_log_path)
        return True

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        pos = len(source_dir) + 1
        work_dir = params.work_dir
        build_log_path = (
            os.path.join(work_dir, "build.log")
            if "JAVAWARNING_BUILD_LOG" not in os.environ
            else os.path.join(source_dir, os.environ.get("JAVAWARNING_BUILD_LOG"))
        )
        # build_err_path = os.path.join(work_dir, "build.err")
        rules = params["rules"]

        # 解析编译log，提取编译警告结果
        issues = list()
        fi = open(build_log_path)
        for line in fi.readlines():
            if (line.find(": warning: [") != -1 or line.find(": 警告: [") != -1 or
                    line.find(": error: [") != -1 or line.find(": 错误: [") != -1):
                infos = line.split(":")
                path = infos[0].strip()[pos:]
                line_num = int(infos[1].strip())
                temp = infos[3].split("]")
                rule = temp[0].strip()[1:]
                # 这个可以优化，后面还有一些信息
                msg = temp[1].strip()
                # 增加规则过滤
                if rule not in rules:
                    continue
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line_num})

        fi.close()

        return issues


tool = JavaWarning

if __name__ == "__main__":
    pass
