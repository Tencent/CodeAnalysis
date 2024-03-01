# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
task基础类，用于task的定义与执行
task的主要工作是承担各个工具的公共执行部分，以及指定task类型的公共功能
例如：
    结果处理，工具不应该关注这块的内容，所以需要task来实现具体操作

"""


class ITaskModel(object):
    def __init__(self, tool):
        self.tool = tool

    def runner(self, params):
        """

        :return: task是否成功
        """
        raise NotImplementedError()
