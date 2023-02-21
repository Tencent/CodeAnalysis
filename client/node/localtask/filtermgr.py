# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2023 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地任务执行器,只执行本地配置好的项目的扫描
"""
import logging

logger = logging.getLogger(__name__)


class FilterManager(object):
    @staticmethod
    def get_local_filtered_paths(include_paths, exclude_paths, dog_server, repo_id, proj_id, org_sid, team_name):
        """
        从server端获取默认过滤路径，并与本地过滤路径参数合并，得到本地使用的过滤路径
        :return:
        """
        default_filtered_paths = dog_server.get_default_filtered_paths(repo_id, proj_id, org_sid, team_name)
        return {
            "inclusion": include_paths + default_filtered_paths["inclusion"],
            "exclusion": exclude_paths + default_filtered_paths["exclusion"],
            "re_inclusion": default_filtered_paths["re_inclusion"],
            "re_exclusion": default_filtered_paths["re_exclusion"]
        }
