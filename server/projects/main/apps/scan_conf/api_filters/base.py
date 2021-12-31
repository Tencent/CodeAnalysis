# -*- coding: utf-8 -*-
"""
scan_conf - base filters
"""
# 第三方 import
from django_filters import rest_framework as filters

# 项目内 import
from apps.scan_conf import models


class NumberInFilter(filters.NumberFilter, filters.BaseInFilter):
    pass


class CharInFilter(filters.CharFilter, filters.BaseInFilter):
    pass


class PackageMapFilter(filters.FilterSet):
    checkrule_name = filters.CharFilter(field_name="checkrule__display_name", help_text="检查规则名",
                                        lookup_expr="icontains")
    checkrule_real_name = filters.CharFilter(field_name="checkrule__real_name", help_text="检查规则真实名",
                                             lookup_expr="icontains")
    checkrule_category = NumberInFilter(field_name="checkrule__category", help_text="检查规则分类")
    severity = NumberInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    checktool = NumberInFilter(help_text="检查工具，可多选，格式为1,2,3")
    state = NumberInFilter(help_text="状态，1为生效中，2为已屏蔽")
    checkrule_disable = filters.BooleanFilter(field_name="checkrule__disable", help_text="规则状态")
    checkrule_language = filters.CharFilter(field_name="checkrule__languages__name")

    class Meta:
        model = models.PackageMap
        fields = ["checkrule_name", "checkrule_real_name", "checkrule_category",
                  "severity", "checktool", "state", "checkrule_disable", "checkrule_language"]


class CheckRuleFilter(filters.FilterSet):
    """规则筛选
    """
    display_name = filters.CharFilter(help_text="规则展示名称", lookup_expr="icontains")
    real_name = filters.CharFilter(help_text="规则真实名称", lookup_expr="icontains")
    category = NumberInFilter(help_text="检查规则分类")
    severity = NumberInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    checktool = NumberInFilter(help_text="工具，可多选，格式为1,2,3")
    language_name = filters.CharFilter(field_name="languages__name", help_text="规则适用语言")
    label_name = filters.CharFilter(field_name="labels__name", help_text="规则标签")
    disable = filters.BooleanFilter(field_name="disable", help_text="规则状态")

    class Meta:
        model = models.CheckRule
        fields = ["display_name", "real_name", "category", "severity",
                  "checktool", "language_name", "label_name", "disable"]
