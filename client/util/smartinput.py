# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
输入工具类,重新封装输入函数,具有错误重试功能
"""

import logging
import getpass

from util.exceptions import InputRetryError

logger = logging.getLogger(__name__)


class SmartInput(object):
    def __base_input(self, prompt, is_password):
        """
        基础的输入,带密码掩码功能
        :param prompt: 提示信息
        :param is_password: 是否是密码输入
        :return: 输入的数据
        """
        if is_password:
            input_data = getpass.getpass(prompt)
        else:
            input_data = input(prompt)
        return input_data

    def __error_retry_input(self, input_data, check_func, retry_prompt, retry_times, is_password=False):
        """
        检查输入,如果输入有误,重新提示输入,直到输入正确,或超过最多重试次数
        :param input_data: 输入数据
        :param check_func: 检查回调函数,返回True(输入正确)|False(输入有误)
        :param retry_prompt: 重试输入的提示信息
        :param retry_times: 重试总次数,默认可以重试2次
        :param is_password: 是否是密码输入
        :return:
        """
        if check_func(input_data):
            return input_data
        else:  # 不符合要求,需要重试
            retry_cnt = 1
            while retry_cnt <= retry_times:
                input_data = self.__base_input(retry_prompt, is_password)
                if check_func(input_data):
                    return input_data
                retry_cnt += 1
            logger.error("%s次输入错误,退出!" % (retry_times+1))
            raise InputRetryError("%s次输入错误,退出!" % (retry_times+1))

    def input(self, prompt, check_func=None, retry_prompt=None, retry_times=2, is_password=False):
        """
        提示用户输入,可以设置错误重试次数,可以设置密码掩码输入,不在屏幕显示实时输入的信息
        :param prompt: 首次输入提示信息
        :param timeout: 每次输入的超时值(秒),默认10s
        :param check_func: 检查回调函数,返回True(输入正确)|False(输入有误)
        :param retry_prompt: 重试输入的提示信息
        :param retry_times: 允许重试的最大次数, 默认可以重试2次
        :param is_password: 是否是密码输入
        :return:
        """
        data = self.__base_input(prompt, is_password)
        if check_func and retry_prompt and retry_times:
            data = self.__error_retry_input(data, check_func, retry_prompt, retry_times, is_password)
        return data
