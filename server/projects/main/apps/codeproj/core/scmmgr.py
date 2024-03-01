# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - scm core
"""

import logging

from django.conf import settings

from apps.authen.models import ScmAccount, ScmAuth, ScmAuthInfo, ScmSshInfo
from apps.base.models import Origin
from util.cdcrypto import encrypt
from util.exceptions import ScmInfoError
from util.scm import SCM_PLATFORM_NAME_AS_KEY, ScmAccessDeniedError, ScmClient, ScmClientError, ScmNotFoundError, \
    ScmPlatformEnum

logger = logging.getLogger(__name__)


class ScmClientManager(object):

    @classmethod
    def get_scm_client_with_repo(cls, repo, scm_url=None):
        """指定仓库初始化ScmClient客户端
        :param repo: Repository
        :param scm_url: str
        :return: ScmClient
        """
        auth_info = repo.auth_info
        if scm_url:
            target_url = scm_url
        else:
            target_url = repo.get_scm_url_with_auth()
        return ScmClient(repo.scm_type, target_url,
                         auth_type=auth_info.get("auth_type", ScmAuth.ScmAuthTypeEnum.PASSWORD),
                         username=auth_info.get("scm_username"), password=auth_info.get("scm_password"),
                         ssh_key=auth_info.get("scm_ssh_key"), ssh_password=auth_info.get("scm_ssh_password"),
                         scm_platform=auth_info.get("scm_platform"))

    @classmethod
    def get_scm_client_with_project(cls, project, scm_url=None):
        """指定项目初始化ScmClient客户端
        :param project: Project
        :param scm_url: str
        :return: ScmClient
        """
        auth_info = project.auth_info
        if scm_url:
            target_url = scm_url
        else:
            target_url = project.get_scm_url_with_auth()
        return ScmClient(project.scm_type, target_url,
                         auth_type=auth_info.get("auth_type", ScmAuth.ScmAuthTypeEnum.PASSWORD),
                         username=auth_info.get("scm_username"), password=auth_info.get("scm_password"),
                         ssh_key=auth_info.get("scm_ssh_key"), ssh_password=auth_info.get("scm_ssh_password"),
                         scm_platform=auth_info.get("scm_platform"))

    @classmethod
    def get_scm_client_with_toollib(cls, toollib, scm_url=None):
        """指定工具依赖初始化ScmClient客户端
        :param toollib: ToolLib
        :param scm_url: str
        :return: ScmClient
        """
        auth_info = toollib.auth_info
        if scm_url:
            target_url = scm_url
        else:
            target_url = toollib.get_scm_url_with_auth()
        return ScmClient(toollib.scm_type, target_url,
                         auth_type=auth_info.get("auth_type", ScmAuth.ScmAuthTypeEnum.PASSWORD),
                         username=auth_info.get("scm_username"), password=auth_info.get("scm_password"),
                         ssh_key=auth_info.get("scm_ssh_key"), ssh_password=auth_info.get("scm_ssh_password"),
                         scm_platform=auth_info.get("scm_platform"))

    @classmethod
    def get_scm_client(cls, scm_type, scm_url, auth_type=None, username=None,
                       password=None, ssh_key=None, ssh_password=None, **kwargs):
        """初始化ScmClient客户端
        :param scm_type: str，代码库类型
        :param scm_url: str，代码库链接
        :param auth_type: str，授权类型
        :param username: str，用户名
        :param password: str，密码
        :param ssh_key: str，SSH密钥
        :param ssh_password: str，SSH口令
        :return:
        """
        return ScmClient(scm_type, scm_url, auth_type=auth_type,
                         username=username, password=password,
                         ssh_key=ssh_key, ssh_password=ssh_password, **kwargs)

    @classmethod
    def get_scm_client_by_credential(cls, scm_type, scm_url, credential_info, is_encrypt=False):
        """根据credential信息获取scm_client
        :param scm_type: str, scm类型
        :param scm_url: str, scm url
        :param credential_info: dict, 凭证信息
        :param is_encrypt: bool, 凭证关键信息是否加密，默认false
        :return: scm_client
        """
        auth_type = credential_info.get("auth_type")
        if auth_type == ScmAuth.ScmAuthTypeEnum.OAUTH:
            access_token = credential_info.get("access_token")
            if is_encrypt:
                access_token = encrypt(access_token, settings.PASSWORD_KEY)
            scm_client = cls.get_scm_client(scm_type, scm_url, auth_type, password=access_token)
        elif auth_type == ScmAuth.ScmAuthTypeEnum.PASSWORD:
            username = credential_info.get("username")
            password = credential_info.get("password")
            if is_encrypt:
                password = encrypt(password, settings.PASSWORD_KEY)
            scm_client = cls.get_scm_client(scm_type, scm_url, auth_type, username=username, password=password)
        elif auth_type == ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            ssh_private_key = credential_info.get("ssh_private_key")
            password = credential_info.get("password")
            if is_encrypt:
                ssh_private_key = encrypt(ssh_private_key, settings.PASSWORD_KEY)
                password = encrypt(password, settings.PASSWORD_KEY)
            scm_client = cls.get_scm_client(scm_type, scm_url, auth_type, ssh_key=ssh_private_key,
                                            ssh_password=password)
        else:
            raise ScmInfoError(msg={"auth_type": "代码库鉴权类型不符合: %s" % auth_type})
        return scm_client


class ScmAuthManager(object):

    @classmethod
    def create_or_update_auth(cls, auth_key, auth_type, scm_account=None, scm_oauth=None, scm_ssh=None):
        """创建或更新授权信息
        :param auth_key: str, 代码库或项目类型的授权信息Key值
        :param auth_type: str, 授权类型
        :param scm_account: ScmAccount 代码库账号信息
        :param scm_oauth: ScmAuthInfo 代码库OAuth授权信息
        :param scm_ssh: ScmSSHInfo 代码库SSH授权信息
        :return: ScmAuth
        """
        scm_auth, created = ScmAuth.objects.get_or_create(
            auth_key=auth_key,
            defaults={
                "auth_type": auth_type,
                "scm_account": scm_account,
                "scm_oauth": scm_oauth,
                "scm_ssh": scm_ssh,
            }
        )
        if not created:
            scm_auth.auth_type = auth_type
            scm_auth.scm_account = scm_account
            scm_auth.scm_ssh = scm_ssh
            scm_auth.scm_oauth = scm_oauth
            scm_auth.save()
        return scm_auth

    @classmethod
    def create_repository_auth(cls, repository, user, scm_oauth=None, scm_auth_type=None, scm_ssh_info=None,
                               scm_account=None):
        """
        创建代码库授权

        :param repository: Repository, 代码库
        :param user: User，用户
        :param scm_auth_type: str，授权类型
        :prama scm_oauth: ScmAuthInfo 代码库OAuth授权信息
        :param scm_ssh_info: ScmSSHInfo 代码库SSH授权信息
        :param scm_account: ScmAccount 代码库账号信息
        :return:
        """
        auth_key = "%s_%s" % (ScmAuth.KeyEnum.REPO, repository.id)
        logger.debug("create repo scm auth: %s" % auth_key)
        scm_auth = cls.create_or_update_auth(
            auth_key=auth_key, auth_type=scm_auth_type,
            scm_oauth=scm_oauth,
            scm_account=scm_account,
            scm_ssh=scm_ssh_info)
        repository.scm_auth = scm_auth
        repository.save(user=user)

    @classmethod
    def create_project_auth(cls, project, user, scm_auth_type=None, scm_ssh_info=None, scm_account=None):
        """
        创建项目授权

        :param project: Project，项目
        :param user: User，用户
        :param scm_auth_type: str，授权类型
        :param scm_ssh_info: ScmSSHInfo 代码库SSH授权信息
        :param scm_account: ScmAccount 代码库账号信息
        """
        auth_key = "%s_%s" % (ScmAuth.KeyEnum.PROJECT, project.id)
        logger.debug("create project scm auth: %s" % auth_key)
        scm_auth = cls.create_or_update_auth(
            auth_key=auth_key, auth_type=scm_auth_type,
            scm_account=scm_account, scm_ssh=scm_ssh_info)
        project.scm_auth = scm_auth
        project.save(user=user)

    @classmethod
    def create_checktool_auth(cls, checktool, user, scm_auth_type=None,
                              scm_ssh_info=None, scm_account=None, scm_oauth=None):
        """
        创建工具授权

        :param checktool: CheckTool，工具
        :param user: User，用户
        :param scm_auth_type: str，授权类型
        :param scm_ssh_info: ScmSSHInfo 代码库SSH授权信息
        :param scm_account: ScmAccount 代码库账号信息
        :param scm_oauth: ScmAuthInfo Oauth授权信息
        """
        auth_key = "%s_%s" % (ScmAuth.KeyEnum.TOOL, checktool.id)
        logger.debug("create checktool scm auth: %s" % auth_key)
        # 兼容逻辑
        if scm_auth_type == ScmAuth.ScmAuthTypeEnum.OAUTH and not scm_oauth:
            scm_oauth = cls.get_scm_auth(user)
        scm_auth = cls.create_or_update_auth(
            auth_key=auth_key, auth_type=scm_auth_type,
            scm_account=scm_account, scm_ssh=scm_ssh_info,
            scm_oauth=scm_oauth)
        checktool.scm_auth = scm_auth
        checktool.save(user=user)

    @classmethod
    def create_toollib_auth(cls, toollib, user, scm_auth_type=None,
                            scm_ssh_info=None, scm_account=None, scm_oauth=None):
        """
        创建工具依赖授权

        :param toollib: ToolLib, 工具依赖
        :param user: User，用户
        :param scm_auth_type: str，授权类型
        :param scm_ssh_info: ScmSSHInfo 代码库SSH授权信息
        :param scm_account: ScmAccount 代码库账号信息
        """
        auth_key = "%s_%s" % (ScmAuth.KeyEnum.TOOLLIB, toollib.id)
        logger.debug("create toollib scm auth: %s" % auth_key)
        # 兼容逻辑
        if scm_auth_type == ScmAuth.ScmAuthTypeEnum.OAUTH and not scm_oauth:
            scm_oauth = cls.get_scm_auth(user)
        scm_auth = cls.create_or_update_auth(
            auth_key=auth_key, auth_type=scm_auth_type,
            scm_account=scm_account, scm_ssh=scm_ssh_info,
            scm_oauth=scm_oauth)
        toollib.scm_auth = scm_auth
        toollib.save(user=user)

    @classmethod
    def get_origin_with_name(cls, name):
        """通过名称获取渠道
        :param name: str，渠道名称
        :return: Origin
        """
        origin, _ = Origin.objects.get_or_create(name=name)
        return origin

    @classmethod
    def create_or_update_scm_account(cls, user, scm_username, scm_password, auth_origin=settings.DEFAULT_ORIGIN_ID, **kwargs):
        """创建或更新用户名密码授权信息

        :param user: User, 授权用户
        :param scm_username: str，用户名称
        :param scm_password: str，用户密码
        :param auth_origin: str，授权来源，默认为Codedog
        :return:
        """
        auth_origin = cls.get_origin_with_name(name=auth_origin)
        scm_account, created = ScmAccount.objects.get_or_create(
            user=user, scm_username=scm_username, auth_origin=auth_origin,
            defaults={
                "scm_password": encrypt(scm_password, settings.PASSWORD_KEY),
            })
        logger.info("%s user:%s account info with %s" % ("create" if created else "update", user, auth_origin))
        if not created:
            scm_account.scm_password = encrypt(scm_password, settings.PASSWORD_KEY)
            scm_account.save()
        return scm_account

    @classmethod
    def get_scm_accounts(cls, user):
        """获取指定用户的授权信息
        :param user: User，授权用户
        :return: QuerySet ScmAccount
        """
        return ScmAccount.objects.filter(user=user)

    @classmethod
    def get_scm_account_with_id(cls, user, account_id):
        """获取指定用户指定编号的授权信息
        :param user: User，授权用户
        :param account_id: int，授权编号
        :return: ScmAccount
        """
        return cls.get_scm_accounts(user=user).filter(id=account_id).first()

    @classmethod
    def create_or_update_scm_ssh(cls, user, credential_id, credential_name, ssh_private_key, password,
                                 auth_origin=settings.DEFAULT_ORIGIN_ID):
        """创建SSH信息
        :param user: User
        :param credential_id: str，凭证ID
        :param credential_name: str，凭证名称
        :param ssh_private_key: str，SSH私钥
        :param password: str，私钥口令
        :param auth_origin: str, 授权来源，默认为Codedog
        :return: ScmSSH
        """

        auth_origin, _ = Origin.objects.get_or_create(name=auth_origin)
        scm_ssh_info, created = ScmSshInfo.objects.get_or_create(
            user=user,
            indentity=credential_id,
            auth_origin=auth_origin,
            defaults={
                "name": credential_name,
                "ssh_private_key": encrypt(ssh_private_key, settings.PASSWORD_KEY),
                "password": encrypt(password, settings.PASSWORD_KEY),
            })
        logger.info("%s user:%s sshtoken info with %s" % ("create" if created else "update", user, auth_origin))
        if not created:
            scm_ssh_info.name = credential_name
            scm_ssh_info.ssh_private_key = encrypt(ssh_private_key, settings.PASSWORD_KEY)
            scm_ssh_info.password = encrypt(password, settings.PASSWORD_KEY)
            scm_ssh_info.save()
        return scm_ssh_info

    @classmethod
    def create_or_update_scm_auth(cls, user, access_token, refresh_token, auth_origin=settings.DEFAULT_ORIGIN_ID, **kwargs):
        """创建OAuth授权信息
        :param user: User，授权用户
        :param access_token: str，OAuth授权token
        :param refresh_token: str，OAuth更新Token
        :param auth_origin: str，授权来源，默认为Codedog
        :return: ScmAuthInfo
        """
        auth_origin = cls.get_origin_with_name(name=auth_origin)
        # 获取Token过期时间(仅针对部分scm平台)
        expires_in, created_at = kwargs.get("expires_in", None), kwargs.get("created_at", None)
        expires_at = expires_in + created_at if expires_in and created_at else None
        scm_auth_info, created = ScmAuthInfo.objects.get_or_create(
            user=user,
            auth_origin=auth_origin,
            scm_platform=kwargs.get("scm_platform", ScmPlatformEnum.GIT_OA),
            defaults={
                "gitoa_access_token": encrypt(access_token, settings.PASSWORD_KEY),
                "gitoa_refresh_token": encrypt(refresh_token, settings.PASSWORD_KEY),
                "scm_platform_desc": kwargs.get("scm_platform_desc"),
                "expires_at": expires_at
            }
        )
        logger.info("%s user:%s oauth info with %s" % ("create" if created else "update", user, auth_origin))
        if not created:
            scm_auth_info.gitoa_access_token = encrypt(access_token, settings.PASSWORD_KEY)
            scm_auth_info.gitoa_refresh_token = encrypt(refresh_token, settings.PASSWORD_KEY)
            if expires_at:
                scm_auth_info.expires_at = expires_at
            scm_auth_info.save()
        return scm_auth_info

    @classmethod
    def get_scm_auth(cls, user, scm_platform=None, auth_origin=settings.DEFAULT_ORIGIN_ID):
        """获取指定渠道的授权信息
        :param user: User，授权用户
        :param scm_platform: str, scm授权平台
        :param auth_origin: str，授权来源，默认为Codedog
        :return: ScmAuthInfo
        """
        if isinstance(scm_platform, str):
            scm_platform = SCM_PLATFORM_NAME_AS_KEY.get(scm_platform, ScmPlatformEnum.GIT_OA)
        if not scm_platform:
            scm_platform = ScmPlatformEnum.GIT_OA
        auth_origin = cls.get_origin_with_name(name=auth_origin)
        scm_auth_info = ScmAuthInfo.objects.filter(
            user=user, auth_origin=auth_origin, scm_platform=scm_platform).first()
        return scm_auth_info

    @classmethod
    def get_scm_sshs(cls, user):
        """获取指定用户的授权信息
        :param user: User，授权用户
        :return: QuerySet ScmSshInfo
        """
        return ScmSshInfo.objects.filter(user=user)

    @classmethod
    def get_scm_sshinfo_with_id(cls, user, sshinfo_id):
        """获取指定用户指定编号的授权信息
        :param user: User，授权用户
        :param sshinfo_id: int，凭证编号
        :return: ScmSshInfo
        """
        return cls.get_scm_sshs(user=user).filter(id=sshinfo_id).first()

    @classmethod
    def get_scm_authinfos(cls, user):
        """获取指定用户的Oauth授权信息
        :param user: User，授权用户
        :return: QuerySet ScmAuthInfo
        """
        return ScmAuthInfo.objects.filter(user=user)

    @classmethod
    def get_scm_authinfo_with_id(cls, user, authinfo_id):
        """获取指定用户指定编号的授权信息
        :param user: User，授权用户
        :param authinfo_id: int，凭证编号
        :return: ScmAuthInfo
        """
        return cls.get_scm_authinfos(user=user).filter(id=authinfo_id).first()

    @classmethod
    def check_scm_url_credential(cls, scm_type, scm_url, credential_info, branch=None, is_encrypt=False):
        """校验scm_url凭证
        :param scm_type: str, scm类型
        :param scm_url: str, scm地址
        :param credential_info: dict, 凭证信息
        :param branch: str, 分支名称，存在则校验分支是否存在
        :param is_encrypt: bool, 是否对关键字段加密，默认不加密
        """
        if branch:
            scm_url = "%s#%s" % (scm_url, branch) if scm_type == 'git' else "%s/%s" % (scm_url, branch)
        scm_client = ScmClientManager.get_scm_client_by_credential(scm_type, scm_url, credential_info, is_encrypt)
        try:
            if branch:
                scm_client.branch_check()
            else:
                scm_client.auth_check()
        except ScmNotFoundError:
            raise ScmInfoError(msg={"cd_error": "代码库分支不存在" if branch else "代码库地址不存在"})
        except ScmAccessDeniedError:
            raise ScmInfoError(msg={"cd_error": "代码库帐号无权限"})
        except ScmClientError:
            raise ScmInfoError(msg={"cd_error": "代码库密码错误"})
        except Exception as e:
            logger.exception("auth check exception: %s" % e)
            raise ScmInfoError(msg={"cd_error": "代码库及帐号不匹配"})
