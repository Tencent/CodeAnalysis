# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""任务执行独立进程
"""

import logging
import locale
import json
import os
import sys
import time
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from node.app import settings
from task.runtask import TaskRunner
from task.response import TaskResponse
from util.errcode import E_NODE_TASK_SCM_FAILED, OK, E_NODE_TASK
from util.gitconfig import GitConfig
from util.scmcache import SshFlieClient
from util.tooldisplay import ToolDisplay
from util.cmdscm import ScmCommandError

logger = logging.getLogger('task.puppytask')


class TaskMain(object):
    def __init__(self, request_file, response_file="task_response.json"):
        self._request_file = os.path.realpath(request_file)
        self._response_file = os.path.realpath(response_file)

    def run(self):
        # 记录开始时间
        time_format = "%Y-%m-%d %H:%M:%S"
        task_start_time = time.strftime(time_format,time.localtime(time.time()))

        try:
            if settings.DEBUG:
                level = logging.DEBUG
            else:
                level = logging.INFO
            format_pattern = '%(asctime)s-%(levelname)s: %(message)s'
            logging.basicConfig(level=level, format=format_pattern)

            # set locale for all categories to the user’s default setting (in the LANG env variable)
            try:
                locale.setlocale(locale.LC_ALL, '')
            except Exception as err:
                logger.error(err)
                os.environ["LC_ALL"] = "en_US.UTF-8"
                os.environ["LANG"] = "en_US.UTF-8"

            # git默认配置
            GitConfig.set_default_config()

            # 执行任务
            response = TaskRunner(self._request_file, self._response_file).run_task()
        except Exception as err:
            if isinstance(err, ScmCommandError):
                task_code = E_NODE_TASK_SCM_FAILED
            else:
                task_code = getattr(err, 'code', E_NODE_TASK)
            task_msg = u"%s: %s" % (type(err).__name__, err)
            task_data = traceback.format_exc()
            err_data = getattr(err, 'data', '')
            if err_data:
                task_data += err_data
            response = TaskResponse(status=task_code, result=task_data, message=task_msg)
        finally:
            # 删除临时ssh文件
            SshFlieClient.remove_temp_ssh_file()

        if response.status != OK:
            logger.warning('task status code is %d', response.status)
            if response.message:
                logger.warning('task messsage: %s', response.message)
            if response.result:
                with open(request_file, "r") as rf:
                    task_request = json.load(rf)
                    task_params = task_request.get("task_params")
                if not ToolDisplay.is_sensitive_tool(task_params):
                    logger.warning('task result: \n%s', response.result)

        # 记录结束时间
        task_end_time = time.strftime(time_format,time.localtime(time.time()))
        # 增加开始结束时间字段,供server记录和展示
        response["start_time"] = task_start_time
        response["end_time"] = task_end_time
        response["time_format"] = time_format

        with open(self._response_file, 'w') as fp:
            json.dump(response, fp, indent=1)
            logger.info('task result: %s', self._response_file)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        request_file = sys.argv[1]
        TaskMain(request_file).run()
    elif len(sys.argv) == 3:
        request_file = sys.argv[1]
        response_file = sys.argv[2]
        TaskMain(request_file, response_file).run()
    else:
        logger.error("puppytask参数不对!启动失败!")
