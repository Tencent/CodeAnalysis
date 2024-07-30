# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""GitLab的API接口访问
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

GITLAB_URL = os.environ.get("GITLAB_URL") or "https://gitlab.com"

GITLAB_APIS = {
    "get_projects": "%s/api/v4/projects" % GITLAB_URL,
    "get_a_project": "%s/api/v4/projects/{project_id}" % GITLAB_URL,
    "get_branches": "%s/api/v4/projects/{project_id}/repository/branches" % GITLAB_URL,
    "get_revision": "%s/api/v4/projects/{project_id}/repository/branches/{branch_name}" % GITLAB_URL,
    "get_files": "%s/api/v4/projects/{project_id}/repository/files/{path}" % GITLAB_URL,
    "get_revision_time": "%s/api/v4/projects/{project_id}/repository/commits/{revision}" % GITLAB_URL,
    "get_paths": "%s/api/v4/projects/{project_id}/repository/tree" % GITLAB_URL,
    "get_oauth": "%s/oauth/token" % GITLAB_URL,
}


class GitLabAPIClient(BaseClient):
    """GitLab API类
    """

    def __init__(self, scm_url, password=None, **kwargs):
        """
        初始化参数
        :param scm_url: scm库地址
        :param password: token值
        """
        super(GitLabAPIClient, self).__init__(scm_url, **kwargs)
        logger.info("[GitLab] scm_url:%s, branch:%s" % (self._scm_url, self._branch))
        self._token = password
        self._headers = {"Authorization": "Bearer %s" % self._token}
        self._project_path = self._get_project_path()
        self._enquote_project_path = quote(self._project_path, safe="")

    def _get_project_path(self):
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
            params["search"] = name_pattern
            params["search_namespaces"] = True
        r = self.get(GITLAB_APIS["get_projects"], params=params)

        projects = []
        for project_info in self.get_json(r):
            projects.append({
                "id": project_info["id"],
                "name": project_info["name"],
                "name_with_namespace": project_info["name_with_namespace"],
                "html_url": project_info["web_url"],
                "git_url": project_info["http_url_to_repo"],
            })

        return projects

    def get_project_info(self):
        """获取单个项目信息
        :return dict
        """
        r = self.get(GITLAB_APIS["get_a_project"].format(project_id=self._enquote_project_path),
                     raise_exception=False)
        if self.is_ok(r):
            info = self.get_json(r)
            if info and self.compare_url(self._scm_url, info["http_url_to_repo"], info["web_url"]):
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
        r = self.get(GITLAB_APIS["get_branches"].format(project_id=self._enquote_project_path))
        branches = []
        for branch_info in self.get_json(r):
            branches.append({
                "name": branch_info["name"],
                "current_commit_name": branch_info["commit"]["committer_name"],
                "current_commit_date": branch_info["commit"]["committed_date"],
                "current_commit_message": branch_info["commit"]["message"]
            })

        return branches

    @property
    def latest_revision(self):
        """获取指定代码库指定分支的最新版本号
        return : str - 版本号
        """
        r = self.get(GITLAB_APIS["get_revision"].format(
            project_id=self._enquote_project_path, branch_name=quote(self._branch, safe="")))
        data = self.get_json(r)
        return data["commit"]["id"]

    def cat_file(self, path, revision=None):
        """获取指定代码库指定分支的指定文件内容
        :params : path - 文件路径
        return : 文件内容
        """
        path = quote(path, safe="")
        params = {"ref": self._branch}
        if revision:
            params = {"ref": revision}
        r = self.get(GITLAB_APIS["get_files"].format(project_id=self._enquote_project_path, path=path),
                     params=params, raise_exception=False)
        if self.is_ok(r):
            data = self.get_json(r)
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
        r = self.get(GITLAB_APIS["get_revision_time"].format(
            project_id=self._enquote_project_path, revision=revision), raise_exception=False)
        if self.is_ok(r):
            data = self.get_json(r)
            committed_date_utc = datetime.strptime(data["committed_date"], '%Y-%m-%dT%H:%M:%S.%f%z')
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
        logger.info("list path: %s-%s" % (path, revision))
        params = {}
        if path is not None:
            params["path"] = path
        if revision is not None:
            params["ref"] = revision
        else:
            params["ref"] = self._branch
        r = self.get(GITLAB_APIS["get_paths"].format(project_id=self._enquote_project_path),
                     params=params, raise_exception=False)
        data = self.get_json(r)
        if self.is_ok(r):
            paths = []
            type_dict = {"tree": "dir", "blob": "file"}
            for item in data:
                paths.append({
                    "name": item["name"],
                    "type": type_dict[item["type"]]
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
        r = self.post(GITLAB_APIS["get_oauth"], params=data, raise_exception=False)
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
        r = self.post(GITLAB_APIS["get_oauth"], params=auth_info)
        data = self.get_json(r)

        return {"access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "created_at": data["created_at"]}
