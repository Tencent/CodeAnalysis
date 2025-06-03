#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2025 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from task.codelintmodel import CodeLintModel
from tool.util.compile import BasicCompile
from tool.util.loong.loong_beta import Loong
from task.basic.datahandler.blamer import FILE_LAST_CHANGE_BLAME
from task.basic.datahandler.filter import NO_VERSION_FILTER
from util.exceptions import CompileTaskError
from util.logutil import LogPrinter


class JavaAPIFinderForFile(CodeLintModel):
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
        work_dir = params["work_dir"]

        loong = Loong(
            dbdir=work_dir,
            project_root=source_dir,
            jar_mode=True,
        )
        loong.parse()
        result = loong.scan()

        return result

    def set_blame_type(self):
        return FILE_LAST_CHANGE_BLAME

    def set_filter_type_list(self):
        return [NO_VERSION_FILTER]


tool = JavaAPIFinderForFile


if __name__ == "__main__":
    pass
