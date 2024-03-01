# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
清理资源文件
"""

import logging
import time
import os
import psutil

from node.app import settings
from util.pathlib import PathMgr

DATA_DIR = settings.DATA_DIR

logger = logging.getLogger(__name__)


class Cleaner(object):
    """资源清理类"""
    @staticmethod
    def del_old_file():
        """
        1. 清理对象：sourcedir，taskdir
        2. 清理逻辑：
            1. 删除超过时间限制的所有文件
            2. 空闲空间低于底线则按时间清理文件，直到空闲空间达到规定
            3. 删除非本地项目的项目中的代码文件
        """
        # logger.info('start del_old_file.')
        # 将所有资源文件放入数组
        source_dir_path = settings.SOURCE_DIR
        task_dir_path = settings.TASK_DIR

        def get_file_path_dict(dir_path):
            if not os.path.exists(dir_path):
                return {}
            dir_path_dict = {}
            for file_path in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_path)
                # 2020-09-10 bugfix 执行项目编译命令时，可能会在sourcedirs或taskdirs下创建软链接，直接删除，避免后续处理异常
                if os.path.islink(file_path):
                    logger.info("{} is a link, delete.".format(file_path))
                    PathMgr().safe_rmpath(file_path)
                    continue
                file_create_time = os.path.getctime(file_path)
                dir_path_dict[file_create_time] = file_path
            return dir_path_dict

        dir_dict = {}
        dir_dict.update(get_file_path_dict(source_dir_path))
        dir_dict.update(get_file_path_dict(task_dir_path))

        if not dir_dict:
            # logger.info('done del_old_file.')
            return
        # logger.info('old_file_list check done.')
        # (针对所有资源文件)删除超过时间限制的所有文件
        now = time.time()
        expired_time = now - settings.SOURCE_RETAIN_TIME.total_seconds()
        file_create_time_list = sorted(dir_dict)
        index = 0
        while index < len(file_create_time_list):
            if file_create_time_list[index] < expired_time:
                file_path = dir_dict.pop(file_create_time_list[index])
                PathMgr().safe_rmpath(file_path)
            else:
                break
            index += 1
        # logger.info('old file clean done.')
        # (针对所有资源文件)空闲空间低于底线则按时间清理文件，直到空闲空间达到规定
        file_create_time_list = sorted(dir_dict)  # 获取修改后
        if not file_create_time_list:
            # logger.info('done del_old_file.')
            return
        index = 0
        # 如果不存在data目录,先创建,后续才能判断可用磁盘空间
        if not os.path.exists(settings.DATA_DIR):
            os.makedirs(settings.DATA_DIR)
        # 如果磁盘空间小于MIN_REMAIN_SIZE，开始清理，直到空间达到MAX_REMAIN_SIZE
        if psutil.disk_usage(settings.DATA_DIR).free < settings.MIN_REMAIN_SIZE:
            while psutil.disk_usage(settings.DATA_DIR).free < settings.MAX_REMAIN_SIZE:
                file_path = dir_dict.pop(file_create_time_list[index])
                PathMgr().safe_rmpath(file_path)
                index += 1
                if index >= len(file_create_time_list):
                    break
        if psutil.disk_usage(settings.DATA_DIR).free < settings.MIN_REMAIN_SIZE:
            logger.error("del_old_file结束，但空间仍然不足，请手动清理！")
