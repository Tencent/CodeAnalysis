# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scm client
"""

from django.conf import settings

from util.cdcrypto import decrypt
from util.scm.base import SCM_PLATFORM_NUM_AS_KEY, ScmErrorHandler, ScmPlatformEnum
from util.scm.errorcatch import ErrorCatcher
from util.scm.git import GitRemoteClient
from util.scm.svn import SvnRemoteClient


def ScmClient(scm_type, scm_url, auth_type=None, username=None, password=None,
              ssh_key=None, ssh_password=None, scm_platform=ScmPlatformEnum.GIT_OA, **kwargs):
    """本办法是工厂方法，故意做成类是一个类来使用。

    :param scm_type: svn, git
    :param scm_url: 源码路径
    :param auth_type: str, 鉴权类型
    :param username: str, 用户名
    :param password: str, 凭证
    :param ssh_key: str, SSH密钥
    :param ssh_password: str，SSH密钥口令
    :param scm_platform: int，代码库管理平台
    """
    if password:
        password = decrypt(password, settings.PASSWORD_KEY)
    if ssh_key:
        ssh_key = decrypt(ssh_key, settings.PASSWORD_KEY)
    if ssh_password:
        ssh_password = decrypt(ssh_password, settings.PASSWORD_KEY)
    if isinstance(scm_platform, str):
        scm_platform_name = scm_platform
    else:
        scm_platform_name = SCM_PLATFORM_NUM_AS_KEY.get(scm_platform, "tgit")
    if scm_type == "svn":
        return ErrorCatcher(SvnRemoteClient(scm_url, username, password, ssh_key, ssh_password),
                            ScmErrorHandler.svn_error_handler)
    elif scm_type == "git":
        if auth_type == "oauth":
            username = "oauth2"
        return ErrorCatcher(GitRemoteClient(scm_url, username, password, ssh_key, ssh_password, scm_platform_name),
                            ScmErrorHandler.git_error_handler)
    else:
        raise Exception("not yet support scm_type: %s" % scm_type)
