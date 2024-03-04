# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base serializer
"""
# python 原生import
import json
import logging

# 第三方 import
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from rest_framework import exceptions, serializers

# 项目内 import
from apps.authen.serializers.base import CodedogUserInfoSerializer, ScmAuthCreateSerializer, ScmAuthSerializer
from apps.authen.serializers.base import UserSimpleSerializer
from apps.authen.serializers.base_org import OrganizationSimpleSerializer
from apps.base.serializers import CDBaseModelSerializer
from apps.codeproj import core, models
from apps.codeproj.core import LabelManager, ProjectTeamManager
from apps.job import models as job_models
from apps.nodemgr.models import ExecTag, Node
from apps.scan_conf.models import CheckRule, CheckTool, Label, PackageMap
from util import scm
from util.cdcrypto import encrypt
from util.operationrecord import OperationRecordHandler
from util.time import localnow

logger = logging.getLogger(__name__)


class MemberConfAddSerializer(serializers.Serializer):
    """通用成员配置添加成员序列化
    """
    users = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username', many=True,
                                         help_text="成员列表")
    role = serializers.ChoiceField(choices=models.BasePerm.PERMISSION_CHOICES,
                                   help_text="角色，1为管理员，2为普通成员")


class ProjectTeamSimpleSerializer(CDBaseModelSerializer):
    """项目组简单序列化
    """

    org_sid = serializers.StringRelatedField(source="organization.org_sid")

    def update(self, instance, validated_data):
        """更新项目组状态
        """
        status = validated_data.get("status")
        if status is None or status == instance.status:
            return instance
        user = self.context["request"].user
        instance = ProjectTeamManager.set_project_team_status(instance, user, status)
        return instance

    class Meta:
        model = models.ProjectTeam
        fields = ["name", "display_name", "status", "org_sid"]
        read_only_fields = ["name", "display_name", "org_sid"]


class ProjectTeamSerializer(CDBaseModelSerializer):
    """项目组序列化
    """
    admins = serializers.SerializerMethodField(help_text="项目管理员")
    display_name = serializers.CharField(max_length=128, help_text="项目展示名称",
                                         allow_null=True, allow_blank=True, required=False)
    organization = OrganizationSimpleSerializer(read_only=True)

    def get_admins(self, instance):
        admins = instance.get_members(models.ProjectTeam.PermissionEnum.ADMIN)
        return [UserSimpleSerializer(instance=user).data for user in admins]

    def create(self, validated_data):
        user = self.context["request"].user
        org_sid = self.context["view"].kwargs.get("org_sid")
        org = models.Organization.objects.get(org_sid=org_sid)
        name = validated_data.pop("name")
        return ProjectTeamManager.create_project_team(org, name, user, **validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        name = validated_data.pop("name")
        return ProjectTeamManager.update_project_team(instance, name, user, **validated_data)

    class Meta:
        model = models.ProjectTeam
        fields = '__all__'
        read_only_fields = ["organization"]


class ProjectTeamLabelSerializer(CDBaseModelSerializer):
    """标签序列化
    """

    def create(self, validated_data):
        user = self.context["request"].user
        org_sid = self.context["view"].kwargs.get("org_sid")
        team_name = self.context["view"].kwargs.get("team_name")
        project_team = models.ProjectTeam.objects.get(name=team_name, organization__org_sid=org_sid)
        name = validated_data.pop("name")
        return LabelManager.create_label(project_team, name, user, **validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        name = validated_data.pop("name")
        return LabelManager.update_label(instance, name, user, **validated_data)

    class Meta:
        model = models.Label
        fields = "__all__"
        read_only_fields = ["project_team"]


class OnlySuperAdminReadField(serializers.Field):
    """仅超级管理员可见的字段
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        request = self.context.get("request")
        if request and request.user and request.user.is_staff:
            return value
        else:
            return ""


class ScanTaskSerializer(serializers.Serializer):
    task_version = serializers.CharField(max_length=16, help_text="Task版本号", allow_null=True, required=False)
    module_name = serializers.CharField(max_length=64, help_text="模块名称")
    task_name = serializers.CharField(max_length=32, help_text="Task名称")
    task_params = serializers.JSONField(help_text="Task 参数")
    result_code = serializers.IntegerField(min_value=0, max_value=399, help_text="结果代码",
                                           allow_null=True, required=False)
    result_msg = serializers.CharField(max_length=256, help_text="结果信息", allow_null=True, required=False)
    result_data_url = serializers.CharField(help_text="结果数据链接", allow_null=True, required=False)
    log_url = serializers.CharField(help_text="执行日志链接", allow_null=True, required=False)
    tag = serializers.CharField(max_length=64, allow_null=True, help_text="标签", required=False)
    start_time = serializers.CharField(max_length=64, allow_null=True, help_text="起始时间字符串", required=False)
    end_time = serializers.CharField(max_length=64, allow_null=True, help_text="结束时间字符串", required=False)
    time_format = serializers.CharField(max_length=64, allow_null=True, help_text="时间格式字符串", required=False)
    processes = serializers.ListField(child=serializers.CharField(max_length=64), help_text="子进程列表", required=False)
    finished_processes = serializers.ListField(child=serializers.CharField(max_length=64), help_text="已完成子进程列表",
                                               allow_null=True, required=False)
    private_processes = serializers.ListField(child=serializers.CharField(max_length=64), help_text="私有子进程列表",
                                              allow_null=True, required=False)


class ScanJobInitSerializer(serializers.Serializer):
    force_create = serializers.BooleanField(help_text="是否忽略已有任务强制启动", default=False, write_only=True)
    incr_scan = serializers.BooleanField(help_text="扫描类型, True表示增量，False表示全量", required=False)
    created_from = serializers.CharField(help_text="扫描渠道", required=False, default="codedog_client")
    revision = serializers.CharField(help_text="指定版本号", allow_null=True, required=False)
    last_revision = serializers.CharField(help_text="指定参照版本号", allow_null=True, required=False)
    co_url = serializers.CharField(help_text="合作平台的任务链接", allow_null=True, required=False)
    co_author = serializers.CharField(help_text="合作平台的任务负责人", allow_null=True, required=False)
    task_names = serializers.ListField(child=serializers.CharField(help_text="Task名称", max_length=32),
                                       allow_empty=True, allow_null=True, required=False)


class ScanJobCreateSerializer(serializers.Serializer):
    job_context = serializers.JSONField(help_text="Job Context")
    tasks = serializers.ListField(child=ScanTaskSerializer())
    force_create = serializers.BooleanField(help_text="是否忽略已有任务强制启动", default=False, write_only=True)
    scan_type = serializers.IntegerField(help_text="扫描类型", required=False, allow_null=True)

    def validate_job_context(self, job_context):
        if not job_context or not job_context.get("scm_revision") or \
                not job_context.get("scm_url") or \
                not job_context.get("scan_type"):
            raise serializers.ValidationError("job_context格式错误，不能为空或缺少必要的key")
        return job_context


class CodeLintInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CodeLintInfo
        fields = '__all__'
        read_only_fields = ['project']


class CodeMetricCCInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CodeMetricCCInfo
        fields = '__all__'
        read_only_fields = ['project']


class CodeMetricDupInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CodeMetricDupInfo
        fields = '__all__'
        read_only_fields = ['project']


class CodeMetricClocInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CodeMetricClocInfo
        fields = '__all__'
        read_only_fields = ['project']


class ProjectCheckProfileSerializer(serializers.ModelSerializer):
    """规则集简化版序列化
    """

    class Meta:
        model = models.CheckProfile
        fields = ["id", "name", "custom_checkpackage", "checkpackages"]


class ScanSchemeCheckprofileCustomSerialiazer(serializers.Serializer):
    private = serializers.BooleanField(label="切换为自定义规则集", help_text="切换为自定义规则集")


class LintBaseSettingConfSerializer(CDBaseModelSerializer):
    """代码扫描配置序列化
    """
    checkprofile_id = serializers.IntegerField(help_text="规则集编号", default=0, write_only=True)
    labels = serializers.SlugRelatedField(queryset=Label.objects.all(), slug_field='name', many=True,
                                          required=False, allow_null=True, write_only=True, help_text="标签列表")
    checkprofile = ProjectCheckProfileSerializer(read_only=True)
    scan_scheme = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.LintBaseSetting
        fields = '__all__'

    def validate_default_author(self, value):
        if value:
            value = value.strip().lower()
        return value

    def validate_checkprofile_id(self, value):
        if value != 0:
            if not models.CheckProfile.objects.filter(id=value):
                raise serializers.ValidationError({"checkprofile_id": "编号为%s的规则集不存在" % value})
        return value

    def update(self, instance, validated_data):
        """更新项目的代码扫描配置

        注：如果开启了代码扫描但是没有配置规则集（如首次开启）时，自动配置默认规则
        """
        request = self.context.get("request")
        user = request.user if request else None
        labels = validated_data.get("labels", None)
        checkprofile_id = validated_data.pop("checkprofile_id", None)

        instance = serializers.ModelSerializer.update(self, instance, validated_data)
        if instance.enabled:
            # 如果指定规则集编号，则进行更新
            if checkprofile_id:
                core.ScanSchemeManager.update_check_profile(
                    scan_scheme=instance.scan_scheme, checkprofile_id=checkprofile_id, user=user)
            # 没有配置规则集（如首次开启）时，自动配置默认规则
            elif not instance.checkprofile:
                instance.checkprofile = core.ScanSchemeManager.create_default_check_profile(
                    scan_scheme=instance.scan_scheme, user=user, labels=labels)
                instance.save(user=user)
            # 通过标签更新规则集
            elif labels:
                instance.checkprofile = core.ScanSchemeManager.create_default_check_profile(
                    scan_scheme=instance.scan_scheme, user=user, labels=labels)
                instance.save(user=user)
        if user:
            OperationRecordHandler.add_scanscheme_operation_record(
                instance.scan_scheme, "修改代码分析设置", user, validated_data)
        return instance


class MetricSettingConfSerializer(CDBaseModelSerializer):
    """代码度量配置序列化
    """

    class Meta:
        model = models.MetricSetting
        exclude = ["codediff_scan_enabled", "core_file_path", "file_mon_path"]
        read_only_fields = ['scan_scheme']

    def create(self, validated_data):
        instance = serializers.ModelSerializer.create(self, validated_data)
        return instance

    def update(self, instance, validated_data):
        instance = serializers.ModelSerializer.update(self, instance, validated_data)
        request = self.context.get("request")
        user = request.user if request else None
        if user:
            instance.save(user=user)
            OperationRecordHandler.add_scanscheme_operation_record(
                instance.scan_scheme, "修改代码度量设置", user, validated_data)
        return instance


class ScanSchemePermConfSerializer(CDBaseModelSerializer):
    """权限配置序列化
    """
    edit_managers = serializers.SlugRelatedField(
        slug_field="username", many=True, read_only=True)
    execute_managers = serializers.SlugRelatedField(
        slug_field="username", many=True, read_only=True)
    edit_managers_list = serializers.ListField(
        child=serializers.CharField(max_length=32), help_text="扫描方案可编辑成员员列表", write_only=True,
        required=False, allow_null=True)
    execute_managers_list = serializers.ListField(
        child=serializers.CharField(max_length=32), help_text="关联分支项目可创建/启动成员列表", write_only=True,
        required=False, allow_null=True)

    def re_users(self, users):
        results = []
        if users:
            if not isinstance(users, list):
                users = json.loads(users)
            for name in users:
                if not name:
                    continue
                results.append(name.split("(")[0])
        return results

    def validate_edit_managers_list(self, value):
        return self.re_users(value)

    def validate_execute_managers_list(self, value):
        return self.re_users(value)

    def _get_or_create_user(self, users):
        """用于创建user
        """
        users_data = []
        for username in users:
            user_data, _ = User.objects.get_or_create(username=username)
            users_data.append(user_data)
        return users_data

    def update(self, instance, validated_data):
        """更新工具
        """
        request = self.context.get("request")
        user = request.user if request else None
        edit_managers_list = validated_data.get("edit_managers_list", [])
        execute_managers_list = validated_data.get("execute_managers_list", [])
        edit_managers = self._get_or_create_user(edit_managers_list)
        execute_managers = self._get_or_create_user(execute_managers_list)
        instance = super().update(instance, validated_data)
        instance.edit_managers.set(edit_managers)
        instance.execute_managers.set(execute_managers)
        instance.save(user=user)
        # 添加扫描方案日志
        OperationRecordHandler.add_scanscheme_operation_record(
            instance.scan_scheme, "更新权限配置", user, validated_data)
        return instance

    class Meta:
        model = models.ScanSchemePerm
        fields = ['id', 'scan_scheme', 'edit_scope', 'edit_managers', 'execute_scope', 'execute_managers',
                  'edit_managers_list', 'execute_managers_list']
        read_only_fields = ['scan_scheme']


class ScanDirSerializer(serializers.ModelSerializer):
    """扫描目录序列化
    """

    def create(self, validated_data):
        project_id = self.context["view"].kwargs.get("project_id")
        project = models.Project.objects.get(id=project_id)
        validated_data["scan_scheme"] = project.scan_scheme
        return serializers.ModelSerializer.create(self, validated_data)

    class Meta:
        model = models.ScanDir
        fields = '__all__'
        read_only_fields = ["scan_scheme"]


class DefaultScanPathSerializer(CDBaseModelSerializer):
    """默认过滤扫描目录序列化
    """

    class Meta:
        model = models.DefaultScanPath
        fields = "__all__"

    def create(self, validated_data):
        """创建默认的扫描目录
        """
        request = self.context["request"]
        user = request.user if request else None
        if models.DefaultScanPath.objects.filter(dir_path=validated_data.get("dir_path")).count() > 0:
            raise serializers.ValidationError({"cd_error": "%s路径已存在" % validated_data["dir_path"]})
        instance = models.DefaultScanPath.objects.create(creator=user, **validated_data)
        return instance

    def update(self, instance, validated_data):
        """更新默认的扫描目录
        """
        request = self.context["request"]
        user = request.user if request else None
        instance.dir_path = validated_data.get("dir_path", instance.dir_path)
        instance.path_type = validated_data.get("path_type", instance.path_type)
        instance.category = validated_data.get("category", instance.category)
        instance.description = validated_data.get("description", instance.description)
        try:
            return instance.save(user=user)
        except IntegrityError as err:
            logger.exception("update default path exception: %s" % err)
            raise serializers.ValidationError({"cd_error": "%s路径已存在" % validated_data["dir_path"]})


class SchemeDefaultScanPathExcludeMapSerializer(serializers.ModelSerializer):
    """扫描目录映射表序列化
    """

    scan_scheme = serializers.PrimaryKeyRelatedField(read_only=True, help_text="扫描方案编号")
    default_scan_path_detail = DefaultScanPathSerializer(
        source="default_scan_path", read_only=True, help_text="默认过滤路径详情")

    def create(self, validated_data):
        """创建目录映射
        """
        request = self.context['request']
        user = request.user if request else None
        scheme_id = self.context["view"].kwargs.get("scheme_id")
        scan_scheme = models.ScanScheme.objects.filter(id=scheme_id).first()
        default_scan_path = validated_data["default_scan_path"]
        if not scan_scheme:
            raise serializers.ValidationError({"cd_error": "编号为%d的扫描方案不存在" % scheme_id})
        instance, created = models.SchemeDefaultScanPathExcludeMap.objects.get_or_create(
            scan_scheme=scan_scheme,
            default_scan_path=default_scan_path,
            defaults={"creator": user}
        )
        if created:
            OperationRecordHandler.add_scanscheme_operation_record(
                scan_scheme, "屏蔽默认路径%s" % default_scan_path.dir_path, user, validated_data)
        return instance

    class Meta:
        model = models.SchemeDefaultScanPathExcludeMap
        fields = "__all__"


class ScanDirConfSerializer(serializers.ModelSerializer):
    """扫描方案过滤路径序列化
    """

    class Meta:
        model = models.ScanDir
        fields = '__all__'
        read_only_fields = ["scan_scheme"]

    def create(self, validated_data):
        user = self.context["request"].user
        scan_scheme_id = self.context["view"].kwargs.get("scheme_id")
        exist_count = models.ScanDir.objects.filter(
            scan_scheme_id=scan_scheme_id, dir_path=validated_data["dir_path"]).count()
        if exist_count > 0:
            raise serializers.ValidationError("创建失败，该路径已存在")
        scan_dir = models.ScanDir.objects.create(scan_scheme_id=scan_scheme_id, **validated_data)
        OperationRecordHandler.add_scanscheme_operation_record(
            scan_dir.scan_scheme, "新增过滤目录", user, validated_data)
        return scan_dir

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if models.ScanDir.objects.filter(scan_scheme_id=instance.scan_scheme_id, dir_path=validated_data["dir_path"]
                                         ).exclude(id=instance.id).exists():
            raise serializers.ValidationError("更新失败，该路径已存在")
        instance = super().update(instance, validated_data)
        if user:
            OperationRecordHandler.add_scanscheme_operation_record(
                instance.scan_scheme, "修改过滤目录", user, validated_data)
        return instance


class ScanDirConfBulkCreateSerialzier(serializers.Serializer):
    scandirs = serializers.ListField(
        child=ScanDirConfSerializer(), label="scan dir 列表",
        help_text="包含'dir_path', 'scan_type', 'path_type'")


class RepositorySimpleSerializer(CDBaseModelSerializer):
    """代码库简略版序列化
    """
    scm_auth = ScmAuthSerializer(read_only=True)

    class Meta:
        model = models.Repository
        fields = ['id', 'name', 'scm_url', 'scm_type', 'bg', 'department', 'center', 'scm_auth', 'symbol']
        read_only_fields = ['scm_url', 'scm_type', 'scm_auth_type', 'created_from']


class RepositoryUrlSerializer(serializers.ModelSerializer):
    """代码库url序列化
    """
    project_num = serializers.SerializerMethodField()
    scheme_num = serializers.SerializerMethodField()

    def get_project_num(self, repo):
        return repo.project_set.count()

    def get_scheme_num(self, repo):
        return repo.scanscheme_set.count()

    class Meta:
        model = models.Repository
        fields = ["scm_url", "project_num", "scheme_num"]
        read_only_fields = ["scm_url"]


class RepositorySerializer(CDBaseModelSerializer):
    """代码库序列化
    """
    branch_count = serializers.SerializerMethodField()
    scheme_count = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    subscribed = serializers.SerializerMethodField()
    scm_auth = ScmAuthSerializer(read_only=True)
    recent_active = serializers.SerializerMethodField()
    creator_info = CodedogUserInfoSerializer(source="creator", read_only=True)
    organization = OrganizationSimpleSerializer(read_only=True)
    project_team = ProjectTeamSimpleSerializer(read_only=True)

    def get_recent_active(self, repo):
        job = job_models.Job.objects.filter(project__repo=repo).order_by("-start_time") \
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
        return repo.get_scanschemes().count()

    def get_job_count(self, repo):
        return job_models.Job.objects.filter(project__repo=repo).count()

    def get_subscribed(self, repo):
        request = self.context.get("request")
        user = request.user if request else None
        if user and repo.subscribers.filter(username=user.username):
            return True
        else:
            return False

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        # 更新字段
        instance.name = validated_data.get("name", instance.name)
        instance.save(user=user)
        if user:
            OperationRecordHandler.add_repo_operation_record(instance, "更新代码库基本信息", user, validated_data)
        return instance

    class Meta:
        model = models.Repository
        fields = ['id', 'name', 'scm_url', 'ssh_url', 'scm_type', 'branch_count',
                  'scheme_count', 'subscribed', 'scm_auth', 'created_time',
                  "recent_active", "created_from", "creator", "creator_info",
                  'job_count', "project_team", "organization"]
        read_only_fields = ['scm_url', 'ssh_url', 'scm_type', 'scm_auth_type', 'created_from', "recent_active"]


class RepositoryCreateSerializer(CDBaseModelSerializer):
    """代码库创建序列化，用于代码库创建场景
    """
    ssh_url = serializers.CharField(max_length=256, help_text="代码库SSH链接",
                                    required=False, allow_null=True)
    scm_auth = ScmAuthCreateSerializer(help_text="关联授权信息", required=False)
    admins = serializers.ListField(
        child=serializers.CharField(max_length=64, label="用户名", help_text="用户名"),
        label="管理员列表", help_text="管理员列表", required=False, allow_null=True, write_only=True)
    users = serializers.ListField(
        child=serializers.CharField(max_length=64, label="用户名", help_text="用户名"),
        label="成员列表", help_text="成员列表", required=False, allow_null=True, write_only=True)

    def validate_scm_url(self, scm_url):
        """校验SCM Url格式是否准确（不做鉴权判断）
        """
        if not scm_url:
            raise serializers.ValidationError("该项为必填项")
        scm_type = self.initial_data.get("scm_type")
        scm_client = scm.ScmClient(scm_type, scm_url, "password")
        svn_scm_url = scm_url if scm_type == models.Repository.ScmTypeEnum.SVN else None

        try:
            _scm_url = scm_client.get_repository()
        except Exception as e:
            raise serializers.ValidationError("scm_url格式错误：%s" % str(e))
        if scm_url:
            if models.Repository.objects.filter(scm_url=_scm_url):
                raise serializers.ValidationError("scm_url指定项目已存在")
            return svn_scm_url if svn_scm_url else scm_url
        else:
            raise serializers.ValidationError("scm_url格式错误")

    def validate(self, attrs):
        scm_type = attrs["scm_type"]
        scm_url = attrs["scm_url"]
        ssh_url = attrs.get("ssh_url")
        scm_auth = attrs.get("scm_auth")
        request = self.context.get("request")
        user = request.user

        if not scm_auth:
            return super().validate(attrs)

        auth_type = scm_auth.get("auth_type")
        scm_platform = scm_auth.get("scm_platform", scm.ScmPlatformEnum.GIT_OA)
        if auth_type == models.ScmAuth.ScmAuthTypeEnum.OAUTH:
            scm_auth_info = core.ScmAuthManager.get_scm_auth(user, scm_platform)
            # 注意判空
            scm_password = scm_auth_info.gitoa_access_token if scm_auth_info and scm_auth_info.gitoa_access_token \
                else None
            if not scm_password:
                raise serializers.ValidationError({"scm_auth": "未授权给Codedog平台"})
            scm_client = scm.ScmClient(
                scm_type, scm_url, auth_type, username=user.username, password=scm_password,
                scm_platform=scm_platform)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.PASSWORD:
            scm_account = scm_auth.get("scm_account")
            scm_account_id = scm_account.id if scm_account else None
            scm_account = core.ScmAuthManager.get_scm_account_with_id(user, scm_account_id)
            if not scm_account:
                raise serializers.ValidationError({"scm_account": ["用户名密码凭证不存在"]})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=scm_account.scm_username, password=scm_account.scm_password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            scm_ssh = scm_auth.get("scm_ssh")
            scm_ssh_id = scm_ssh.id if scm_ssh else None
            scm_ssh_info = core.ScmAuthManager.get_scm_sshinfo_with_id(user, scm_ssh_id)
            if not scm_ssh_info:
                raise serializers.ValidationError({"scm_ssh": ["SSH凭证不存在"]})
            scm_url = ssh_url if ssh_url else scm_url

            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       ssh_key=scm_ssh_info.ssh_private_key, ssh_password=scm_ssh_info.password)
        else:
            raise serializers.ValidationError({"auth_type": ["不支持%s鉴权方式" % auth_type]})

        try:
            scm_client.auth_check()
        except scm.ScmNotFoundError:
            raise serializers.ValidationError({"scm_url": "代码库地址不存在"})
        except scm.ScmAccessDeniedError:
            raise serializers.ValidationError({"scm_username": "代码库帐号无权限"})
        except scm.ScmClientError:
            raise serializers.ValidationError({"scm_password": "代码库密码错误"})
        except Exception as e:
            logger.exception("validate repo scm auth exception: %s" % e)
            raise serializers.ValidationError({"scm_username": "代码库及帐号不匹配"})
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        scm_auth = validated_data.pop("scm_auth", {})
        scm_platform = scm_auth.get("scm_platform")
        # 格式化（svn类型的url未格式化）
        scm_type = validated_data.pop("scm_type")
        scm_url = validated_data.pop("scm_url")
        ssh_url = validated_data.pop("ssh_url", None)
        scm_client = scm.ScmClient(scm_type, scm_url, "password")
        scm_url = scm_client.get_repository()
        ssh_url = scm.ScmUrlFormatter.get_git_ssh_url(ssh_url) if ssh_url else \
            scm.ScmClient(scm_type, scm_url, "password").get_ssh_url()
        admins = validated_data.get("admins", [])
        users = validated_data.get("users", [])
        logger.info("create repo, scm_url: %s, ssh_url: %s" % (scm_url, ssh_url))
        if scm_auth.get("auth_type") == models.ScmAuth.ScmAuthTypeEnum.OAUTH:
            scm_auth_info = core.ScmAuthManager.get_scm_auth(
                user, scm_platform=scm_platform)
        else:
            scm_auth_info = None
        with transaction.atomic():
            # 创建代码库
            repo = core.RepositoryManager.create_repository_with_url(
                scm_type=scm_type, scm_url=scm_url, user=user, ssh_url=ssh_url, **validated_data)
            logger.info("[Repo: %s] set repo admins: %s" % (repo.id, admins))
            repo.assign_members_perm(admins, models.Repository.PermissionEnum.ADMIN)
            logger.info("[Repo: %s] set repo user: %s" % (repo.id, users))
            repo.assign_members_perm(users, models.Repository.PermissionEnum.USER)

            if not repo:
                raise serializers.ValidationError({"cd_error": "代码库地址无效或已经接入"})
            if scm_auth:
                # 保存账号信息
                core.ScmAuthManager.create_repository_auth(
                    repo, user, scm_auth_type=scm_auth.get("auth_type"),
                    scm_account=scm_auth.get("scm_account"),
                    scm_ssh_info=scm_auth.get("scm_ssh"),
                    scm_auth_info=scm_auth_info
                )
        return repo

    class Meta:
        model = models.Repository
        fields = ['id', 'name', 'scm_url', 'ssh_url', 'scm_type', "admins", "users",
                  'bg', 'department', 'center', 'created_from', 'scm_auth']


class RepositorySubscribedSerializer(serializers.Serializer):
    subscribed = serializers.BooleanField(label="关注代码库", help_text="关注代码库")


class RepositoryAuthSerializer(CDBaseModelSerializer):
    """代码库鉴权序列化
    """
    scm_auth = ScmAuthSerializer(read_only=True)

    class Meta:
        model = models.Repository
        fields = ['id', 'name', 'scm_url', 'scm_type', 'scm_auth']
        read_only_fields = ['scm_url', 'scm_type', 'name']


class RepositoryAuthUpdateSerializer(serializers.Serializer):
    """代码库鉴权序列化
    """
    scm_auth = ScmAuthCreateSerializer()

    class Meta:
        model = models.Repository
        fields = ['id', 'name', 'scm_url', 'ssh_url', 'scm_type', 'scm_auth']
        read_only_fields = ['scm_url', 'ssh_url', 'scm_type', 'name']

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        scm_auth = attrs.get("scm_auth")
        scm_account = scm_auth.get("scm_account")
        scm_ssh = scm_auth.get("scm_ssh")
        scm_platform = scm_auth.get("scm_platform")
        auth_type = scm_auth.get("auth_type")
        scm_type = self.instance.scm_type
        scm_url = self.instance.scm_url
        ssh_url = self.instance.ssh_url if self.instance.ssh_url else scm_url
        if auth_type == models.ScmAuth.ScmAuthTypeEnum.PASSWORD:
            scm_account = core.ScmAuthManager.get_scm_account_with_id(
                user, account_id=scm_account.id) if scm_account else None
            if not scm_account:
                raise serializers.ValidationError({"scm_account": "您名下没有指定的用户名密码授权信息: %s" % scm_account})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=scm_account.scm_username, password=scm_account.scm_password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.OAUTH:
            scm_auth_info = models.ScmAuthInfo.objects.filter(
                user=user, auth_origin__name=settings.DEFAULT_ORIGIN_ID, scm_platform=scm_platform).first()
            scm_password = scm_auth_info.gitoa_access_token if scm_auth_info and scm_auth_info.gitoa_access_token \
                else None
            if not scm_password:
                raise serializers.ValidationError({"scm_auth_info": "未授权给Codedog平台"})
            scm_client = scm.ScmClient(scm_type, scm_url, auth_type,
                                       username=user.username, password=scm_password)
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            scm_ssh_info = core.ScmAuthManager.get_scm_sshinfo_with_id(
                user, sshinfo_id=scm_ssh.id) if scm_ssh else None
            if not scm_ssh_info:
                raise serializers.ValidationError({"scm_auth_info": "您名下没有指定的SSH授权信息: %s" % scm_ssh})
            scm_client = scm.ScmClient(scm_type, ssh_url, auth_type,
                                       ssh_key=scm_ssh_info.ssh_private_key, ssh_password=scm_ssh_info.password)
        else:
            raise serializers.ValidationError({"auth_type": ["不支持%s鉴权方式" % auth_type]})

        try:
            scm_client.auth_check()
        except scm.ScmNotFoundError:
            raise serializers.ValidationError({"scm_url": "代码库地址不存在"})
        except scm.ScmAccessDeniedError:
            raise serializers.ValidationError({"scm_username": "代码库帐号无权限"})
        except scm.ScmClientError:
            raise serializers.ValidationError({"scm_password": "代码库密码错误"})
        except Exception as e:
            logger.exception("auth check exception: %s" % e)
            raise serializers.ValidationError({"scm_username": "代码库及帐号不匹配"})
        return super().validate(attrs)

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
            )

        if user:
            OperationRecordHandler.add_repo_operation_record(instance, "修改代码库凭证信息", user, validated_data)
        return instance


class ProjectAuthSerializer(CDBaseModelSerializer):
    """项目鉴权序列化
    """
    scm_auth = ScmAuthSerializer(read_only=True)

    class Meta:
        model = models.Project
        fields = ['id', 'branch', 'scm_url', 'scm_type', 'scm_auth']
        read_only_fields = ['scm_url', 'scm_type', 'branch']


class ScanSchemeSyncSerializer(serializers.Serializer):
    """扫描方案同步序列化
    """
    ref_scheme = serializers.IntegerField(help_text="参照扫描方案编号")

    def validate_ref_scheme(self, ref_scheme_id):
        """校验编号
        """
        request = self.context.get("request")
        user = request.user
        ref_scheme = models.ScanScheme.objects.filter(id=ref_scheme_id).first()
        if not ref_scheme:
            raise serializers.ValidationError({"cd_error": "参考扫描方案编号-%d不存在" % ref_scheme_id})
        if not user.has_perm('view_repository', ref_scheme.repo):
            raise serializers.ValidationError({"cd_error": "你没有参考扫描方案的查看权限"})
        return ref_scheme


class ScanSchemeRepoInfoSimpleSerializer(serializers.ModelSerializer):
    """扫描方案-代码库信息简单序列化
    """

    repo = serializers.SerializerMethodField(read_only=True)

    def get_repo(self, instance):
        repo = instance.repo
        return {'id': repo.id, 'scm_url': repo.scm_url, 'name': repo.name} if repo else None

    class Meta:
        model = models.ScanScheme
        fields = ['id', 'name', 'repo', 'refer_scheme']


class RefSchemeSimpleSerializer(CDBaseModelSerializer):
    """RefScheme方案简略版序列化
    """
    is_template = serializers.SerializerMethodField()

    def get_is_template(self, instance):
        """是否为模板
        """
        return False if instance.repo else True

    class Meta:
        model = models.ScanScheme
        fields = ["id", "scheme_key", "repo", "is_template", "name"]


class ScanSchemeSimpleSerializer(CDBaseModelSerializer):
    """扫描方案简略版序列化
    """
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, required=False)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all(), required=False,
                                       allow_null=True)
    refer_scheme_info = RefSchemeSimpleSerializer(source="refer_scheme", help_text="refer方案信息", read_only=True)

    class Meta:
        model = models.ScanScheme
        fields = "__all__"
        read_only_fields = ['repo', 'refer_scheme']

    def validate_name(self, name):
        if models.ScanScheme.objects.filter(name=name, repo=self.instance.repo).exclude(id=self.instance.id):
            raise serializers.ValidationError("该名称已被使用")
        return name

    def update(self, instance, validated_data):
        """更新
        """
        request = self.context.get("request")
        user = request.user if request else None
        # 更新默认扫描方案
        default_flag = validated_data.get('default_flag', False)
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


class ScanSchemeSerializer(CDBaseModelSerializer):
    """扫描方案序列化，用于展示扫描方案内容
    """
    lintbasesetting = LintBaseSettingConfSerializer(read_only=True)
    metricsetting = MetricSettingConfSerializer(read_only=True)
    scan_dirs = serializers.ListSerializer(source="scandir_set", child=ScanDirSerializer(), read_only=True)
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, required=False)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all(),
                                       required=False, allow_null=True)
    branch_info = serializers.SerializerMethodField()

    class Meta:
        model = models.ScanScheme
        fields = "__all__"
        read_only_fields = ['repo', 'refer_scheme', 'scheme_key']

    def validate_name(self, name):
        if models.ScanScheme.objects.filter(name=name, repo=self.instance.repo).exclude(id=self.instance.id):
            raise serializers.ValidationError("该名称已被使用")
        return name

    def get_branch_info(self, instance):
        """获取使用分支列表
        """
        projects = models.Project.objects.filter(scan_scheme=instance, repo=instance.repo)
        return {
            "num": projects.count(),
            # "detail": ProjectSimpleSerializer(projects, many=True).data
        }

    def update(self, instance, validated_data):
        """更新
        """
        request = self.context.get("request")
        user = request.user if request else None
        # 修改配置语言
        languages = validated_data.pop("languages", instance.languages.all())
        instance.languages.add(*languages)
        ids = [language.id for language in languages]
        remove_languages = instance.languages.exclude(id__in=ids)
        instance.languages.remove(*remove_languages)
        # 更新默认扫描方案
        default_flag = validated_data.pop('default_flag', False)
        if default_flag:
            models.ScanScheme.objects.filter(repo_id=instance.repo_id, default_flag=True).update(default_flag=False)
        instance.default_flag = default_flag
        # 标记方案状态
        status = validated_data.pop("status", None)
        if status:
            if status == models.ScanScheme.StatusEnum.DISACTIVE and instance.default_flag is True:
                raise serializers.ValidationError("当前方案为默认方案，不允许废弃")
            else:
                instance.status = status
        instance = super().update(instance, validated_data)
        instance.save(user=user)
        if user:
            OperationRecordHandler.add_scanscheme_operation_record(instance, "修改基本信息", user, validated_data)
        return instance


class ScanSchemeCreateSerializer(CDBaseModelSerializer):
    """扫描方案创建序列化
    """
    name = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)
    lintbasesetting = LintBaseSettingConfSerializer()
    metricsetting = MetricSettingConfSerializer()
    scandir_set = ScanDirConfSerializer(many=True, required=False, allow_null=True)
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, required=False)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all(),
                                       required=False, allow_null=True)
    labels = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(),
                                                required=False, many=True, write_only=True)
    templates = serializers.PrimaryKeyRelatedField(
        queryset=models.ScanSchemeTemplate.objects.filter(public=True),
        help_text="模板编号列表", write_only=True, required=False, many=True, allow_null=True)

    class Meta:
        model = models.ScanScheme
        fields = "__all__"
        read_only_fields = ['repo', 'default_flag', "refer_template_ids"]

    def validate_name(self, name):
        repo_id = self.context["view"].kwargs.get("repo_id")
        if models.ScanScheme.objects.filter(name=name, repo=repo_id):
            raise serializers.ValidationError("该名称已被使用")
        return name

    def create_from_templates(self, repo_id, scheme_template_list, user, **kwargs):
        """通过模板创建扫描方案
        """
        scheme_template_ids = sorted([item.id for item in scheme_template_list])
        logger.info("[Repo: %s][User: %s] create scheme with templates: %s" % (repo_id, user, scheme_template_list))
        merged_scheme_template = core.ScanSchemeTemplateManager.merge_scheme_template(scheme_template_list)
        merged_scheme_template.update(**kwargs)
        scan_scheme = core.ScanSchemeManager.create_scheme_with_template(
            repo_id, merged_scheme_template, kwargs.get("languages", []), user,
            refer_template_ids=scheme_template_ids)
        core.ScanSchemeManager.set_default_scanscheme(scan_scheme)
        OperationRecordHandler.add_scanscheme_operation_record(
            scan_scheme, "通过方案模板[%s]创建扫描方案[%s]" % (scheme_template_ids, scan_scheme.name), user,
            merged_scheme_template)
        return scan_scheme

    def create_from_settings(self, repo_id, validated_data, lint_setting, metric_setting, user):
        """通过基础配置创建方案
        """
        scan_dirs = validated_data.pop("scandir_set", [])
        checkprofile_id = lint_setting.pop("checkprofile_id", 0)
        lint_setting.pop("labels", None)
        scan_scheme = core.ScanSchemeManager.init_scheme(repo_id=repo_id, user=user, **validated_data)
        core.ScanSchemeManager.create_scheme_lint_setting(scan_scheme, user=user, **lint_setting)
        core.ScanSchemeManager.create_scheme_metric_setting(scan_scheme, user=user, **metric_setting)
        core.ScanSchemeManager.create_scheme_scan_dirs(scan_scheme, scan_dirs)
        if checkprofile_id == 0:
            # 创建规则集
            checkprofile = core.ScanSchemeManager.create_default_check_profile(
                scan_scheme, user=user, labels=validated_data.get("labels"))
            checkprofile_id = checkprofile or None  # 规则集可能为空
        else:
            # 拷贝规则集
            checkprofile_id = core.ScanSchemeManager.copy_from_check_profile(
                scan_scheme, from_checkprofile_id=checkprofile_id, user=user)
        core.ScanSchemeManager.update_check_profile(scan_scheme, checkprofile_id, user=user)
        core.ScanSchemeManager.set_default_scanscheme(scan_scheme)
        OperationRecordHandler.add_scanscheme_operation_record(scan_scheme, "创建扫描方案", user, validated_data)
        return scan_scheme

    def create(self, validated_data):
        """创建新的扫描方案
        """
        request = self.context.get("request")
        user = request.user if request else None
        repo_id = self.context["view"].kwargs.get("repo_id")
        logger.info("[Repo: %s] create scheme, validated_data: %s" % (repo_id, validated_data))
        templates = validated_data.pop("templates", [])
        lint_setting = validated_data.pop("lintbasesetting", {})
        metric_setting = validated_data.pop("metricsetting", {})
        if templates:
            logger.info("[Repo: %s] create scheme with templates: %s" % (repo_id, templates))
            return self.create_from_templates(
                repo_id, templates, user, **validated_data
            )
        else:
            logger.info("[Repo: %s] create scheme with settings" % repo_id)
            return self.create_from_settings(repo_id, validated_data, lint_setting, metric_setting, user)


class ScanSchemeInitialSerializer(serializers.Serializer):
    """扫描方案初始化 - 用于代码库初始化扫描方案
    """
    name = serializers.CharField(max_length=128, help_text="扫描方案名称", allow_null=True, allow_blank=True)
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, required=False)
    lint_enabled = serializers.BooleanField(help_text="启用代码扫描", default=False)
    cc_scan_enabled = serializers.BooleanField(help_text="启用圈复杂度", default=False)
    dup_scan_enabled = serializers.BooleanField(help_text="启用重复代码", default=False)
    cloc_scan_enabled = serializers.BooleanField(help_text="启用代码统计", default=False)
    build_cmd = serializers.CharField(help_text="编译命令, 咨询项目的开发,如果还有问题联系bensonqin或yalechen",
                                      allow_null=True, allow_blank=True)
    envs = serializers.CharField(help_text="环境变量", allow_null=True, allow_blank=True, )
    pre_cmd = serializers.CharField(max_length=512, help_text="前置命令, 项目编译前需要执行的命令", allow_null=True,
                                    allow_blank=True)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all(),
                                       required=False, allow_null=True)
    labels = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(),
                                                required=False, many=True, write_only=True)


class ScanSchemeCopySerializer(serializers.Serializer):
    """扫描方案copy序列化
    """
    name = serializers.CharField(max_length=128, help_text="扫描方案名称")
    ref_scheme = serializers.SlugRelatedField(slug_field="id", help_text="拷贝的扫描方案编号",
                                              queryset=models.ScanScheme.objects.all())

    def validate_name(self, name):
        repo_id = self.context["view"].kwargs.get("repo_id")
        if models.ScanScheme.objects.filter(name=name, repo=repo_id):
            raise serializers.ValidationError("该名称已被使用")
        return name

    def validate_ref_scheme(self, ref_scheme):
        request = self.context.get("request")
        user = request.user if request else None
        # 模板，且没有权限则raise
        org_sid = self.context["view"].kwargs.get("org_sid")
        if not ref_scheme.repo and not core.ScanSchemePermManager.check_user_view_perm(ref_scheme, user, org_sid):
            raise serializers.ValidationError("没有使用该方案模板权限")
        return ref_scheme


class ScanBranchSerializer(serializers.Serializer):
    """扫描分支列表
    """
    branch = serializers.CharField(read_only=True)
    schemes = serializers.SerializerMethodField(read_only=True)

    def get_schemes(self, branch_data):
        """获取扫描方案列表
        """
        repo_id = self.context["view"].kwargs.get("repo_id")
        schemes = []
        branch_projects = models.Project.objects.select_related("scan_scheme"). \
            only("scan_scheme_id", "scan_scheme__name").filter(repo_id=repo_id, branch=branch_data["branch"])
        for branch_project in branch_projects:
            schemes.append({
                "project_id": branch_project.id,
                "scan_scheme_id": branch_project.scan_scheme_id,
                "scan_scheme_name": branch_project.scan_scheme.name
            })
        return schemes


class RepoProjectInitialSerializer(serializers.Serializer):
    """项目初始化序列化，用于首次创建项目
    """
    id = serializers.ReadOnlyField()
    branch = serializers.CharField(max_length=200, help_text="扫描分支")
    scan_scheme = ScanSchemeInitialSerializer(help_text="扫描方案初始化参数", required=False)
    scan_path = serializers.CharField(max_length=512, help_text="扫描路径",
                                      required=False, allow_null=True, allow_blank=True)
    global_scheme_id = serializers.IntegerField(help_text="全局扫描方案编号",
                                                required=False, write_only=True, allow_null=True)
    custom_scheme_name = serializers.CharField(help_text="自定义方案名称",
                                               max_length=128, write_only=True, required=False)
    repo = RepositorySerializer(read_only=True)

    def validate_global_scheme_id(self, global_scheme_id):
        """校验global_scheme_id数据有效性
        """
        user = self.context["request"].user
        if not global_scheme_id:
            return global_scheme_id
        global_scheme = models.ScanScheme.objects.filter(repo__isnull=True, id=global_scheme_id).first()
        if not global_scheme:
            raise serializers.ValidationError("方案模板不存在")
        org_sid = self.context["view"].kwargs.get("org_sid")
        if not core.ScanSchemePermManager.check_user_view_perm(global_scheme, user, org_sid):
            raise exceptions.NotFound({"cd_error": "方案模板不存在"})
        else:
            return global_scheme

    def validate(self, attrs):
        """校验参数
        """
        scan_scheme = attrs.get("scan_scheme")
        global_scheme_id = attrs.get("global_scheme_id")
        if not scan_scheme and not global_scheme_id:
            raise exceptions.ValidationError({"cd_error": "需填写初始化方案参数或方案模板编号"})
        return attrs

    def check_branch_validate(self, repo, branch):
        """检查分支是否存在
        """
        if repo.scm_type == models.Repository.ScmTypeEnum.GIT:
            scm_url = "%s#%s" % (repo.get_scm_url_with_auth(), branch)
        else:
            scm_url = "%s/%s" % (repo.get_scm_url_with_auth(), branch)
        logger.info("check branch validate: %s" % scm_url)
        scm_client = core.ScmClientManager.get_scm_client_with_repo(repo, scm_url=scm_url)
        try:
            scm_client.branch_check()
        except scm.ScmNotFoundError:
            raise serializers.ValidationError("代码库分支不存在")
        except scm.ScmAccessDeniedError:
            raise serializers.ValidationError("代码库帐号无权限")
        except scm.ScmClientError:
            raise serializers.ValidationError("代码库密码错误")
        except Exception as e:
            logger.exception("check branch validate exception: %s" % e)
            raise serializers.ValidationError("代码库及帐号不匹配")

    def create(self, validated_data):
        """创建扫描方案、分支

        创建方案完成后，如果没有方案，则设置为默认方案
        """
        repo_id = self.context["view"].kwargs.get("repo_id")
        request = self.context.get("request")
        user = request.user if request else None
        repo = models.Repository.objects.get(id=repo_id)
        # 1. 判断已经接入项目
        if models.Project.objects.filter(repo_id=repo_id).count() > 0:
            raise serializers.ValidationError("当前代码库已经存在项目，请勿重复初始化")
        # 2. 校验分支有效性
        self.check_branch_validate(repo, validated_data["branch"])
        scan_scheme_data = validated_data.pop("scan_scheme", None)
        global_scheme = validated_data.pop("global_scheme_id", None)
        custom_scheme_name = validated_data.pop("custom_scheme_name", None)
        # 3. 创建扫描方案和项目
        with transaction.atomic():
            # 使用模板创建方案
            if global_scheme:
                custom_scheme_name = custom_scheme_name if custom_scheme_name else global_scheme.name
                scan_scheme = core.ScanSchemeManager.create_scheme_with_ref_scheme(
                    repo.id, global_scheme, user=user, name=custom_scheme_name)
                OperationRecordHandler.add_project_operation_record(
                    scan_scheme, "使用参照模板[%s-%s]创建扫描方案[%s]" % (
                        global_scheme.id, global_scheme.name, scan_scheme.name),
                    user, {})
            else:
                # 创建扫描方案
                scan_scheme = core.ScanSchemeManager.create_init_scheme(repo.id, user=user, **scan_scheme_data)
                OperationRecordHandler.add_project_operation_record(
                    scan_scheme, "创建建扫描方案[%s]" % scan_scheme.name, user, scan_scheme_data)
            # 设置默认扫描方案，如果同时有多个方案正在初始化，可能会失败
            core.ScanSchemeManager.set_default_scanscheme(scan_scheme)
            # 创建项目
            # project = models.Project.objects.create(repo=repo, branch=validated_data["branch"],
            #                                         scan_scheme=scan_scheme, creator=user)
            project, _ = core.ProjectManager.create_project(
                repo=repo, scan_scheme=scan_scheme, branch=validated_data["branch"],
                scan_path=validated_data.get("scan_path"), creator=user)
            # 在Analysis Server创建项目
            try:
                core.ProjectManager.create_project_on_analysis_server(project, user)
            except Exception as err:
                logger.exception("create project on analysis server failed: %s" % str(err))
                raise serializers.ValidationError({"cd_error": "创建项目失败，请稍后重试"})
        if user:
            OperationRecordHandler.add_scanscheme_operation_record(
                scan_scheme, "创建扫描方案-%s" % scan_scheme.name, user, validated_data)
            OperationRecordHandler.add_project_operation_record(
                project, "创建分支项目-%s" % project.branch, user, validated_data)
        return project


class ProjectSimpleSerializer(CDBaseModelSerializer):
    """扫描项目简略序列化
    """
    scan_scheme = ScanSchemeSimpleSerializer(read_only=True)
    project_url = serializers.SerializerMethodField(read_only=True)
    creator_info = CodedogUserInfoSerializer(source="creator", read_only=True)

    class Meta:
        model = models.Project
        fields = "__all__"

    def get_project_url(self, project):
        return "%s/repos/%s/projects/%s" % (settings.LOCAL_DOMAIN, project.repo_id, project.id)


class ProjectSerializer(CDBaseModelSerializer):
    """扫描项目序列化
    """
    scan_path = serializers.CharField(max_length=512, help_text="扫描路径",
                                      required=False, allow_null=True, allow_blank=True)
    scan_scheme_id = serializers.PrimaryKeyRelatedField(queryset=models.ScanScheme.objects.all(), allow_null=True,
                                                        help_text="扫描方案", write_only=True, required=False)
    global_scheme_id = serializers.IntegerField(help_text="全局扫描方案编号",
                                                required=False, write_only=True, allow_null=True)
    custom_scheme_name = serializers.CharField(help_text="自定义方案名称",
                                               max_length=128, write_only=True, required=False)
    project_key = serializers.ReadOnlyField()
    repo = RepositorySimpleSerializer(read_only=True)
    scan_scheme = ScanSchemeSimpleSerializer(read_only=True)

    def validate_scan_scheme_id(self, scan_scheme):
        """校验scan_scheme数据有效性
        :param scan_scheme: int
        :return: int
        """
        repo_id = self.context["view"].kwargs.get("repo_id")
        user = self.context["request"].user
        if not scan_scheme:
            return scan_scheme
        if not models.ScanScheme.objects.filter(repo_id=repo_id, id=scan_scheme.id):
            raise serializers.ValidationError("当前代码库不存在该扫描方案")
        if not core.ScanSchemeManager.check_scheme_usable_permission(scan_scheme, user):
            raise exceptions.PermissionDenied("您没有执行该操作的权限，该扫描方案已私有化，"
                                              "您不在该方案权限配置的关联分支项目权限成员列表中！！！")
        return scan_scheme

    def validate_global_scheme_id(self, global_scheme_id):
        """校验global_scheme_id数据有效性
        """
        user = self.context["request"].user
        if not global_scheme_id:
            return global_scheme_id
        global_scheme = models.ScanScheme.objects.filter(repo__isnull=True, id=global_scheme_id).first()
        if not global_scheme:
            raise serializers.ValidationError("方案模板不存在")
        org_sid = self.context["view"].kwargs.get("org_sid")
        if not core.ScanSchemePermManager.check_user_view_perm(global_scheme, user, org_sid):
            raise exceptions.NotFound({"cd_error": "方案模板不存在"})
        else:
            return global_scheme

    def check_branch_validate(self, repo, branch):
        """检查分支是否存在
        """
        if repo.scm_type == models.Repository.ScmTypeEnum.GIT:
            scm_url = "%s#%s" % (repo.get_scm_url_with_auth(), branch)
        else:
            scm_url = "%s/%s" % (repo.get_scm_url_with_auth(), branch)
        logger.info("check branch validate: %s" % scm_url)
        scm_client = core.ScmClientManager.get_scm_client_with_repo(repo, scm_url=scm_url)
        try:
            scm_client.branch_check()
        except scm.ScmNotFoundError:
            raise serializers.ValidationError({"cd_error": "代码库分支不存在"})
        except scm.ScmAccessDeniedError:
            raise serializers.ValidationError({"cd_error": "代码库帐号无权限"})
        except scm.ScmClientError:
            raise serializers.ValidationError({"cd_error": "代码库密码错误"})
        except Exception as e:
            logger.exception("check branch validate exception: %s" % e)
            raise serializers.ValidationError({"cd_error": "代码库及帐号不匹配"})

    def validate(self, attrs):
        """请求参数校验
        """
        repo_id = self.context["view"].kwargs.get("repo_id")
        scan_scheme = attrs.get("scan_scheme_id", None)
        global_scheme = attrs.get("global_scheme_id", None)
        if not global_scheme and not scan_scheme:
            raise serializers.ValidationError({"cd_error": "未指定扫描方案模板或扫描方案"})
        if global_scheme:
            custom_scheme_name = attrs.get("custom_scheme_name", None)
            if not custom_scheme_name:
                custom_scheme_name = global_scheme.name
            if models.ScanScheme.objects.filter(repo_id=repo_id, name=custom_scheme_name):
                raise serializers.ValidationError({"cd_error": "当前代码库已存在方案名称[%s]，请调整后重试" % custom_scheme_name})
        return serializers.ModelSerializer.validate(self, attrs)

    class Meta:
        model = models.Project
        fields = "__all__"

    def create(self, validated_data):
        """创建项目
        """
        repo_id = self.context["view"].kwargs.get("repo_id")
        request = self.context.get("request")
        user = request.user if request else None
        branch = validated_data.pop("branch")
        scan_scheme = validated_data.pop("scan_scheme_id", None)
        global_scheme = validated_data.pop("global_scheme_id", None)
        custom_scheme_name = validated_data.pop("custom_scheme_name", None)

        repo = models.Repository.objects.get(id=repo_id)
        # if core.RepositoryManager.check_repo_migrating(repo):
        #     logger.error("[Repo: %s] 代码库迁移中，无法创建新项目..." % repo.id)
        #     raise serializers.ValidationError("当前代码库正在进行数据迁移，请稍后再试")
        self.check_branch_validate(repo, branch)

        if global_scheme:
            custom_scheme_name = custom_scheme_name if custom_scheme_name else global_scheme.name
            scan_scheme = core.ScanSchemeManager.create_scheme_with_ref_scheme(
                repo.id, global_scheme, user=user, name=custom_scheme_name)
            OperationRecordHandler.add_project_operation_record(
                scan_scheme, "参照模板[%s-%s]创建扫描方案[%s]" % (
                    global_scheme.id, global_scheme.name, scan_scheme.name),
                user, validated_data)

        # 避免请求失败异常
        with transaction.atomic():
            scan_project, created = core.ProjectManager.create_project(
                repo=repo, scan_scheme=scan_scheme, branch=branch,
                scan_path=validated_data.get("scan_path"),
                creator=user, created_from=validated_data.get("created_from", models.Project.CreatedFromEnum.WEB))
            if created:
                try:
                    core.ProjectManager.create_project_on_analysis_server(scan_project, user)
                except Exception as err:
                    logger.exception("create project on analysis server failed: %s" % str(err))
                    raise serializers.ValidationError({"cd_error": "创建项目失败，请稍后重试"})

        if user:
            OperationRecordHandler.add_project_operation_record(scan_project, "创建项目", user, validated_data)
        return scan_project


class ProjectUpdatetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ['status']

    def update(self, instance, validated_data):
        """更新项目状态
        """
        user = self.context["request"].user
        status = validated_data.get("status")
        if status == models.Project.StatusEnum.ARCHIVED_WITHOUT_CLEAN:
            instance.update_remark({
                "archived_time": str(localnow()),
                "clean_time": str(localnow() + settings.PROJECT_ARCHIVE_CLEAN_TIMEOUT)})
        elif status == models.Project.StatusEnum.ACTIVE \
                and instance.status in [
            models.Project.StatusEnum.ARCHIVED,
            models.Project.StatusEnum.ARCHIVING,
            models.Project.StatusEnum.ARCHIVED_WITHOUT_CLEAN
        ]:
            raise serializers.ValidationError({"cd_error": "归档项目无法更新状态"})
        instance.status = status
        instance.save()
        OperationRecordHandler.add_project_operation_record(
            instance, "更新项目状态", user.username, message=validated_data
        )
        return instance


class ProjectBranchNameSerializer(serializers.Serializer):
    """分支项目序列化
    """
    branch = serializers.CharField(read_only=True, help_text="分支名称")


class TaskNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'name', 'get_enabled_display', 'get_state_display']


class ProjectTaskBriefSerializer(serializers.ModelSerializer):
    result_code_msg = serializers.CharField(read_only=True)
    waiting_time = serializers.DurationField(read_only=True)
    execute_time = serializers.DurationField(read_only=True)
    params_path = OnlySuperAdminReadField()
    result_path = OnlySuperAdminReadField()
    task_name = serializers.SerializerMethodField()
    node = TaskNodeSerializer()

    def get_task_name(self, task):
        user = self.context["request"].user
        if user and user.is_superuser:
            return task.task_name
        checktool = CheckTool.objects.filter(name=task.task_name).first()
        task_name = checktool.display_name if checktool and checktool.show_display_name else None
        return task_name

    class Meta:
        model = job_models.Task
        exclude = ['exec_tags', 'progress_rate']


class JobRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.Job
        fields = ['remarks']


class ProjectJobSerializer(serializers.ModelSerializer):
    repo_scm_url = serializers.SerializerMethodField()

    def get_repo_scm_url(self, project):
        """获取代码库地址
        """
        return project.repo.scm_url

    class Meta:
        model = models.Project
        fields = ['id', 'branch', 'repo_id', 'scan_scheme', 'repo_scm_url', 'scan_path']


class ProjectJobDetailSerializer(serializers.ModelSerializer):
    task_set = ProjectTaskBriefSerializer(many=True, read_only=True)
    result_code_msg = serializers.CharField(read_only=True)
    waiting_time = serializers.DurationField(read_only=True)
    execute_time = serializers.DurationField(read_only=True)
    project = ProjectJobSerializer(read_only=True)
    context_path = OnlySuperAdminReadField()

    class Meta:
        model = job_models.Job
        exclude = ['result_path']


class ProjectTaskProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.TaskProgress
        fields = '__all__'


class TaskDetailSerializer(ProjectTaskBriefSerializer):
    taskprogress_set = ProjectTaskProgressSerializer(many=True, read_only=True)
    tag = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = job_models.Task
        exclude = ['exec_tags', 'processes', 'progress_rate']


class ProjectScanPuppyIniSerializer(serializers.Serializer):
    codedog_env = serializers.CharField(help_text="服务端地址", required=False, allow_null=True, allow_blank=True)
    source_dir = serializers.CharField(help_text="代码地址")
    total_scan = serializers.BooleanField(label="是否全量扫描", help_text="是否全量扫描", default=False)


class SchemeTemplateCheckRuleSerializer(serializers.Serializer):
    checkrule_id = serializers.IntegerField(help_text="规则ID")
    severity = serializers.ChoiceField(choices=CheckRule.SEVERITY_CHOICES,
                                       help_text="严重级别，1致命，2错误，3警告，4提示", required=False)
    rule_params = serializers.CharField(help_text="规则参数", required=False)
    state = serializers.ChoiceField(choices=PackageMap.STATE_CHOICES,
                                    help_text="状态，1生效中，2已屏蔽", required=False)

    def validate(self, attrs):
        # 校验规则，存在则使用该规则
        checkrule_id = attrs.get('checkrule_id', None)
        if checkrule_id:  # 否则采用ID获取规则
            checkrule = CheckRule.objects.filter(id=checkrule_id).first()
            if not checkrule:
                raise serializers.ValidationError(
                    {'detail': 'checkrule_id：%s未匹配到对应规则' % checkrule_id})
        else:
            raise serializers.ValidationError(
                {'detail': '需要checkrule_id参数'})
        attrs['checkrule'] = checkrule
        return attrs


class ScanSchemeTemplateSerializer(CDBaseModelSerializer):
    """扫描方案模板序列化
    """
    tag = serializers.SlugRelatedField(queryset=ExecTag.objects.all(), help_text="关联节点标签", slug_field="name",
                                       required=False, allow_null=True)
    labels = serializers.SlugRelatedField(queryset=Label.objects.all(), slug_field="name", many=True)
    basic_conf = serializers.JSONField(help_text="基础配置", required=False)
    lint_conf = serializers.JSONField(help_text="扫描配置", required=False)
    metric_conf = serializers.JSONField(help_text="度量配置", required=False)
    profile_conf = serializers.ReadOnlyField(help_text="规则集配置")
    checkrule_list = SchemeTemplateCheckRuleSerializer(help_text="自定义规则", required=False, allow_null=True, many=True)
    public = serializers.BooleanField(help_text="是否开放", default=False, required=False)

    owners = serializers.SlugRelatedField(
        slug_field="username", read_only=True, many=True)
    owner_list = serializers.ListField(
        child=serializers.CharField(max_length=16), help_text="负责人成员列表", write_only=True, required=False,
        allow_null=True)

    def to_representation(self, instance):
        """返回的conf_content为json格式
        """
        response = super().to_representation(instance)
        if response["basic_conf"] is not None:
            response["basic_conf"] = json.loads(response["basic_conf"])
        if response["lint_conf"] is not None:
            response["lint_conf"] = json.loads(response["lint_conf"])
        if response["metric_conf"] is not None:
            response["metric_conf"] = json.loads(response["metric_conf"])
        return response

    def create(self, validated_data):
        """创建扫描方案模板
        """
        request = self.context["request"]
        user = request.user
        owner_list = validated_data.pop("owner_list", []) + [user.username]
        owners = User.objects.filter(username__in=owner_list)
        scheme_template = core.ScanSchemeTemplateManager.create_scheme_template(validated_data, owners, user)
        OperationRecordHandler.add_schemetemplate_operation_record(scheme_template, "创建扫描方案模板", user,
                                                                   validated_data)
        return scheme_template

    def update(self, instance, validated_data):
        """更新扫描方案模板
        """
        request = self.context["request"]
        user = request.user
        owner_list = validated_data.pop("owner_list", [])
        owners = User.objects.filter(username__in=owner_list)
        scheme_template = core.ScanSchemeTemplateManager.update_scheme_template(instance, validated_data, owners, user)
        OperationRecordHandler.add_schemetemplate_operation_record(scheme_template, "修改扫描方案模板", user,
                                                                   validated_data)
        return scheme_template

    class Meta:
        model = models.ScanSchemeTemplate
        fields = "__all__"


class ApiRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["id", "scm_url", "name", "scm_type"]


class APIProjectsSerializer(CDBaseModelSerializer):
    """api创建项目
    {
        "name": "",
        "scm_type": null,
        "scm_url": "",
        "scm_username": "",
        "scm_password": "",
        "tag": null,
        "scm_initial_revision": "",
        "admins": [],
        "users": [],
        "languages": []
    }
    """
    scm_url = serializers.CharField(max_length=400, label="代码库地址", help_text="代码库地址，分支用#间隔", write_only=True)
    scan_path = serializers.CharField(max_length=512, help_text="扫描路径",
                                      required=False, allow_null=True, allow_blank=True)
    scm_type = serializers.ChoiceField(label="代码库类型", help_text="git 或者 svn",
                                       choices=models.Repository.SCM_TYPE_CHOICES)
    scm_platform = serializers.ChoiceField(label="代码库平台类型", choices=scm.SCM_PLATFORM_CHOICES,
                                           required=False, default=scm.ScmPlatformEnum.GIT_OA,
                                           write_only=True, allow_null=True)
    auth_type = serializers.ChoiceField(label="鉴权类型", help_text="账号密码", required=False, write_only=True,
                                        choices=models.ScmAuth.SCM_AUTH_TYPE_CHOICES,
                                        default=models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
    scm_username = serializers.CharField(max_length=32, label="代码库帐号", help_text="代码库帐号", required=False,
                                         allow_null=True, write_only=True)
    scm_password = serializers.CharField(max_length=64, label="代码库密码", help_text="代码库密码", required=False,
                                         allow_null=True, write_only=True)
    admins = serializers.ListField(child=serializers.CharField(max_length=64, label="用户名", help_text="用户名"),
                                   label="管理员列表", help_text="管理员列表", required=False, allow_null=True, write_only=True)
    users = serializers.ListField(child=serializers.CharField(max_length=64, label="用户名", help_text="用户名"),
                                  label="成员列表", help_text="成员列表", required=False, allow_null=True, write_only=True)
    # 初始化设置字段
    name = serializers.CharField(max_length=128, label="代码库名称", help_text="代码库名称",
                                 required=False, allow_null=True, write_only=True)
    scheme_templates = serializers.ListField(child=serializers.CharField(max_length=128), help_text="模板名称",
                                             write_only=True, required=False, allow_null=True)
    scheme_id = serializers.IntegerField(help_text="扫描方案编号", required=False, allow_null=True, write_only=True)
    scheme_name = serializers.CharField(max_length=128, label="扫描方案名称", required=False,
                                        help_text="如果存在该方案则直接复用，为空表示使用默认方案", allow_blank=True, write_only=True)
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all(), required=False,
                                       allow_null=True, write_only=True)
    lint_enabled = serializers.BooleanField(label="启用代码扫描", help_text="启用代码扫描（仅新建扫描方案时生效）",
                                            default=False, write_only=True)
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(), help_text="扫描语言（仅新建扫描方案时生效）",
                                             slug_field="name", many=True, required=False, write_only=True)
    labels = serializers.SlugRelatedField(queryset=Label.objects.all(), slug_field='name', many=True,
                                          required=False, allow_null=True, write_only=True, help_text="标签（仅新建扫描方案时生效）")
    cc_scan_enabled = serializers.BooleanField(label="启用圈复杂度", help_text="启用圈复杂度（仅新建扫描方案时生效）",
                                               default=False, write_only=True)
    dup_scan_enabled = serializers.BooleanField(label="启用重复代码", help_text="启用重复代码（仅新建扫描方案时生效）",
                                                default=False, write_only=True)
    cloc_scan_enabled = serializers.BooleanField(label="启用代码统计", help_text="启用代码统计（仅新建扫描方案时生效）",
                                                 default=False, write_only=True)
    refer_scheme_id = serializers.PrimaryKeyRelatedField(queryset=models.ScanScheme.objects.all(),
                                                         help_text="参照扫描方案", required=False, allow_null=True)
    description = serializers.CharField(max_length=512, label="扫描方案详细描述", required=False,
                                        allow_null=True, allow_blank=True, write_only=True)
    # 只读字段
    repo = ApiRepositorySerializer(read_only=True)
    project_id = serializers.IntegerField(source="id", read_only=True)
    project_url = serializers.SerializerMethodField()
    scm_auth = serializers.DictField(source="simple_auth_info", read_only=True)
    scan_scheme_name = serializers.StringRelatedField(source="scan_scheme.name", read_only=True)

    def get_project_url(self, project):
        return "%s/repos/%s/projects/%s" % (settings.LOCAL_DOMAIN, project.repo.id, project.id)

    def validate_scm_password(self, value):
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def validate_admins(self, value):
        if not isinstance(value, list):
            value = json.loads(value)
        result = []
        for name in value:
            if not name:
                continue
            result.append(name.split("(")[0])
        if not value:
            result = [self.context["request"].user]
        return result

    def validate_users(self, value):
        if not isinstance(value, list):
            value = json.loads(value)
        result = []
        for name in value:
            if not name:
                continue
            result.append(name.split("(")[0])
        return result

    def get_data_from_view_kwargs(self, **view_kwargs):
        """通过view_kwargs获取数据
        """
        return {}

    def create_repo(self, request, repo_url, created_from, validated_data, ssh_url=None, **view_data):
        """创建代码库并设置相关权限
        """
        logger.info("create repo with url: %s" % repo_url)
        admins = []
        if validated_data.get("admins"):
            admins = validated_data["admins"]
        try:
            repo = core.RepositoryManager.create_repository(
                scm_type=validated_data["scm_type"],
                scm_url=repo_url,
                ssh_url=ssh_url,
                name=validated_data.get("name"),
                created_from=created_from,
                user=request.user,
                admins=admins
            )
        except Exception as err:
            logger.exception("create repo failed, repo_url: %s, err: %s" % (repo_url, err))
            raise serializers.ValidationError({"cd_error": "创建代码库失败-%s" % str(err)})

        OperationRecordHandler.add_repo_operation_record(repo, "通过%s创建代码库" % created_from, request.user, {})
        if validated_data.get("admins"):
            logger.info("[Repo: %s] set repo admins: %s" % (repo.id, admins))
            repo.assign_members_perm(admins, models.Repository.PermissionEnum.ADMIN)
        logger.info("[Repo: %s] set repo user: %s" % (repo.id, validated_data.get("users", [])))
        repo.assign_members_perm(validated_data.get("users", []), models.Repository.PermissionEnum.USER)
        return repo

    def create_repo_auth(self, repo, user, validated_data):
        """创建代码库鉴权
        """
        if not validated_data.get("scm_username") or not validated_data.get("scm_password"):
            return
        scm_auth_type = validated_data.get("auth_type")
        scm_username = validated_data.get("scm_username")
        scm_password = validated_data.get("scm_password")
        scm_account = models.ScmAccount.objects.filter(user=user, scm_username=scm_username,
                                                       auth_origin_id=settings.DEFAULT_ORIGIN_ID).first()
        if not scm_account:
            scm_account = models.ScmAccount.objects.create(
                user=user,
                scm_username=scm_username,
                scm_password=scm_password,
                auth_origin_id=settings.DEFAULT_ORIGIN_ID
            )
            logger.info("[Repo: %s][User: %s] create scm auth: %s" % (repo.id, user, scm_username))
        core.ScmAuthManager.create_repository_auth(repository=repo, user=user,
                                                   scm_auth_type=scm_auth_type,
                                                   scm_account=scm_account)
        OperationRecordHandler.add_repo_operation_record(repo, "更新代码库鉴权", user,
                                                         {"scm_username": scm_username, "scm_auth_type": scm_auth_type})

    def create_scheme_with_template(self, repo_id, scheme_template_list, user, **kwargs):
        """通过模板创建扫描方案
        """
        scheme_templates = models.ScanSchemeTemplate.objects.filter(name__in=scheme_template_list)
        if not scheme_templates:
            raise serializers.ValidationError({"cd_error": "方案模板不存在: %s" % scheme_template_list})
        scheme_template_ids = list(scheme_templates.values_list("id", flat=True).order_by("id"))
        logger.info("[Repo: %s][User: %s] create scheme with templates: %s" % (repo_id, user, scheme_templates))
        merged_scheme_template = core.ScanSchemeTemplateManager.merge_scheme_template(scheme_templates)
        merged_scheme_template.update(**kwargs)
        scan_scheme = core.ScanSchemeManager.create_scheme_with_template(
            repo_id, merged_scheme_template, kwargs.get("languages", []), user,
            refer_template_ids=scheme_template_ids)
        OperationRecordHandler.add_scanscheme_operation_record(
            scan_scheme, "通过方案模板创建扫描方案[%s]" % scan_scheme.name, user,
            merged_scheme_template)
        return scan_scheme

    def check_scm_auth(self, scm_url, validated_data):
        """检查鉴权信息是否有效
        """
        logger.info("校验代码库[%s]鉴权有效性" % scm_url)
        scm_auth_type = validated_data.get("auth_type")
        scm_username = validated_data.get("scm_username")
        scm_password = validated_data.get("scm_password")
        scm_platform = validated_data.get("scm_platform")
        if not scm_username or not scm_password:
            logger.info("账号或密码为空，校验失败")
            return False
        scm_type = validated_data["scm_type"]
        scm_client = scm.ScmClient(
            scm_type, scm_url, scm_auth_type, username=scm_username, password=scm_password,
            scm_platform=scm_platform)
        try:
            scm_client.auth_check()
            return True
        except scm.ScmNotFoundError:
            logger.info("代码库地址不存在")
            return False
        except scm.ScmAccessDeniedError:
            logger.info("代码库账号无权限")
            return False
        except scm.ScmClientError:
            logger.info("代码库密码错误")
            return False
        except Exception as e:
            logger.info("auth check exception: %s" % e)
            return False

    def create(self, validated_data):
        view_kwargs = self.context["view"].kwargs
        request = self.context['request']
        # 1. 创建/查询代码库 + 添加成员到代码库成员
        scm_client = scm.ScmClient(validated_data["scm_type"], validated_data["scm_url"], "password")
        repo_url = scm_client.get_repository()
        repo_ssh_url = scm.ScmClient(validated_data["scm_type"], repo_url, "password").get_ssh_url()
        logger.debug("scm url format: %s => %s, ssh url: %s" % (validated_data["scm_url"], repo_url, repo_ssh_url))
        branch = scm_client.get_branch()
        view_data = self.get_data_from_view_kwargs(**view_kwargs)
        repo = core.RepositoryManager.get_repository(repo_url, **view_data)
        created_from = validated_data.get("created_from", models.Project.CreatedFromEnum.API)
        refer_scheme = validated_data.get("refer_scheme_id")
        if not repo:
            repo = self.create_repo(request, repo_url, created_from, validated_data, ssh_url=repo_ssh_url, **view_data)
            self.create_repo_auth(repo, request.user, validated_data)
        if self.check_scm_auth(repo_url, validated_data):
            repo.assign_perm(request.user.username, models.Repository.PermissionEnum.USER)
            OperationRecordHandler.add_repo_operation_record(repo, "通过SCM鉴权添加到代码库管理员", request.user,
                                                             {"scm_username": validated_data.get("scm_username")})
        # 2. 查询/新建扫描方案，根据语言及各项开关初始化扫描方案
        if validated_data.get("scheme_id"):
            try:
                scan_scheme = models.ScanScheme.objects.get(repo=repo, id=validated_data["scheme_id"])
            except models.ScanScheme.DoesNotExist:
                raise serializers.ValidationError("当前代码库没有该编号的扫描方案[%s]" % validated_data["scheme_id"])
            logger.info("get scan scheme with id: %s" % validated_data["scheme_id"])
        elif validated_data.get("scheme_name"):
            scan_scheme = models.ScanScheme.objects.filter(
                repo=repo, name=validated_data["scheme_name"]
            ).first()
            logger.info("get scan scheme with name: %s" % validated_data.get("scheme_name"))
            if not scan_scheme and validated_data.get("scheme_templates"):
                scan_scheme = self.create_scheme_with_template(repo.id, validated_data["scheme_templates"],
                                                               user=request.user,
                                                               name=validated_data.get("scheme_name"),
                                                               languages=validated_data.get("languages", []),
                                                               created_from=created_from)
                logger.info("create scan scheme with template: %s" % validated_data.get("scheme_template_list"))
        else:
            scan_scheme = core.ScanSchemeManager.get_default_scanscheme(repo.id)
            logger.info("scan scheme name not exist: %s, get default scheme: %s" % (
                validated_data.get("scheme_name"), scan_scheme))
        if not scan_scheme:
            if refer_scheme:
                logger.info("create scan scheme with refer scheme: %s" % refer_scheme)
                scan_scheme = core.ScanSchemeManager.create_scheme_with_ref_scheme(
                    repo_id=repo.id,
                    ref_scheme=refer_scheme,
                    user=request.user,
                    name=validated_data.get("scheme_name"),
                    created_from=created_from
                )
                OperationRecordHandler.add_scanscheme_operation_record(
                    scan_scheme, "通过%s拷贝扫描方案[%s]" % (created_from, refer_scheme.name), request.user, {})
            else:
                scan_scheme = core.ScanSchemeManager.create_init_scheme(
                    repo_id=repo.id,
                    user=request.user,
                    name=validated_data.get("scheme_name"),
                    languages=validated_data.get("languages"),
                    tag=validated_data.get("tag"),
                    lint_enabled=validated_data["lint_enabled"],
                    labels=validated_data.get("labels"),
                    cc_scan_enabled=validated_data["cc_scan_enabled"],
                    dup_scan_enabled=validated_data["dup_scan_enabled"],
                    cloc_scan_enabled=validated_data["cloc_scan_enabled"],
                    created_from=created_from,
                    description=validated_data.get("description")

                )
                logger.info("create init scan scheme: %s" % scan_scheme.name)
                OperationRecordHandler.add_scanscheme_operation_record(
                    scan_scheme, "通过%s创建扫描方案" % created_from, request.user, {})
            core.ScanSchemeManager.set_default_scanscheme(scan_scheme)  # 尝试设置为默认，如果已有，则无变化
        # 3. 创建项目，绑定分支和代码库方案
        # 注：使用事务，Analysis Server创建失败时可以重新创建
        with transaction.atomic():
            project, created = core.ProjectManager.create_project(
                repo=repo, scan_scheme=scan_scheme, branch=branch,
                scan_path=validated_data.get("scan_path"),
                creator=request.user, created_from=created_from,
            )
            if created:
                try:
                    core.ProjectManager.create_project_on_analysis_server(project, request.user)
                except Exception as err:
                    logger.exception("create project on analysis server failed: %s" % str(err))
                    raise serializers.ValidationError({"cd_error": "创建项目失败，请稍后重试"})
                project.save(user=request.user)
                OperationRecordHandler.add_project_operation_record(project, "通过%s创建项目" %
                                                                    created_from, request.user, {})
        return project

    class Meta:
        model = models.Project
        fields = "__all__"
        read_only_fields = ["branch", "status", "scan_scheme", "refer_project", "project_key"]


class ServerScanCreateSerializer(serializers.Serializer):
    """扫描启动序列化
    """
    incr_scan = serializers.BooleanField(help_text="是否增量", required=False)
    force_create = serializers.BooleanField(help_text="是否忽略已有任务强制启动", default=False, write_only=True)
    created_from = serializers.CharField(help_text="扫描渠道", required=False, default="tca_web")
