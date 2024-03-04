#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from task.codelintmodel import CodeLintModel
from tool.util.compile import BasicCompile
from tool.util.loong.loong_beta import Loong
from util.exceptions import CompileTaskError
from util.logutil import LogPrinter


class JavaAPIFinderForCode(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.js = None
        self.ap = None
        self.ast = None
        self.diff_files = None

        self.out_dir = None

    def compile(self, params):
        LogPrinter.info("Tool compile start.")
        build_cmd = params.get("build_cmd")
        if not build_cmd:
            raise CompileTaskError("编译语言项目执行静态分析需要输入编译命令，请填入编译命令后重试！")
        BasicCompile(
            params,
            sensitive=self.sensitive,
            sensitive_word_maps=self.sensitive_word_maps,
            build_cmd=BasicCompile.generate_shell_file(build_cmd),
        ).compile()
        LogPrinter.info("Tool compile done.")
        return True

    def analyze(self, params):
        source_dir = params["source_dir"]
        work_dir = params.work_dir
        self.out_dir = params["work_dir"]

        loong = Loong(
            dbdir=work_dir,
            project_root=source_dir,
            jar_mode=False,
        )
        loong.parse()
        result = loong.scan()

        return result


tool = JavaAPIFinderForCode


if __name__ == "__main__":
    pass
