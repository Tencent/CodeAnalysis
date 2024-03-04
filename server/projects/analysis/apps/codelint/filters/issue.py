# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - issue filter
"""

from django_filters import rest_framework as filters

from apps.codelint import models


class LintIssueFilterSet(filters.FilterSet):
    """问题筛选过滤器
    """
    state = filters.BaseInFilter(help_text="问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3")
    severity = filters.BaseInFilter(help_text="严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4")
    resolution = filters.BaseInFilter(help_text="解决方式, 0为无，1为修复，2为无需修复，3为误报，"
                                                "4为重复单过滤，5为路径过滤，6为规则移除")
    author = filters.CharFilter(help_text="问题责任人", lookup_expr="exact")
    scan_open = filters.NumberFilter(help_text="发现问题的扫描编号", lookup_expr="exact")
    scan_fix = filters.NumberFilter(help_text="修复问题的扫描编号", lookup_expr="exact")
    ci_time_gte = filters.DateTimeFilter(field_name="ci_time", help_text="修复问题的起始时间", lookup_expr="gte")
    ci_time_lte = filters.DateTimeFilter(field_name="ci_time", help_text="修复问题的结束时间", lookup_expr="lte")
    file_path = filters.CharFilter(help_text="文件路径", lookup_expr="icontains")
    checkrule_real_name = filters.CharFilter(help_text="检查规则名", lookup_expr="icontains")
    checktool_name = filters.CharFilter(help_text="检查工具名", lookup_expr="icontains")
    checkrule_display_name = filters.CharFilter(help_text="检查规则名_前端展示名", lookup_expr="icontains")
    checkpackage = filters.BaseInFilter(help_text="问题所属的规则包", method="checkpackage_filter")

    def checkpackage_filter(self, queryset, name, value):
        if value is None:
            return queryset
        try:
            checkpackage_gids = '(' + ','.join(value) + ')'
        except ValueError:
            return queryset
        return queryset.extra(tables=['codelint_packagerulemap'],
                              where=["codelint_issue.checkrule_gid=codelint_packagerulemap.checkrule_gid",
                                     "codelint_packagerulemap.checkpackage_gid in %s" % checkpackage_gids])

    class Meta:
        model = models.Issue
        fields = ["state", "severity", "resolution", "author",
                  "scan_open", "scan_fix", "ci_time_gte", "ci_time_lte", "file_path",
                  "checktool_name", "checkrule_real_name", "checkrule_display_name", "checkpackage"]


class InvalidIssueFilterSet(filters.FilterSet):
    """无效问题筛选过滤器
    """
    project = filters.NumberFilter(help_text="指定项目", lookup_expr="exact")
    scope = filters.NumberFilter(help_text="范围，1表示当前项目，2表示代码库", lookup_expr="exact")

    class Meta:
        model = models.InvalidIssue
        fields = ["project", "scope"]


class WontFixIssueFilterSet(InvalidIssueFilterSet):
    """无需处理问题筛选过滤器
    """

    class Meta:
        model = models.WontFixIssue
        fields = ["project", "scope"]


class CheckToolScanFilterSet(filters.FilterSet):
    """扫描工具筛选过滤器
    """

    tools = filters.CharFilter(help_text="工具列表，请使用英文,分隔", method="tool_filter")

    def tool_filter(self, queryset, name, value):
        if value is None:
            return queryset
        tools = value.split(',')
        return queryset.filter(name__in=tools)

    class Meta:
        model = models.CheckToolScan
        fields = ["name"]
