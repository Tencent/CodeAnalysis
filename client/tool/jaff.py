#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import json

from task.codelintmodel import CodeLintModel
from tool.util.compile import BasicCompile
from tool.util.loong.javascaner import JavaScaner
from tool.util.loong.loong import Loong
from task.basic.datahandler.blamer import FILE_LAST_CHANGE_BLAME
from task.basic.datahandler.filter import NO_VERSION_FILTER
from tool.util.ruleparamer import RuleParamer
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

        rules = RuleParamer.java_param_formart(params["rule_list"])
        with open("rules.json", "w") as f1:
            f1.write(json.dumps(rules))
            f1.close()

        self.js = JavaScaner(source_dir, work_dir, jar_mode=True)
        need_ast = False
        need_field = False
        for rule_info in rules:
            if "up_exist_method" in rule_info or "up_no_exist_method" in rule_info or "need_method_chain" in rule_info:
                LogPrinter.info("条件符合，执行ast解析.")
                need_ast = True
            if "field" in rule_info:
                LogPrinter.info("条件符合，执行字节码遍历解析.")
                need_field = True
        self.js.parser(need_bc=True, need_ast=need_ast, need_field=need_field)

        loong = Loong(
            config=os.path.join(work_dir, "rules.json"),
            dbdir=work_dir,
            project_root=source_dir,
            jar_mode=True,
        )
        result = loong.scan()

        return result

    def set_blame_type(self):
        return FILE_LAST_CHANGE_BLAME

    def set_filter_type_list(self):
        return [NO_VERSION_FILTER]


tool = JavaAPIFinderForFile


if __name__ == "__main__":
    pass
