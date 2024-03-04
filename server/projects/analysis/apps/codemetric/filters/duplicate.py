# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - duplicate filters
"""

from django_filters import rest_framework as filters

from apps.codemetric import models


class MetricDupFileFilterSet(filters.FilterSet):
    """重复代码文件筛选过滤器
    """
    issue_state = filters.BaseInFilter(field_name="issue__state",
                                       help_text="问题状态, 1为未处理，2为可忽略，3为关闭，可多选，格式为1,2,3")
    change_type = filters.BaseInFilter(help_text="重复文件更改类型，add为新增，del为删除，mod为删除，可多选，格式为add,del,mod")
    issue_owner = filters.CharFilter(field_name="issue__owner", help_text="问题责任人", lookup_expr="exact")
    last_modifier = filters.CharFilter(help_text="最近修改人", lookup_expr="exact")
    file_path = filters.CharFilter(help_text="文件路径", lookup_expr="icontains")
    duplicate_rate_gte = filters.NumberFilter(field_name="duplicate_rate", help_text="重复率最小值", lookup_expr="gte")
    duplicate_rate_lte = filters.NumberFilter(field_name="duplicate_rate", help_text="重复率最大值", lookup_expr="lte")

    class Meta:
        model = models.DuplicateFile
        fields = ["issue_state", "issue_owner", "change_type", "last_modifier",
                  "duplicate_rate_gte", "duplicate_rate_lte", "file_path"]
