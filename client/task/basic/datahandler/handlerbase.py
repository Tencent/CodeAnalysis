# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
结果处理操作类的接口类
"""


class HandlerBase(object):
    """
    datahandle 的处理接口类，所有的结果处理都基于此接口类实现
    """

    def __init__(self, handle_type):
        self.handle_type = handle_type

    def run(self, params):
        raise NotImplementedError()

    @staticmethod
    def get_tool_handle_type_name():
        # 所有继承该类的类，需要在toolmodel中实现一个函数用于获取进行结果处理的类型
        # 例如：set_format_type
        # 而继承该类的类中必须实现本函数，返回对应toolmodel中的函数名
        # 例如formater中本函数返回值为 “set_format_type”
        raise NotImplementedError()
