# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checkrule serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core import CommonManager, ToolLibMapManager, ToolLibSchemeManager, \
                                CheckToolManager, ToolLibManager
from apps.scan_conf.serializers.base.rule import CheckRuleSerializer
from apps.base.serializers import CDBaseModelSerializer
from apps.authen.models import Organization
from apps.authen.serializers.base import ScmAuthCreateSerializer, ScmAuthSerializer
from apps.authen.serializers.base_org import OrganizationSimpleSerializer
from apps.codeproj.core import ScmAuthManager

logger = logging.getLogger(__name__)


class CheckToolWhiteKeySerializer(serializers.ModelSerializer):
    """工具白名单序列化，可用于工具白名单添加
    """
    organization = serializers.SerializerMethodField()
    org_sid = serializers.SlugRelatedField(slug_field="org_sid", queryset=Organization.objects.all(),
                                           write_only=True, help_text="团队唯一标识")

    def get_organization(self, instance):
        org = CheckToolManager.get_org(instance.tool_key)
        if org:
            return OrganizationSimpleSerializer(instance=org).data
        return None

    def validate_org_sid(self, org):
        request = self.context.get("request")
        user = request.user if request else None
        if user and (user.is_superuser or user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org)):
            return org
        raise serializers.ValidationError("没有该团队管理员权限，添加工具白名单失败")

    def create(self, validated_data):
        view = self.context.get("view")
        checktool_id = view.kwargs.get("checktool_id")
        checktool = models.CheckTool.objects.filter(id=checktool_id).first()
        if not checktool:
            raise serializers.ValidationError("ID为%d的工具不存在" % checktool_id)
        org = validated_data.get("org_sid")
        tool_key = CheckToolManager.get_tool_key(org=org)
        instance, _ = CheckToolManager.add_white_key(tool_key=tool_key, tool_id=checktool.id)
        return instance

    class Meta:
        model = models.CheckToolWhiteKey
        fields = ["id", "tool_id", "organization", "org_sid"]
        read_only_fields = ["id", "tool_id", "organization"]


class CheckToolWhiteKeyAddSerializer(serializers.Serializer):
    """工具白名单添加序列化
    """
    organizations = serializers.SlugRelatedField(slug_field="org_sid", queryset=Organization.objects.all(),
                                                 many=True, help_text="团队唯一标识列表")

    def validate_organizations(self, orgs):
        request = self.context.get("request")
        user = request.user if request else None
        if not user:
            raise serializers.ValidationError("没有团队管理员权限，批量添加工具白名单失败")
        if user.is_superuser:
            return orgs
        for org in orgs:
            if not user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org):
                raise serializers.ValidationError("没有【团队: %s】的管理员权限，批量添加工具白名单失败" % org.name)
        return orgs


class CheckToolWhiteKeyDeleteSerializer(serializers.Serializer):
    """工具白名单删除序列化
    """
    whitelist = serializers.PrimaryKeyRelatedField(queryset=models.CheckToolWhiteKey.objects.all(), many=True,
                                                   help_text="工具白名单列表")


class CheckToolSerializer(CDBaseModelSerializer):
    """工具简单序列化
    """
    languages = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True, help_text="工具支持的语言")
    scan_app = serializers.SlugRelatedField(slug_field="name", read_only=True, help_text="scan_app")
    org_detail = serializers.SerializerMethodField()

    def get_org_detail(self, checktool):
        return CheckToolManager.get_org_detail(checktool)

    class Meta:
        model = models.CheckTool
        fields = ["id", "creator", "created_time", "modified_time", "languages", "build_flag", "status",
                  "display_name", "show_display_name", "description", "open_maintain", "open_user", "scan_app",
                  "org_detail", "license"]


class CheckToolStatusUpdateSerializer(serializers.Serializer):
    """用于更新工具运营状态
    """
    status = serializers.ChoiceField(label="工具状态", help_text="0正常运营，1暂停使用，2已下架，3体验运营",
                                     choices=models.CheckTool.STATUS_CHOICES)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        status = validated_data.get("status", instance.status)
        checktool = CheckToolManager.update_status(instance, status, user)
        return checktool


class CheckToolRuleSerializer(CheckRuleSerializer):
    """工具规则序列化，支持工具规则创建/更新
    """

    def validate_disable(self, value):
        if value and not self.initial_data.get("disabled_reason"):
            raise serializers.ValidationError("失效原因不可为空")
        return value

    def validate_owner(self, value):
        """校验owner，默认创建者加入到owner中
        """
        request = self.context.get("request")
        user = request.user
        if not value:
            result = user.username
        else:
            result = value.split("(")[0]
        return result

    def _create_or_update(self, validated_data, instance=None):
        """工具规则创建or更新
        """
        request = self.context.get("request")
        user = request.user if request else None
        view = self.context.get("view")
        checktool_id = view.kwargs.get("checktool_id")
        checktool = models.CheckTool.objects.filter(id=checktool_id).first()
        if not checktool:
            raise serializers.ValidationError("ID为%d的工具不存在" % checktool_id)
        real_name = validated_data.pop("real_name")
        checkrule = CheckToolManager.create_or_update_rule(
            checktool, real_name, user, checkrule=instance, **validated_data)
        return checkrule

    def create(self, validated_data):
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(validated_data, instance)

    class Meta:
        model = models.CheckRule
        exclude = ["tool_key"]
        read_only_fields = ["disabled_time"]


class ToolLibSerializer(CDBaseModelSerializer):
    """工具依赖序列化
    """

    class Meta:
        model = models.ToolLib
        fields = ["id", "creator", "created_time", "modified_time", "name", "description", \
                  "envs", "lib_type", "lib_os", "os"]


class ToolLibEditSerializer(CDBaseModelSerializer):
    """工具依赖详情序列化，支持工具依赖创建/更新序列化
    """

    scm_auth = ScmAuthCreateSerializer(write_only=True, help_text="关联授权信息", allow_null=True, required=False)
    envs = serializers.JSONField(help_text="环境变量", required=False)
    lib_os = serializers.CharField(help_text="依赖适用系统")

    def get_user(self):
        request = self.context.get("request")
        user = request.user if request else None
        # 从脚本执行
        if self.context.get("is_local_script", False) and self.context.get("user"):
            user = self.context.get("user")
        return user

    def validate_lib_type(self, lib_type):
        """非超管仅能创建私有依赖，超管可选择
        """
        user = self.get_user()
        if user and user.is_superuser:
            return lib_type
        return models.ToolLib.LibTypeEnum.PRIVATE

    def validate(self, attrs):
        scm_type = attrs.get("scm_type")
        scm_url = attrs.get("scm_url")
        # 工具依赖地址为link类型，则跳过scm_url鉴权
        if scm_type == models.ToolLib.ScmTypeEnum.LINK:
            return super().validate(attrs)
        # 对scm_url执行凭证鉴权处理
        user = self.get_user()
        scm_auth = attrs.get("scm_auth")
        # TODO: 后续实现scm_url连通性测试
        # 默认允许不传递凭证，传递凭证则对凭证进行校验
        if not scm_auth:
            # raise serializers.ValidationError({"scm_auth": "凭证为必填项"})
            return super().validate(attrs)
        # 校验凭证有效性
        credential_info = CommonManager.get_and_check_scm_auth(scm_auth, user, instance=self.instance)
        ScmAuthManager.check_scm_url_credential(scm_type, scm_url, credential_info)
        return super().validate(attrs)

    def _create_or_update(self, validated_data, instance=None):
        user = self.get_user()
        name = validated_data.pop("name")
        scm_auth = validated_data.pop("scm_auth", None)
        instance, _ = ToolLibManager.create_or_update(name, user, instance=instance, **validated_data)
        # 保存凭证信息
        if validated_data.get("scm_type") != models.ToolLib.ScmTypeEnum.LINK:
            if scm_auth:
                ScmAuthManager.create_toollib_auth(
                    instance, user, scm_auth_type=scm_auth.get("auth_type"),
                    scm_account=scm_auth.get("scm_account"),
                    scm_ssh_info=scm_auth.get("scm_ssh"),
                    scm_oauth=scm_auth.get("scm_oauth"),
                )
            elif instance:
                # 更新时允许移除scm_auth
                instance.scm_auth = None
                instance.save(user=user)
        return instance

    def create(self, validated_data):
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(validated_data, instance)

    class Meta:
        model = models.ToolLib
        exclude = ["lib_key"]


class ToolLibDetailSeriaizer(ToolLibEditSerializer):
    """工具依赖详情序列化
    """
    scm_auth = ScmAuthSerializer(read_only=True)


class ToolLibMapSerializer(serializers.ModelSerializer):
    """工具-依赖方案-依赖映射序列化，支持依赖映射创建
    """

    def validate(self, attrs):
        view = self.context.get("view")
        libscheme_id = view.kwargs.get("libscheme_id")
        libscheme = models.ToolLibScheme.objects.filter(id=libscheme_id).first()
        if not libscheme:
            raise serializers.ValidationError("ID为%d的工具依赖不存在" % libscheme_id)
        attrs["libscheme"] = libscheme
        # 校验依赖
        toollib = attrs.get("toollib")
        if not CheckToolManager.check_use_toollib_perm(libscheme.checktool, toollib):
            raise serializers.ValidationError("没有依赖%s权限" % toollib.name)
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        libscheme = validated_data.pop("libscheme")
        toollib = validated_data.pop("toollib")
        return ToolLibMapManager.create(libscheme, toollib, user, **validated_data)

    class Meta:
        model = models.ToolLibMap
        fields = "__all__"
        read_only_fields = ["libscheme", "pos"]


class ToolLibMapDetailSerializer(serializers.ModelSerializer):
    """工具-依赖方案-依赖映射详情序列化
    """

    toollib = ToolLibSerializer(read_only=True)

    class Meta:
        model = models.ToolLibMap
        fields = "__all__"
        read_only_fields = ["libscheme", "toollib", "pos"]


class ToolLibMapJsonSerializer(serializers.Serializer):
    """工具-依赖方案-依赖映射序列化
    """
    toollib = serializers.PrimaryKeyRelatedField(queryset=models.ToolLib.objects.all(), help_text="工具依赖")
    pos = serializers.IntegerField(help_text="序号", default=0)


class ToolLibSchemeSerializer(CDBaseModelSerializer):
    """工具-依赖方案序列化，支持工具-依赖方案创建/更新
    """
    tool_libs = ToolLibMapJsonSerializer(many=True, required=False, write_only=True)
    toollib_maps = ToolLibMapDetailSerializer(source="toollibmap", many=True, read_only=True)
    condition = serializers.CharField(max_length=128, allow_null=True, allow_blank=True)
    os = serializers.ListField(read_only=True)

    def validate(self, attrs):
        view = self.context.get("view")
        checktool_id = view.kwargs.get("checktool_id")
        checktool = models.CheckTool.objects.filter(id=checktool_id).first()
        if not checktool:
            raise serializers.ValidationError("ID为%d的工具不存在" % checktool_id)
        attrs["checktool"] = checktool
        tool_libs = attrs.get("tool_libs")
        # 校验依赖
        if tool_libs:
            exist_error = False
            error_msg = []
            for tool_lib in tool_libs:
                toollib = tool_lib.get("toollib")
                if not CheckToolManager.check_use_toollib_perm(checktool, toollib):
                    error_msg.append({"toollib": ["没有依赖%s权限" % toollib.name]})
                    exist_error = True
                else:
                    error_msg.append({})
            if exist_error:
                raise serializers.ValidationError({"tool_libs": error_msg})
        return super().validate(attrs)

    def _create_or_update(self, validated_data, instance=None):
        request = self.context.get("request")
        user = request.user if request else None
        checktool = validated_data.pop("checktool")
        tool_libs = validated_data.pop("tool_libs", [])
        instance, _ = ToolLibSchemeManager.create_or_update(checktool, user, tool_libs=tool_libs,
                                                            instance=instance, **validated_data)
        return instance

    def create(self, validated_data):
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(validated_data, instance)

    class Meta:
        model = models.ToolLibScheme
        fields = "__all__"
        read_only_fields = ["checktool", "pos"]
