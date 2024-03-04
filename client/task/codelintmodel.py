# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
代码检查工具模板类，继承自 IToolModel。
用于直接封装代码检查工具，所有代码检查类工具，必须继承自该模板类。
"""

from task.toolmodel import IToolModel
from task.basic.datahandler.issueignore import CODELINT_ISSUE_IGNORE


class CodeLintModel(IToolModel):
    def __init__(self, params):
        IToolModel.__init__(self, params)

    def compile(self, params):
        pass

    def analyze(self, params):
        pass

    def set_issue_ignore_type(self):
        """
        设置问题忽略的类型
        :return:
        """
        return CODELINT_ISSUE_IGNORE

    def set_no_branch_diff_skip(self, params):
        '''
        与对比分支无差异时，是否跳过。
        适用场景：codelint类型工具跳过；codemetric类型工具不跳过。
        :return:
        '''
        if params.get("no_branch_diff") is True:
            return True
        return False
