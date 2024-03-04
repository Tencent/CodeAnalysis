# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""工蜂社区版的API接口访问
"""
import base64
import logging
import os
import time
from datetime import datetime

from clients import exceptions
from clients.base_client import BaseClient

logger = logging.getLogger(__name__)

TGITSAAS_API_URL = os.environ.get("TGITSAAS_URL", "https://git.code.tencent.com")

TGITSAAS_APIS = {
    "get_oauth": "%s/oauth/token" % TGITSAAS_API_URL,
    "get_projects": "%s/api/v3/projects" % TGITSAAS_API_URL,
    "get_a_project": "%s/api/v3/projects/{project_id}" % TGITSAAS_API_URL,
    "get_branches": "%s/api/v3/projects/{project_id}/repository/branches" % TGITSAAS_API_URL,
    "get_commits": "%s/api/v3/projects/{id}/repository/commits" % TGITSAAS_API_URL,
    "get_a_commit": "%s/api/v3/projects/{id}/repository/commits/{commit}" % TGITSAAS_API_URL,
    "get_files": "%s/api/v3/projects/{project_id}/repository/files" % TGITSAAS_API_URL,
    "get_paths": "%s/api/v3/projects/{id}/repository/tree" % TGITSAAS_API_URL,
}


class TGitSaaSAPIClient(BaseClient):
    """工蜂SaaS版 OAuth API类 --通过 OAuth或者注册token鉴权
    """

    def __init__(self, scm_url, password=None, **kwargs):
        """初始化参数
        :param scm_url: scm库地址
        :param password: token值
        """
        super(TGitSaaSAPIClient, self).__init__(scm_url, **kwargs)
        logger.info("[TGitSaaS] scm_url: %s, branch: %s" % (self._scm_url, self._branch))
        self._token = password
        self._headers = {"OAUTH-TOKEN": self._token} if self._token else {}
        self._projects = {}

    def list_repos(self, name_pattern=None):
        """获取代码库列表
        :params name_pattern:str,名称匹配，用于筛选
        :return: list - 格式如下：
        [
            {
                "id": "代码库ID",
                "name": "代码库名字",
                "full_name": "用户名/代码库名字",
                "public":True/False,
                "html_url":"代码库url",
                "git_url":"代码库url（包含.git）",
            }
        ]
        """
        params = {"per_page": 100, "page": 1}
        if name_pattern:
            params["search"] = name_pattern
        r = self.get(TGITSAAS_APIS["get_projects"], params=params)
        projects = []
        for project_info in self.get_json(r):
            projects.append({
                "id": project_info["id"],
                "name": project_info["name"],
                "name_with_namespace": project_info["name_with_namespace"],
                "public": project_info["public"],
                "html_url": project_info["web_url"],
                "git_url": project_info["http_url_to_repo"],
            })

        return projects

    def get_project_by_namespace(self):
        """通过项目命名空间获取项目信息
        :return: dict
        """
        namespace = "%2F".join(
            self._scm_url.replace(".git", "").replace("http://", "").replace("https://", "").split('/')[1:])
        r = self.get(TGITSAAS_APIS["get_a_project"].format(project_id=namespace), raise_exception=False)
        if self.is_ok(r):
            return self.get_json(r)
        else:
            logger.error("get project with namespace failed, scm_url: %s" % self._scm_url)
            return None

    def get_project_info(self):
        """获取当前项目的信息
        :return: 项目编号
        """
        # 判断是否有项目缓存
        if self._projects.get(self._scm_url):
            return self._projects[self._scm_url]
        # 查询当前用户名下项目
        project_name = self._scm_url.split('/')[-1].replace(".git", "")
        # projects 列表可能超过100个
        params = {"search": project_name, "per_page": 100, "order_by": "path"}
        r = self.get(TGITSAAS_APIS["get_projects"], params=params)
        project_info = None
        for item in self.get_json(r):
            logger.info("current http url: %s, web url: %s" % (item["http_url_to_repo"], item["web_url"]))
            if self.compare_url(self._scm_url, item["http_url_to_repo"], item["web_url"]):
                project_info = item
                break
        if project_info:
            self._projects[self._scm_url] = project_info
            return project_info
        # 通过命名空间查询
        project = self.get_project_by_namespace()
        if project and self.compare_url(self._scm_url, project["http_url_to_repo"], project["web_url"]):
            self._projects[self._scm_url] = project
            return project
        else:
            logger.error("project doesn't exist")
            raise exceptions.NotFoundException("代码库路径可能不存在或无访问权限")

    def get_project_id(self):
        """获取当前项目的id编号
        """
        project_info = self.get_project_info()
        return project_info["id"]

    def list_branches(self):
        """获取分支列表
        :return: list - 格式如下：
        """
        project_id = self.get_project_id()
        params = {"per_page": 100, "page": 1}
        r = self.get(TGITSAAS_APIS["get_branches"].format(project_id=project_id), params=params)
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
        :return: str - 版本号
        """
        project_id = self.get_project_id()
        params = {"ref_name": self._branch}
        r = self.get(TGITSAAS_APIS["get_commits"].format(id=project_id), params=params)
        data = self.get_json(r)
        if len(data) > 0:
            return data[0]["id"]
        else:
            logger.error("get latest revision fail, scm url: %s, error reason: no commit" % self._scm_url)
            raise exceptions.NotFoundException(msg="项目在%s没有提交记录" % self._branch)

    def cat_file(self, path, revision=None):
        """获取指定代码库指定分支的指定文件内容
        :params : path - 文件路径 ; revision - 文件版本
        return : 文件内容
        """
        params = {"file_path": path}
        if revision:
            params["ref"] = revision
        else:
            params["ref"] = self._branch
        project_id = self.get_project_id()
        params = {"ref": revision, "file_path": path.replace("\\", os.sep)}
        r = self.get(TGITSAAS_APIS["get_files"].format(project_id=project_id), params=params, raise_exception=False)
        if self.is_ok(r):
            data = self.get_json(r)
            if data.get("content") is not None:
                content = base64.b64decode(data["content"])
                try:
                    content = content.decode("utf-8")
                except Exception as err:
                    logger.exception("decode content failed: %s" % err)
                    content = content.decode("gbk", "replace")
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
            raise exceptions.ServerException(msg="Git平台服务异常，请稍后再试")

    def get_revision_time(self, revision):
        """ 获取代码库指定版本的创建时间
        :params: project_id - 项目id ; revision - 版本号
        : return: datetime - 提交时间
        """
        logger.info("get revision datetime: %s" % revision)
        project_id = self.get_project_id()
        params = {"ref_name": self._branch}
        r = self.get(TGITSAAS_APIS["get_a_commit"].format(id=project_id, commit=revision), params=params,
                     raise_exception=False)
        if self.is_ok(r):
            data = self.get_json(r)
            committed_date_utc = datetime.strptime(data["committed_date"], "%Y-%m-%dT%H:%M:%S%z")
            committed_date = committed_date_utc.astimezone(tz=None).replace(tzinfo=None)
            committed_timestamp = time.mktime(committed_date.timetuple())
            print("[get_revision_time] convert: %s -> %s -> %s" % (
                committed_date_utc, committed_date, committed_timestamp))
            return committed_timestamp
        elif r.status == 404:
            raise exceptions.NotFoundException(msg="SHA %s could not be resolved" % revision)
        elif 400 <= r.status < 500:
            logger.error("get_revision_time error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="获取版本号时间异常，请稍后再试")
        else:
            logger.error("get_revision_time error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git Code平台服务异常，请稍后再试")

    get_revision_datetime = get_revision_time

    def ls_tree(self, path, revision=None):
        """返回指定路径下的子目录和文件列表
        :param path: 需要查询的列表，如果为空，则列出根目录下的目录和文件
        :param revision: 需要查询的版本，为空时表示最新版本
        :return: list: 包含start_revision和end_revision之间的版本号
        [{
            "name": "filename or directory name",
            "type": "file or dir",
        }]
        """
        logger.info("list path: %s-%s" % (path, revision))
        project_id = self.get_project_id()
        params = {}
        if path is not None:
            params["path"] = path
        if revision is not None:
            params["ref_name"] = revision
        else:
            params["ref_name"] = self._branch
        r = self.get(TGITSAAS_APIS["get_paths"].format(id=project_id), params=params,
                     raise_exception=False)
        if self.is_ok(r):
            data = self.get_json(r)
            paths = []
            for item in data:
                path_info = {"name": item["name"]}
                if item["type"] == "blob":
                    path_info["type"] = "file"
                elif item["type"] in ["commit", "tree"]:
                    path_info["type"] = "dir"
                paths.append(path_info)
            if len(paths) > 0:
                return paths
            else:
                raise exceptions.NotFoundException(msg="Path %s does not exist" % path)
        elif r.status == 404:
            raise exceptions.NotFoundException(msg="SHA %s could not be resolved" % revision)
        elif 400 <= r.status < 500:
            logger.error("list error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.BadRequestException(msg="获取目录列表异常，请稍后再试")
        else:
            logger.error("list error, code: %s, error: %s" % (r.status, self.get_text(r)))
            raise exceptions.ServerException(msg="Git Code平台服务异常，请稍后再试")

    def revision_lt(self, version_start, version_end):
        """ 比较版本大小
        :param version_start:起始版本
        :param version_end:结束版本
        :return 布尔值
            False 表示 version_start>=version_end
            True 表示 version_start<version_end
        """
        version_start_time = self.get_revision_time(version_start)
        version_end_time = self.get_revision_time(version_end)
        if version_start_time >= version_end_time:
            return False
        else:
            return True

    def get_oauth(self, auth_info):
        """OAuth授权
        :param auth_info: dict
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
        r = self.post(TGITSAAS_APIS["get_oauth"], params=data, headers=headers, raise_exception=False)
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
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {"client_id": auth_info["client_id"],
                  "client_secret": auth_info["client_secret"],
                  "grant_type": "refresh_token",
                  "refresh_token": auth_info["refresh_token"],
                  "redirect_uri": auth_info["redirect_uri"]
                  }
        r = self.get(TGITSAAS_APIS["get_oauth"], headers=headers, params=params)
        data = self.get_json(r)

        return {"access_token": data["access_token"],
                "refresh_token": data["refresh_token"]}
