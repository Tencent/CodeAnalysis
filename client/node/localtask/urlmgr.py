# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codedog url 管理
"""

import logging

from node.localtask.urlclient import CodeDogTrialUrl

logger = logging.getLogger(__name__)


class UrlMap(object):
    @staticmethod
    def get_frontend_url(server_url):
        """
        根据后端url,获取展示用的前端url
        :param server_url:
        :return:
        """
        if "server/main" in server_url:
            return server_url.split("server/main")[0]
        else:
            return server_url.rstrip('/')


class UrlMgr(object):
    """
    获取 codedog 前端页面展示 url
    """
    def __init__(self, front_end_url, repo_id=None, proj_id=None, org_sid=None, team_name=None):
        self._url_client = CodeDogTrialUrl(front_end_url, repo_id, proj_id, org_sid, team_name)

    def get_user_info_url(self):
        """
        获取用户信息页url
        """
        return self._url_client.get_user_info_url()

    def get_proj_overview_url(self):
        """
        获取项目概览页面url
        """
        return self._url_client.get_proj_overview_url()

    def get_scan_history_url(self):
        """
        获取扫描任务列表url
        """
        return self._url_client.get_scan_history_url()

    def get_job_url(self, job_id):
        """
        获取当前job的任务页面url
        """
        return self._url_client.get_job_url(job_id)

    def get_issues_url(self):
        """
        获取代码检查列表url
        """
        return self._url_client.get_issues_url()

    def get_scan_open_issues_url(self, scan_id):
        """
        获取某次任务新增问题列表url
        """
        return self._url_client.get_scan_open_issues_url(scan_id)

    def get_scan_fix_issues_url(self, scan_id):
        """
        获取某次任务关闭问题列表url
        """
        return self._url_client.get_scan_fix_issues_url(scan_id)

    def get_cc_file_list_url(self):
        """
        获取圈复杂度扫描结果url(文件列表视图)
        """
        return self._url_client.get_cc_file_list_url()

    def get_cc_worse_file_list_url(self):
        """
        获取圈复杂度恶化文件列表url
        """
        return self._url_client.get_cc_worse_file_list_url()

    def get_duplicate_result_url(self):
        """
        获取重复代码扫描结果url
        """
        return self._url_client.get_duplicate_result_url()

    def get_cloc_result_url(self):
        """
        获取代码统计扫描结果url
        """
        return self._url_client.get_cloc_result_url()

    def get_scheme_url(self, scheme_id):
        """
        获取扫描方案url
        :param repo_id: 仓库id
        :param scheme_id:扫描方案id
        :return:
        """
        return self._url_client.get_scheme_url(scheme_id)
