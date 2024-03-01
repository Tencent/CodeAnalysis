# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""Gitee的API接口访问
"""
import base64
import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import quote, urlparse

from clients import exceptions
from clients.base_client import BaseClient

logger = logging.getLogger(__file__)

GITEE_URL = os.environ.get("GITEE_URL", "https://gitee.com")

GITEE_APIS = {
    "get_repos": "%s/api/v5/user/repos" % GITEE_URL,
    "get_a_repo": "%s/api/v5/repos/{repo_path}" % GITEE_URL,
    "get_branches": "%s/api/v5/repos/{repo_path}/branches" % GITEE_URL,
    "get_commits": "%s/repos/{repo_path}/commits" % GITEE_URL,
    "get_revision": "%s/api/v5/repos/{repo_path}/branches/{branch_name}" % GITEE_URL,
    "get_files": "%s/api/v5/repos/{repo_path}/contents/{path}" % GITEE_URL,
    "get_revision_time": "%s/api/v5/repos/{repo_path}/commits/{revision}" % GITEE_URL,
    "get_a_commit": "%s/api/v5/repos/{repo_path}/commits/{revision}" % GITEE_URL,
    "get_oauth": "%s/oauth/token" % GITEE_URL,
}


class GiteeAPIClient(BaseClient):
    """GitLab API类
    """

    def __init__(self, scm_url, password=None, **kwargs):
        """
        初始化参数
        :param scm_url: scm库地址
        :param password: token值
        """
        super(GiteeAPIClient, self).__init__(scm_url, **kwargs)
        logger.info("[Gitee] scm_url:%s, branch:%s" % (self._scm_url, self._branch))
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
        :params name_pattern:str,名称匹配，用于筛选
        :return: list - 格式如下：
        [
            {
                "id": "代码库ID",
                "name": "代码库名字",
                "full_name": "用户名/代码库名字",
                "private":True/False,
                "html_url":"代码库url",
                "git_url":"代码库url（包含.git）",
            }
        ]
        """
        params = {"per_page": 100, "page": 1}
        if name_pattern:
            params["q"] = name_pattern
        r = self.get(GITEE_APIS["get_repos"], params=params)

        repos = []
        for repo_info in self.get_json(r):
            repos.append({
                "id": repo_info["id"],
                "name": repo_info["name"],
                "name_with_namespace": repo_info["full_name"],
                "html_url": repo_info["url"],
                "git_url": repo_info["html_url"],
            })

        return repos

    def get_repo_info(self):
        """获取单个项目信息
        :return dict
        """
        r = self.get(GITEE_APIS["get_a_repo"].format(repo_path=self._repo_path),
                     raise_exception=False)
        if self.is_ok(r):
            info = self.get_json(r)
            print(info)
            if info and self.compare_url(self._scm_url, info["html_url"]):
                return info
            else:
                raise exceptions.NotFoundException("项目可能不存在或没有项目访问权限")
        else:
            raise exceptions.NotFoundException("项目可能不存在或没有项目访问权限")

    def list_branches(self):
        """获取分支列表
        :params: project_id:项目id
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
        r = self.get(GITEE_APIS["get_branches"].format(repo_path=self._repo_path))
        branches = []
        for branch_info in self.get_json(r):
            print(branch_info)
            branches.append({
                "name": branch_info["name"],
            })

        return branches

    @property
    def latest_revision(self):
        """获取指定代码库指定分支的最新版本号
        return : str - 版本号
        """
        r = self.get(GITEE_APIS["get_revision"].format(repo_path=self._repo_path, branch_name=self._branch))
        data = self.get_json(r)
        return data["commit"]["sha"]

    def cat_file(self, path, revision=None):
        """获取指定代码库指定分支的指定文件内容
        :params : path - 文件路径
        return : 文件内容
        """
        path = quote(path, safe="")
        params = {"ref": self._branch}
        if revision:
            params = {"ref": revision}
        r = self.get(GITEE_APIS["get_files"].format(repo_path=self._repo_path, path=path),
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
        :params: revision - 版本号
        : return: int - 提交时间戳（（转换为本地时间）
        """
        r = self.get(GITEE_APIS["get_a_commit"].format(
            repo_path=self._repo_path, revision=revision), raise_exception=False)
        data = self.get_json(r)
        if self.is_ok(r):
            commit_date_str = data["commit"]["committer"]["date"]
            committed_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%S%z')
            committed_date = committed_date.replace(tzinfo=None)
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
        logger.info("list path: %s-%s" % (path, revision))
        params = {}
        if path is None:
            path = ''
        if revision is not None:
            params["ref"] = revision
        else:
            params["ref"] = self._branch
        r = self.get(GITEE_APIS["get_files"].format(repo_path=self._repo_path, path=path),
                     params=params, raise_exception=False)
        data = self.get_json(r)
        print(data)
        if self.is_ok(r):
            paths = []
            for item in data:
                paths.append({
                    "name": item["name"],
                    "type": item["type"]
                })
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
        """OAuth授权
        :param auth_info : dict
        :return: dict
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if not auth_info.get("code"):
            raise exceptions.BadRequestException(msg="缺少授权码 authorization_code")
        if not auth_info.get("client_id"):
            raise exceptions.BadRequestException(msg="缺少客户端编号 client_id")
        if not auth_info.get("client_secret"):
            raise exceptions.BadRequestException(msg="缺少客户端密钥 client_secret")
        data = {
            "grant_type": "authorization_code",
            "client_id": auth_info.get("client_id"),  # APP_ID
            "client_secret": auth_info.get("client_secret"),
            "code": auth_info.get("code"),
            "redirect_uri": auth_info.get("redirect_uri"),
        }
        r = self.post(GITEE_APIS["get_oauth"], params=data, headers=headers, raise_exception=False)
        if self.is_ok(r):
            return self.get_json(r)
        elif 400 <= r.status < 500:
            logger.error("git oauth error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="授权异常，请稍后再试，异常原因：%s" % self.get_text(r))
        else:
            logger.error("git oauth error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git Code平台服务异常，请稍后再试，异常原因：%s" % self.get_text(r))

    def get_token_through_refresh_token(self, auth_info):
        """通过refresh token得到access_token
        :return: str - access_token
        """
        auth_info.update({"grant_type": "refresh_token"})
        r = self.post(GITEE_APIS["get_oauth"], params=auth_info)
        data = self.get_json(r)

        return {"access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "created_at": data["created_at"]}
