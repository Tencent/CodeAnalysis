# -*- coding: utf-8 -*-
"""
scan_conf - v3 serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers.base import CheckRuleDescSerializer
from apps.scan_conf.core import CheckRuleManager
from apps.base.serializers import CDBaseModelSerializer

logger = logging.getLogger(__name__)


class CheckRuleSimpleSerializer(serializers.ModelSerializer):
    """检查规则简单序列化
    """
    category_name = serializers.CharField(source="get_category_display")
    severity_name = serializers.CharField(source="get_severity_display")
    languages = serializers.SlugRelatedField(help_text="适用语言", slug_field="name", many=True, read_only=True)
    org_detail = serializers.SerializerMethodField()

    def get_org_detail(self, checkrule):
        return CheckRuleManager.get_org_detail(checkrule)

    class Meta:
        model = models.CheckRule
        fields = ["id", "category_name", "severity_name", "display_name", "category", "severity",
                  "rule_params", "rule_title", "disable", "languages", "solution", "org_detail"]


class CheckRuleSerializer(CheckRuleSimpleSerializer):
    """检查规则序列化
    """
    checkruledesc = CheckRuleDescSerializer(help_text="规则描述")

    class Meta:
        model = models.CheckRule
        fields = ["id", "category_name", "severity_name", "display_name", "real_name", "category", "severity",
                  "rule_params", "rule_title", "disable", "languages", "solution", "org_detail", "checkruledesc"]


class CheckPackageRuleAddSerializer(serializers.Serializer):
    """规则包规则增加序列化
    """
    checkrules = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=models.CheckRule.objects.all()), help_text="规则列表")


class ScanSchemeCheckPackageSerializer(CDBaseModelSerializer):
    """分析方案规则包序列化
    """
    labels = serializers.SlugRelatedField(queryset=models.Label.objects.all(),
                                          slug_field='name', many=True, help_text="规则包标签")
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(),
                                             slug_field="name", many=True, help_text="适用语言")
    checkrule_count = serializers.SerializerMethodField()

    def get_checkrule_count(self, checkpackage):
        """获取规则包中的规则数量
        """
        return checkpackage.checkrule.all().count()

    class Meta:
        model = models.CheckPackage
        fields = ["id", "name", "description", "languages", "labels", "checkrule_count", "package_type"]
        read_only_fields = ["package_type"]


class ScanSchemeCheckProfileSimpleSerializer(CDBaseModelSerializer):
    """分析方案规则配置序列化
    """
    custom_checkpackage = ScanSchemeCheckPackageSerializer(read_only=True)

    class Meta:
        model = models.CheckProfile
        fields = ["id", "custom_checkpackage", "checkpackages"]
        read_only_fields = ['custom_checkpackage']


class ScanSchemePackageMapSerializer(serializers.ModelSerializer):
    """分析方案规则配置的规则包与规则的映射
    """
    checkrule = CheckRuleSimpleSerializer(read_only=True)

    class Meta:
        model = models.PackageMap
        exclude = ["checktool"]
