# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job - base filters
"""

# 原生 import
import logging

# 第三方 import
from django_filters import rest_framework as filters

# 项目内 import
from apps.job import models

logger = logging.getLogger(__name__)


class JobFilterSet(filters.FilterSet):
    repo = filters.NumberFilter(
        help_text="代码库编号", lookup_expr="exact", field_name="project__repo_id")
    project = filters.NumberFilter(
        help_text="项目编号", lookup_expr="exact", field_name="project_id")
    create_time_gte = filters.DateTimeFilter(field_name="create_time",
                                             help_text="任务开始筛选的起始时间", lookup_expr="gte")
    create_time_lte = filters.DateTimeFilter(field_name="create_time",
                                             help_text="任务开始筛选的结束时间", lookup_expr="lte")
    end_time_gte = filters.DateTimeFilter(field_name="end_time",
                                          help_text="任务结束筛选的起始时间", lookup_expr="gte")
    end_time_lte = filters.DateTimeFilter(field_name="end_time",
                                          help_text="任务结束筛选的结束时间", lookup_expr="lte")
    result_code_gte = filters.NumberFilter(
        help_text="错误码", lookup_expr="gte", field_name="result_code")
    result_code_lte = filters.NumberFilter(
        help_text="错误码", lookup_expr="lte", field_name="result_code")
    result_msg = filters.CharFilter(help_text="结果信息", lookup_expr="icontains")
    state = filters.BaseInFilter(
        help_text="任务状态, 0为等待中，1为执行中，2为关闭，3为入库中，可多选，格式为1,2,3")
    created_from = filters.CharFilter(
        help_text="创建来源", lookup_expr="icontains")
    creator = filters.CharFilter(help_text="创建用户", lookup_expr="icontains")
    scm_url = filters.CharFilter(
        help_text="代码库地址", lookup_expr="icontains", field_name="project__repo__scm_url")

    class Meta:
        model = models.Job
        fields = ["repo", "project", "create_time_gte", "create_time_lte", "end_time_gte", "end_time_lte",
                  "result_code_gte", "result_code_lte", "state", "result_msg", "created_from", "creator", "scm_url"]


class TaskFilterSet(filters.FilterSet):
    start_time_gte = filters.DateTimeFilter(
        field_name="start_time", help_text="工具开始时间", lookup_expr="gte")
    start_time_lte = filters.DateTimeFilter(
        field_name="start_time", help_text="工具结束时间", lookup_expr="lte")
    result_code_gte = filters.NumberFilter(
        help_text="错误码", lookup_expr="gte", field_name="result_code")
    result_code_lte = filters.NumberFilter(
        help_text="错误码", lookup_expr="lte", field_name="result_code")
    result_msg = filters.CharFilter(help_text="结果信息", lookup_expr="icontains")
    state = filters.BaseInFilter(
        help_text="任务状态, 0为等待中，1为执行中，2为关闭，3为入库中，可多选，格式为1,2,3")
    task_name = filters.CharFilter(help_text="工具名称")
    created_from = filters.CharFilter(help_text="启动渠道", field_name="job__created_from")

    class Meta:
        model = models.Task
        fields = ["start_time_gte", "start_time_lte",
                  "result_code_gte", "result_code_lte", "state",
                  "result_msg", "task_name", "tag", "node", "created_from"]


class TaskProcessFilterSet(filters.FilterSet):
    start_time_gte = filters.DateTimeFilter(
        field_name="start_time", help_text="工具进程开始时间", lookup_expr="gte")
    start_time_lte = filters.DateTimeFilter(
        field_name="start_time", help_text="工具进程结束时间", lookup_expr="lte")
    result_code_gte = filters.NumberFilter(
        help_text="错误码", lookup_expr="gte", field_name="result_code")
    result_code_lte = filters.NumberFilter(
        help_text="错误码", lookup_expr="lte", field_name="result_code")
    result_msg = filters.CharFilter(help_text="结果信息", lookup_expr="icontains")
    state = filters.BaseInFilter(
        help_text="任务状态, 0为等待中，1为执行中，2为关闭，3为入库中，可多选，格式为1,2,3")
    task_name = filters.CharFilter(help_text="工具名称", field_name="task__name")
    tag = filters.NumberFilter(
        field_name="task__tag_id", help_text="节点标签")

    class Meta:
        model = models.TaskProcessRelation
        fields = ["start_time_gte", "start_time_lte",
                  "result_code_gte", "result_code_lte", "state",
                  "result_msg", "task_name", "tag", "node"]
