# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base scheme serializers
"""

import logging

# 第三方 import
from rest_framework import serializers

# 项目内 import
from apps.codeproj import models
from apps.codeproj.core import ScanSchemeManager, ScanSchemePermManager
from apps.base.serializers import CDBaseModelSerializer
from apps.nodemgr.models import ExecTag
from apps.scan_conf.models import Label

from util.exceptions import ServerConfigError
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class SchemeTypeEnum:
    PERSONAL = 1
    ORG = 2
    PUBLIC = 3


REPOTYPE_CHOICES = (
    (SchemeTypeEnum.PERSONAL, "个人扫描方案模板"),
    (SchemeTypeEnum.ORG, "组织扫描方案模板"),
    (SchemeTypeEnum.PUBLIC, "公开扫描方案模板")
)


class GlobalScanSchemeTemplateCreateSerializer(CDBaseModelSerializer):
    """方案模板创建序列化
    """
    scheme_type = serializers.ChoiceField(
        write_only=True, help_text="模板类型，1表示个人扫描方案，2表示组织扫描方案，3表示系统模板",
        default=SchemeTypeEnum.PERSONAL, choices=REPOTYPE_CHOICES)
    languages = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Language.objects.all())
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all())
    labels = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(),
                                                required=False, many=True, write_only=True)
    lint_enabled = serializers.BooleanField(help_text="启用代码扫描", default=False)
    cc_scan_enabled = serializers.BooleanField(help_text="启用圈复杂度", default=False)
    dup_scan_enabled = serializers.BooleanField(help_text="启用重复代码", default=False)
    cloc_scan_enabled = serializers.BooleanField(help_text="启用代码统计", default=False)

    def validate_scheme_type(self, scheme_type):
        request = self.context.get("request")
        user = request.user if request else None
        if scheme_type == SchemeTypeEnum.PUBLIC and not (user and user.is_superuser):
            raise serializers.ValidationError("仅平台管理员才能创建系统分析方案模板")
        return scheme_type

    def validate(self, attrs):
        scheme_type = attrs['scheme_type']
        if scheme_type == SchemeTypeEnum.PUBLIC:
            scheme_key = "public"
        else:
            try:
                view = self.context.get("view")
                org_sid = view.kwargs.get("org_sid", None)
                scheme_key = models.ScanScheme.get_org_scheme_key(org_sid)
            except Exception:
                raise serializers.ValidationError("无效团队，方案模板创建失败")
        attrs['scheme_key'] = scheme_key
        return super().validate(attrs)

    def create(self, validated_data):
        """创建扫描方案
        """
        request = self.context.get("request")
        user = request.user if request else None
        scheme_key = validated_data.pop('scheme_key')
        name = validated_data.pop("name", None)
        if not name:
            raise serializers.ValidationError('方案模板名称为必填项')
        try:
            global_scheme = ScanSchemeManager.init_global_scheme_template(name, scheme_key, user, **validated_data)
        except ServerConfigError as err:
            logger.exception("create global scheme error: %s" % err.msg)
            raise serializers.ValidationError({"cd_error": err.msg})
        scheme = ScanSchemeManager.create_init_scheme(repo_id=None, user=user,
                                                      global_scheme=global_scheme, **validated_data)
        OperationRecordHandler.add_scanscheme_operation_record(scheme, "创建扫描方案模板", user, validated_data)
        return scheme

    class Meta:
        model = models.ScanScheme
        exclude = ["repo", "status", "refer_scheme", "default_flag"]
        read_only_fields = ["scheme_key"]


class GlobalScanSchemeTemplateSerializer(CDBaseModelSerializer):
    """方案模板序列化
    """
    languages = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Language.objects.all())
    tag = serializers.SlugRelatedField(slug_field="name", queryset=ExecTag.objects.all())

    def check_user_edit_perm_with_scheme(self, instance, user):
        logger.debug("[Scheme: %s][User: %s] check scanscheme edit perm" % (instance.id, user))
        if not ScanSchemePermManager.check_user_edit_manager_perm(instance, user):
            raise serializers.ValidationError({"cd_error": "当前用户%s没有修改该方案模板的权限" % user})
        return True

    def update(self, instance, validated_data):
        """更新扫描方案
        """
        request = self.context.get("request")
        user = request.user if request else None
        self.check_user_edit_perm_with_scheme(instance, user)
        name = validated_data.get("name")
        if models.ScanScheme.objects.filter(repo__isnull=True, name=name,
                                            scheme_key=instance.scheme_key,
                                            creator=user).exclude(id=instance.id).exists():
            raise serializers.ValidationError({"cd_error": "当前方案模板名称重复，请调整名称"})
        instance = ScanSchemeManager.update_scheme_basic_conf(instance, user, **validated_data)
        OperationRecordHandler.add_scanscheme_operation_record(instance, "修改基本信息", user, validated_data)
        return instance

    class Meta:
        model = models.ScanScheme
        exclude = ["repo", "status", "refer_scheme", "default_flag"]
        read_only_fields = ["scheme_key"]


class ScanSchemeSyncConfSerializer(serializers.Serializer):
    """模板/分析方案同步配置序列化
    """
    sync_basic_conf = serializers.BooleanField(help_text="同步基础配置", default=False)
    sync_lint_rule_conf = serializers.BooleanField(help_text="同步代码检查规则配置", default=False)
    sync_lint_build_conf = serializers.BooleanField(help_text="同步代码检查编译配置", default=False)
    sync_metric_conf = serializers.BooleanField(help_text="同步代码度量配置", default=False)
    sync_filter_path_conf = serializers.BooleanField(help_text="同步过滤路径配置", default=False)
    sync_filter_other_conf = serializers.BooleanField(help_text="同步过滤其他配置", default=False)
    sync_all = serializers.BooleanField(help_text="同步全部配置", default=False)


class GlobalScanSchemeTemplatePushSerializer(ScanSchemeSyncConfSerializer):
    """模板同步序列化
    """
    schemes = serializers.PrimaryKeyRelatedField(queryset=models.ScanScheme.objects.all(), many=True,
                                                 allow_null=True, required=False)
    all_schemes = serializers.BooleanField(help_text="所有子扫描方案", default=False)

    def validate_schemes(self, schemes):
        scheme_id = self.context["view"].kwargs.get("scheme_id")
        # 过滤不匹配的子扫描方案
        return [scheme for scheme in schemes if scheme.repo and scheme.refer_scheme_id == scheme_id]
