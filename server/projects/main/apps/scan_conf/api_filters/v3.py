# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 filters
"""
# 第三方
from django_filters import rest_framework as filters

# 项目内
from apps.scan_conf import models
from apps.scan_conf.api_filters import base


class ToolLibFilter(base.ToolLibFilter):
    """工具依赖筛选项
    """
    pass


class CheckToolFilter(base.CheckToolFilter):
    """工具筛选项
    """
    pass


class CheckPackageFilter(filters.FilterSet):
    """规则包筛选

    ```python
    # 筛选条件:
    name: str, 规则包名称, 包含
    label: str, 规则包标签名称
    language: str, 规则包语言, universal代表通用规则包
    ```
    """
    name = filters.CharFilter(help_text="规则包名称", lookup_expr="icontains")
    label = filters.CharFilter(field_name="labels__name", help_text="规则包标签名")
    language = filters.CharFilter(label="language", help_text="规则包语言", method="language_filter")

    def language_filter(self, queryset, name, value):
        if value == 'universal':  # 通用的
            return queryset.filter(languages__isnull=True)
        elif value:
            return queryset.filter(languages__name=value)
        return queryset

    class Meta:
        model = models.CheckPackage
        fields = ['name', "language", "label"]


class PackageMapFilter(base.PackageMapFilter):
    """规则包规则映射列表筛选
    """
    pass


class CheckRuleFilter(base.CheckRuleFilter):
    """规则筛选
    """
    language = filters.CharFilter(field_name="languages__name", help_text="规则适用语言")
    checkpackage = base.NumberInFilter(label="checkpackage", help_text="规则包筛选", method="checkpackage_filter")

    def checkpackage_filter(self, queryset, name, value):
        return queryset.filter(checkpackage__in=value).order_by("display_name")

    class Meta:
        model = models.CheckRule
        fields = ["name", "real_name", "display_name", "category", "severity",
                  "checktool", "language", "language_name", "disable", "checkpackage"]
