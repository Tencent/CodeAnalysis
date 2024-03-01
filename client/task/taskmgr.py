# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
task管理类，负责生成task任务与排队执行
'''

import logging
import os

from task.sourcemgr import SourceManager
from task.initparams import InitParams

logger = logging.getLogger(__name__)


class TaskMgr:
    def __init__(self, tool_name, task_types, task_dir, params):
        '''
        :param tool_name: 调用的工具类
        :param task_types: task类型组，允许多个task同时传入
        :param task_dir: task执行的工作路径
        :param params: task执行的参数
        '''
        self.task_queue = []
        self.error_code = 0
        self.error_msg = 'nothing'
        self.params = params
        self.params['task_dir'] = task_dir
        self.params['tool_name'] = tool_name
        self.params['work_dir'] = os.path.join(task_dir, 'workdir')

        self.task_types = task_types
        try:
            tool_model = __import__("tool." + tool_name)
        except ModuleNotFoundError as err:
            logger.warning("不是内置工具,使用自定义工具模块(%s)" % str(err))
            tool_model = __import__("tool.customtool")
            tool_name = "customtool"
            # raise NodeError(E_NODE, '工具不存在，需要联系管理员进行确认！')
        self.tool = getattr(tool_model, tool_name).tool(params)
        self.params['src_type'] = self.tool.set_inc_source_type()
        for task_type in task_types:
            task = self._taskproducer(task_type)
            if task:
                self.task_queue.append(task)

    def taskrunner(self):
        '''
        按task队列逐一执行
        :return: 返回执行结果
        '''
        # 通过任务队列长度来判断task是否为连续执行，用于task的跨机器执行判断
        length = len(self.task_queue) - 1
        last_flag = False  # 用于标记当前启动的task是否存在连续的前置task
        for task in self.task_queue:
            have_next = False
            if length > 0:
                have_next = True
                length -= 1
            # 将task状态插入params中，让工具或其他环节可以捕获
            self.params['hava_next'] = have_next
            self.params['last_flag'] = last_flag
            source = SourceManager(self.params, task.task_type, self.tool, have_next, last_flag)
            logger.info('task start : %s' % task.task_type)
            params = source.pre_task()
            if not last_flag:  # 仅task列表第一个task才会执行
                InitParams.prepare_params_after_load_source(self.params)
            result = task.runner(params)
            self.params = source.done_task(result)
            logger.info('task done : %s' % task.task_type)
            last_flag = True

        return self.params

    def _taskproducer(self, task_type):
        '''
        task对象生成
        :param task_type: 任务类型
        :return: 返回一个task任务的对象
        '''
        try:
            if not task_type == 'datahandle':
                getattr(self.tool, task_type)
        except AttributeError:  # 表示tool的对应app中未实现task相应函数
            return None
        task_file = __import__('task.model.' + task_type)
        model = getattr(task_file, 'model')
        task = getattr(model, task_type).task
        return task(self.tool)

    @staticmethod
    def check_tool_usable(tool_name, task_params):
        """
        检查task可行性，具体内容：
        1. 检查工具封装代码文件是否存在
        2. 调用tool.py中的check函数进行具体的检查
        :param tool_name:
        :param task_params:
        :return: 支持该工具的task类型数组，若不支持返回空数组
        """
        try:
            tool_model = __import__("tool." + tool_name)
        except ModuleNotFoundError:
            # logger.exception("不是内置工具,使用自定义工具模块.")
            tool_model = __import__("tool.customtool")
            tool_name = "customtool"

        tool = getattr(tool_model, tool_name).tool(task_params)
        tool_params = task_params.get("checktool")
        if tool_name == "customtool":
            tool_usable_set = tool.check_tool_usable(task_params)
        else:
            tool_usable_set = tool.check_tool_usable(tool_params)
        # puppy默认能执行所有的结果处理
        tool_usable_set.append('datahandle')
        return tool_usable_set

    @staticmethod
    def get_private_processes(tool_name):
        '''
        根据需求实现一个获取工具在本地是否存在私有进程
        :return: 工具在本地的私有进程数组
        '''
        try:
            tool_model = __import__("tool." + tool_name)
        except ModuleNotFoundError:
            # logger.exception("不是内置工具,使用自定义工具模块.")
            tool_model = __import__("tool.customtool")
            tool_name = "customtool"
            # return []
        tool = getattr(tool_model, tool_name).tool()
        private_process_set = tool.get_private_processes()
        return private_process_set

    def get_tool_version(self):
        if self.tool:
            return self.tool.version
        return None


if __name__ == '__main__':
    pass
