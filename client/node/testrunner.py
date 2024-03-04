# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
测试任务执行器,执行单个测试任务
"""

import logging
import json
import os
import time

from node.common.taskdirmgr import TaskDirCtl
from node.common.taskrunner import TaskRunner
from util.taskscene import TaskScene
from util.pathlib import PathMgr
from node.common.task import Task

logger = logging.getLogger(__name__)


class TestRunner(TaskRunner):
    """测试任务执行器,执行单个任务
    """
    def __init__(self, request_file):
        """构造函数
        """
        TaskRunner.__init__(self)
        self._request_file = request_file  # 任务参数文件
        # 设置TaskScene环境变量，供后续使用
        os.environ["TaskScene"] = TaskScene.TEST
        # 初始环境变量,保存下来,执行子进程时使用该环境变量,避免被污染
        self._origin_os_env = dict(os.environ)

    def run(self):
        """执行单个本地测试任务
        """
        task_dir, task_id = TaskDirCtl().acquire_task_dir()
        logger.debug('created task_dir: %s', task_dir)
        task_log = os.path.join(task_dir, 'task.log')
        task_request_file = os.path.join(task_dir, 'task_request.json')
        task_response_file = os.path.join(task_dir, 'task_response.json')
        with open(self._request_file, 'r') as fp:
            request = json.load(fp)
        request['task_id'] = task_id
        request['task_dir'] = task_dir
        request['task_params']['task_scene'] = TaskScene.TEST
        with open(task_request_file, 'w') as fp:
            json.dump(request, fp, indent=2)

        # 启动任务
        task_name = request['task_name']
        task = Task(task_id, task_name, task_request_file, task_response_file, task_log, env=self._origin_os_env)
        task.start()
        self._running_task.append(task)

        # 等待任务执行完成
        while self._running_task:
            time.sleep(3)
            self._handle_exist_task()

        # 删除临时文件夹
        tmp_issue_dir = os.path.join(task_dir, "workdir/tmp_dir")
        if os.path.exists(tmp_issue_dir):
            PathMgr().rmpath(tmp_issue_dir)

        with open(task_response_file, 'r') as fp:
            task_response = json.load(fp)
        rt_code = task_response['status']
        if rt_code == 0:
            logger.info("%s task succeed." % task_name)
        else:
            logger.info("%s task fail, please check log file!" % task_name)
        return rt_code
