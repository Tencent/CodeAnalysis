# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
结果处理模块
"""

import time
import logging

from node.quicktask.quickscan import QuickScan
from task.taskmodel import ITaskModel
from task.basic.datahandler.blamer import Blamer
from task.basic.datahandler.filter import Filter, PostFilter
from task.basic.datahandler.formater import Formater
from task.basic.datahandler.submodulehandle import SubmoduleHandle
from task.basic.datahandler.packdiffinfo import PackDiffInfo
from task.basic.datahandler.addfileinfo import AddFileInfo
from task.basic.datahandler.addpersoninfo import AddPersonInfo
from task.basic.datahandler.issuehash import IssueHash
from task.basic.datahandler.issuesplit import IssueSplit
from task.basic.datahandler.issueignore import IssueIgnore
from util.reporter import Reporter, InfoType

logger = logging.getLogger(__name__)

# 结果处理操作队列，用于存储目前现有结果操作步骤
HANDLE_QUEUE = [
    Formater,
    Filter,
    SubmoduleHandle,
    Blamer,
    PostFilter,
    IssueIgnore,
    PackDiffInfo,
    AddFileInfo,
    IssueHash,
    AddPersonInfo,
    IssueSplit,
]


class DataHandleTask(ITaskModel):
    def __init__(self, tool):
        """
        结果处理的构造函数
        :param tool:
        """
        ITaskModel.__init__(self, tool)
        self.task_type = DataHandleTask
        pass

    def runner(self, params):
        """
        执行结果处理，调用结果处理的适配类
        :return: task是否成功
        """
        Reporter(params).update_task_progress(InfoType.DataHandleTask)
        # 调整扫描结果数据结构
        # 循环执行结果处理队列
        for datahander_type in HANDLE_QUEUE:
            if QuickScan.is_quick_scan() and datahander_type not in [Formater, IssueIgnore]:
                continue
            tool_handle_type_name = datahander_type.get_tool_handle_type_name()
            logger.info(f"[Start] {tool_handle_type_name}")
            start_time = time.time()
            datahander_type(getattr(self.tool, tool_handle_type_name)()).run(params)
            logger.info(f"[End] {tool_handle_type_name} (use time: {time.time() - start_time})")

        logger.info("datahandle done!")
        return params["result"]


task = DataHandleTask

"""
创建一个结果处理的流程：
1. 继承task.basic.datahandler.handlerbase实现一个处理类
2. 将处理类放入本文件的全局变量HANDLE_QUEUE队列中，请严格检查处理次序，datahandle将按队列顺序执行
3. 在继承类中，按照handlerbase中的要求实现get_tool_handle_type_name函数
4. 在toolmodel中创建对应的工具默认选项
"""
