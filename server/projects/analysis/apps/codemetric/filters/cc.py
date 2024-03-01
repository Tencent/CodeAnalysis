# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - cc filters
"""

from django_filters import rest_framework as filters


from apps.codemetric import models


class MetricCCFileFilterSet(filters.FilterSet):
    """圈复杂度文件筛选过滤器
    """
    state = filters.BaseInFilter(help_text="问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3")
    change_type = filters.BaseInFilter(help_text="圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3")
    author = filters.CharFilter(help_text="问题责任人", lookup_expr="exact")
    most_weight_modifier = filters.CharFilter(help_text="最大权重修改人", lookup_expr="exact")
    last_modifier = filters.CharFilter(help_text="最近修改人",  lookup_expr="exact")
    file_path = filters.CharFilter(help_text="文件路径", lookup_expr="icontains")
    scan_open = filters.NumberFilter(help_text="发现问题的扫描编号", method="scan_open_filter")
    scan_close = filters.NumberFilter(help_text="修复问题的扫描编号", method="scan_close_filter")
    is_tapdbug = filters.BooleanFilter(help_text="是Tapd缺陷单，默认为False",  method="is_tapdbug_filter")
    worse = filters.BooleanFilter(help_text="圈复杂度是否恶化", lookup_expr="exact")
    ci_time_gte = filters.DateTimeFilter(field_name="ci_time", help_text="发现问题的起始时间", lookup_expr="gte")
    ci_time_lte = filters.DateTimeFilter(field_name="ci_time", help_text="发现问题的结束时间", lookup_expr="lte")
    over_cc_sum_gte = filters.NumberFilter(field_name="over_cc_sum", help_text="圈复杂度总和最小值", lookup_expr="gte")
    over_cc_sum_lte = filters.NumberFilter(field_name="over_cc_sum", help_text="圈复杂度总和最大值", lookup_expr="lte")
    over_cc_avg_gte = filters.NumberFilter(field_name="over_cc_avg", help_text="平均圈复杂度最小值", lookup_expr="gte")
    over_cc_avg_lte = filters.NumberFilter(field_name="over_cc_avg", help_text="平均圈复杂度总和最大值", lookup_expr="lte")
    over_cc_func_count_gte = filters.NumberFilter(field_name="over_cc_func_count", help_text="超标圈复杂度函数个数最小值",
                                                  lookup_expr="gte")
    over_cc_func_count_lte = filters.NumberFilter(field_name="over_cc_func_count", help_text="超标圈复杂度函数个数最大值",
                                                  lookup_expr="lte")

    def is_tapdbug_filter(self, queryset, name, value):
        if value is True:
            return queryset.filter(tapd_bug_id__isnull=False)
        elif value is False:
            return queryset.filter(tapd_bug_id__isnull=True)
        else:
            return queryset

    def scan_open_filter(self, queryset, name, value):
        if value:
            return queryset.filter(scan_open__scan_id=value)
        else:
            return queryset

    def scan_close_filter(self, queryset, name, value):
        if value:
            return queryset.filter(scan_close__scan_id=value)
        else:
            return queryset

    class Meta:
        model = models.CyclomaticComplexityFile
        fields = ["state", "change_type", "author", "last_modifier", "most_weight_modifier", "file_path", "scan_open",
                  "scan_close", "is_tapdbug", "worse", "over_cc_sum_gte", "over_cc_sum_lte", "over_cc_avg_gte",
                  "over_cc_avg_lte", "over_cc_func_count_gte", "over_cc_func_count_lte", "ci_time"]


class MetricCCNIssueFilterSet(filters.FilterSet):
    """圈复杂度问题筛选过滤器
    """
    status = filters.BaseInFilter(help_text="问题状态，1为需要关注，2为无需关注，可多选，格式为1,2,3")
    change_type = filters.BaseInFilter(help_text="圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3")
    most_weight_modifier = filters.CharFilter(help_text="最大权重修改人", lookup_expr="exact")
    author = filters.CharFilter(help_text="问题责任人", lookup_expr="exact")
    last_modifier = filters.CharFilter(help_text="最近修改人",  lookup_expr="exact")
    file_path = filters.CharFilter(help_text="文件路径", lookup_expr="icontains")
    ccn_gte = filters.NumberFilter(field_name="ccn", help_text="圈复杂度最小值", lookup_expr="gte")
    ccn_lte = filters.NumberFilter(field_name="ccn", help_text="圈复杂度最大值", lookup_expr="lte")

    class Meta:
        model = models.CyclomaticComplexity
        fields = ["status", "change_type", "author", "last_modifier", "most_weight_modifier",
                  "ccn_gte", "ccn_lte", "file_path"]
