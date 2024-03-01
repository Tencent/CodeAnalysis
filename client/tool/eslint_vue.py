#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
from tool.eslint import Eslint
from task.codelintmodel import CodeLintModel


VERSION = "1.1"


class EslintVue(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.params = params
        pass

    def analyze(self, params):
        params.lang = __name__.split("_")[1]
        envs = os.environ
        work_dir = os.getcwd()

        # 表示Eslint扫描Js以及React框架
        eslint_type = "VUE"
        eslint_ext = ".js,.jsx,.vue"
        if "ESLINT_%s_EXT" % eslint_type in envs:
            eslint_ext = envs.get("ESLINT_%s_EXT" % eslint_type)

        error_output = os.path.join(work_dir, "%s_eslint_result.xml" % eslint_type.lower())

        eslint = Eslint(params)
        config_path, rule_filte_flag = eslint.config(params, eslint_type)

        eslint.scan(params, config_path, error_output, eslint_ext)

        return eslint.data_handle(params, error_output, rule_filte_flag)

    def check_tool_usable(self, tool_params):
        return Eslint(self.params).check_tool_usable(tool_params)


tool = EslintVue

if __name__ == "__main__":
    pass
