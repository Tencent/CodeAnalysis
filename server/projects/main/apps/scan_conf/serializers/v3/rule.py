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
from apps.scan_conf.serializers import base
from apps.scan_conf.core import CheckRuleManager

logger = logging.getLogger(__name__)


class CheckRuleDescSerializer(base.CheckRuleDescSerializer):
    """规则描述序列化
    """
    pass


class CheckRuleSimpleSerializer(base.CheckRuleSimpleSerializer):
    """规则简单序列化，用于仅展示规则简要信息，包含规则所属团队信息
    """
    org_detail = serializers.SerializerMethodField()

    def get_org_detail(self, checkrule):
        return CheckRuleManager.get_org_detail(checkrule)
    
    class Meta(base.CheckRuleSimpleSerializer.Meta):
        fields = base.CheckRuleSimpleSerializer.Meta.fields + ["org_detail"]


class CheckRuleToolSimpleSerializer(base.CheckRuleToolSimpleSerializer):
    """规则的工具简单序列化，用于在规则中序列化显示其工具简要信息
    """
    pass


class CheckRuleSerializer(CheckRuleSimpleSerializer):
    """规则详情序列化，用于展示规则的详细信息，包含规则详情和工具信息
    """
    checkruledesc = CheckRuleDescSerializer(help_text="规则描述")
    checktool = CheckRuleToolSimpleSerializer(read_only=True)

    class Meta(CheckRuleSimpleSerializer.Meta):
        fields = CheckRuleSimpleSerializer.Meta.fields + ["checkruledesc", "checktool"]
