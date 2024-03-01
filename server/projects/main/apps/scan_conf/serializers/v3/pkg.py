# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 checkrule serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers import base
from apps.scan_conf.serializers.v3.rule import CheckRuleSimpleSerializer, CheckRuleToolSimpleSerializer
from apps.base.serializers import CDBaseModelSerializer

logger = logging.getLogger(__name__)


class CheckProfilePackageAddSerializer(base.CheckProfilePackageAddSerializer):
    """用于分析方案-规则配置-批量添加官方规则包序列化
    """
    pass


class CheckPackageRuleAddSerializer(base.CheckPackageRuleAddSerializer):
    """用于规则包批量添加规则序列化
    """
    pass


class CheckPackageRuleUpdateSerializer(base.CheckPackageRuleUpdateSerializer):
    """用于规则包批量更新规则严重级别、规则参数、状态等序列化
    """
    pass


class CheckPackageRuleSeverityUpdateSerializer(base.CheckPackageRuleSeverityUpdateSerializer):
    """用于规则包批量更新规则严重级别序列化
    """
    pass


class CheckPackageRuleStateUpdateSerializer(base.CheckPackageRuleStateUpdateSerializer):
    """用于规则包批量更新规则状态序列化
    """
    pass


class CheckPackageRuleDeleteSerializer(base.CheckPackageRuleDeleteSerializer):
    """用于规则包批量删除规则序列化
    """
    pass


class ScanSchemeCheckPackageSerializer(CDBaseModelSerializer):
    """分析方案-规则配置-规则包序列化
    """
    labels = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True, help_text="规则包标签")
    languages = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True, help_text="适用语言")
    checkrule_count = serializers.SerializerMethodField()

    def get_checkrule_count(self, checkpackage):
        """获取规则包中的规则数量
        """
        return checkpackage.checkrule.all().count()

    class Meta:
        model = models.CheckPackage
        fields = ["id", "name", "description", "languages", "labels", "checkrule_count", "package_type"]


class ScanSchemeCheckProfileSimpleSerializer(CDBaseModelSerializer):
    """分析方案-规则配置序列化
    """
    custom_checkpackage = ScanSchemeCheckPackageSerializer(read_only=True)

    class Meta:
        model = models.CheckProfile
        fields = ["id", "custom_checkpackage", "checkpackages"]


class ScanSchemePackageMapSerializer(serializers.ModelSerializer):
    """分析方案-规则配置-规则包与规则的映射序列化
    """
    checkrule = CheckRuleSimpleSerializer(read_only=True)
    checktool = CheckRuleToolSimpleSerializer(read_only=True)

    class Meta:
        model = models.PackageMap
        fields = "__all__"
