# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
修改git默认配置,供启动puppy和task时使用
"""

import os
import logging
import subprocess

from util.subprocc import SubProcController
from task.basic.common import subprocc_log

logger = logging.getLogger(__name__)


class GitConfig(object):
    """工具拉取管理类"""
    @staticmethod
    def set_default_config():
        """
        设置git默认配置
        :return:
        """
        try:
            # 设置git config --global core.longpaths true
            # 防止在Windows下出现由于绝对路径过长（超出260字符）导致拉取失败的情况
            # logger.info("设置git config --global core.longpaths true，预防git拉代码文件全路径过长错误。")
            subprocess.check_call(["git", "config", "--global", "core.longpaths", "true"])

            # 解决git命令行操作时中文文件名乱码
            # logger.info("设置git config --global core.quotepath off，解决git命令行操作时中文文件名乱码。")
            subprocess.check_call(["git", "config",  "--global", "core.quotepath", "off"])
        except Exception as err:
            logger.warning(f"set git config encounter error: {str(err)}")

    @staticmethod
    def set_blame_ignore():
        """
        设置git blame ignore，指定配置文件中的commit将被忽略
        :return:
        """
        source_dir = os.getenv("SOURCE_DIR")
        if source_dir and os.path.exists(source_dir):
            ignore_file = os.getenv("GIT_BLAME_IGNORE_FILE")
            if ignore_file:
                cmd_args = ["git", "config", "--local", "blame.ignoreRevsFile", ignore_file]
                logger.info('设置了GIT_BLAME_IGNORE_FILE环境变量,执行命令: %s' % ' '.join(cmd_args))
                spc = SubProcController(
                    command=cmd_args,
                    cwd=source_dir,
                    stdout_line_callback=subprocc_log,
                    stderr_line_callback=subprocc_log,
                    stdout_filepath=None,
                    stderr_filepath=None
                )
                spc.wait()
