# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地任务执行器,只执行本地配置好的项目的扫描
"""
import logging

from node.localtask.filtermgr import FilterManager
from node.common.userinput import UserInput
from task.initparams import InitParams
from util.checklanguage import LanguageChecker
from util.logutil import LogPrinter

logger = logging.getLogger(__name__)


class LanguageManager(object):
    @staticmethod
    def auto_identify_languages(source_dir, include_paths, exclude_paths,
                                dog_server, repo_id, proj_id, org_sid, team_name):
        """
        自动识别语言
        """
        language_list = []
        if source_dir:
            logger.info("未输入语言信息,自动识别代码语言...")
            # 构造一个带过滤路径参数的task_params
            task_prarams = {
                "source_dir": source_dir,
                "path_filters": FilterManager.get_local_filtered_paths(include_paths, exclude_paths,
                                                                       dog_server, repo_id, proj_id, org_sid, team_name)
            }
            InitParams.modify_path_filters(task_prarams)
            language_data = LanguageChecker.recognize_language(source_dir, task_prarams)
            language_list = list(language_data.keys())
        if language_list:
            language_str = ','.join(language_list)
            LogPrinter.info(f"Project language: {language_str}")
            return UserInput().format_languages(language_str)
        else:
            LogPrinter.warning("Project language is empty, probably contains no code!")
            return []
