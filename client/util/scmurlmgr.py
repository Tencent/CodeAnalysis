# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scm url操作工具类
"""

import logging

logger = logging.getLogger(__name__)


class BaseScmUrlMgr(object):
    @staticmethod
    def format_url(scm_url):
        """
        格式化scm url路径,去掉前后空格,去掉目录最后的斜杠,将https://统一为http://
        :param scm_url: scm url
        :return:
        """
        scm_url = scm_url.strip()
        scm_url = scm_url.rstrip('/')
        scm_url = scm_url.replace("https://", "http://")
        return scm_url

    @staticmethod
    def check_ssh_scm_type(scm_url):
        """
        检查ssh鉴权方式url的scm类型
        :param scm_url:
        :return: 返回git或svn,如果url不是ssh鉴权类型,返回None
        """
        if scm_url.startswith("git@"):
            return "git"
        if scm_url.startswith("svn+ssh://"):
            return "svn"
        return None

    @staticmethod
    def get_last_dir_name_from_url(scm_url):
        """从url中提取最后部分的地址名称"""
        dirname = scm_url.strip()
        dirname = dirname.rstrip('/')
        dirname = dirname.split('/')[-1]
        if dirname.endswith(".git"):
            dirname = dirname.replace(".git", "")
        if dirname.endswith(".zip"):
            dirname = dirname.replace(".zip", "")
        if dirname.endswith(".7z"):
            dirname = dirname.replace(".7z", "")
        # 如果url包含分支，即 .git#BranchName 的格式，目录名删除.git
        if ".git#" in dirname:
            dirname = dirname.replace(".git#", "#")
        return dirname


class GitUrlMgr(object):
    @staticmethod
    def split_url(branch_url):
        """
        将分支url拆分为git url和分支
        :param branch_url: 带branch信息的git url
        :return:
        """
        items = branch_url.split("#", 1)
        if len(items) == 2:
            url, branch = items
        else:  # 不带分支名,默认为master
            url = branch_url
            branch = "master"
        return url, branch

    def url_equal(self, remote_full_url, local_full_url):
        """
        比较 git 服务端的代码库链接和分支与本地代码库链接和分支是否相同
        :param remote_full_url: str, 服务端 scm url,包含分支信息(如果不包含,默认为master)
        :param local_full_url: str, 本地代码库 scm url,包含分支信息(如果不包含,默认为master)
        :return boolean, True表示相同，False表示不同
        """
        remote_full_url = BaseScmUrlMgr.format_url(remote_full_url)
        local_full_url = BaseScmUrlMgr.format_url(local_full_url)

        # 都转换成http格式再比较
        if remote_full_url.startswith("git@"):
            remote_full_url = self.ssh_to_http(remote_full_url)
        if local_full_url.startswith("git@"):
            local_full_url = self.ssh_to_http(local_full_url)

        remote_url, remote_branch = self.split_url(remote_full_url)
        local_url, local_branch = self.split_url(local_full_url)

        if remote_url.endswith(".git"):
            remote_url = remote_url.rsplit(".git", 1)[0]
        if local_url.endswith(".git"):
            local_url = local_url.rsplit(".git", 1)[0]

        return remote_url == local_url and remote_branch == local_branch

    def ssh_to_http(self, url):
        """
        :param url:
        :return:http格式的url;如果原来不是ssh格式的url,直接返回原url
        """
        if url.startswith("git@"):
            items = url.split("git@", 1)
            new_url = items[1]
            items = new_url.split(":", 1)
            new_url = "http://%s/%s" % (items[0], items[1])
            return new_url
        else:
            return url

    def http_to_ssh(self, url):
        """
        将http格式的url转换成ssh格式
        :param url:
        :return:
        """
        if url.startswith("http://"):
            items = url.split("http://", 1)
            # 增加前缀
            new_url = "git@%s" % items[1]
            # 替换第一个斜杠为冒号
            pos = new_url.find('/')
            return "%s:%s" % (new_url[:pos], new_url[pos+1:])
        else:
            return url


class SvnUrlMgr(object):
    def url_equal(self, remote_url, local_url):
        """
        比较两个svn url是否相同
        :param remote_url: str, 服务端 scm url
        :param local_url: str, 本地代码库 scm url
        :return: return boolean, True表示相同，False表示不同
        """
        remote_url = BaseScmUrlMgr.format_url(remote_url)
        local_url  = BaseScmUrlMgr.format_url(local_url)

        if remote_url.startswith("svn+ssh://"):
            remote_url = self.ssh_to_http(remote_url)
        if local_url.startswith("svn+ssh://"):
            local_url = self.ssh_to_http(local_url)

        return remote_url == local_url

    def ssh_to_http(self, url):
        """
        将ssh格式的url转换成http格式
        :param url:
        :return:http格式的url;如果原来不是ssh格式的url,直接返回原url
        """
        if url.startswith("svn+ssh://"):
            items = url.split("svn+ssh://", 1)
            new_url = items[1]
            if '@' in new_url:
                items = new_url.split("@", 1)
                new_url = "http://%s" % items[1]
            else:
                new_url = "http://%s" % new_url
            return new_url
        else:
            return url

    def http_to_ssh(self, url):
        """
        将http格式的url转换成ssh格式
        :param url:
        :return:
        """
        if url.startswith("http://"):
            items = url.split("http://", 1)
            return "svn+ssh://%s" % items[1]
        else:
            return url


class ScmUrlMgr(object):
    def __init__(self, scm_type):
        self._client = None
        if scm_type == "svn":
            self._client = SvnUrlMgr()
        elif scm_type == "git":
            self._client = GitUrlMgr()
        elif scm_type == "tgit":
            self._client = GitUrlMgr()
        else:
            raise Exception("Not supported scm type: %s" % scm_type)

    def get_scm_url_mgr(self):
        return self._client
