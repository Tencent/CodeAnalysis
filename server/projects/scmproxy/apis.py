# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
# 
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""ScmProxy API 列表
"""

import logging
import os
import re
import shutil
import stat
import tempfile
from functools import wraps

import settings
from clients.gitee.client import GiteeAPIClient
from clients.github.client import GitHubAPIClient
from clients.gitlab.client import GitLabAPIClient
from clients.tgitsaas.client import TGitSaaSAPIClient
from lib.cmdscm import ScmClient
from utils import get_source_dir

logger = logging.getLogger(__file__)


class ScmInit(object):
    """scm初始化装饰器，用于在目标方法调用前添加scm_client参数
    """
    SCM_CLIENT_DICT = {
        "tgitsaas": TGitSaaSAPIClient,
        "github": GitHubAPIClient,
        "gitee": GiteeAPIClient,
        "gitlab": GitLabAPIClient
    }

    def __init__(self, checkout=True):
        """构造函数
        :param checkout: boolean，是否需要checkout代码
        """
        self._checkout = checkout

    def __get_source_dir(self, scm_url):
        """获取源码目录路径
        :return: str，源码路径
        """
        return os.path.join(settings.SOURCE_DIR, get_source_dir(scm_url))

    def __write_ssh_key_to_local(self, ssh_key):
        """将ssh key写到本地临时文件，并设置600权限
        :param ssh_key: str
        :return: str, 本地文件路径
        """
        temp_ssh_file = tempfile.NamedTemporaryFile(prefix="proxy", delete=False, dir=settings.TEMP_DIR)
        temp_ssh_file.write(ssh_key.encode())
        temp_ssh_file.write(b"\n")
        temp_ssh_file.close()
        temp_ssh_path = temp_ssh_file.name
        os.chmod(temp_ssh_path, stat.S_IWUSR | stat.S_IRUSR)
        return temp_ssh_path

    def __checkout_sourdir(self, scm_client, source_dir):
        """checkout
        :param source_dir: str，指定路径
        """
        if not self._checkout:
            logger.info("no need to checkout")
            return
        logger.info("start to checkout or update: %s" % source_dir)
        if os.path.exists(source_dir):
            try:
                scm_client.update(enable_submodules=False, enable_lfs=False, enable_reset=False)
            except Exception as err:
                logger.exception("update source dir %s failed: %s" % (source_dir, err))
                shutil.rmtree(source_dir, ignore_errors=True)
                logger.exception("remove old source dir and checkout out again: %s" % source_dir)
                scm_client.checkout(enable_submodules=False, enable_lfs=False)
        else:
            scm_client.checkout(enable_submodules=False, enable_lfs=False)
        logger.info("end to checkout or update: %s" % source_dir)

    def __get_client_by_scm_type(self, scm_type, scm_url, method_name, scm_platform=None, **kwargs):
        """通过scm类型获取相应客户端
        :param scm_type: str, scm类型
        :param scm_url: str，scm链接
        :param method_name: str, 方法名
        :param kwargs: dict
        :return: ScmClient
        """
        source_dir = self.__get_source_dir(scm_url)
        if scm_platform in self.SCM_CLIENT_DICT and method_name in dir(self.SCM_CLIENT_DICT[scm_platform]):
            ScmClientClass = self.SCM_CLIENT_DICT[scm_platform]
            scm_client = ScmClientClass(scm_url, **kwargs)
        elif scm_type in self.SCM_CLIENT_DICT and method_name in dir(self.SCM_CLIENT_DICT[scm_type]):
            ScmClientClass = self.SCM_CLIENT_DICT[scm_type]
            scm_client = ScmClientClass(scm_url, **kwargs)
        elif scm_type.startswith("ssh"):
            scm_type = scm_type.split('+')[-1]
            ssh_key = kwargs.get("ssh_key") or kwargs.get("password", "")
            ssh_key_path = self.__write_ssh_key_to_local(ssh_key)
            scm_client = ScmClient(scm_type, scm_url, source_dir, ssh_file=ssh_key_path)
            self.__checkout_sourdir(scm_client, source_dir)
        else:
            scm_client = ScmClient(scm_type, scm_url, source_dir, kwargs.get("username"),
                                   kwargs.get("password"))
            self.__checkout_sourdir(scm_client, source_dir)
        return scm_client

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_args = list(args)
            # 方法默认第一个是scm_info参数
            scm_info = args[1]
            logger.info("method: %s, scm_url: %s, scm_type: %s, username: %s" % (
                func.__name__, scm_info["scm_url"], scm_info["scm_type"], scm_info.get("username")))
            scm_client = self.__get_client_by_scm_type(scm_info["scm_type"], scm_info["scm_url"], func.__name__,
                                                       scm_platform=scm_info.get("scm_platform"),
                                                       username=scm_info.get("username"),
                                                       password=scm_info.get("password"),
                                                       ssh_key=scm_info.get("ssh_key"),
                                                       coding_project_id=scm_info.get("coding_project_id"))
            scm_info['scm_client'] = scm_client
            func_args[1] = scm_info
            return func(*func_args, **kwargs)

        return wrapper


class ScmAPI(object):

    @ScmInit()
    def latest_revision(self, scm_info):
        """最新版本号

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :return: str - 最新版本号
        """
        scm_client = scm_info['scm_client']
        return scm_client.latest_revision

    @ScmInit()
    def start_revision(self, scm_info):
        """最初版本号

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :return: str - 最初版本号
        """
        scm_client = scm_info['scm_client']
        return scm_client.start_revision

    @ScmInit(checkout=False)
    def auth_check(self, scm_info):
        """鉴权校验
        :param scm_info: scm信息
        :return: boolean值
            False 表示 正确
            True 表示 错误
        """
        scm_client = scm_info['scm_client']
        scm_client.check_auth(raise_exception=True)
        return True

    @ScmInit(checkout=False)
    def branch_check(self, scm_info):
        """鉴权校验
        :param scm_info: scm信息
        :return: boolean值
            False 表示 正确
            True 表示 错误
        """
        scm_client = scm_info['scm_client']
        scm_client.info_by_remote()
        return True

    @ScmInit()
    def cat_file(self, scm_info, path, revision):
        """获取文件内容
        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param path: 文件路径
        :param revision: 文件版本
        :type revision: str
        :return: str - 文件内容
        """
        scm_client = scm_info['scm_client']
        file_content = scm_client.cat_file(path, revision)
        return re.sub("[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", file_content)

    @ScmInit()
    def get_revision_time(self, scm_info, revision):
        """取指定版本的创建时间 -- 支持 Git OA接口

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param revision: 文件版本
        :return: int，时间戳
        """
        scm_client = scm_info['scm_client']
        return scm_client.get_revision_time(revision)

    @ScmInit()
    def revision_lt(self, scm_info, start_revision, end_revision):
        """比较版本大小 -- 支持 Git OA接口

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param start_revision: 起始版本
        :param end_revision: 结束版本
        :return: Boolean值
            False 表示 start_revision >= end_revision
            True 表示 start_revision < end_revision
        """
        logger.info("revision_lt, start_revision: %s, end_revision: %s", start_revision, end_revision)
        scm_client = scm_info['scm_client']
        return scm_client.revision_lt(start_revision, end_revision)

    @ScmInit()
    def revisions_range(self, scm_info, start_revision, end_revision):
        """返回指定版本号之间（包括指定的版本号）的版本列表

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
        :param start_revision: 起始版本，为空表示初始版本
        :param end_revision: 结束版本，为空表示最新版本
        :return: list: 包含start_revision和end_revision之间的版本号
        """
        logger.info("revision_range, start_revision: %s, end_revision: %s", start_revision, end_revision)
        scm_client = scm_info['scm_client']
        return scm_client.revision_range(start_revision=start_revision, end_revision=end_revision)

    def git_oauth(self, scm_info, auth_info):
        """Git OAuth授权

        :param scm_info: scm信息，包括scm_client, scm_url, username, password
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
        logger.info("get oauth, scm_url: %s" % scm_info.get("scm_url"))
        ScmAPIClient = ScmInit.SCM_CLIENT_DICT.get(scm_info.get("scm_platform"))
        return ScmAPIClient(scm_info.get("scm_url", "")).get_oauth(auth_info)

    def get_token_through_refresh_token(self, scm_info, auth_info):
        """根据Refresh Token刷新Token

        :param scm_info: scm信息，包括scm_client, scm_url, username, password, scm_platform
        :param auth_info: dict - 格式如下：
            {
                "refresh_token": "xxx",
            }
        :return: dict - 格式如下：
            {
                "access_token": "xx",
                "refresh_token": "xx",
                "expires_in": xx,
                "created_at": xx
            }
        """
        logger.info("refresh token from %s scm platform" % scm_info.get("scm_platform"))
        ScmAPIClient = ScmInit.SCM_CLIENT_DICT.get(scm_info.get("scm_platform"))
        return ScmAPIClient(scm_info.get("scm_url", "")).get_token_through_refresh_token(auth_info)


def register_apis(server):
    scm_api = ScmAPI()
    server.register_function(scm_api.cat_file, "cat_file")
    server.register_function(scm_api.auth_check, "auth_check")
    server.register_function(scm_api.branch_check, "branch_check")
    server.register_function(scm_api.revision_lt, "revision_lt")
    server.register_function(scm_api.start_revision, "start_revision")
    server.register_function(scm_api.latest_revision, "latest_revision")
    server.register_function(scm_api.revisions_range, "revisions_range")
    server.register_function(scm_api.get_revision_time, "get_revision_time")
    server.register_function(scm_api.git_oauth, "git_oauth")
    server.register_function(scm_api.get_token_through_refresh_token, "get_token_through_refresh_token")


if __name__ == '__main__':
    pass
