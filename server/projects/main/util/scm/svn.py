# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
SVN源码库的操作功能
"""

import logging
import re
from datetime import datetime

from django.conf import settings

from util.scm.base import IScmClient, ScmUrlFormatter
from util.scm.rpcproxy import CustomServerProxy

logger = logging.getLogger(__name__)


class SvnRemoteClient(IScmClient):

    def __init__(self, scm_url, username=None, password=None, ssh_key=None, ssh_password=None):
        """
        初始化函数

        :param scm_url: scm库地址
        :param username: 域帐号
        :param password: 密码
        :param ssh_key: 私钥
        :param ssh_password: 私钥口令
        """

        self._repository = None
        self._branch = None
        self._scm_url = scm_url

        if ssh_key:
            self._scm_info = {
                'scm_type': 'ssh+svn',
                'scm_url': self.get_ssh_url(),
                'ssh_key': ssh_key,
                'ssh_password': ssh_password
            }
        else:
            self._scm_info = {
                'scm_type': 'svn',
                'scm_url': scm_url.strip(),
                'username': username,
                'password': password
            }
        self._svn_proxy = CustomServerProxy(settings.SCMPROXY, timeout=int(settings.SCMPROXY_TIMEOUT))

    @property
    def latest_revision(self):
        """最新版本号
        """
        return self._svn_proxy.latest_revision(self._scm_info)

    def get_repository(self):
        """代码库地址
        """
        return ScmUrlFormatter.get_svn_url(self._scm_url)

    def get_branch(self):
        """分支名称
        """
        index = self._scm_url.find("_proj")
        return self._scm_url[index + 6:] if index > 0 else 'trunk'

    def get_http_url(self):
        """ssh格式的url
        """
        if self._scm_url.startswith("svn+ssh"):
            http_url = re.sub("^svn+ssh", "http", self._scm_url)
        elif not self._scm_url.startswith("http"):
            http_url = "http://%s" % self._scm_url
        else:
            http_url = self._scm_url
        return http_url

    def get_ssh_url(self):
        """ssh格式的url
        """
        if self._scm_url.startswith("http"):
            ssh_url = re.sub("^http[s]", "svn+ssh", self._scm_url)
        elif not self._scm_url.startswith("svn+ssh"):
            ssh_url = "svn+ssh://%s" % self._scm_url
        else:
            ssh_url = self._scm_url
        return ssh_url

    def auth_check(self):
        """SCM鉴权校验

        :return: boolean, True表示鉴权信息正常，False表示鉴权信息异常
        :raise: ScmError错误
        """
        return self._svn_proxy.auth_check(self._scm_info)

    def branch_check(self):
        """SCM分支校验

        :return: boolean, True表示分支存在，False表示分支不存在
        :raise: ScmError错误
        """
        return self._svn_proxy.branch_check(self._scm_info)

    def url_equal(self, url):
        """检查url链接是否相同

        :param url: str, 代码库地址
        :return boolean: True表示相同，False表示不相同
        """
        if not url:
            return False
        scm_url = self._scm_url.replace("https://", "http://").strip().rstrip("/")
        url = url.replace("https://", "http://").strip().rstrip("/")
        return scm_url == url

    def cat(self, path, revision):
        """获取文件内容

        :param path: 文件路径
        :param revision: 文件版本
        :type revision: str
        :return: 文件内容
        """
        return self._svn_proxy.cat_file(self._scm_info, path, revision)

    def get_revision_datetime(self, revision):
        """获取指定版本的创建时间
        :param revision: 文件版本
        :return: datetime对象
        """
        revision_timestamp = self._svn_proxy.get_revision_time(self._scm_info, revision)
        if revision_timestamp:
            return datetime.fromtimestamp(revision_timestamp)
        return None
