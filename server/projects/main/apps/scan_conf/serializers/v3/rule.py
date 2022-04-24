# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
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
from apps.scan_conf.core import CheckRuleManager

logger = logging.getLogger(__name__)


class CheckRuleDescSerializer(base.CheckRuleDescSerializer):
    """规则描述序列化
    """
    pass


class CheckRuleSimpleSerializer(serializers.ModelSerializer):
    """规则简单序列化
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
    """规则详情序列化
    """
    checkruledesc = CheckRuleDescSerializer(help_text="规则描述")

    class Meta:
        model = models.CheckRule
        fields = ["id", "category_name", "severity_name", "display_name", "real_name", "category", "severity",
                  "rule_params", "rule_title", "disable", "languages", "solution", "org_detail", "checkruledesc"]
