# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
# 代码规范工具任务参数
"""


class JobParams(object):
    job_context = {
        "project_id": 1,
        "repo_id": 1,
        "scheme_id": 1,
        "scheme_name": "",
        "job_runtime_limit": 600,
        "ignore_submodule_clone": True,
        "ignore_submodule_issue": False,
        "issue_global_ignore": False,
        "daily_save": True,
        "oteam_score_flag": False,
        "lfs_flag": True,
        "issue_revision_merge_flag": False,
        "code_yaml_filter": None,
        "scm_type": "git",
        "scm_url": "",
        "path_filters": {
            "inclusion": [],
            "exclusion": [],
            "re_inclusion": [],
            "re_exclusion": []
        },
        "scm_initial_revision": None
    }
