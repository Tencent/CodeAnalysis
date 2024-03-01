# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.nodemgr.filters 说明
"""
# 原生 import
import logging

# 第三方 import
from django.db.models import Q
from django_filters import rest_framework as filters

# 项目内 import
from apps.nodemgr import models

logger = logging.getLogger(__name__)


class NodeFilter(filters.FilterSet):
    """节点筛选
    """
    name = filters.CharFilter(help_text="节点名称", lookup_expr="icontains")
    manager = filters.CharFilter(field_name="manager__username", help_text="负责人", lookup_expr="icontains")
    exec_tags = filters.ModelChoiceFilter(field_name="exec_tags__name", to_field_name="name",
                                          queryset=models.ExecTag.objects.all(), help_text="节点标签")
    state = filters.NumberFilter(help_text="节点运行状态, 0表示空闲，1表示忙碌中", lookup_expr="exact")
    enabled = filters.BaseInFilter(help_text="节点可用性，0表示失效，1表示活跃，2表示掉线，可多选，格式为1,2,3")
    related_managers = filters.CharFilter(field_name="related_managers__username", help_text="节点相关责任人",
                                          lookup_expr="icontains")
    addr = filters.CharFilter(help_text="节点IP地址", lookup_expr="icontains")

    class Meta:
        model = models.Node
        fields = ["name", "manager", "exec_tags", "state", "enabled", "related_managers", "addr"]


class TagFilter(filters.FilterSet):
    """标签筛选
    """
    name = filters.CharFilter(help_text="标签名称", lookup_expr="icontains")
    display_name = filters.CharFilter(help_text="标签展示名称", lookup_expr="icontains")
    fuzzy_name = filters.CharFilter(help_text="标签名称综合模糊匹配", method="fuzzy_name_filter")
    tag_type = filters.NumberFilter(help_text="标签类型， 1表示公共标签，2表示非公共标签，99表示已停用标签", lookup_expr="exact")

    def fuzzy_name_filter(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(display_name__icontains=value))

    class Meta:
        model = models.ExecTag
        fields = ["name", "display_name", "fuzzy_name", "tag_type"]
