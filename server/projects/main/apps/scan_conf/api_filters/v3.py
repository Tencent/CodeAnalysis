# -*- coding: utf-8 -*-
"""
scan_conf - v3 filters
"""
# 第三方
from django_filters import rest_framework as filters

# 项目内
from apps.scan_conf import models
from apps.scan_conf.api_filters import base


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


class PackageMapFilter(filters.FilterSet):
    """规则包pm筛选项
    """
    checkrule_name = filters.CharFilter(field_name="checkrule__display_name", help_text="检查规则名",
                                        lookup_expr="icontains")
    checkrule_category = base.NumberInFilter(field_name="checkrule__category", help_text="检查规则分类")
    severity = base.NumberInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    state = base.NumberInFilter(help_text="状态，1为生效中，2为已屏蔽")
    checkrule_disable = filters.BooleanFilter(field_name="checkrule__disable", help_text="规则状态")
    checkrule_language = filters.CharFilter(field_name="checkrule__languages__name")

    class Meta:
        model = models.PackageMap
        fields = ["checkrule_name", "checkrule_category",
                  "severity", "state", "checkrule_disable", "checkrule_language"]


class CheckRuleFilter(filters.FilterSet):
    """规则筛选
    """
    display_name = filters.CharFilter(help_text="规则展示名称", lookup_expr="icontains")
    category = base.NumberInFilter(help_text="检查规则分类")
    severity = base.NumberInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    language = filters.CharFilter(field_name="languages__name", help_text="规则适用语言")
    disable = filters.BooleanFilter(field_name="disable", help_text="规则状态")
    checkpackage = base.NumberInFilter(label="checkpackage", help_text="规则包筛选", method="checkpackage_filter")

    def checkpackage_filter(self, queryset, name, value):
        return queryset.filter(checkpackage__in=value).order_by("display_name")

    class Meta:
        model = models.CheckRule
        fields = ["display_name", "category", "severity", "language", "disable", "checkpackage"]
