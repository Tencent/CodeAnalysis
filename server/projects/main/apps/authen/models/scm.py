# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""Scm模型
"""
# 原生 import
import logging

# 第三方 import
from django.db import models
from django.contrib.auth.models import User
from util.scm import ScmPlatformEnum, SCM_PLATFORM_CHOICES, SCM_PLATFORM_NUM_AS_KEY

# 项目内 import
from apps.base.models import Origin


logger = logging.getLogger(__name__)


class ScmAccount(models.Model):
    """
    代码库账号信息，支持用户配置多个账号
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scm_username = models.CharField(max_length=128, verbose_name="代码库帐号")
    scm_password = models.CharField(max_length=256, verbose_name="代码库密码")
    auth_origin = models.ForeignKey(Origin, help_text="创建渠道", on_delete=models.SET_NULL, blank=True, null=True)
    scm_platform = models.IntegerField(help_text="凭证所属平台", choices=SCM_PLATFORM_CHOICES,
                                       default=ScmPlatformEnum.GIT_OA)
    scm_platform_desc = models.CharField(max_length=32, verbose_name="补充其他所属平台", blank=True, null=True)

    def __str__(self):
        return "Account-%s-%s-%s-[%s]%s" % (self.user, self.scm_username, self.auth_origin, self.scm_platform,
                                            SCM_PLATFORM_NUM_AS_KEY.get(self.scm_platform))

    @property
    def credential_info(self):
        return {
            "auth_type": ScmAuth.ScmAuthTypeEnum.PASSWORD,
            "creator": self.user,
            "username": self.scm_username,
            "password": self.scm_password,
            "scm_platform": self.scm_platform,
        }

    class Meta:
        unique_together = ("user", "scm_username", "auth_origin", "scm_platform")


class ScmSshInfo(models.Model):
    """
    代码库ssh key凭据信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    indentity = models.CharField(max_length=128, verbose_name="凭据id")
    name = models.CharField(max_length=128, verbose_name="名称")
    git_token = models.CharField(max_length=128, verbose_name="Git 私人令牌", blank=True, null=True)  # 加密
    ssh_private_key = models.TextField(verbose_name="ssh private key")
    password = models.TextField(verbose_name="代码库密码", blank=True, null=True)  # 加密
    auth_origin = models.ForeignKey(Origin, help_text="创建渠道", on_delete=models.SET_NULL, blank=True, null=True)
    scm_platform = models.IntegerField(help_text="凭证所属平台", choices=SCM_PLATFORM_CHOICES,
                                       default=ScmPlatformEnum.GIT_OA)
    scm_platform_desc = models.CharField(max_length=32, verbose_name="补充所属平台", blank=True, null=True)

    class Meta:
        unique_together = ("user", "indentity", "auth_origin", "scm_platform")

    @property
    def credential_info(self):
        return {
            "auth_type": ScmAuth.ScmAuthTypeEnum.SSHTOKEN,
            "creator": self.user,
            "credential_name": self.name,
            "credential_id": self.id,
            "ssh_private_key": self.ssh_private_key,
            "password": self.password,
            "token": self.git_token,
            "scm_platform": self.scm_platform
        }

    def __str__(self):
        return "SSH-%s-%s-%s-[%s]%s" % (self.user, self.indentity, self.auth_origin,
                                        self.scm_platform, SCM_PLATFORM_NUM_AS_KEY.get(self.scm_platform))


class ScmBaseAuth(models.Model):
    """Scm授权信息
    """

    class KeyEnum(object):
        REPO = "REPO_"
        PROJECT = "RPOJ_"
        TOOL = "CHECKTOOL_"
        TOOLLIB = "TOOLLIB_"

    class ScmAuthTypeEnum(object):
        PASSWORD = "password"
        SSHTOKEN = "ssh_token"

    SCM_AUTH_TYPE_CHOICES = (
        (ScmAuthTypeEnum.PASSWORD, "账号密码"),
        (ScmAuthTypeEnum.SSHTOKEN, "SSH + Token授权"),
    )

    auth_key = models.CharField(max_length=56, help_text="关联指定代码库或指定项目", unique=True)
    auth_type = models.CharField(max_length=56, choices=SCM_AUTH_TYPE_CHOICES, help_text="授权方式")
    scm_account = models.ForeignKey(ScmAccount, on_delete=models.SET_NULL, help_text="关联的用户名和密码", null=True,
                                    blank=True)
    scm_ssh = models.ForeignKey(ScmSshInfo, on_delete=models.SET_NULL,
                                help_text="关联的SSH信息", null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    modified_time = models.DateTimeField(auto_now=True, help_text="修改时间")

    @property
    def scm_username(self):
        if self.auth_type == self.ScmAuthTypeEnum.PASSWORD:
            return self.scm_account.scm_username if self.scm_account else None
        else:
            return self.scm_ssh.user.username if self.scm_ssh else None

    @property
    def scm_password(self):
        if self.auth_type == self.ScmAuthTypeEnum.PASSWORD:
            return self.scm_account.scm_password if self.scm_account else None
        else:
            return self.scm_ssh.ssh_private_key if self.scm_ssh else None

    @property
    def auth_info(self):
        if self.auth_type == self.ScmAuthTypeEnum.PASSWORD:
            if self.scm_account:
                username = self.scm_account.scm_username
                password = self.scm_account.scm_password
            else:
                username, password, scm_platform = None, None, None
            return {"auth_type": self.auth_type, "scm_username": username, "scm_password": password}
        elif self.auth_type == self.ScmAuthTypeEnum.SSHTOKEN:
            if self.scm_ssh:
                ssh_key = self.scm_ssh.ssh_private_key
                ssh_password = self.scm_ssh.password
                username = self.scm_ssh.user.username if self.scm_ssh.user else None
                name = self.scm_ssh.name
            else:
                username, ssh_key, ssh_password, name = None, None, None, None
            return {"auth_type": self.auth_type, "name": name, "scm_username": username,
                    "scm_ssh_key": ssh_key, "scm_ssh_password": ssh_password}
        else:
            raise Exception("auth type not supported: %s" % self.auth_type)

    def __str__(self):
        return "%s-%s" % (self.auth_key, self.auth_type)


ScmAuth = ScmBaseAuth
