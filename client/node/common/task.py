# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""任务类,每个任务都会创建一个Task类实例
"""


import logging
import os
import sys
import time
import json
import psutil
import traceback

from node import app
from node.app import settings
from util import errcode
from util.envset import EnvSet
from util.pathlib import PathMgr
from util.tooldisplay import ToolDisplay
from util.logutil import LogPrinter
from util.subprocc import SubProcController
from tool.util.pythontool import PythonTool
from util.exceptions import ConfigError

logger = logging.getLogger(__name__)


class Task(object):
    """任务对象。每个任务都会创建一个Task类实例"""
    def __init__(self, task_id, task_name, request_file, response_file, log_file, env):
        """
        :param task_id(int): 任务id
        :param task_name(str): 任务名，对应task包下的py名
        :param request_file: 任务request文件路径
        :param response_file: 任务response文件路径
        :param log_file: 任务日志文件路径
        :param env: 任务执行的环境变量
        """
        self.task_id = task_id
        self.task_name = task_name
        self.task_log = log_file
        self.request_file = request_file
        self.response_file = response_file
        self.env = env

        self._done = False

        self.code = None
        self.msg = None
        self.data = None
        self._task_proc = None
        self._task_expired_time = None

    def _read_tail_lines(self, filepath):
        """读取文件末尾的1024字节
        """
        try:
            with open(filepath, 'r') as fh:
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                pos = 1024
                if size>pos:
                    fh.seek(size-pos, os.SEEK_SET)
                    lines = fh.readlines()
                    return lines[1:]
                else:
                    fh.seek(0, os.SEEK_SET)
                    return fh.readlines()
        except Exception as err:
            message = "read file(%s) tail lines error: %s" % (filepath, str(err))
            logger.error(message)
            return message

    def terminate(self):
        """kill the task"""
        if settings.PLATFORMS[sys.platform] == "windows":
            # 在windows平台上只调用terminate，只能关闭子进程，无法关闭孙子进程，需要通过递归遍历子进程来关闭
            # 先关闭子进程，原因：子进程如果一直在启动孙进程，先关闭孙进程再关闭子进程，两步之间可能会有孙进程漏关
            try:
                task_proc = psutil.Process(self._task_proc.pid)
                children = task_proc.children(recursive=True)
                self._task_proc.terminate() # 关闭子进程
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
            except Exception as err:
                logger.error("kill task failed: %s" % err)
        else:
            # linux/mac平台，调用subprocc模块stop方法中止进程，会使用进程组的方式杀掉子孙进程（windows不支持该方式）
            self._task_proc.stop()
        # 重置
        self._task_proc = None

    def _check_task_expired(self):
        """检查任务是否超时,如果超时,终止任务

        :return: True | False
        """
        if self._task_expired_time:
            if time.time() > self._task_expired_time:
                self.terminate()  # 终止任务
                self.code = errcode.E_NODE_TASK_EXPIRED
                self.msg = u"任务(id:%d, name:%s)执行超时。" % (self.task_id, self.task_name)
                return True
        else:
            return False

    def _check_task_done(self):
        """检查任务是否执行完毕

        :return: True | False
        """

        proc_status = self._task_proc.poll()
        if proc_status is None: # 未执行完成
            # 判断是否超时
            if self._check_task_expired():
                return True
            else:
                return False
        else:
            if proc_status != 0:
                self.code = errcode.E_NODE_TASK
                self.msg = 'task process exited with code: %d' % proc_status
                self.data = ''.join(self._read_tail_lines(self.task_log))
            return True

    @property
    def done(self):
        """任务执行完
        """
        if not self._done:
            self._done = self._check_task_done()
        return self._done

    def start(self):
        """start to run the task

        :param running_tasks: running task list
        :param lock_source_dir: lock to manipulate source dir
        """
        try:
            with open(self.request_file, 'r', encoding='utf-8') as rf:
                task_request = json.load(rf)
                task_display_name = ToolDisplay.get_tool_display_name(task_request)

            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # LogPrinter.info('running in a PyInstaller bundle')
                puppy_task_name = "scantask"
                if settings.PLATFORMS[sys.platform] == 'windows':
                    puppy_task_name = '%s.exe' % puppy_task_name

                puppy_task_path = os.path.join(settings.BASE_DIR, puppy_task_name)
                # 以可执行程序的方式调用
                cmd_args = [puppy_task_path, self.request_file, self.response_file]
            else:
                python_cmd = "python3"  # python3命令
                # LogPrinter.info('running in python code')
                if not PythonTool.is_local_python_command_available(python_cmd, python_version="3"):
                    raise ConfigError("python3 command is not available, please install Python3.")

                cmd_args = [python_cmd, 'task/puppytask.py', self.request_file, self.response_file]

            LogPrinter.info(f'Task_{task_request["id"]} ({task_display_name}) starts ...')

            # 命令行参数加上引号，避免路径包含空格触发命令异常
            cmd_args = PathMgr().format_cmd_arg_list(cmd_args)

            self._task_proc = SubProcController(cmd_args,
                                                stdout_filepath=self.task_log,
                                                stderr_filepath=self.task_log,
                                                env=EnvSet().get_origin_env(self.env))

            self._task_expired_time = time.time() + app.settings.TASK_EXPIRED.total_seconds()

        except Exception as err:
            logger.exception('encounter error when starting task process')
            self.code = errcode.E_NODE_TASK
            self.msg = u"%s: %s" % (type(err).__name__, err)
            self.data = traceback.format_exc()
            self._done = True
