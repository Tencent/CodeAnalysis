# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - tool models
"""
import logging

# 第三方
from django.db import models
from django.contrib.auth.models import User

# 项目内
from apps.scan_conf.models.base import Language, ScanApp, Process
from apps.authen.models import ScmAuth
from apps.base.basemodel import CDBaseModel
from util.scm import ScmClient

logger = logging.getLogger(__name__)


class CheckTool(CDBaseModel):
    """工具表
    """

    class StatusEnum(object):
        RUNNING = 0
        SUSPENDING = 1
        DISABLE = 2
        TRIAL = 3

    STATUS_CHOICES = (
        (StatusEnum.RUNNING, '正常运营'),
        (StatusEnum.SUSPENDING, '暂停使用'),
        (StatusEnum.DISABLE, '已下架'),
        (StatusEnum.TRIAL, '体验运营')
    )

    class ScopeEnum(object):
        PUBLIC = 0
        PRIVATE = 1
        MAINTAIN = 2
        CUSTOM = 3

    SCOPE_CHOICES = (
        (ScopeEnum.PUBLIC, '公开工具'),
        (ScopeEnum.PRIVATE, '私有工具'),
        (ScopeEnum.MAINTAIN, '协同工具'),
        (ScopeEnum.CUSTOM, '自定义工具')
    )

    class AccessRoleEnum(object):
        OTHER = 0  # 其他访问角色
        CO_ADMIN = 1  # 协作成员角色
        ADMIN = 2  # 管理员角色

    class OpEnum(object):
        DELRULE = 0  # 移除规则操作
        DISABLETOOL = 1  # 下架工具操作
        PRIVATETOOL = 2  # 私有化工具操作

    class ScmTypeEnum(object):
        CC = 'cc'
        GIT = 'git'
        SVN = 'svn'

    SCM_TYPE_CHOICES = (
        (ScmTypeEnum.CC, 'ClearCase'),
        (ScmTypeEnum.GIT, 'Git'),
        (ScmTypeEnum.SVN, 'SVN')
    )

    name = models.CharField(max_length=64, unique=True, help_text='工具名称')
    virtual_name = models.CharField(max_length=64, null=True, blank=True, help_text='工具虚拟名称')
    display_name = models.CharField(max_length=64, null=True, blank=True, help_text='工具展示名称')
    show_display_name = models.BooleanField(default=False, help_text="是否使用工具展示名称")
    scan_app = models.ForeignKey(ScanApp, null=True, blank=True, on_delete=models.CASCADE, help_text='应用')
    license = models.CharField(max_length=64, null=True, blank=True, help_text='License')
    description = models.CharField(max_length=256, help_text='工具描述')
    languages = models.ManyToManyField(Language, related_name="checktool", help_text="支持的语言")
    owners = models.ManyToManyField(User, related_name="own_checktools", help_text="负责人")
    open_maintain = models.BooleanField(default=False, help_text="是否所有人可协同")
    co_owners = models.ManyToManyField(User, related_name="co_checktools", help_text="协同人")
    open_user = models.BooleanField(default=False, help_text="是否所有人可用")
    users = models.ManyToManyField(User, related_name="usable_checktools", help_text="可使用者")
    open_saas = models.BooleanField(default=False, help_text="是否公有云可用")
    status = models.IntegerField(choices=STATUS_CHOICES, default=StatusEnum.RUNNING, help_text='工具状态')
    task_processes = models.ManyToManyField(Process, through='ToolProcessRelation', help_text='任务子进程')
    scm_url = models.CharField(max_length=128, null=True, blank=True, help_text='工具仓库地址')
    run_cmd = models.CharField(max_length=128, blank=True, null=True, help_text='工具执行命令，工作目录为git工具库根目录')
    envs = models.TextField(null=True, blank=True, help_text='环境变量')
    build_flag = models.BooleanField(default=False, help_text="是否是编译型工具")
    scm_auth = models.ForeignKey(ScmAuth, on_delete=models.SET_NULL, blank=True, null=True, help_text='工具授权凭证')
    scm_type = models.CharField(max_length=16, choices=SCM_TYPE_CHOICES, default=ScmTypeEnum.GIT, help_text='代码库类型')
    tool_key = models.CharField(max_length=64, null=True, help_text="工具key值，org_'<org_id>'")
    image_url = models.CharField(max_length=200, null=True, blank=True, help_text="镜像地址")

    @property
    def auth_info(self):
        if self.scm_auth:
            logger.info("using checktool scm_auth")
            return self.scm_auth.auth_info
        else:
            return {}

    def get_all_users(self):
        """获取工具全部成员
        """
        return (self.owners.all() | self.co_owners.all() | self.users.all()).distinct()

    def get_all_usernames(self):
        """获取工具全部成员名称
        """
        allusers = self.get_all_users()
        return [u.username for u in allusers]

    def is_public(self):
        """判断工具是否为公开工具
        """
        return self.open_user or self.open_maintain

    def get_access_role(self, user):
        """获取访问成员角色
        """
        if user:
            if user.is_superuser or self.owners.filter(username=user.username).exists():
                return self.AccessRoleEnum.ADMIN
            elif self.co_owners.filter(username=user.username).exists():
                return self.AccessRoleEnum.CO_ADMIN
        return self.AccessRoleEnum.OTHER

    def get_show_name(self, user=None):
        """获取展示名称
        :param user: User, 访问用户
        """
        if self.show_display_name:
            return self.display_name
        if user and (user.is_superuser or self.get_all_users().filter(username=user.username).exists()):
            # 超管或有使用权限的用户都可以查看到展示名称
            return self.display_name
        return self.virtual_name or self.id

    def __str__(self):
        return "%s" % self.display_name


class ToolProcessRelation(models.Model):
    """工具进程映射表
    """
    checktool = models.ForeignKey(CheckTool, on_delete=models.CASCADE, help_text="工具")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, help_text="任务子进程")
    # 一个工具子进程的优先级，0为最高，为空时按照创建的先后顺序来
    priority = models.IntegerField(null=True, blank=True, help_text="优先级")

    class Meta:
        ordering = ['priority']
        unique_together = ("checktool", "process")


class ToolLib(CDBaseModel):
    """工具依赖表
    """

    class ScmTypeEnum(object):
        GIT = "git"
        SVN = "svn"
        LINK = "link"  # 链接下载

    SCM_TYPE_CHOICES = (
        (ScmTypeEnum.GIT, "Git"),
        (ScmTypeEnum.SVN, "SVN"),
        (ScmTypeEnum.LINK, "Link"),
    )

    class LibTypeEnum(object):
        PRIVATE = 'private'
        PUBLIC = 'public'

    LIB_TYPE_CHOICES = (
        (LibTypeEnum.PRIVATE, "私有依赖"),
        (LibTypeEnum.PUBLIC, "公共依赖"),
    )

    class LibEnvEnum(object):
        LINUX = 'linux'
        MAC = 'mac'
        WINDOWS = 'windows'
        LINUX_ARM64 = 'linux_arm64'

    LIB_ENV_CHOICES = (
        (LibEnvEnum.LINUX, "linux"),
        (LibEnvEnum.MAC, "mac"),
        (LibEnvEnum.WINDOWS, "windows"),
        (LibEnvEnum.LINUX_ARM64, "linux_arm64"),
    )

    name = models.SlugField(max_length=64, help_text="依赖名称")
    description = models.CharField(max_length=128, null=True, blank=True, help_text="依赖描述")
    scm_url = models.CharField(max_length=128, help_text="依赖地址")
    scm_type = models.CharField(max_length=16, choices=SCM_TYPE_CHOICES, help_text="依赖类型")
    scm_auth = models.ForeignKey(ScmAuth, on_delete=models.SET_NULL, null=True, help_text="鉴权凭证")
    envs = models.JSONField(null=True, blank=True, help_text="环境变量")
    lib_type = models.CharField(max_length=16, choices=LIB_TYPE_CHOICES,
                                default=LibTypeEnum.PRIVATE, help_text="依赖类型")
    lib_os = models.CharField(max_length=128, null=True, blank=True, help_text="适用系统，按;分隔")
    lib_key = models.CharField(max_length=64, help_text="lib key值，default，org_'<org_id>'")
    extra_data = models.JSONField(null=True, blank=True, help_text="额外字段，如headers")

    @property
    def os(self):
        if self.lib_os:
            return [v.strip() for v in self.lib_os.split(';')]
        return []

    @property
    def auth_info(self):
        if self.scm_auth:
            logger.info("using toollib scm_auth")
            return self.scm_auth.auth_info
        else:
            return {}

    def get_format_url(self, scm_url, git_suffix=True, https_prefix=False, **kwargs):
        """获取格式化的链接
        """
        if git_suffix:
            if not scm_url.endswith(".git") and self.scm_type == self.ScmTypeEnum.GIT:
                scm_url = "%s.git" % scm_url
        if https_prefix:
            scm_url = scm_url.replace("http://", "https://")
        return scm_url

    def get_scm_url_with_auth(self, **kwargs):
        """根据凭证获取代码库信息
        """
        if self.scm_type == self.ScmTypeEnum.LINK:
            return self.scm_url
        # 格式化scm_url
        scm_client = ScmClient(self.scm_type, self.scm_url, "password")
        scm_url = scm_client.get_repository()
        if self.scm_auth and self.scm_auth.auth_type == ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            ssh_scm_url = ScmClient(self.scm_type, scm_url, "password").get_ssh_url()
            if ssh_scm_url:
                return ssh_scm_url
        return self.get_format_url(scm_url, **kwargs)

    def __str__(self):
        return "%s-%s" % (self.name, self.lib_key)

    class Meta:
        unique_together = ("name", "lib_key")


class ToolLibScheme(CDBaseModel):
    """工具依赖方案表
    """
    checktool = models.ForeignKey(CheckTool, related_name="libscheme", on_delete=models.CASCADE, help_text="工具")
    condition = models.CharField(max_length=128, null=True, blank=True, help_text="条件")
    tool_libs = models.ManyToManyField(ToolLib, through="ToolLibMap", related_name="libscheme",
                                       blank=True, help_text="工具依赖")
    scheme_os = models.CharField(max_length=128, null=True, blank=True, help_text="适用系统")
    default_flag = models.BooleanField(default=False, help_text="默认依赖")

    @property
    def os(self):
        if self.scheme_os:
            return [v.strip() for v in self.scheme_os.split(';')]
        return []


class ToolLibMap(models.Model):
    """工具依赖映射表
    """
    libscheme = models.ForeignKey(ToolLibScheme, related_name="toollibmap", on_delete=models.CASCADE,
                                  help_text="工具依赖方案")
    toollib = models.ForeignKey(ToolLib, related_name="toollibmap", on_delete=models.CASCADE, help_text="依赖")
    pos = models.BigIntegerField(help_text="序号")

    def __str__(self):
        return "toollibmap-%s-%s" % (self.libscheme_id, self.toollib_id)

    class Meta:
        unique_together = ("libscheme", "toollib")
        ordering = ["pos"]
