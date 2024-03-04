# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
TaskProcessMgr
"""
import os
import sys
import logging

from node.toolloader.loadtool import ConfigUtil, ToolLoader
from task.taskmgr import TaskMgr
from util.envset import EnvSet

logger = logging.getLogger(__name__)


class TaskProcessMgr(object):
    @staticmethod
    def get_execute_processes(task_display_name, supported_procs, config_procs):
        """
        获取本地当前可以直接执行的工具进程
        中间有一个进程不支持,后续的进程也不能执行,比如本地支持compile,datahandle,但不支持analyze,那么直接可以执行的只有compile进程
        :param task_display_name: 任务展示名称，供日志输出使用
        :param supported_procs: 本地节点支持的工具进程
        :param config_processes: 项目配置需要扫描的工具进程
        :return: 本地要执行的工具进程
        """
        if not config_procs:
            logger.error("扫描失败! 工具(%s)扫描进程为空,请联系管理员配置工具进程!" % task_display_name)
            # 直接退出进程
            sys.exit(-1)
        execute_procs = []
        for proc_name in config_procs:
            if proc_name in supported_procs:
                execute_procs.append(proc_name)
            else:
                # 中途有一个不支持,则后续进程都不支持,因为进程要按顺序执行
                break
        return execute_procs

    @staticmethod
    def get_supported_processes(origin_os_env, task_name, task_params, custom_tools):
        """
        判断工具进程能否在本地执行,返回本地支持的工具进程
        :param task_name: 任务名称
        :param task_params: 任务参数
        :return:
        """
        # 先恢复环境变量,再加载工具环境变量
        os.environ.update(origin_os_env)

        # 加载工具执行需要的环境变量
        task_params["tool_name"] = task_name
        task_list = ConfigUtil.generate_task_list(task_params)
        ToolLoader(tool_names=[task_name], task_list=task_list, custom_tools=custom_tools,
                   include_common=True).set_tool_env()

        # 加载任务环境变量
        EnvSet().set_task_env(task_params)

        # 获取本地工具支持的进程类型
        task_params["task_name"] = task_name
        supported_processes = TaskMgr.check_tool_usable(task_name, task_params)

        # 判断完成后,恢复环境变量,避免影响后续执行
        os.environ.update(origin_os_env)

        return supported_processes
