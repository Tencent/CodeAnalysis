# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 apis
"""


# 项目内 import
from apps.codeproj.apis import v2
from apps.codeproj.apimixins import ProjectTeamBaseAPIView


class PTProjectDetailView(v2.ProjectDetailView, ProjectTeamBaseAPIView):
    """项目详情接口

    ### Get
    应用场景：获取项目详情
    """


class PTProjectScanListView(v2.ProjectScanListView, ProjectTeamBaseAPIView):
    """项目扫描列表接口

    ### Get
    应用场景：获取项目扫描列表
    """


class PTProjectScanDetailView(v2.ProjectScanDetailView, ProjectTeamBaseAPIView):
    """项目扫描详情接口

    ### GET
    应用场景：获取指定的项目扫描详情
    """


class PTProjectScanLatestDetailView(v2.ProjectScanLatestDetailView, ProjectTeamBaseAPIView):
    """项目扫描最新一次的详情接口

    ### GET
    应用场景：获取项目最新扫描详情
    """


class PTProjectMyOverviewDetailView(v2.ProjectMyOverviewDetailView, ProjectTeamBaseAPIView):
    """项目概览信息 - 与我相关的信息

    ### GET
    应用场景：获取项目概览信息 - 与我相关的信息
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


class PTProjectOverviewCheckToolScanView(v2.ProjectOverviewCheckToolScanView, ProjectTeamBaseAPIView):
    """项目概览信息 - 代码工具概览数据

    ### GET
    应用场景：获取项目概览信息 - 代码工具概览数据
    """
