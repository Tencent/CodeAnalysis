# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
分析模块
"""


import logging

from task.taskmodel import ITaskModel
from util.reporter import Reporter, InfoType

logger = logging.getLogger(__name__)


class AnalyzeTask(ITaskModel):
    def __init__(self, tool):
        """

        :param tool:
        """
        ITaskModel.__init__(self, tool)
        self.task_type = AnalyzeTask

    def runner(self, params):
        """
        :return: task是否成功
        """
        Reporter(params).update_task_progress(InfoType.AnalyzeTask)

        # 判断与对比分支无差异时，是否需要跳过。如果是，直接返回空
        if self.tool.set_no_branch_diff_skip(params):
            logger.info("与对比分支无差异,满足skip条件,跳过analyze步骤,直接返回空结果(说明: 只有codelint类工具跳过,codemetric不跳过).")
            params["tool_skip"] = True
            return []

        # params如果没有tool_skip字段时,才需要判断;如果有上个阶段,则已经判断过,无需重复判断
        if "tool_skip" not in params:
            params["tool_skip"] = self.tool.set_tool_skip_condition(params)
        if params["tool_skip"]:
            logger.info("满足skip条件,跳过analyze步骤,直接返回空结果.")
            return []

        return self.tool.analyze(params)

    pass


task = AnalyzeTask
