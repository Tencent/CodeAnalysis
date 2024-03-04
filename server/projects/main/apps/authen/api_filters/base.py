# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.authon.api_filters.base
"""
# 原生
import logging

# 第三方
from django_filters import rest_framework as filters

# 项目内
from apps.authen import models

logger = logging.getLogger(__name__)


class OrganizationFilter(filters.FilterSet):
    """团队筛选项

    name: str, 团队名称, 模糊匹配
    status: int, 团队状态
    """

    name = filters.CharFilter(help_text="团队名称", lookup_expr="icontains")

    class Meta:
        model = models.Organization
        fields = ["name", "status"]
