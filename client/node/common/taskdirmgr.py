# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
管理task目录的请求,清理等
"""

import logging
import os.path

from node.app import settings

logger = logging.getLogger(__name__)


class TaskDirCtl(object):
    """本地task目录管理类
    """
    def __init__(self):
        self._task_dirs_root = settings.TASK_DIR

    def acquire_task_dir(self, task_id=None, dirname_prefix="task_"):
        """申请任务目录

        :param task_id: 任务id
        :param dirname_prefix: taskdir名称前缀
        :return:任务目录路径
        """
        if task_id:
            task_dir = os.path.join(self._task_dirs_root, f"{dirname_prefix}{task_id}")
            if os.path.exists(task_dir):
                suffix_no = 1
                while True:
                    if not os.path.exists(os.path.join(self._task_dirs_root, f"{dirname_prefix}{task_id}_{suffix_no}")):
                        break
                    suffix_no += 1
                task_dir = os.path.join(self._task_dirs_root, f"{dirname_prefix}{task_id}_{suffix_no}")
        else:  # 没有传task_id，根据本地task dir名称排序，创建一个新的
            task_id = 1
            while True:
                if not os.path.exists(os.path.join(self._task_dirs_root, f"{dirname_prefix}{task_id}")):
                    break
                task_id += 1
            task_dir = os.path.join(self._task_dirs_root, f"{dirname_prefix}{task_id}")

        # 此时task_dir尚未创建，需要新建目录
        os.makedirs(task_dir)
        return task_dir, task_id
