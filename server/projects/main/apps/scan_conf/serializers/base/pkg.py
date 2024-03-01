# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checkpackage,checkprofile serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models

logger = logging.getLogger(__name__)


class CheckProfilePackageAddSerializer(serializers.Serializer):
    """用于分析方案-规则配置-批量添加官方规则包序列化
    """
    checkpackages = serializers.PrimaryKeyRelatedField(
        queryset=models.CheckPackage.objects.filter(package_type=models.CheckPackage.PackageTypeEnum.OFFICIAL),
        many=True)


class CheckPackageRuleAddSerializer(serializers.Serializer):
    """用于规则包批量添加规则序列化
    """
    checkrules = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=models.CheckRule.objects.all()),
        required=False, allow_null=True, help_text="规则列表"
    )
    checktool = serializers.PrimaryKeyRelatedField(
        queryset=models.CheckTool.objects.all(), 
        required=False, allow_null=True, help_text="工具"
    )

    def validate(self, attrs):
        checkrules = attrs.get("checkrules")
        checktool = attrs.get("checktool")
        if not checktool and not checkrules:
            raise serializers.ValidationError({"cd_error": "请传入checkrules或checktool"})
        return attrs


class CheckPackageRuleUpdateSerializer(serializers.Serializer):
    """用于规则包批量更新规则严重级别、规则参数、状态等序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    severity = serializers.ChoiceField(choices=models.CheckRule.SEVERITY_CHOICES, help_text="严重级别")
    rule_params = serializers.CharField(help_text="规则参数", allow_null=True, allow_blank=True)
    state = serializers.ChoiceField(choices=models.PackageMap.STATE_CHOICES, help_text="状态，1生效中，2已屏蔽")


class CheckPackageRuleSeverityUpdateSerializer(serializers.Serializer):
    """用于规则包批量更新规则严重级别序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    severity = serializers.ChoiceField(choices=models.CheckRule.SEVERITY_CHOICES, help_text="严重级别")


class CheckPackageRuleStateUpdateSerializer(serializers.Serializer):
    """用于规则包批量更新规则状态序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    state = serializers.ChoiceField(choices=models.PackageMap.STATE_CHOICES, help_text="状态，1生效中，2已屏蔽")
    remark = serializers.CharField(allow_null=True, allow_blank=True, required=False, help_text="remark")


class CheckPackageRuleDeleteSerializer(serializers.Serializer):
    """用于规则包批量删除规则序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    reason = serializers.CharField(max_length=128, help_text="删除原因")
