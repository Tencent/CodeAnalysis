# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 checktool serializers
"""
import logging

# 第三方
from rest_framework import serializers
from rest_framework.exceptions import ParseError

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers import base
from apps.scan_conf.core import CommonManager, CheckToolManager
from apps.authen.models import Organization
from apps.authen.serializers.base import ScmAuthCreateSerializer, ScmAuthSerializer
from apps.codeproj.core import ScmAuthManager

logger = logging.getLogger(__name__)


def get_and_check_view_org(self):
    """获取并校验视图中是否存在有效团队"""
    view = self.context.get("view")
    org_sid = view.kwargs.get("org_sid", None)
    org = Organization.objects.filter(org_sid=org_sid).first()
    if not org:
        raise ParseError("唯一标识为%s的团队不存在" % org_sid)
    return org


class CheckToolWhiteKeySerializer(base.CheckToolWhiteKeySerializer):
    """工具白名单序列化，可用于工具白名单添加
    """
    pass


class CheckToolWhiteKeyAddSerializer(base.CheckToolWhiteKeyAddSerializer):
    """工具白名单添加序列化
    """
    pass


class CheckToolWhiteKeyDeleteSerializer(base.CheckToolWhiteKeyDeleteSerializer):
    """工具白名单删除序列化
    """
    pass


class CheckToolSerializer(base.CheckToolSerializer):
    """工具简单序列化
    """
    pass


class CheckToolEditSeriaizer(CheckToolSerializer):
    """工具详情序列化，支持工具创建/更新
    """
    scan_app = serializers.SlugRelatedField(queryset=models.ScanApp.objects.all(), slug_field="name",
                                            required=False, help_text="scan_app")
    task_processes = serializers.SlugRelatedField(queryset=models.Process.objects.all(), slug_field="name",
                                                  many=True, required=False, help_text="工具子进程")
    scm_type = serializers.ChoiceField(label="代码库类型", help_text="git 或者 svn",
                                       choices=models.CheckTool.SCM_TYPE_CHOICES,
                                       default=models.CheckTool.ScmTypeEnum.GIT)
    scm_auth = ScmAuthCreateSerializer(write_only=True, help_text="关联授权信息", allow_null=True, required=False)

    def get_user(self):
        request = self.context.get("request")
        user = request.user if request else None
        # 从脚本执行
        if self.context.get("is_local_script", False) and self.context.get("user"):
            user = self.context.get("user")
        return user

    def validate(self, attrs):
        attrs["org"] = get_and_check_view_org(self)
        user = self.get_user()
        scm_type = attrs.get("scm_type")
        scm_auth = attrs.get("scm_auth")
        scm_url = attrs.get('scm_url')
        run_cmd = attrs.get('run_cmd')
        # 非超管，scm_url和run_cmd必填
        if not (user and user.is_superuser):
            if not scm_url:
                raise serializers.ValidationError({"scm_url": "工具代码库地址必填"})
            if not run_cmd:
                raise serializers.ValidationError({"run_cmd": "工具执行命令必填"})
        # 存在时则进行凭证校验
        if scm_url and scm_auth:
            # 校验凭证有效性
            credential_info = CommonManager.get_and_check_scm_auth(scm_auth, user, instance=self.instance)
            ScmAuthManager.check_scm_url_credential(scm_type, scm_url, credential_info)
        return super().validate(attrs)

    def _create_or_update(self, validated_data, instance=None):
        user = self.get_user()
        name = validated_data.pop("name")
        scm_auth = validated_data.pop("scm_auth", None)
        checktool = CheckToolManager.create_or_update(name, user, checktool=instance, **validated_data)
        # 保存账号信息
        if scm_auth:
            ScmAuthManager.create_checktool_auth(
                checktool, user, scm_auth_type=scm_auth.get("auth_type"),
                scm_account=scm_auth.get("scm_account"),
                scm_ssh_info=scm_auth.get("scm_ssh"),
                scm_oauth=scm_auth.get("scm_oauth"),
            )
        elif instance:
            # 更新时允许移除scm_auth
            checktool.scm_auth = None
            checktool.save(user=user)
        return checktool

    def create(self, validated_data):
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(validated_data, instance)

    class Meta:
        model = models.CheckTool
        read_only_fields = ["open_maintain", "open_user", "languages", "status"]
        exclude = ["users", "co_owners", "owners", "open_saas", "tool_key"]


class CheckToolDetailSeriaizer(CheckToolEditSeriaizer):
    """工具详情序列化，仅用于get，创建更新请使用CheckToolEditSeriaizer
    """
    scm_auth = ScmAuthSerializer(read_only=True)


class CheckToolStatusUpdateSerializer(base.CheckToolStatusUpdateSerializer):
    """用于更新工具运营状态
    """
    pass


class CheckToolRuleSerializer(base.CheckToolRuleSerializer):
    """工具规则序列化，支持工具规则创建/更新
    """
    pass


class CheckToolCustomRuleSerializer(CheckToolRuleSerializer):
    """工具自定义规则序列化，支持工具自定义规则创建/更新
    """

    def _create_or_update(self, validated_data, instance=None):
        validated_data["org"] = get_and_check_view_org(self)
        return super()._create_or_update(validated_data, instance=instance)


class ToolLibSerializer(base.ToolLibSerializer):
    """工具依赖序列化
    """
    pass


class ToolLibEditSerializer(base.ToolLibEditSerializer):
    """工具依赖详情序列化，支持工具依赖创建/更新序列化
    """

    def validate(self, attrs):
        attrs["org"] = get_and_check_view_org(self)
        return super().validate(attrs)


class ToolLibDetailSeriaizer(base.ToolLibDetailSeriaizer):
    """工具依赖详情序列化
    """
    pass


class ToolLibSchemeSerializer(base.ToolLibSchemeSerializer):
    """工具-依赖方案序列化，支持工具-依赖方案创建/更新
    """
    pass


class ToolLibMapSerializer(base.ToolLibMapSerializer):
    """工具-依赖方案-依赖映射序列化，支持依赖映射创建
    """
    pass


class ToolLibMapDetailSerializer(base.ToolLibMapDetailSerializer):
    """工具-依赖方案-依赖映射详情序列化
    """
    pass
