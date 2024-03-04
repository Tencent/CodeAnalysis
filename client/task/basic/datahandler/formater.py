# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
用于对扫描结果格式化
"""

import logging

from util.reporter import Reporter, InfoType
from util.exceptions import TaskFormatError
from task.basic.datahandler.handlerbase import HandlerBase

logger = logging.getLogger(__name__)


NORMAL_FORMAT = 1
NO_FORMAT = 3
CCN_FORMAT = 4


class Formater(HandlerBase):
    def run(self, params):
        """

        :param params:
        :return:
        """
        if not params:
            return params

        Reporter(params).update_task_progress(InfoType.FormatTask)
        if self.handle_type == NORMAL_FORMAT:
            return self._normal_format(params)
        elif self.handle_type == NO_FORMAT:
            return params
        elif self.handle_type == CCN_FORMAT:
            return self._ccn_format(params)
        raise TaskFormatError("format type is not exist: %s" % self.handle_type)

    def _normal_format(self, params):
        """
        代码扫描的结果格式化
        1. 调整扫描结果格式,将同一个文件的问题集中到一起,方便后续结果处理
        输入格式:
            [issue1, issue2, ...]
        输出格式:
            [{'path': xxx, 'issues': [new_issue1, new_issue2, ...]}
            其中 new_issue 会将原 issue 中的 path 字段去掉.
        2. 结果中的path统一为使用linux文件分隔符
        :param params:
        :return:
        """
        params["result"] = self.__common_format(params["result"], params["tool_name"])
        return params

    def _ccn_format(self, params):
        """
        代码扫描的结果格式化
        1. 调整扫描结果格式,将同一个文件的问题集中到一起,方便后续结果处理
        输入格式:
            [issue1, issue2, ...]
        输出格式:
            [{'path': xxx, 'issues': [new_issue1, new_issue2, ...]}
            其中 new_issue 会将原 issue 中的 path 字段去掉.
        2. 结果中的path统一为使用linux文件分隔符
        :param params:
        :return:
        """
        params["result"]["detail"] = self.__common_format(params["result"]["detail"], params["tool_name"])
        return params

    def __common_format(self, result, tool_name):
        """

        :param result:
        :param tool_name:
        :return:
        """
        issues = self.__insert_checker_name(result, tool_name)
        fileissues = {}
        for issue in issues:
            path = issue.pop("path")
            path = path.replace("\\", "/")  # 转换为linux文件分隔符,方便后续对比操作
            try:
                fileissues[path]["issues"].append(issue)
            except KeyError:
                fileissues[path] = {"path": path, "issues": [issue]}
        return list(fileissues.values())

    def __insert_checker_name(self, result, checker_name):
        """
        server端要求issue上报时，每个issue中要有check字段表示工具名称，此处统一插入处理
        :param result: 插入前的issue集合
        :param checker_name: 工具名称
        :return: 插入后的issue集合
        """
        if not result:
            return result
        for issue in result:
            issue["checker"] = checker_name
        return result

    @staticmethod
    def get_tool_handle_type_name():
        return "set_format_type"
