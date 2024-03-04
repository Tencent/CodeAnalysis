# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - base filter
"""
# 第三方
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django_filters import rest_framework as filters

# 项目内
from apps.scan_conf import models
from apps.base.filters import NumberInFilter, CharInFilter


class ToolLibFilter(filters.FilterSet):
    """工具依赖列表筛选
    """
    name = filters.CharFilter(lookup_expr="icontains", help_text="依赖名称")
    os = CharInFilter(help_text="依赖系统", method="os_filter")

    def os_filter(self, queryset, name, value):
        # 利用正则来处理lib_os筛选
        os = ';%s;' % (';|;'.join(value))
        return queryset.annotate(cos=Concat(Value(';'), 'lib_os', Value(';'))).filter(cos__iregex=r"%s" % os)

    class Meta:
        model = models.ToolLib
        fields = ["name", "lib_type", "os"]


class CheckToolFilter(filters.FilterSet):
    name = filters.CharFilter(help_text="工具名称", lookup_expr="icontains")
    display_name = filters.CharFilter(help_text="工具展示名称", lookup_expr="icontains")
    virtual_name = filters.CharFilter(help_text="工具虚拟名称", lookup_expr="icontains")
    fuzzy_name = filters.CharFilter(help_text="工具名称，综合模糊匹配", method="checktool_name_filter")
    scope = filters.NumberFilter(label="scope", help_text="工具公开私有类型，0公开，1私有，2协同, 3自定义", method="scope_filter")
    status = filters.NumberFilter(help_text="工具状态：0为正常运营，1为暂停使用，2已下架，3为体验运营")

    def checktool_name_filter(self, queryset, name, value):
        """工具名称筛选，支持工具name和display_name、virtual_name筛选"""
        return queryset.filter(Q(name__icontains=value) |
                               Q(display_name__icontains=value) |
                               Q(virtual_name__icontains=value))

    def scope_filter(self, queryset, name, value):
        if value == models.CheckTool.ScopeEnum.PUBLIC:  # 公开
            return queryset.filter(Q(open_maintain=True) | Q(open_user=True))
        if value == models.CheckTool.ScopeEnum.PRIVATE:  # 私有
            return queryset.filter(open_maintain=False, open_user=False)
        if value == models.CheckTool.ScopeEnum.MAINTAIN:  # 协同
            return queryset.filter(open_maintain=True)
        return queryset

    class Meta:
        model = models.CheckTool
        fields = ["name", "display_name", "virtual_name", "fuzzy_name", "scope", "status"]


class PackageMapFilter(filters.FilterSet):
    """规则包规则映射列表筛选
    """
    checkrule_name = filters.CharFilter(help_text="规则名称，综合模糊匹配", method="checkrule_name_filter")
    checkrule_display_name = filters.CharFilter(field_name="checkrule__display_name", help_text="检查规则名",
                                        lookup_expr="icontains")
    checkrule_real_name = filters.CharFilter(field_name="checkrule__real_name", help_text="检查规则真实名",
                                             lookup_expr="icontains")
    checkrule_category = NumberInFilter(field_name="checkrule__category", help_text="检查规则分类")
    severity = NumberInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    checktool = NumberInFilter(help_text="检查工具，可多选，格式为1,2,3")
    state = NumberInFilter(help_text="状态，1为生效中，2为已屏蔽")
    checkrule_disable = filters.BooleanFilter(field_name="checkrule__disable", help_text="规则状态")
    checkrule_language = filters.CharFilter(field_name="checkrule__languages__name")

    def checkrule_name_filter(self, queryset, name, value):
        """规则筛选，支持规则real_name和display_name"""
        return queryset.filter(Q(checkrule__real_name__icontains=value) |
                               Q(checkrule__display_name__icontains=value))

    class Meta:
        model = models.PackageMap
        fields = ["checkrule_name", "checkrule_display_name", "checkrule_real_name", "checkrule_category",
                  "severity", "checktool", "state", "checkrule_disable", "checkrule_language"]


class CheckRuleFilter(filters.FilterSet):
    """规则列表筛选
    """
    name = filters.CharFilter(help_text="规则名称，综合模糊匹配", method="checkrule_name_filter")
    real_name = filters.CharFilter(help_text="规则真实名称", lookup_expr="icontains")
    display_name = filters.CharFilter(help_text="规则展示名称", lookup_expr="icontains")
    category = NumberInFilter(help_text="检查规则分类")
    severity = NumberInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    checktool = NumberInFilter(help_text="工具，可多选，格式为1,2,3")
    language_name = filters.CharFilter(field_name="languages__name", help_text="规则适用语言")
    label_name = filters.CharFilter(field_name="labels__name", help_text="规则标签")
    disable = filters.BooleanFilter(field_name="disable", help_text="规则状态")

    def checkrule_name_filter(self, queryset, name, value):
        """规则筛选，支持规则real_name和display_name"""
        return queryset.filter(Q(real_name__icontains=value) | Q(display_name__icontains=value))

    class Meta:
        model = models.CheckRule
        fields = ["name", "real_name", "display_name", "category", "severity",
                  "checktool", "language_name", "label_name", "disable"]
