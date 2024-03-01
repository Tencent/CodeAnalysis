# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codeproj.apis codeproj的 v1_pt 接口
"""

# 第三方 import
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

# 项目内 import
from apps.codeproj import serializers
from apps.codeproj.apis import v1, v2
from apps.codeproj.models import Scan
from apps.codeproj.apimixins import ProjectTeamBaseAPIView
from apps.authen.backends import MainServerInternalAuthentication


class PTProjectScanListCreateApiView(v1.ProjectScanListCreateApiView, ProjectTeamBaseAPIView):
    """项目扫描列表接口
    使用对象：服务内部

    ### Get
    应用场景：获取项目扫描历史列表

    ### Post
    应用场景：在指定项目创建一个扫描记录，如果项目不存在，则返回404
    """


class PTProjectScanResultDetailApiView(v1.ProjectScanResultDetailApiView, ProjectTeamBaseAPIView):
    """项目扫描结果详情接口
    使用对象：服务内部

    ### Get
    应用场景：获取Scan详情，包括关联的各个功能模块的Scan信息

    ### put
    应用场景：任务完成后，将任务执行结果保存到扫描中
    """


class PTProjectOverviewApiView(v1.ProjectOverviewApiView, ProjectTeamBaseAPIView):
    """项目扫描概览接口

    ### Get
    应用场景：获取指定项目的扫描概览
    > query_params: scan_revision: 指定查询的扫描版本号，如不指定则为最新的；latest_scan_time: 指定截止的查询时间
    """


class PTProjectLatestScanOverviewApiView(v1.ProjectLatestScanOverviewApiView, ProjectTeamBaseAPIView):
    """项目最新扫描概览接口

    ### Get
    应用场景：获取指定项目指定版本的最新一次扫描
    > scan_revision: 指定查询的扫描版本号，如不指定则为当前项目最新的一次扫描
    """


class PTProjectOverviewLintScanLatestDetailView(v2.ProjectOverviewLintScanLatestDetailView, ProjectTeamBaseAPIView):
    """项目概览信息 - 代码检查最新扫描详情

    ### GET
    应用场景：获取项目概览信息 - 代码检查最新扫描详情
    """


class PTProjectOverviewLintScanListView(v2.ProjectOverviewLintScanListView, ProjectTeamBaseAPIView):
    """项目概览信息 - 代码检查列表

    ### GET
    应用场景：获取项目概览信息 - 代码检查列表
    """


class PTProjectOverviewCycScanListView(v2.ProjectOverviewCycScanListView, ProjectTeamBaseAPIView):
    """项目概览信息 - 圈复杂度扫描列表

    ### GET
    应用场景：获取项目概览信息 - 圈复杂度扫描列表
    """


class PTProjectOverviewDupScanListView(v2.ProjectOverviewDupScanListView, ProjectTeamBaseAPIView):
    """项目概览信息 - 重复代码扫描列表

    ### GET
    应用场景：获取项目概览信息 - 重复代码扫描列表
    """


class PTProjectOverviewClocScanListView(v2.ProjectOverviewClocScanListView, ProjectTeamBaseAPIView):
    """项目概览信息 - 代码统计扫描列表

    ### GET
    应用场景：获取项目概览信息 - 代码统计扫描列表
    """


class PTProjectScanListApiView(generics.ListAPIView, ProjectTeamBaseAPIView):
    """项目扫描列表接口
    ### Get
    应用场景：获取项目扫描历史列表
    """

    schema = None
    serializer_class = serializers.ProjectScanSerializer
    authentication_classes = (MainServerInternalAuthentication, )
    filter_backends = (DjangoFilterBackend,)
    filter_fields = {"result_code": ("gte", "lt"), }

    def get_queryset(self):
        project = self.get_project()
        order_by = self.request.GET.get("order_by")
        order_by = order_by.split(",") if order_by else ["-id"]
        return Scan.objects.filter(project_id=int(project.id)).order_by(*order_by)
