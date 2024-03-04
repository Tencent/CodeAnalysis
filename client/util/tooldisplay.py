# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
管理本地工具展示名称
"""

from util.logutil import LogPrinter


class ToolDisplay(object):
    """
    管理本地工具展示
    """
    @staticmethod
    def get_tool_display_name(task_request):
        """
        获取工具展示名称，供日志打印使用
        :param task_request:
        :return:
        """
        show_name = None
        try:
            tool_params = task_request['task_params']['checktool']
            if tool_params:
                display_name = tool_params.get('display_name')
                virtual_name = tool_params.get('virtual_name')
                show_display_name = tool_params.get('show_display_name')
                # 如果不展示display_name，则展示virtual_name
                if show_display_name:
                    if display_name:
                        show_name = display_name
                elif virtual_name:
                    show_name = "Tool_%s" % virtual_name
        except KeyError:
            LogPrinter.exception('task_params is wrong.')

        if show_name:
            return show_name
        else:  # 未获取到展示名称，则展示task_name
            return task_request['task_name']

    @staticmethod
    def is_sensitive_tool(task_params):
        """
        判断工具是否敏感工具，后续需要对日志脱敏，并隐藏工具名
        :param task_params:
        :return: True-敏感；False-非敏感
        """
        if not task_params:
            return True

        tool_params = task_params.get("checktool")
        if not tool_params:
            return True

        show_display_name = tool_params.get('show_display_name')
        # 不显示display_name，即需要显示虚拟名称，说明是敏感工具
        if not show_display_name:
            return True
        else:
            return False

    @staticmethod
    def print_log(is_sensitive, sensitive_word_maps, message):
        """
        将日志中的敏感词替换掉，再打印日志
        :param is_sensitive:
        :param sensitive_word_maps:
        :param message:
        :return:
        """
        if is_sensitive:
            for key, value in sensitive_word_maps.items():
                if key in message:
                    message = message.replace(key, value)
        LogPrinter.info(message)
