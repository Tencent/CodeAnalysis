# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" 与codedog server通信的API重试类
"""

import time
import logging

from util.api.dogapi import CodeDogApiServer
from util.wrapper import SyncWrapper, Retry


logger = logging.getLogger(__name__)


class RetryDogServer(object):
    """
    访问CodeDog Server的API重试类
    """
    def __init__(self, server_url, token):
        self._server_url = server_url
        self._token = token

    def __retry_on_error(self, error, method_name):
        """
        失败重试函数
        :param error:
        :return:
        """
        # 不需要重试的方法
        if method_name in ["update_task_progress"]:
            raise error
        err_msg = str(error)
        # 遇到以下错误，server可能正在升级，需要1分钟左右的时间，因此重试间隔增加30s（加上原来的5s，一共35s，至少会重试2次，可以满足1分钟的server更新）
        # 400 - 服务器不理解请求的语法
        # 500 -（服务器内部错误）服务器遇到错误，无法完成请求
        if "Error[400]" in err_msg or "Error[500]" in err_msg:
            logger.info("服务器可能正在升级,等待30s后重试...")
            time.sleep(30)
        # 重试直到成功为止
        return

    def get_api_server(self, retry_times=-1):
        """根据实际情况获取api server对象

        :param retry_times: 异常重试次数,默认为-1,即一直重试直到成功
        :param token: api访问token
        :return: api server对象
        """
        api_server = CodeDogApiServer(self._token, self._server_url)
        return SyncWrapper(Retry(server=api_server, on_error=self.__retry_on_error, total=retry_times))
