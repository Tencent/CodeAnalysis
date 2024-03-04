# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 serializer for scan scheme
基础扫描方案序列化模块
"""

import logging

# 第三方 import
from django.contrib.auth.models import User
from rest_framework import serializers

# 项目内 import
from apps.codeproj import models
from apps.codeproj.serializers import base_scheme
from apps.codeproj.core import ScanSchemePermManager
from apps.authen.serializers.base import UserSimpleSerializer
from apps.base.serializers import CDBaseModelSerializer

from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class GlobalScanSchemeTemplateCreateSerializer(base_scheme.GlobalScanSchemeTemplateCreateSerializer):
    """分析方案模板创建序列化
    """

    class Meta:
        model = models.ScanScheme
        exclude = ["repo", "status", "refer_scheme", "default_flag"]
        read_only_fields = ["scheme_key"]


class GlobalScanSchemeTemplateSerializer(base_scheme.GlobalScanSchemeTemplateSerializer):
    """分析方案模板序列化
    """

    def check_user_view_perm_with_scheme(self, instance, user):
        org_sid = self.context["view"].kwargs.get("org_sid")
        logger.debug("[Org: %s][Scheme: %s][User: %s] check scanscheme edit perm" % (org_sid, instance.id, user))
        if not ScanSchemePermManager.check_user_edit_manager_perm(instance, user):
            raise serializers.ValidationError({"cd_error": "当前用户%s没有修改该方案模板的权限" % user})
        return True

    class Meta:
        model = models.ScanScheme
        exclude = ["repo", "status", "refer_scheme", "default_flag"]
        read_only_fields = ["scheme_key"]


class GlobalScanSchemeTemplatePushSerializer(base_scheme.GlobalScanSchemeTemplatePushSerializer):
    """模板同步序列化
    """
    pass


class ScanSchemePermConfSerializer(CDBaseModelSerializer):
    """权限配置序列化
    """
    edit_managers = UserSimpleSerializer(many=True, read_only=True)
    execute_managers = UserSimpleSerializer(many=True, read_only=True)
    edit_managers_list = serializers.SlugRelatedField(queryset=User.objects.all(), write_only=True,
                                                      slug_field="username", many=True, help_text="管理员列表")
    execute_managers_list = serializers.SlugRelatedField(queryset=User.objects.all(), write_only=True,
                                                         slug_field="username", many=True, help_text="普通成员")

    def format_managers(self, users):
        """格式化managers，忽略非团队内成员
        """
        view = self.context.get("view")
        org_sid = view.kwargs.get("org_sid", None)
        org = models.Organization.objects.filter(org_sid=org_sid).first()
        managers = []
        if org:
            for user in users:
                if user.has_perm("view_organization", org):
                    managers.append(user)
        return managers

    def update(self, instance, validated_data):
        """更新工具
        """
        request = self.context.get("request")
        user = request.user if request else None
        edit_managers_list = validated_data.pop("edit_managers_list", [])
        execute_managers_list = validated_data.pop("execute_managers_list", [])
        edit_managers = self.format_managers(edit_managers_list)
        execute_managers = self.format_managers(execute_managers_list)
        instance = super().update(instance, validated_data)
        instance.edit_managers.set(edit_managers)
        instance.execute_managers.set(execute_managers)
        instance.save(user=user)
        OperationRecordHandler.add_scanscheme_operation_record(
            instance.scan_scheme, "更新权限配置", user, validated_data)
        return instance

    class Meta:
        model = models.ScanSchemePerm
        fields = ["id", "scan_scheme", "edit_managers", "execute_scope", "execute_managers", "edit_managers_list",
                  "execute_managers_list"]
        read_only_fields = ["scan_scheme"]
