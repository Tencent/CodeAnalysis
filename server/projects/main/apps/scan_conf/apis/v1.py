# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v1 apis
"""
import re
import logging
from collections import defaultdict

# 第三方
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers import v1 as serializers


logger = logging.getLogger(__name__)


class CheckToolDisplayNameListAPIView(generics.ListAPIView):
    """工具展示名称列表接口，仅IsAdminUser可调用

    ### get
    应用场景：获取工具展示名称列表
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.CheckToolNameSimpleSerializer
    pagination_class = None

    def get_queryset(self):
        tools = self.request.query_params.get("tools")
        if tools:
            tools = re.split(r'[,;]', tools)
        else:
            tools = []
        return models.CheckTool.objects.filter(name__in=tools)


class CheckPackageRuleIDListAPIView(generics.GenericAPIView):
    """规则包对应规则编号列表接口

    ### get
    应用场景：获取规则包的规则编号列表
    """
    pagination_class = None

    def get(self, request, **kwargs):
        checkpackage_id = kwargs['package_id']
        checkpackage = get_object_or_404(models.CheckPackage, id=checkpackage_id)
        rule_ids = list(models.PackageMap.objects.filter(
            checkpackage=checkpackage).values_list("checkrule_id", flat=True))
        return Response(data=rule_ids)


class CheckRuleTypeMapAPIView(generics.GenericAPIView):
    """规则包-规则编号列表

    ### get
    应用场景：获取规则类型映射信息
    """
    pagination_class = None

    def get(self, request, **kwargs):
        checkrule_types = models.CheckRule.objects.values("id", "category")
        ruletype_dict = defaultdict(list)
        for rule_type in checkrule_types:
            ruletype_dict[rule_type["category"]].append(rule_type["id"])
        return Response(data=ruletype_dict)
