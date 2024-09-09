# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
CodeDog 前端 URL 页面链接管理，包括标准版和Coding版等，不直接调用，通过 urlmgr.py 中的 UrlMgr 类来调用对应CodeDog版本的 URL 类
"""

import logging

from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class CodeDogTrialUrl(object):
    def __init__(self, base_url, repo_id, proj_id, org_sid, team_name):
        self._base_url = base_url
        self._repo_url = urljoin(base_url, f"t/{org_sid}/p/{team_name}/code-analysis/repos/{repo_id}/")
        self._proj_url = urljoin(base_url,
                                 f"t/{org_sid}/p/{team_name}/code-analysis/repos/{repo_id}/projects/{proj_id}/")

    def get_user_info_url(self):
        """
        获取用户信息页url
        """
        return urljoin(self._base_url, "user/token")

    def get_proj_overview_url(self):
        """
        获取项目概览页面url
        """
        return urljoin(self._proj_url, "overview")

    def get_scan_history_url(self):
        """
        获取扫描任务列表url
        """
        return urljoin(self._proj_url, "scan-history")

    def get_job_url(self, job_id):
        """
        获取当前job的任务页面url
        """
        return urljoin(self._proj_url, f"scan-history/{job_id}")

    def get_issues_url(self):
        """
        获取代码检查列表url
        """
        return urljoin(self._proj_url, "codelint-issues")

    def get_scan_open_issues_url(self, scan_id):
        """
        获取某次任务新增问题列表url
        """
        return urljoin(self._proj_url, "codelint-issues?scan_open=%s&state=1" % scan_id)

    def get_scan_fix_issues_url(self, scan_id):
        """
        获取某次任务关闭问题列表url
        """
        return urljoin(self._proj_url, "codelint-issues?scan_fix=%s" % scan_id)

    def get_cc_file_list_url(self):
        """
        获取圈复杂度扫描结果url(文件列表视图)
        """
        return urljoin(self._proj_url, "metric/ccfiles")

    def get_cc_worse_file_list_url(self):
        """
        获取圈复杂度恶化文件列表url
        """
        return urljoin(self._proj_url, "metric/ccfiles?worse=true&state=1")

    def get_duplicate_result_url(self):
        """
        获取重复代码扫描结果url
        """
        return urljoin(self._proj_url, "metric/dupfiles")

    def get_cloc_result_url(self):
        """
        获取代码统计扫描结果url
        """
        return urljoin(self._proj_url, "metric/clocs")

    def get_scheme_url(self, scheme_id):
        """
        获取扫描方案url
        :param repo_id: 仓库id
        :param scheme_id:扫描方案id
        :return:
        """
        return urljoin(self._repo_url, "schemes/%s/basic" % scheme_id)
