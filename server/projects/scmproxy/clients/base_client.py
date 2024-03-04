# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""基础客户端接口
"""
import json
import logging

from clients import exceptions
from clients.http_client import HttpClient

logger = logging.getLogger(__name__)


class BaseClient(object):
    """基础客户端类
    """

    def __init__(self, scm_url, **kwargs):
        """获取代码库链接
        :param scm_url: str, 代码库链接
        """
        self._client = HttpClient()
        self._headers = {}
        items = scm_url.split("#", 1)
        if len(items) == 2:
            self._scm_url, self._branch = items
        else:
            self._scm_url = scm_url
            self._branch = "master"

    def get_headers(self, headers=None):
        """获取请求头部
        """
        default_headers = {
            'User-Agent': "TCA HTTP Client",
            'Accept-Encoding': ', '.join(('gzip', 'deflate')),
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
        if not self._headers and not headers:
            return default_headers
        if self._headers:
            default_headers.update(self._headers)
        if headers:
            default_headers.update(headers)
        return default_headers

    def _request(self, method, url, **kwargs):
        logger.info("request url: %s" % url)
        params = kwargs.pop("params", None)
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", None)
        raise_exception = kwargs.pop("raise_exception", True)
        response = self._client.session(
            method, url, params=params, headers=self.get_headers(headers),
            data=data, json_data=kwargs)
        if raise_exception:
            self.raise_for_status(response)
        return response

    def get(self, url, **kwargs):
        """get请求
        """
        kwargs.setdefault("allow_redirects", True)
        r = self._request("get", url, **kwargs)
        return r

    def post(self, url, **kwargs):
        """post请求
        """
        r = self._request("post", url, **kwargs)
        return r

    def raise_for_status(self, response):
        """在raise_for_status函数的基础上增加content字段输出
        :param response: requests.Response - 响应结果
        :return: None
        :raise Excaption
        """
        content = response.data.decode("utf-8")
        if response.status == 401:
            logger.error("帐号密码错误, 错误消息: %s" % content)
            raise exceptions.AuthorizationException(msg="帐号密码错误")
        elif response.status == 403:
            logger.error("项目可能不存在或没有项目访问权限, 错误消息: %s" % content)
            raise exceptions.ForbiddenException(msg="项目可能不存在或没有项目访问权限")
        elif response.status == 404:
            logger.error("项目可能不存在或没有项目访问权限, 错误消息: %s" % content)
            raise exceptions.NotFoundException(msg="项目可能不存在或没有项目访问权限")
        elif 400 <= response.status < 500:
            http_error_msg = "%s 请求错误，请稍后再试, 错误消息: %s" % (response.status, content)
            logger.error(http_error_msg)
            raise exceptions.BadRequestException(msg="请求错误，请稍后再试")
        elif 500 <= response.status < 600:
            http_error_msg = "%s Server Error: %s" % (response.status, content)
            logger.error(http_error_msg)
            raise exceptions.ServerException(msg="Git Code平台服务异常，请稍后再试")

    def is_ok(self, response):
        """判断响应是否正常
        """
        try:
            self.raise_for_status(response)
        except exceptions.HTTPBaseException:
            return False
        return True

    def get_text(self, response):
        """从响应结果中提取数据
        """
        try:
            return response.data.decode("utf-8")
        except UnicodeDecodeError:
            return response.data.decode("iso-8859-1")

    def get_json(self, response):
        """从响应结果中提取数据并转换为json格式
        """
        return json.loads(self.get_text(response))

    def compare_url(self, scm_url, http_url, web_url=None):
        """将代码库地址、web地址与scm地址比较
        """
        scm_url = scm_url.replace("https://", "http://").replace(".git", "")
        http_url = http_url.replace("https://", "http://").replace(".git", "") if http_url else ""
        web_url = web_url.replace("https://", "http://") if web_url else ""
        if scm_url == http_url or scm_url == web_url:
            return True
        else:
            return False

    def latest_revision(self):
        """最新版本号
        :return: str - 最新版本号
        """
        raise NotImplemented

    def start_revision(self):
        """最初版本号
        :return: str - 最初版本号
        """
        raise NotImplemented

    def cat(self, scm_info, path, revision):
        """获取文件内容 -- 支持 Git OA接口

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param path: 文件路径
        :param revision: 文件版本
        :type revision: str
        :return: str - 文件内容
        """
        raise NotImplemented

    def get_revision_datetime(self, scm_info, revision):
        """取指定版本的创建时间 -- 支持 Git OA接口

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param revision: 文件版本
        :return: datetime对象
        """
        raise NotImplemented

    def list(self, path, revision):
        """返回指定路径下的子目录和文件列表

        :param path: 需要查询的列表，如果为空，则列出根目录下的目录和文件
        :param revision: 需要查询的版本，为空时表示最新版本
        :return: list: 指定路径下的目录文件
        [{
            "name": "filename or directory name",
            "type": "file or dir",
        }]
        """
        raise NotImplemented

    def log(self, scm_info, start_revision=None, end_revision=None):
        """获取指定版本区间的提交日志

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param start_revision: 起始版本
        :param end_revision: 结束版本
        :return: datetime对象
            author - string - the name of the author who committed the revision
            date - float time - the date of the commit
            message - string - the text of the log message for the commit
            revision - pysvn.Revision - the revision of the commit
        """
        raise NotImplemented

    def revision_lt(self, start_revision, end_revision):
        """比较版本大小 -- 支持 Git OA接口

        :param start_revision: 起始版本
        :param end_revision: 结束版本
        :return: Boolean值
            False 表示 start_revision >= end_revision
            True 表示 start_revision < end_revision
        """
        raise NotImplemented

    def revisions_range(self, scm_info, start_revision, end_revision):
        """返回指定版本号之间（包括指定的版本号）的版本列表

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param start_revision: 起始版本，为空表示初始版本
        :param end_revision: 结束版本，为空表示最新版本
        :return: list: 包含start_revision和end_revision之间的版本号
        """
        raise NotImplemented

    def list_repos(self, name_pattern=None):
        """获取代码库列表

        :param name_pattern: 名称
        :return: list - 格式如下：
            [
                {
                    "id": "项目编号",
                    "name": "项目名称",
                    "namespace": "项目group路径",
                    "public": True表示开源，False表示不开源,
                    "repo_url": "项目代码库URL（包含.git)",
                    "web_url": "项目代码库URL",
                    "default_branch": "项目默认分支"
                }
            ]
        """
        raise NotImplemented

    def list_branches(self):
        """获取分支列表
        :return: list - 格式如下:
            [
                "name": "分支名称",
                "current_commit_id": "分支版本",
                "current_commit_message": "分支提交信息简略版",
                "current_commit_author": "分支提交人",
                "current_commit_date": "分支提交时间"
            ]
        """
        raise NotImplemented

    def git_oauth(self, scm_info, auth_info):
        """Git OAuth授权
        :param scm_info: dict
        :param auth_info: dict - 格式如下：
            {
                "client_id": "xxx",
                "client_secret": "xxx",
                "authorization_code": "xxx"
            }
        :return: dict - 格式如下：
            {
                "access_token": xx,
                "refresh_token": xx
            }
        """
        raise NotImplemented
