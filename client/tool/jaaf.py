#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2025 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import json

from task.codelintmodel import CodeLintModel
from tool.util.compile import BasicCompile
from tool.util.ruleparamer import RuleParamer
from tool.util.loong.bcparser import ByteCodeParser
from tool.util.loong.astparser import ASTParser
from tool.util.loong.loong import Loong
from util.exceptions import CompileTaskError
from util.logutil import LogPrinter


class JavaASTAPIFinder(CodeLintModel):
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

        rules = RuleParamer.java_param_formart(params["rule_list"])
        with open("rules.json", "w") as f1:
            f1.write(json.dumps(rules))
            f1.close()
        if not rules:
            return []

        ast = ASTParser(source_dir, work_dir)
        ast.parser()
        bcp = ByteCodeParser(source_dir, work_dir)
        bcp.parser()

        loong = Loong(
            config=os.path.join(work_dir, "rules.json"),
            dbdir=work_dir,
            project_root=source_dir,
            jar_mode=False,
        )
        result = loong.scan()
        return result


tool = JavaASTAPIFinder


if __name__ == "__main__":
    pass
