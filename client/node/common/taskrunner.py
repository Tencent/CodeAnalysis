# -*- encoding: utf-8 -*-
"""
任务执行器父类,测试任务/本地扫描任务/轮询任务 均继承该父类,实现各自的子类方法
"""

import logging

from util.logutil import LogPrinter

logger = logging.getLogger(__name__)


class TaskRunner(object):
    def __init__(self):
        self._running_task = []  # 记录当前在执行的任务列表

    def _handle_exist_task(self):
        """管理当前在执行的任务,如果任务结束,从self._running_task列表中删除
        """
        for task in self._running_task[:]:
            if task.done:
                LogPrinter.info(f'Task_{task.task_id} is done.')
                self._running_task.remove(task)

    def run(self):
        """任务执行
        """
        raise NotImplementedError()
