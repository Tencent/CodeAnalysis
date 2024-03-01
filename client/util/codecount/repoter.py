# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
节点任务，向server上报代码量
"""

import logging
import threading

from util.taskscene import TaskScene
from util.api.dogserver import RetryDogServer
from node.app import settings
from util.crypto import Crypto
from util.codecount.codestat import CodeLineCount

logger = logging.getLogger(__name__)


class CodeLineReporter(threading.Thread):
    """代码行上报类
    """
    def __init__(self, task_params):
        threading.Thread.__init__(self)
        self._task_params = task_params
        self._task_scene = task_params.get('task_scene', None)

    def run(self):
        """统计代码行并向server上报

                :param source_dir: 代码目录
                :return:
                """
        # 本地项目无需上报,直接返回
        if self._task_scene and self._task_scene in [TaskScene.LOCAL, TaskScene.TEST]:
            return
        try:
            # 从param中获取server_url
            server_url = self._task_params.get("server_url", None)
            # 从param中获取token并解密
            encrypted_token = self._task_params.get("token", None)
            token = Crypto(settings.PASSWORD_KEY).decrypt(encrypted_token)

            dog_server = RetryDogServer(server_url, token).get_api_server(retry_times=0)

            job_id = self._task_params['job_id']
            # 查询是否已经上报过
            data = dog_server.get_job_code_line(self._task_params, job_id)
            if data and data["code_line_num"]:
                logger.info("已经上报过代码行数,本次分析无需上报.")
                return
            # 统计代码行 - 整个目录统计,不按照增量和过滤路径过滤,比较耗时
            code_line_dict = CodeLineCount(self._task_params).run()
            # 上报代码行数据
            logger.info("上报代码行数: %s", code_line_dict)
            dog_server.update_job_code_line(self._task_params, job_id, code_line_dict)
        except Exception as err:
            logger.exception('update_job_code_line fail: %s' % str(err))
