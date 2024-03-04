# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""源码管理
"""

import logging
import os
import shutil
import threading
import time

import psutil

import settings

logger = logging.getLogger("sourcemgr")


class SourceManager(threading.Thread):
    """源码管理线程
    """
    daemon = True

    def __init__(self, workspace=None):
        """初始化函数
        """
        super(SourceManager, self).__init__()
        self._workspace = workspace
        self._interval_time = 60 * 60  # 1小时

    def run(self):
        """定时清理代码
        """
        while True:
            try:
                logger.info('Traverse directory at %s to remove overdue source' % self._workspace)
                # 1. 先按时间顺序清理
                now = time.time()
                projects = {}
                for src in os.listdir(self._workspace):
                    src_path = os.path.join(self._workspace, src)
                    # 每个git项目在.git都有一份index文件，如果仓库更新，index文件会发生变化
                    last_use_time = self._get_last_use_time(src_path)
                    if now - last_use_time > settings.SOURCE_RETAIN_TIME:
                        try:
                            logger.info(
                                "Remove source %s, because it has not been updated for more than 14 days." % src_path)
                            if os.path.isdir(src_path):
                                shutil.rmtree(src_path, ignore_errors=True)
                            else:
                                os.remove(src_path)
                        except Exception as err:
                            logger.exception("Remove source %s exception: %s" % (src_path, err))

                    else:
                        projects[src] = last_use_time
                # 2. 如果空间不足，则继续按时间清理，直到空间满足大小
                project_src_list = sorted(projects, key=lambda k: projects[k])
                if psutil.disk_usage(settings.SOURCE_DIR).free < settings.MIN_REMAIN_SIZE:
                    for src_path in project_src_list:
                        try:
                            logger.info("Remove source %s, because disk free size(%s) < MIN_REMAIN_SIZE(%s)."
                                        % (src_path, psutil.disk_usage(settings.SOURCE_DIR).free,
                                           settings.MIN_REMAIN_SIZE))
                            shutil.rmtree(src_path, ignore_errors=True)
                        except Exception as err:
                            logger.exception(
                                "Remove source %s exception: %s" % (src_path, err))
                        if psutil.disk_usage(settings.SOURCE_DIR).free > settings.MIN_REMAIN_SIZE:
                            break

            except Exception as err:
                logger.exception("SourceManager run exception: %s" % err)
            time.sleep(self._interval_time)

    def _get_last_use_time(self, src_path):
        git_dir = os.path.join(src_path, ".git")
        fetch_head_file = os.path.join(src_path, ".git/FETCH_HEAD")
        index_file = os.path.join(src_path, ".git/index")
        if os.path.exists(fetch_head_file):
            last_use_time = os.path.getmtime(fetch_head_file)
        elif os.path.exists(index_file):
            last_use_time = os.path.getmtime(index_file)
        elif os.path.exists(git_dir):
            last_use_time = os.path.getmtime(git_dir)
        else:
            last_use_time = os.path.getmtime(src_path)
        return last_use_time
