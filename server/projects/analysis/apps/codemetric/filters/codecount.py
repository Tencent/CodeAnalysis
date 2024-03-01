# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - codecount filters
"""
import os

from django_filters import rest_framework as filters

from apps.codemetric import models


class MetricClocFileFilterSet(filters.FilterSet):
    """文件筛选列表
    """
    change_type = filters.BaseInFilter(help_text="重复文件更改类型，add为新增，del为删除，mod为删除，可多选，格式为add,del,mod")
    file_path = filters.CharFilter(help_text="文件路径", method="file_path_filter")

    def file_path_filter(self, queryset, name, value):
        """文件路径筛选
        """
        if value:
            dir_path = os.path.dirname(value)
            file_name = os.path.basename(value)
            if dir_path:
                queryset = queryset.filter(dir_path=dir_path)
            if file_name:
                queryset = queryset.filter(file_name=file_name)
        return queryset

    class Meta:
        model = models.ClocFile
        fields = ["change_type", "file_path"]
