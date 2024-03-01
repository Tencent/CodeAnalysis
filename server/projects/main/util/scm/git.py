# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Git源码库的操作功能
"""

import logging
import re
from datetime import datetime

from django.conf import settings

from util.scm.base import IScmClient, ScmUrlFormatter
from util.scm.rpcproxy import CustomServerProxy

logger = logging.getLogger(__name__)


class GitRemoteClient(IScmClient):
    """Git 远程客户端 - 通过 GitProxy 获取项目信息"""

    def __init__(self, scm_url, username=None, password=None, ssh_key=None, ssh_password=None, scm_platform_name=None):
        """
        初始化函数

        :param scm_url: scm库地址
        :param username: 域帐号
        :param password: 密码
        :param ssh_key: 私钥
        :param ssh_password: 私钥口令
        """
        self._scm_url = scm_url.strip()
        if ssh_key:
            self._scm_info = {
                "scm_type": "ssh+git",
                "scm_url": self.get_ssh_url(),
                "ssh_key": ssh_key,
                "ssh_password": ssh_password
            }
        elif username == "oauth2":
            self._scm_info = {
                "scm_type": "git-oauth",
                "scm_platform": scm_platform_name,
                "scm_url": self.get_http_url(),
                "username": username,
                "password": password,
            }
        else:
            self._scm_info = {
                "scm_type": "git",
                "scm_url": self.get_http_url(),
                "username": username,
                "password": password
            }
        self._git_proxy = CustomServerProxy(settings.SCMPROXY, timeout=int(settings.SCMPROXY_TIMEOUT))
        self._repository = None
        self._branch = None

    @property
    def latest_revision(self):
        """最新版本号
        """
        return self._git_proxy.latest_revision(self._scm_info)

    @property
    def start_revision(self):
        """最初版本号
        """
        return self._git_proxy.start_revision(self._scm_info)

    def get_repository(self):
        """代码库地址
        """
        scm_url = self._scm_info["scm_url"].rstrip("/")
        return ScmUrlFormatter.get_git_url(scm_url)

    def get_branch(self):
        """分支名称
        """
        index = self._scm_info["scm_url"].find("#")
        return self._scm_info["scm_url"][index + 1:] if index > 0 else "master"

    def get_ssh_url(self):
        """获取SSH代码库地址
        """
        if self._scm_url.startswith("http"):
            ssh_url = re.sub("^http[s]?://", "git@", self._scm_url).replace("/", ":", 1)
        elif self._scm_url.startswith("ssh://"):
            ssh_url = self._scm_url
        elif not self._scm_url.startswith("git@"):
            ssh_url = "git@%s" % self._scm_url.replace("/", ":", 1)
        else:
            ssh_url = self._scm_url
        return ssh_url

    def get_http_url(self):
        """获取HTTP代码库地址
        """
        if self._scm_url.startswith("git@"):
            http_url = re.sub("^git@", "http://", self._scm_url.replace(":", "/", 1))
        elif self._scm_url.startswith("ssh://git@"):
            http_url = re.sub(r"(:\d+/)", "/", self._scm_url.replace("ssh://git@", "http://"))
        elif self._scm_url.startswith("ssh://"):
            http_url = re.sub(r"(:\d+/)", "/", self._scm_url.replace("ssh://", "http://"))
        elif not self._scm_url.startswith("http"):
            http_url = "http://%s" % self._scm_url.replace(":", "/", 1)
        else:
            http_url = self._scm_url
        return http_url

    def auth_check(self):
        """SCM鉴权校验

        :return: boolean, True表示鉴权信息正常，False表示鉴权信息异常
        :raise: ScmError错误
        """
        return self._git_proxy.auth_check(self._scm_info)

    def branch_check(self):
        """SCM分支校验

        :return: boolean, True表示分支存在，False表示分支不存在
        :raise: ScmError错误
        """
        return self._git_proxy.branch_check(self._scm_info)

    def url_equal(self, url):
        """检查url链接是否相同

        :param url: str, 代码库地址
        :return boolean: True表示相同，False表示不相同
        """
        if not url:
            return False
        scm_url = self.get_http_url()

        # 获取检查的url链接和分支
        url_items = url.strip().split("#", 1)
        if len(url_items) == 2:
            url, branch = url_items
        else:
            url = url
            branch = "master"
        http_url = ScmUrlFormatter.get_git_url(url)

        # 获取代码库的链接和分支
        scm_items = scm_url.split("#", 1)
        if len(scm_items) == 2:
            scm_url, scm_branch = scm_items
        else:
            scm_url = scm_url
            scm_branch = "master"
        scm_url = ScmUrlFormatter.get_git_url(scm_url)

        if url.startswith(
                ("git@", "ssh://git@")) and url == self.get_ssh_url() and scm_branch.lower() == branch.lower():
            return True

        return scm_url == http_url and scm_branch.lower() == branch.lower()

    def cat(self, path, revision):
        """获取文件内容

        :param path: 文件路径
        :param revision: 文件版本
        :type revision: str
        :return: 文件内容
        """
        content = self._git_proxy.cat_file(self._scm_info, path, revision)
        return content

    def get_revision_datetime(self, revision):
        """获取指定版本的创建时间

        :param revision: 文件版本
        :return: datetime对象
        """
        revision_timestamp = self._git_proxy.get_revision_time(self._scm_info, revision)
        if revision_timestamp:
            return datetime.fromtimestamp(revision_timestamp)
        return None

    def get_oauth(self, auth_info):
        """Git OAuth授权
        """
        return self._git_proxy.git_oauth(self._scm_info, auth_info)

    def get_token_through_refresh_token(self, auth_info):
        """刷新OAuth token

        :param: dict, 包含refresh_token等信息
        :return: boolean, True表示token刷新成功，False表示刷新异常
        """
        return self._git_proxy.get_token_through_refresh_token(self._scm_info, auth_info)
