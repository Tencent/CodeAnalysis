# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""GitHub的API接口访问
"""
import base64
import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import quote, urlparse

import pytz

from clients import exceptions
from clients.base_client import BaseClient

logger = logging.getLogger(__file__)

GITHUB_API_URL = os.environ.get("GITHUB_URL", "https://api.github.com")

GITHUB_APIS = {
    "get_oauth": "https://github.com/login/oauth/access_token",
    "get_a_repo": "%s/repos/{repo_path}" % GITHUB_API_URL,
    "get_repos": "%s/user/repos" % GITHUB_API_URL,
    "get_commits": "%s/repos/{repo_path}/commits" % GITHUB_API_URL,
    "get_branches": "%s/repos/{repo_path}/branches" % GITHUB_API_URL,
    "get_revision": "%s/repos/{path}/commits/{branch_name}" % GITHUB_API_URL,
    "get_files": "%s/repos/{repo_path}/contents/{path}" % GITHUB_API_URL,
    "get_a_commit": "%s/repos/{repo_path}/commits/{revision}" % GITHUB_API_URL,
}


class GitHubAPIClient(BaseClient):
    """GitHub OAuth API类
    """

    def __init__(self, scm_url, password=None, **kwargs):
        """
        初始化函数
        :param scm_url: scm库地址
        :param password: token值
        param: auth_info - 用户信息
        """
        super(GitHubAPIClient, self).__init__(scm_url, **kwargs)
        logger.info("[GitHub] scm_url:%s, branch:%s" % (self._scm_url, self._branch))
        self._username = kwargs.get("username")
        self._token = password
        self._headers = {"Authorization": "token %s" % self._token}
        self._repo_path = self._get_repo_path()

    def _get_repo_path(self):
        """获取代码库名称
        """
        scm_url = re.sub(r".git$", "", self._scm_url.strip())
        parsed_uri = urlparse(scm_url)
        return parsed_uri.path.strip('/')

    def list_repos(self, name_pattern=None):
        """获取代码库列表

        # :params name_pattern:str,名称匹配，用于筛选
        :return: list - 格式如下：
        [
            {
                "id": "代码库ID",
                "name": "代码库名字",
                "full_name": "用户名/代码库名字",
                "size":"代码库大小",
                "private":True/False,
                "html_url":"代码库url",
                "git_url":"代码库url（包含.git）"
                "open_issues_count":"有多少open issue"
            }
        ]
        """
        params = {"per_page": 100, "page": 1}
        r = self.get(GITHUB_APIS["get_repos"], params=params)
        repos = []
        for repo_info in self.get_json(r):
            repos.append({
                "id": repo_info["id"],
                "name": repo_info["name"],
                "full_name": repo_info["full_name"],
                "size": repo_info["size"],
                "private": repo_info["private"],
                "html_url": repo_info["html_url"],
                "git_url": repo_info["git_url"],
                "open_issues_count": repo_info["open_issues_count"]
            })

        return repos

    def list_branches(self):
        """获取分支列表
        :return: list - 格式如下：
        [
            {
                "name": "分支名",
                "current_commit_name": "commit提交者名",
                "current_commit_date": "commit提交时间",
                "current_commit_message": "commit提交信息"
            }
        ]
        """
        params = {"per_page": 100, "page": 1}
        r = self.get(GITHUB_APIS["get_branches"].format(repo_path=self._repo_path),
                     params=params)
        branches = []
        for branch in self.get_json(r):
            cur_branch_info = {"name": branch["name"]}
            cur_branch_commit_url = branch["commit"]["url"] + "?access_token=%s" % self._token
            r = self.get(cur_branch_commit_url)
            result = self.get_json(r)
            cur_branch_info["current_commit_name"] = result["commit"]["committer"]["name"]
            cur_branch_info["current_commit_date"] = result["commit"]["committer"]["date"]
            cur_branch_info["current_commit_message"] = result["commit"]["message"]
            branches.append(cur_branch_info)
        return branches

    def get_repo_info(self):
        """获取单个代码库信息
        :return : dict
        """
        r = self.get(GITHUB_APIS["get_a_repo"].format(repo_path=self._repo_path),
                     raise_exception=False)
        if self.is_ok(r):
            info = self.get_json(r)
            if info and self.compare_url(self._scm_url, info["clone_url"], info["html_url"]):
                return info
            else:
                raise exceptions.NotFoundException("项目可能不存在或没有项目访问权限")
        else:
            raise exceptions.NotFoundException("项目可能不存在或没有项目访问权限")

    @property
    def latest_revision(self):
        """获取指定代码库指定分支的最新版本号
        return : str - 版本号
        """
        params = {"sha": self._branch}
        r = self.get(GITHUB_APIS["get_commits"].format(repo_path=self._repo_path), params=params)
        data = self.get_json(r)
        if len(data) > 0:
            return data[0]["sha"]
        else:
            logger.error("get latest revision fail, scm url: %s, error reason: no commit" % self._scm_url)
            raise exceptions.NotFoundException(msg="项目在%s没有提交记录" % self._branch)

    def cat_file(self, path, revision=None):
        """获取文件内容
        :params: path : 文件路径
        :params: revision - 指定版本，默认为最新版本
        :return : 文件内容

        """
        path = quote(path, safe="")
        params = {"ref": self._branch}
        if revision:
            params = {"ref": revision}
        r = self.get(GITHUB_APIS["get_files"].format(repo_path=self._repo_path, path=path),
                     params=params, raise_exception=False)
        data = self.get_json(r)
        if self.is_ok(r):
            if data["content"]:
                content = base64.b64decode(data["content"])
                try:
                    content = content.decode("utf-8")
                except Exception as err:
                    logger.exception("decode content failed: %s" % err)
                    content = content.decode("gbk")
                return content
            else:
                raise exceptions.ServerException(msg="当前文件无法打开，建议在本地查阅文件")
        elif r.status == 404:
            raise exceptions.NotFoundException(msg="Path '%s' does not exist" % path)
        elif 400 <= r.status < 500:
            logger.error("cat file error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="获取代码文件异常，请稍后再试")
        else:
            logger.error("cat file error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git 平台服务异常，请稍后再试")

    def get_revision_time(self, revision):
        """ 获取代码库指定版本的创建时间
        :params: revision - 版本
        : return: int - 提交时间戳（转换为本地时间）
        """
        r = self.get(GITHUB_APIS["get_a_commit"].format(
            repo_path=self._repo_path, revision=revision), raise_exception=False)
        data = self.get_json(r)
        if self.is_ok(r):
            committed_date_utc = data["commit"]["committer"]["date"]
            committed_date_utc = datetime.strptime(committed_date_utc, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
            committed_date = committed_date_utc.astimezone(tz=None).replace(tzinfo=None)
            committed_timestamp = time.mktime(committed_date.timetuple())
            return committed_timestamp
        elif r.status == 404:
            raise exceptions.NotFoundException(msg="SHA '%s' could not be resolved" % revision)
        elif 400 <= r.status < 500:
            logger.error("get_revision_time error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="获取版本号时间异常，请稍后再试")
        else:
            logger.error("get_revision_time error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git 平台服务异常，请稍后再试")

    def ls_tree(self, path, revision=None):
        """ 获取指定路径下的子目录和文件列表
        :params path: 指定路径，默认为根路径
        :params revision: 版本 默认为最新版本
        :return: list: 包含文件或路径名以及type
        """
        params = {}
        if path is None:
            path = ''
        if revision is not None:
            params["ref"] = revision
        r = self.get(GITHUB_APIS["get_files"].format(repo_path=self._repo_path, path=path),
                     params=params, raise_exception=False)
        data = self.get_json(r)
        if self.is_ok(r):
            paths = []
            for item in data:
                paths.append({"name": item["path"], "type": item["type"]})
            if len(paths) > 0:
                return paths
            else:
                raise exceptions.NotFoundException(msg="Path '%s' does not exist" % path)
        elif r.status == 404:
            raise exceptions.NotFoundException(msg="SHA '%s' could not be resolved" % revision)
        elif 400 <= r.status < 500:
            logger.error("list error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="获取目录列表异常，请稍后再试")
        else:
            logger.error("list error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git 平台服务异常，请稍后再试")

    def revision_lt(self, revision_start, revision_end):
        """ 比较版本大小
        :param revision_start:起始版本
        :param revision_end:结束版本
        :return 布尔值
            False 表示 revision_start>=revision_end
            True 表示 revision_start<revision_end
        """
        revision_start_time = self.get_revision_time(revision_start)
        revision_end_time = self.get_revision_time(revision_end)
        if revision_start_time >= revision_end_time:
            return False
        else:
            return True

    def get_oauth(self, auth_info):
        """通过OAuth app获得access_token
        param: auth_info - 用户信息
        auth_info = {"client_id": xxx,
                     "client_secret": xxx,
                     "code": xxx }
        :return : dict {"access_token": xx}
        """
        if not auth_info.get("code"):
            raise exceptions.BadRequestException(msg="缺少授权码 authorization_code")
        if not auth_info.get("client_id"):
            raise exceptions.BadRequestException(msg="缺少客户端编号 client_id")
        if not auth_info.get("client_secret"):
            raise exceptions.BadRequestException(msg="缺少客户端密钥 client_secret")
        data = {
            "grant_type": "authorization_code",
            "client_id": auth_info.get("client_id"),
            "client_secret": auth_info.get("client_secret"),
            "code": auth_info.get("code"),
            "redirect_uri": auth_info.get("redirect_uri"),
        }
        headers = {"Accept": "application/json"}
        r = self.post(GITHUB_APIS["get_oauth"], params=data, headers=headers, raise_exception=False)
        if self.is_ok(r):
            return self.get_json(r)
        elif 400 <= r.status < 500:
            logger.error("git oauth error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="授权异常，请稍后再试，异常原因：%s" % self.get_text(r))
        else:
            logger.error("git oauth error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git Code平台服务异常，请稍后再试，异常原因：%s" % self.get_text(r))
