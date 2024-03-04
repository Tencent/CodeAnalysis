# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
1. 统计代码行
2. 获取scm info
"""

import os

from task.codemetricmodel import CodeMetricModel
from util.codecount.codestat import CodeLineCount
from util.cmdscm import ScmClient
from util.logutil import LogPrinter

logger = LogPrinter


class LineCount(CodeMetricModel):
    """
    1. 统计代码行
    2. 获取scm info
    """
    def __init__(self, params):
        CodeMetricModel.__init__(self, params)
        pass

    def __get_scm_info(self, params):
        """
        获取scm info信息
        :param params:
        :return:
        """
        source_dir = params["source_dir"]
        scm_type = params["scm_type"]
        scm_client = ScmClient(scm_type=scm_type,
                               scm_url="",
                               source_dir=source_dir,
                               scm_username="",
                               scm_password="")

        # 本地代码url和版本号
        scm_info = scm_client.info()
        return {
            "scm_revision": scm_info.commit_revision,
            "scm_time": scm_info.commit_time
        }

    def analyze(self, params):
        """
        统计source_dir代码行信息
        :param params:
        :return:
        """
        code_line_data = CodeLineCount(params).run()
        scm_info = self.__get_scm_info(params)
        return {
            "code_line": code_line_data,
            "scm_info": scm_info
        }


tool = LineCount

if __name__ == '__main__':
    pass
