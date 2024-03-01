# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
在结果中添加文件层级信息，比如language,owners字段
"""

import logging

from task.basic.datahandler.handlerbase import HandlerBase
from util.checklanguage import LanguageChecker
from util.codeyaml.fileowner import FileOwner

logger = logging.getLogger(__name__)

NO_ADD_FILE_INFO = 0
NORMAL_ADD_FILE_INFO = 1
CCN_ADD_FILE_INFO = 2


class AddFileInfo(HandlerBase):
    @staticmethod
    def get_tool_handle_type_name():
        return "set_add_file_info"

    def run(self, params):
        if self.handle_type == NO_ADD_FILE_INFO:
            return params
        elif self.handle_type == NORMAL_ADD_FILE_INFO:
            return self.__normal_add_file_info(params)
        elif self.handle_type == CCN_ADD_FILE_INFO:
            return self.__ccn_diff_info(params)
        return params

    def __normal_add_file_info(self, params):
        """
        通用处理，适用代码检查类型
        :param params:
        :return:
        """
        if params["result"]:
            # 增加文件负责人
            logger.info("Start: add file owners...")
            params["result"] = FileOwner().add_file_owner_info(params, params["result"])
            logger.info("End: add file owners.")

            # 增加文件语言类型
            logger.info("Start: add file language type...")
            for path_issue in params["result"]:
                file_path = path_issue["path"]
                # 增加当前文件的语言类型
                language_type = LanguageChecker.get_file_language_type(file_path)
                if language_type:
                    path_issue["language"] = language_type
            logger.info("End: add file language type.")
        return params

    def __ccn_diff_info(self, params):
        """
        适用圈复杂度,重复代码
        :param params:
        :return:
        """
        if params["result"] and params["result"]["detail"]:
            # 增加文件负责人
            logger.info("Start: add file owners...")
            params["result"]["detail"] = FileOwner().add_file_owner_info(params, params["result"]["detail"])
            logger.info("End: add file owners.")

            # 增加文件语言类型
            logger.info("Start: add file language type...")
            for path_issue in params["result"]["detail"]:
                file_path = path_issue["path"]
                # 增加当前文件的语言类型
                language_type = LanguageChecker.get_file_language_type(file_path)
                if language_type:
                    path_issue["language"] = language_type
            logger.info("End: add file language type.")

        return params
