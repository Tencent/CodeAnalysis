# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
进程管理类
"""

import logging
import psutil

logger = logging.getLogger(__name__)


class ProcMgr(object):
    """
    进程管理类
    """
    def kill_proc_famliy(self, pid):
        """
        杀掉进程,并递归杀掉其子孙进程
        :param pid:
        :return:
        """
        try:
            task_proc = psutil.Process(pid)
            children = task_proc.children(recursive=True)
            logger.info("kill process: %s" % task_proc)
            task_proc.terminate() # 关闭进程
            # 关闭子孙进程
            logger.info("kill children processes: %s" % children)
            for child in children:
                try:
                    child.kill()  # 发送 kill 信号
                except Exception as err:
                    logger.error("kill child proc failed: %s" % err)
            gone, still_alive = psutil.wait_procs(children, timeout=5)
            for child in still_alive:
                try:
                    child.kill()  # 如果没有关闭，则再发送 SIGkill 信号
                except Exception as err:
                    logger.error("kill child proc failed: %s" % err)
        except psutil.NoSuchProcess as err:
            logger.warning("process is already terminated: %s" % err)
        except Exception as err:
            logger.error("kill task failed: %s" % err)
