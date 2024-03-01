# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base models
"""

# 原生 import
import hashlib
import json
import logging

# 第三方 import
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import IntegrityError, models
from guardian.shortcuts import assign_perm

# 项目内 import
from apps.authen.models import Organization, ScmAuth
from apps.base.basemodel import BasePerm, CDBaseModel
from apps.nodemgr.models import ExecTag
from apps.scan_conf.models import Language
from util.webclients import AnalyseClient

logger = logging.getLogger(__name__)


# ****************************
# * 项目基础信息配置
# ****************************

class ActiveProjectTeamManager(models.Manager):
    """活跃项目筛选器
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=ProjectTeam.StatusEnum.ACTIVE)


class ProjectTeam(CDBaseModel, BasePerm):
    """项目团队
    """

    class PermissionNameEnum:
        CHANGE_TEAM_PERM = "change_projectteam"
        VIEW_TEAM_PERM = "view_projectteam"

    class Meta:
        unique_together = (
            ("organization", "name"),
        )

    class StatusEnum:
        ACTIVE = 1
        DISACTIVE = 2

    STATUS_CHOICES = (
        (StatusEnum.ACTIVE, "活跃"),
        (StatusEnum.DISACTIVE, "禁用"),
    )

    # SlugField会校验，r"^[-a-zA-Z0-9_]+\Z"，只能包含字母，数字，下划线或者中划线
    name = models.SlugField(max_length=64, help_text="项目组名称")
    display_name = models.CharField(max_length=128, help_text="展示名称")
    description = models.TextField(help_text="项目描述信息", null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, help_text="所属组织", null=True, blank=True)
    status = models.IntegerField(help_text="项目团队状态", default=StatusEnum.ACTIVE, choices=STATUS_CHOICES)

    active_pts = ActiveProjectTeamManager()

    def _get_group(self, perm):
        permission_choices = dict(self.PERMISSION_CHOICES)
        group_name = "_".join(("team", str(self.id), permission_choices[perm]))
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            if perm == self.PermissionEnum.ADMIN:
                assign_perm(self.PermissionNameEnum.CHANGE_TEAM_PERM, group, self)
            assign_perm(self.PermissionNameEnum.VIEW_TEAM_PERM, group, self)
        return group

    def __unicode__(self):
        return "%s" % self.name

    def __str__(self):
        return self.__unicode__()


class Label(CDBaseModel):
    """标签
    """

    class Meta:
        unique_together = (
            ("project_team", "name"),
        )

    name = models.CharField(max_length=64, help_text="标签")
    parent_label = models.ForeignKey("self", help_text="上级标签", on_delete=models.SET_NULL, null=True, blank=True)
    index = models.IntegerField(help_text="同级标签序号", default=0)
    description = models.CharField(max_length=256, help_text="标签描述信息", null=True, blank=True)
    project_team = models.ForeignKey(ProjectTeam, on_delete=models.SET_NULL, help_text="所属项目团队",
                                     null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.name

    def __str__(self):
        return self.__unicode__()


class BaseRepository(CDBaseModel):
    """代码库信息
    """

    class PermissionNameEnum:
        CHANGE_REPO_PERM = "change_baserepository"
        VIEW_REPO_PERM = "view_baserepository"

    class Meta:
        unique_together = ("scm_url", "url_key")

    class PermissionEnum(object):
        ADMIN = 0
        USER = 1

    PERMISSION_CHOICES = (
        (PermissionEnum.ADMIN, "admin"),
        (PermissionEnum.USER, "user")
    )

    class ScmTypeEnum(object):
        GIT = "git"
        SVN = "svn"

    SCM_TYPE_CHOICES = (
        (ScmTypeEnum.GIT, "Git"),
        (ScmTypeEnum.SVN, "SVN")
    )

    class CreatedFromEnum(object):
        API = "api"
        WEB = "codedog_web"

    class StateEnum(object):
        ACTIVE = 1
        DISACTIVE = 2

    STATE_CHOICES = (
        (StateEnum.ACTIVE, "活跃"),
        (StateEnum.DISACTIVE, "失活"),
    )

    name = models.CharField(max_length=128, verbose_name="产品名称", help_text="所属产品名称", null=True)
    scm_url = models.CharField(max_length=200, verbose_name="代码库地址")
    ssh_url = models.CharField(max_length=256, verbose_name="代码库SSH格式地址", null=True, blank=True)
    scm_type = models.CharField(max_length=16, choices=SCM_TYPE_CHOICES, verbose_name="代码库类型")
    scm_auth = models.ForeignKey(ScmAuth, on_delete=models.SET_NULL, verbose_name="代码库授权", blank=True, null=True)
    created_from = models.CharField(max_length=32, verbose_name="创建渠道", default=CreatedFromEnum.WEB)
    subscribers = models.ManyToManyField(User, verbose_name="关注人")
    state = models.IntegerField(verbose_name="代码库状态", default=StateEnum.ACTIVE, choices=STATE_CHOICES)
    url_key = models.CharField(max_length=128, verbose_name="代码库key值", null=True, blank=True)
    labels = models.ManyToManyField(Label, help_text="绑定标签", related_name="label_repo", blank=True)
    project_team = models.ForeignKey(ProjectTeam, help_text="所属项目组", on_delete=models.SET_NULL, blank=True, null=True)
    organization = models.ForeignKey(Organization, help_text="所属团队", on_delete=models.SET_NULL, blank=True, null=True)

    def get_format_url(self, git_suffix=True, https_prefix=False, **kwargs):
        """获取格式化的链接
        """
        scm_url = self.scm_url

        if git_suffix:
            if not scm_url.endswith(".git") and self.scm_type == self.ScmTypeEnum.GIT:
                scm_url = "%s.git" % scm_url
        if https_prefix or (hasattr(settings, "HTTPS_CLONE_FLAG") and settings.HTTPS_CLONE_FLAG is True):
            scm_url = scm_url.replace("http://", "https://")
        return scm_url

    def get_scm_url_with_auth(self, **kwargs):
        """根据凭证获取代码库信息
        """
        if self.scm_auth and self.scm_auth.auth_type == ScmAuth.ScmAuthTypeEnum.SSHTOKEN and self.ssh_url:
            return self.ssh_url
        else:
            return self.get_format_url(**kwargs)

    def _get_group(self, perm):
        permission_choices = dict(self.PERMISSION_CHOICES)
        group_name = "_".join(("repo", str(self.id), permission_choices[perm]))
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            if perm == self.PermissionEnum.ADMIN:
                assign_perm(self.PermissionNameEnum.CHANGE_REPO_PERM, group, self)
            assign_perm(self.PermissionNameEnum.VIEW_REPO_PERM, group, self)
        return group

    def get_members(self, perm):
        group = self._get_group(perm)
        users = group.user_set.all()
        return users

    def assign_perm(self, username, perm):
        group = self._get_group(perm)
        user, _ = User.objects.get_or_create(username=username)
        try:
            user.groups.add(group)
        except IntegrityError:
            pass

    def assign_members_perm(self, users, perm):
        group = self._get_group(perm)
        for username in users:
            user, _ = User.objects.get_or_create(username=username)
            try:
                user.groups.add(group)
            except IntegrityError:
                pass

    def remove_perm(self, username, perm):
        group = self._get_group(perm)
        user, _ = User.objects.get_or_create(username=username)
        try:
            user.groups.remove(group)
        except IntegrityError:
            pass

    def get_projects(self):
        return self.baseproject_set.all()

    def get_scanschemes(self):
        return self.basescanscheme_set.all()

    @property
    def scm_username(self):
        if self.scm_auth:
            return self.scm_auth.scm_username

    @property
    def scm_password(self):
        if self.scm_auth:
            return self.scm_auth.scm_password

    @property
    def auth_info(self):
        if self.scm_auth:
            return self.scm_auth.auth_info
        else:
            return {}

    def __str__(self):
        return "%s-%s" % (self.id, self.name)


class BaseScanScheme(CDBaseModel):
    """扫描方案
    """

    class CreatedFromEnum(object):
        API = "api"
        WEB = "web"

    class StatusEnum(object):
        ACTIVE = 1
        DISACTIVE = 2

    STATUS_CHOICES = (
        (StatusEnum.ACTIVE, "活跃"),
        (StatusEnum.DISACTIVE, "废弃"),
    )

    class SchemeTypeEnum(object):
        """扫描方案类型
        """
        SYSTEM = 1
        CUSTOM = 2

    SCHEMETYPE_CHOICES = (
        (SchemeTypeEnum.SYSTEM, "系统创建"),
        (SchemeTypeEnum.CUSTOM, "用户创建"),
    )

    class SchemeKey(object):
        """方案Key值
        """
        PUBLIC = "public"
        ORG_KEY = "org"
        PERSONAL_KEY = "personal"

    name = models.CharField(max_length=128, help_text="扫描方案名称")
    repo = models.ForeignKey(BaseRepository, help_text="关联代码库", on_delete=models.SET_NULL, null=True)
    refer_scheme = models.ForeignKey("self", on_delete=models.SET_NULL, verbose_name="参照扫描方案",
                                     blank=True, null=True)
    refer_template_ids = models.JSONField(verbose_name="关联模板编号列表", null=True, blank=True)
    description = models.TextField(help_text="详细描述", null=True, blank=True)
    tag = models.ForeignKey(ExecTag, on_delete=models.SET_NULL, verbose_name="执行环境", null=True, blank=True)
    languages = models.ManyToManyField(Language, verbose_name="包含语言", help_text="勾选需要扫描的语言")
    default_flag = models.BooleanField(help_text="默认扫描方案标识，一个项目只能有一个默认方案", default=False)
    created_from = models.CharField(max_length=32, help_text="创建渠道", default=CreatedFromEnum.WEB)
    issue_global_ignore = models.BooleanField(default=True, verbose_name="是否开启问题全局忽略，默认为True（开启）")
    status = models.IntegerField(choices=STATUS_CHOICES, default=StatusEnum.ACTIVE, help_text="扫描方案状态")
    scheme_key = models.CharField(max_length=64, verbose_name="扫描方案key值", null=True, blank=True, db_index=True)
    scheme_type = models.IntegerField(help_text="方案类型", default=SchemeTypeEnum.CUSTOM, null=True, blank=True)
    ignore_merged_issue = models.BooleanField(default=False, verbose_name="过滤其他分支合入的问题")
    ignore_branch_issue = models.CharField(max_length=128, help_text="过滤参考分支引入的问题", null=True, blank=True)
    ignore_submodule_clone = models.BooleanField(default=False, verbose_name="是否忽略子模块clone，默认为False（不忽略）")
    ignore_submodule_issue = models.BooleanField(default=True, verbose_name="是否忽略子模块问题，默认为True（忽略）")
    lfs_flag = models.BooleanField(verbose_name="是否开启拉取代码时默认拉取lfs文件，默认为True（开启）", default=True,
                                   null=True, blank=True)

    class Meta:
        unique_together = ("repo", "name")

    def __str__(self):
        return "%s-%s-%s" % (self.id, self.repo_id, self.name) if self.repo_id else "%s-%s" % (self.id, self.name)

    def get_checkprofile(self):
        """获取规则集
        """
        return self.lintbasesetting.checkprofile

    def get_envs(self):
        """获取配置的环境变量
        """
        return self.lintbasesetting.envs.strip() if self.lintbasesetting.envs else ""

    def get_tag_name(self):
        """获取配置的标签名称
        """
        return self.tag.name if self.tag else None

    def get_lang_names(self):
        """获取语言名称列表
        """
        return [lang.name for lang in self.languages.all()]

    def get_projects(self):
        return self.baseproject_set.all()

    @classmethod
    def user_objects(cls, user):
        """规则包筛选
        """
        if user.is_superuser:
            return cls.objects.all()
        else:
            return cls.objects.exclude(scheme_type=cls.SchemeTypeEnum.SYSTEM)

    @classmethod
    def get_basic_conf_template(cls):
        """获取基础配置模板
        """
        return {}

    @classmethod
    def merge_basic_conf_template(cls, basic_conf_1, basic_conf_2):
        """合并基础配置模板
        """
        for item in basic_conf_1:
            if basic_conf_2.pop(item, False) is True:
                basic_conf_1[item] = True
        basic_conf_1.update(**basic_conf_2)
        return basic_conf_1

    @classmethod
    def get_org_scheme_key(cls, org_sid):
        """获取方案模板团队scheme_key值
        """
        return "%s_%s" % (cls.SchemeKey.ORG_KEY, org_sid)


class BaseProject(CDBaseModel):
    """扫描项目
    """

    class Meta:
        index_together = (
            ("repo", "scan_scheme", "branch")
        )

    class StatusEnum(object):
        ACTIVE = 1
        DISACTIVE = 2
        ARCHIVING = 3
        ARCHIVED_WITHOUT_CLEAN = 4
        ARCHIVED = 5

    STATUS_CHOICES = (
        (StatusEnum.ACTIVE, "活跃"),
        (StatusEnum.DISACTIVE, "失活"),
        (StatusEnum.ARCHIVING, "归档中"),
        (StatusEnum.ARCHIVED_WITHOUT_CLEAN, "已归档未清理"),
        (StatusEnum.ARCHIVED, "已归档"),
    )

    class CreatedFromEnum(object):
        API = "api"
        WEB = "codedog_web"
        CODING = "coding"

    branch = models.CharField(max_length=200, help_text="关联分支")
    repo = models.ForeignKey(BaseRepository, help_text="关联代码库", on_delete=models.SET_NULL, null=True)
    scan_scheme = models.ForeignKey(BaseScanScheme, help_text="关联扫描方案", on_delete=models.SET_NULL, null=True)
    scan_path = models.CharField(max_length=512, help_text="扫描路径", null=True, blank=True)
    project_key = models.CharField(max_length=64, help_text="项目Key值", null=True, blank=True, unique=True)
    refer_project = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, help_text="参照项目")
    status = models.IntegerField(default=StatusEnum.ACTIVE, choices=STATUS_CHOICES, verbose_name="项目状态")
    created_from = models.CharField(max_length=32, help_text="创建渠道", default=CreatedFromEnum.WEB)
    scm_initial_revision = models.CharField(max_length=64, help_text="起始版本号", blank=True, null=True)
    scm_auth = models.ForeignKey(ScmAuth, on_delete=models.SET_NULL, verbose_name="项目授权", blank=True, null=True)
    remark = models.TextField(help_text="备注信息", blank=True, null=True)

    @classmethod
    def gen_project_key(cls, repo_id, scheme_id, branch, scan_path):
        if not scan_path:
            scan_path = "/"
        key_string = "{repo_id}#{scheme_id}#{branch}#{path}".format(
            repo_id=repo_id, scheme_id=scheme_id, branch=branch, path=scan_path)
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def refresh_project_key(self):
        project_key = self.gen_project_key(self.repo_id, self.scan_scheme_id, self.branch, self.scan_path)
        self.project_key = project_key
        self.save()

    @property
    def project_name(self):
        """项目名称
        """
        if self.repo.name:
            project_name = "%s#%s" % (self.repo.name, self.branch)
        else:
            project_name = "%s#%s" % (self.repo.scm_url.rsplit("/", 1)[-1], self.branch)
        return project_name

    @property
    def scm_type(self):
        if self.repo:
            return self.repo.scm_type
        else:
            return None

    @property
    def scm_url(self):
        """获取Repo的http_url
        """
        if self.repo:
            if self.repo.scm_type == BaseRepository.ScmTypeEnum.GIT:
                return "%s#%s" % (self.repo.scm_url, self.branch)
            else:
                return "%s/%s" % (self.repo.scm_url.rstrip("/"), self.branch)
        else:
            return None

    @property
    def languages(self):
        if self.scan_scheme:
            return self.scan_scheme.languages
        else:
            return None

    @property
    def auth_info(self):
        if self.scm_auth:
            logger.info("using project scm_auth")
            return self.scm_auth.auth_info
        elif self.repo.scm_auth:
            logger.info("using repo scm_auth")
            return self.repo.scm_auth.auth_info
        else:
            return {}

    @property
    def simple_auth_info(self):
        auth_info = self.auth_info
        return {"auth_type": auth_info.get("auth_type"),
                "scm_username": auth_info.get("username") or auth_info.get("scm_username")}

    @property
    def remark_info(self):
        """备注信息Dict格式
        """
        if self.remark:
            try:
                return json.loads(self.remark)
            except Exception as err:  # NOCA:broad-except(可能存在多种异常)
                logger.exception("[Project: %s] get remark info failed, err: %s, remark: %s" % (
                    self.id, err, self.remark))
                return {}
        else:
            return {}

    def update_remark(self, kwargs):
        """更新备注信息
        """
        self.remark = json.dumps(self.remark_info.update(**kwargs))
        self.save()

    def get_format_url(self, **kwargs):
        """获取格式化的链接
        """
        if self.repo.scm_type == BaseRepository.ScmTypeEnum.GIT:
            return "%s#%s" % (self.repo.get_format_url(**kwargs), self.branch)
        else:
            return "%s/%s" % (self.repo.get_format_url(**kwargs), self.branch)

    def get_scm_url_with_auth(self, **kwargs):
        """根据凭证获取URL
        """
        repo_scm_url = self.repo.get_scm_url_with_auth(**kwargs)
        if self.repo:
            if self.repo.scm_type == BaseRepository.ScmTypeEnum.GIT:
                return "%s#%s" % (repo_scm_url, self.branch)
            else:
                return "%s/%s" % (repo_scm_url, self.branch)
        else:
            return None

    def sync_to_analyse_server(self):
        try:
            AnalyseClient().api("create_project", data={
                "id": self.id,
                "repo_id": self.repo_id,
                "scan_scheme_id": self.scan_scheme_id,
                "scan_path": self.scan_path,
                "creator": self.creator.username if self.creator else None,
                "scm_type": self.scm_type,
                "scm_url": self.scm_url
            })
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def __str__(self):
        return "%s-%s-%s-%s" % (
            self.repo_id, self.branch,
            self.scan_scheme.name if self.scan_scheme else "NoScanScheme",
            self.scan_path
        )


Repository = BaseRepository
ScanScheme = BaseScanScheme
Project = BaseProject
