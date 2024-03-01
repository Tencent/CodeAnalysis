# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 serializer
Serializers 定义：此处定义了供apis.py接口使用的Serializers
"""
# python 原生import
import logging

# 第三方 import
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

# 项目内 import
from apps.authen.serializers.base import ScmAuthCreateSerializer, ScmAuthSerializer
from apps.base.serializers import CDBaseModelSerializer
from apps.codeproj import core
from apps.codeproj import models
from apps.codeproj.serializers import base
from apps.job.models import Job
from apps.scan_conf.serializers.v3 import ScanSchemeCheckProfileSimpleSerializer
from util import scm
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class RepositoryMemberConfSerializer(serializers.Serializer):
    """代码库成员序列化
    """
    user_list = serializers.ListField(child=serializers.CharField(max_length=16), help_text="人员列表")
    role = serializers.ChoiceField(choices=models.Repository.PERMISSION_CHOICES, help_text="角色，0为管理员，1为普通成员")


class RepositoryMemberConfInvitedSerializer(serializers.Serializer):
    """代码库成员被邀请序列化
    """
    inviter = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username", help_text="邀请者")
    role = serializers.ChoiceField(choices=models.Repository.PERMISSION_CHOICES, help_text="角色，0为管理员，1为普通成员")


class ProjectTeamSerializer(base.ProjectTeamSerializer):
    """项目组序列化
    """
    pass


class ProjectTeamLabelSerializer(base.ProjectTeamLabelSerializer):
    """标签序列化
    """
    pass


class RepositoryListSerializer(CDBaseModelSerializer):
    """代码库列表展示序列化
    """
    branch_count = serializers.SerializerMethodField()
    scheme_count = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    recent_active = serializers.SerializerMethodField()
    scm_auth = ScmAuthSerializer(read_only=True)
    project_team = base.ProjectTeamSimpleSerializer(read_only=True)

    def get_recent_active(self, repo):
        job = Job.objects.filter(project__repo=repo).order_by("-start_time") \
            .only('project__branch', 'start_time', 'total_line_num', 'code_line_num') \
            .first()
        if job:
            return {
                "id": job.project_id,
                "branch_name": job.project.branch,
                "active_time": job.start_time,
                "total_line_num": job.total_line_num,
                "code_line_num": job.code_line_num
            }
        return None

    def get_branch_count(self, repo):
        return repo.get_projects().values_list("branch").distinct().count()

    def get_scheme_count(self, repo):
        """获取未废弃的扫描方案总量
        """
        return repo.get_scanschemes().filter(status=models.ScanScheme.StatusEnum.ACTIVE).count()

    def get_job_count(self, repo):
        return Job.objects.filter(project__repo=repo).count()

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        # 更新字段
        instance.name = validated_data.get("name", instance.name)
        instance.ssh_url = validated_data.get("ssh_url", instance.ssh_url)
        instance.save(user=user)

        if user:
            OperationRecordHandler.add_repo_operation_record(instance, "更新代码库基本信息", user, validated_data)
        return instance

    class Meta:
        model = models.Repository
        fields = ["id", "name", "scm_url", "scm_type", "branch_count", "scheme_count", "job_count",
                  "created_time", "recent_active", "created_from", "creator", "scm_auth", "project_team",
                  "ssh_url"]
        read_only_fields = ["scm_url", "scm_type", "created_from"]


class RepositorySimpleSerializerV3(CDBaseModelSerializer):
    """代码库简略版序列化
    """
    scm_auth = ScmAuthSerializer(read_only=True)

    class Meta:
        model = models.Repository
        fields = ["id", "name", "scm_url", "scm_type", "scm_auth"]
        read_only_fields = ["scm_url", "scm_type", "scm_auth_type", "created_from"]


class RepositoryCreateSerializer(CDBaseModelSerializer):
    """代码库创建序列化
    """

    scm_auth = ScmAuthCreateSerializer(help_text="关联授权信息", required=False)

    def validate(self, attrs):
        scm_type = attrs["scm_type"]
        scm_url = attrs["scm_url"]
        ssh_url = attrs.get("ssh_url") or scm_url
        scm_auth = attrs.get("scm_auth")
        request = self.context.get("request")
        user = request.user
        if not scm_auth:
            return serializers.ModelSerializer.validate(self, attrs)

        auth_type = scm_auth.get("auth_type")
        if auth_type == models.ScmAuth.ScmAuthTypeEnum.PASSWORD:
            scm_account = scm_auth.get("scm_account")
            scm_account_id = scm_account.id if scm_account else None
            scm_account = core.ScmAuthManager.get_scm_account_with_id(user, scm_account_id)
            if not scm_account:
                raise serializers.ValidationError({"cd_error": "用户名密码凭证不存在"})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=scm_account.scm_username, password=scm_account.scm_password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            scm_ssh = scm_auth.get("scm_ssh")
            scm_ssh_id = scm_ssh.id if scm_ssh else None
            scm_ssh_info = core.ScmAuthManager.get_scm_sshinfo_with_id(user, scm_ssh_id)
            if not scm_ssh_info:
                raise serializers.ValidationError({"cd_error": "SSH凭证不存在"})
            scm_client = scm.ScmClient(scm_type, ssh_url, auth_type,
                                       ssh_key=scm_ssh_info.ssh_private_key, ssh_password=scm_ssh_info.password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.OAUTH:
            scm_oauth = scm_auth.get("scm_oauth")
            scm_oauth_id = scm_oauth.id if scm_oauth else None
            scm_auth_info = core.ScmAuthManager.get_scm_authinfo_with_id(user, scm_oauth_id)
            # 注意判空
            scm_password = scm_auth_info.gitoa_access_token if scm_auth_info and \
                                                               scm_auth_info.gitoa_access_token else None
            if not scm_password:
                raise serializers.ValidationError({"scm_auth": "请授权给CodeDog"})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=user.username, password=scm_password)
        else:
            raise serializers.ValidationError({"cd_error": "不支持%s鉴权方式" % auth_type})

        try:
            scm_client.auth_check()
        except scm.ScmNotFoundError:
            raise serializers.ValidationError({"cd_error": "代码库地址不存在"})
        except scm.ScmAccessDeniedError:
            raise serializers.ValidationError({"cd_error": "代码库帐号无权限"})
        except scm.ScmClientError:
            raise serializers.ValidationError({"cd_error": "代码库密码错误"})
        except Exception as e:
            logger.exception("validate repo scm auth exception: %s" % e)
            raise serializers.ValidationError({"cd_error": "代码库及帐号不匹配"})
        return serializers.ModelSerializer.validate(self, attrs)

    def get_scm_url(self, scm_type, scm_url, ssh_url):
        """获取scm_url
        """
        if scm.ScmUrlFormatter.check_ssh_url(scm_type, scm_url):
            logger.info("current scm url is ssh format: %s" % scm_url)
            if not ssh_url:
                ssh_url = scm_url
            scm_client = scm.ScmClient(scm_type, scm_url, models.ScmAuth.ScmAuthTypeEnum.SSHTOKEN)
            http_url = scm_client.get_repository()
        else:
            scm_client = scm.ScmClient(scm_type, scm_url, models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
            http_url = scm_client.get_repository()
            if not ssh_url:
                ssh_url = scm_client.get_ssh_url()
        ssh_url = scm.ScmUrlFormatter.get_git_ssh_url(ssh_url)
        return http_url, ssh_url

    def set_scm_auth(self, repo, scm_auth, user):
        """获取SCM鉴权信息
        """
        core.ScmAuthManager.create_repository_auth(
            repo, user, scm_auth_type=scm_auth.get("auth_type"),
            scm_account=scm_auth.get("scm_account"),
            scm_ssh_info=scm_auth.get("scm_ssh"),
            scm_oauth=scm_auth.get("scm_oauth"),
        )

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        org_sid = self.context["view"].kwargs.get("org_sid")
        team_name = self.context["view"].kwargs.get("team_name")
        pt = models.ProjectTeam.objects.get(name=team_name, organization__org_sid=org_sid)
        scm_auth = validated_data.pop("scm_auth", None)
        scm_type = validated_data.pop("scm_type")
        scm_url = validated_data.pop("scm_url")
        ssh_url = validated_data.pop("ssh_url", None)
        scm_url, ssh_url = self.get_scm_url(scm_type, scm_url, ssh_url)
        logger.info("create repo, scm_url: %s, ssh_url: %s" % (scm_url, ssh_url))

        with transaction.atomic():
            repo = core.RepositoryManager.v3_create_repo(pt, scm_type=scm_type, scm_url=scm_url,
                                                         ssh_url=ssh_url, user=user, **validated_data)
            OperationRecordHandler.add_repo_operation_record(repo, "接入代码库", user, validated_data)
            if scm_auth:
                self.set_scm_auth(repo, scm_auth, user)
                OperationRecordHandler.add_repo_operation_record(repo, "设置代码库凭证", user, validated_data)
        return repo

    class Meta:
        model = models.Repository
        fields = ["id", "name", "scm_url", "ssh_url", "scm_type", "created_from", "scm_auth", "labels"]


class RepositoryAuthSerializer(CDBaseModelSerializer):
    """代码库鉴权序列化
    """
    scm_auth = ScmAuthSerializer(read_only=True)

    class Meta:
        model = models.Repository
        fields = ["id", "name", "scm_url", "scm_type", "scm_auth"]
        read_only_fields = ["scm_url", "scm_type", "name"]


class RepositoryAuthUpdateSerializer(serializers.Serializer):
    """代码库鉴权序列化
    """
    scm_auth = ScmAuthCreateSerializer()

    class Meta:
        model = models.Repository
        fields = ["id", "name", "scm_url", "scm_type", "scm_auth"]
        read_only_fields = ["scm_url", "scm_type", "name"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        scm_type = self.instance.scm_type
        scm_url = self.instance.get_format_url()
        ssh_url = self.instance.ssh_url or scm_url

        # 与RepositoryCreateSerializer校验鉴权相同
        scm_auth = attrs.get("scm_auth")
        auth_type = scm_auth.get("auth_type")
        if auth_type == models.ScmAuth.ScmAuthTypeEnum.OAUTH:
            scm_oauth = scm_auth.get("scm_oauth")
            scm_oauth_id = scm_oauth.id if scm_oauth else None
            scm_auth_info = core.ScmAuthManager.get_scm_authinfo_with_id(user, scm_oauth_id)
            # 注意判空
            scm_password = scm_auth_info.gitoa_access_token if scm_auth_info and \
                                                               scm_auth_info.gitoa_access_token else None
            if not scm_password:
                raise serializers.ValidationError({"scm_auth": "请授权给CodeDog"})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=user.username, password=scm_password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.PASSWORD:
            scm_account = scm_auth.get("scm_account")
            scm_account_id = scm_account.id if scm_account else None
            scm_account = core.ScmAuthManager.get_scm_account_with_id(user, scm_account_id)
            if not scm_account:
                raise serializers.ValidationError({"scm_account": "您名下没有指定的用户名密码授权信息: %s" % scm_account})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=scm_account.scm_username, password=scm_account.scm_password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            scm_ssh = scm_auth.get("scm_ssh")
            scm_ssh_id = scm_ssh.id if scm_ssh else None
            scm_ssh_info = core.ScmAuthManager.get_scm_sshinfo_with_id(user, scm_ssh_id)
            if not scm_ssh_info:
                raise serializers.ValidationError({"scm_ssh": "您名下没有指定的SSH授权信息: %s" % scm_ssh})

            scm_client = scm.ScmClient(scm_type, ssh_url, auth_type,
                                       ssh_key=scm_ssh_info.ssh_private_key, ssh_password=scm_ssh_info.password)
        else:
            raise serializers.ValidationError({"auth_type": "不支持%s鉴权方式" % auth_type})

        try:
            scm_client.auth_check()
        except scm.ScmNotFoundError:
            raise serializers.ValidationError({"cd_error": "代码库地址不存在"})
        except scm.ScmAccessDeniedError:
            raise serializers.ValidationError({"cd_error": "代码库帐号无权限"})
        except scm.ScmClientError:
            raise serializers.ValidationError({"cd_error": "代码库密码错误"})
        except Exception as e:
            logger.exception("auth check exceptio: %s" % e)
            raise serializers.ValidationError({"cd_error": "代码库及帐号不匹配"})
        return serializers.ModelSerializer.validate(self, attrs)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        scm_auth = validated_data.get("scm_auth")
        auth_type = scm_auth.get("auth_type")

        with transaction.atomic():
            # 保存账号信息
            core.ScmAuthManager.create_repository_auth(
                instance, user, scm_auth_type=auth_type,
                scm_account=scm_auth.get("scm_account"),
                scm_ssh_info=scm_auth.get("scm_ssh"),
                scm_oauth=scm_auth.get("scm_oauth"),
            )

        if user:
            OperationRecordHandler.add_repo_operation_record(instance, "更新代码库凭证信息", user, validated_data)
        return instance


class ScanSchemeInitialSerializer(serializers.Serializer):
    """扫描方案初始化 - 用于代码库初始化扫描方案
    """
    name = serializers.CharField(max_length=128, help_text="扫描方案名称", allow_null=True, allow_blank=True)
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, required=False)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=models.ExecTag.objects.all(), required=False,
                                       allow_null=True)
    lint_enabled = serializers.BooleanField(help_text="启用代码扫描", default=False)
    cc_scan_enabled = serializers.BooleanField(help_text="启用圈复杂度", default=False)
    dup_scan_enabled = serializers.BooleanField(help_text="启用重复代码", default=False)
    cloc_scan_enabled = serializers.BooleanField(help_text="启用代码统计", default=False)


class ScanSchemeCopySerializer(serializers.Serializer):
    """复制方案模板到扫描方案，仅限方案模板复制，禁止不同扫描方案的复制
    """
    name = serializers.CharField(max_length=128, help_text="分析方案名称")
    ref_scheme = serializers.SlugRelatedField(slug_field="id", help_text="方案模板ID",
                                              queryset=models.ScanScheme.objects.all())

    def validate_name(self, name):
        repo_id = self.context["view"].kwargs.get("repo_id")
        if models.ScanScheme.objects.filter(name=name, repo_id=repo_id):
            raise serializers.ValidationError("该名称已被使用")
        return name

    def validate_ref_scheme(self, ref_scheme):
        repo_id = self.context["view"].kwargs.get("repo_id")
        request = self.context.get("request")
        user = request.user if request else None
        # 模板，且没有权限则raise
        org_sid = self.context["view"].kwargs.get("org_sid")
        if not ref_scheme.repo and not core.ScanSchemePermManager.check_user_view_perm(ref_scheme, user, org_sid):
            raise serializers.ValidationError("没有使用该方案模板权限")
        # 分析方案，如果不是该代码库的则raise
        if ref_scheme.repo_id and ref_scheme.repo_id != repo_id:
            raise serializers.ValidationError("不存在该分析方案")
        return ref_scheme


class RepoProjectInitialSerializer(base.RepoProjectInitialSerializer):
    """代码库初始化执行相关创建，用于首次创建分支项目、扫描方案
    """
    pass


class ScanSchemeBasicConfSerializer(CDBaseModelSerializer):
    """扫描方案基础信息序列化
    """
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, required=False)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=models.ExecTag.objects.all(),
                                       required=False, allow_null=True)
    refer_scheme = base.RefSchemeSimpleSerializer(help_text="父方案简要信息", read_only=True)

    class Meta:
        model = models.ScanScheme
        exclude = ["scheme_key"]
        read_only_fields = ["repo", "refer_scheme", "created_from"]

    def validate_name(self, name):
        if self.instance and models.ScanScheme.objects.filter(name=name,
                                                              repo=self.instance.repo).exclude(id=self.instance.id):
            raise serializers.ValidationError("该名称已被使用")
        return name

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        # 更新默认扫描方案
        default_flag = validated_data.get("default_flag", False)
        if default_flag:
            models.ScanScheme.objects.filter(repo_id=instance.repo_id, default_flag=True).update(default_flag=False)
        instance.default_flag = default_flag
        # 标记方案状态
        status = validated_data.get("status", None)
        if status:
            if status == models.ScanScheme.StatusEnum.DISACTIVE and instance.default_flag is True:
                raise serializers.ValidationError("当前方案为默认方案，不允许废弃")
            else:
                instance.status = status
        scheme = core.ScanSchemeManager.update_scheme_basic_conf(instance, user, **validated_data)
        if user:
            OperationRecordHandler.add_scanscheme_operation_record(instance, "修改基本信息", user, validated_data)
        return scheme


class ScanSchemeLintConfSerializer(CDBaseModelSerializer):
    """代码扫描配置序列化
    """
    checkprofile = ScanSchemeCheckProfileSimpleSerializer(read_only=True)

    class Meta:
        model = models.LintBaseSetting
        fields = ["id", "enabled", "checkprofile", "scan_scheme", "build_cmd", "envs", "pre_cmd"]
        read_only_fields = ["scan_scheme"]

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        instance = core.ScanSchemeManager.update_scheme_lint_settings(instance.scan_scheme, user=user, **validated_data)
        if user:
            OperationRecordHandler.add_scanscheme_operation_record(
                instance.scan_scheme, "修改代码分析设置", user, validated_data)
        return instance


class ScanSchemeMetricConfSerializer(CDBaseModelSerializer):
    """代码度量配置序列化
    """

    class Meta:
        model = models.MetricSetting
        fields = ["id", "cc_scan_enabled", "min_ccn", "dup_scan_enabled", "dup_block_length_min",
                  "dup_block_length_max", "dup_min_dup_times", "dup_max_dup_times", "dup_min_midd_rate",
                  "dup_min_high_rate", "dup_min_exhi_rate", "dup_issue_limit", "cloc_scan_enabled", "scan_scheme"]
        read_only_fields = ["scan_scheme"]

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        instance = super().update(instance, validated_data)
        if user:
            instance.save(user=user)
            OperationRecordHandler.add_scanscheme_operation_record(instance.scan_scheme, "修改代码度量设置", user,
                                                                   validated_data)
        return instance


class ScanSchemDirConfSerializer(base.ScanDirConfSerializer):
    """扫描方案过滤路径配置序列化
    """
    pass


class ScanSchemeRepoInfoSimpleSerializer(base.ScanSchemeRepoInfoSimpleSerializer):
    """扫描方案-代码库信息简单序列化
    """
    pass


class ScanSchemeDirConfBulkCreateSerialzier(serializers.Serializer):
    """扫描方案过滤路径批量创建配置序列化
    """
    scandirs = ScanSchemDirConfSerializer(many=True, help_text="扫描方案过滤路径配置")


class ScanSchemeSimpleSerializerV3(base.ScanSchemeSimpleSerializer):
    """扫描方案序列化
    """

    class Meta:
        model = models.ScanScheme
        exclude = ["refer_scheme"]
        read_only_fields = ["repo"]


class ProjectSimpleSerializerV3(CDBaseModelSerializer):
    """扫描项目简略序列化
    """
    scan_scheme = ScanSchemeSimpleSerializerV3(read_only=True)

    class Meta:
        model = models.Project
        exclude = ["scm_auth", "scm_initial_revision", "refer_project"]


class ProjectSerializer(base.ProjectSerializer):
    """扫描项目序列化
    """
    scan_scheme = ScanSchemeSimpleSerializerV3(read_only=True)
    repo = RepositorySimpleSerializerV3(read_only=True)

    class Meta:
        model = models.Project
        exclude = ["scm_auth", "scm_initial_revision", "refer_project"]
        read_only_fields = ["repo", "scan_scheme", "status", "project_key"]


class ProjectUpdatetSerializer(base.ProjectUpdatetSerializer):
    """分支项目更新序列化
    """
    pass


class APIProjectsSerializer(base.APIProjectsSerializer):
    """扫描项目序列化
    """

    def get_data_from_view_kwargs(self, **view_kwargs):
        """通过view_kwargs获取数据
        """
        org_sid = view_kwargs["org_sid"]
        team_name = view_kwargs["team_name"]
        org = models.Organization.objects.get(org_sid=org_sid)
        pt = models.ProjectTeam.objects.get(name=team_name, organization=org)
        url_key = core.RepositoryManager.get_repo_url_key("ORG_%d_TEAM_%d" % (pt.organization_id, pt.id))
        return {"org_sid": org_sid, "team_name": team_name, "org": org, "pt": pt, "url_key": url_key}

    def create_repo(self, request, repo_url, created_from, validated_data, **view_data):
        """创建代码库并设置相关权限
        """
        org_sid = view_data["org_sid"]
        team_name = view_data["team_name"]
        pt = view_data["pt"]
        logger.info("[Org: %s][PT: %s] create repo with url: %s" % (org_sid, team_name, repo_url))
        admins = validated_data.get("admins", [])
        try:
            repo = core.RepositoryManager.v3_create_repo(
                pt=pt,
                scm_type=validated_data["scm_type"],
                scm_url=repo_url,
                user=request.user,
                name=validated_data.get("name"),
                db_key=validated_data.get("db_key"),
                created_from=created_from,
                admins=admins,
            )
        except Exception as err:
            logger.exception("create repo failed, repo_url: %s, err: %s" % (repo_url, err))
            raise serializers.ValidationError({"cd_error": "创建代码库失败-%s" % str(err)})

        OperationRecordHandler.add_repo_operation_record(repo, "通过%s创建代码库" % created_from, request.user, {})
        if admins:
            logger.info("[Org: %s][PT: %s][Repo: %s] set repo admins: %s" % (org_sid, team_name, repo.id, admins))
            repo.assign_members_perm(admins, models.Repository.PermissionEnum.ADMIN)
        return repo
