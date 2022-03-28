# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
执行单个任务
"""

import os
import time
import json
import logging
import collections

from node.common.taskrunner import TaskRunner
from node.common.task import Task
from task.toolmodel import IToolModel
from util.exceptions import FileServerError
from util.tooldisplay import ToolDisplay
from util.reporter import Reporter, InfoType

logger = logging.getLogger(__name__)


"""
单个任务扫描结果
response_file: <str> 扫描结果文件路径
log_file: <str> 扫描日志
"""
TaskResult = collections.namedtuple("TaskResult", ["task_id", "task_name", "request_file", "response_file",
                                                   "log_file", "log_url", "data_url"])


class ResultCheck(object):
    @staticmethod
    def get_task_result(task, job_web_url, log_url, data_url):
        """
        获取单个任务结果
        :return:
        """
        with open(task.request_file, 'r') as fp:
            task_request = json.load(fp)
        with open(task.response_file, 'r') as fp:
            task_response = json.load(fp)

        error_code = task_response['status']
        error_msg = task_response['message']
        if error_code == 0:
            task_result = TaskResult(task_request['id'], task_request['task_name'],
                                     task.request_file, task.response_file, task.task_log, log_url, data_url)
            return error_code, error_msg, True, task_result
        else:
            # 有一个任务失败，退出该项目的扫描，整个扫描失败
            task_display_name = ToolDisplay.get_tool_display_name(task_request)
            error_msg = f"任务({task_display_name})扫描失败: {error_msg}\n请查看本地日志文件({task.task_log})"
            error_msg += ",\n或前往 %s (点击异常子任务->下载进程日志)" % job_web_url
            error_msg += "查看失败原因."
            logger.warning(error_msg)
            task_result = TaskResult(task_request['id'], task_request['task_name'], task.request_file,
                                     task.response_file, task.task_log, log_url, data_url)
            return error_code, error_msg, False, task_result

    @staticmethod
    def upload_task_result(task, proj_id):
        """
        上传单个扫描结果
        """
        # logger.info('task(%s) result upload to file server start ...' % task.task_name)
        with open(task.request_file) as rf:
            task_request = json.load(rf)
        # 上报进度: 98% - 上传扫描结果
        Reporter(task_request['task_params']).update_task_progress(InfoType.SendResult)

        if task.code is None:  # 扫描正常完成的情况
            with open(task.response_file, 'r') as fp:
                task_response = json.load(fp)
            code = task_response['status']
            data = task_response['result']
            msg = task_response['message']
            node_task_version = task_response['task_version']
        else:  # 扫描异常退出情况
            code = task.code
            data = task.data
            msg = task.msg
            node_task_version = IToolModel.version

        with open(task.request_file) as rf:
            task_request = json.load(rf)
            execute_processes = task_request['execute_processes']
            task_dir = task_request['task_dir']

        # 上传issues和log到文件服务器
        try:
            data_url, log_url = TaskRunner.upload_result_detail(proj_id, task.task_id, task_dir, data, task.task_log)
        except FileServerError as err:
            code = err.code
            msg = f"Fail to send result to file server! Error: {str(err)}"
            data_url = ""
            log_url = ""
            logger.error(msg)

        # 上报进度: 100% - 子任务执行结束
        Reporter(task_request['task_params']).update_task_progress(InfoType.TaskDone)
        # logger.info('task(%s) result upload to file server finished.' % task.task_name)

        return code, msg, log_url, data_url, execute_processes, node_task_version


class SingleTaskRuner(TaskRunner):
    """
    执行单个任务类
    """
    def __init__(self, task_request, env):
        """
        构造函数
        :param task_request: task执行参数
        :param env: task执行的环境变量
        :return:
        """
        TaskRunner.__init__(self)
        self.task_request = task_request
        self.env = env

    def run(self):
        """
        执行单个任务扫描
        """
        log_file = os.path.join(self.task_request['task_dir'], 'task.log')
        request_file = os.path.join(self.task_request['task_dir'], 'task_request.json')
        response_file = os.path.join(self.task_request['task_dir'], 'task_response.json')

        with open(request_file, 'w') as wf:
            json.dump(self.task_request, wf, indent=2)

        # 启动任务
        task = Task(self.task_request['id'], self.task_request['task_name'],
                    request_file, response_file, log_file, env=self.env)
        task.start()
        self._running_task.append(task)

        # 等待任务执行完成
        while self._running_task:
            time.sleep(10)
            self._handle_exist_task()

        return task


class InOrderTasksRunner(object):
    """顺序执行tasks"""
    def __init__(self, execute_request_list, env, job_web_url, proj_id):
        self._execute_request_list = execute_request_list
        self._env = env
        self._job_web_url = job_web_url
        self._proj_id = proj_id

    def run(self):
        error_code = 0
        error_msg = ""
        proj_scan_succ = True
        proj_scan_result = []
        local_task_dirs = []
        for task_request in self._execute_request_list:
            # 执行单个任务扫描，使用未经污染的环境变量
            task = SingleTaskRuner(task_request, env=self._env).run()
            error_code, error_msg, log_url, data_url, execute_processes, node_task_version = \
                ResultCheck.upload_task_result(task, self._proj_id)
            error_code, error_msg, task_succ, task_result = ResultCheck.get_task_result(task,
                                                                                        self._job_web_url,
                                                                                        log_url, data_url)
            local_task_dirs.append(task_request["task_dir"])
            proj_scan_result.append(task_result)
            if not task_succ:
                proj_scan_succ = False
                break
        return proj_scan_succ, proj_scan_result, local_task_dirs, error_code, error_msg
