# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 apis for project
v1 接口定义，供节点端、服务内部、开放接口

URL前缀：/api/projects/
"""

from django.urls import path, include

from apps.codeproj.apis import v1 as apis
from apps.codeproj.apis import v2 as apis_v2

# 服务内部调用，显式采用 MainServerInternalAuthentication 鉴权
# 前缀： /api/projects/
urlpatterns = [
    path("", apis.ProjectCreateApiView.as_view(),
         name="apiv1_project_create"),
    path("<int:project_id>/scans/", apis.ProjectScanListCreateApiView.as_view(),
         name="apiv1_project_scan_list"),
    path("<int:project_id>/scans/<int:scan_id>/", apis.ProjectScanResultDetailApiView.as_view(),
         name="apiv1_project_scan_result_detail"),
    path("<int:project_id>/scans/<int:scan_id>/info/", apis.ProjectScanDetailApiView.as_view(),
         name="apiv1_project_scan_detail"),
    path("<int:project_id>/overview/", apis.ProjectOverviewApiView.as_view(),
         name="apiv1_project_overview"),
    path("<int:project_id>/overview/lintscans/", apis_v2.ProjectOverviewLintScanListView.as_view(),
         name="apiv1_project_lintscan_overview"),
    path("<int:project_id>/overview/cycscans/", apis_v2.ProjectOverviewCycScanListView.as_view(),
         name="apiv1_project_cycscan_overview"),
    path("<int:project_id>/overview/dupscans/", apis_v2.ProjectOverviewDupScanListView.as_view(),
         name="apiv1_project_dupscan_overview"),
    path("<int:project_id>/overview/clocscans/", apis_v2.ProjectOverviewClocScanListView.as_view(),
         name="apiv1_project_clocscan_overview"),
    path("<int:project_id>/overview/latestscan/", apis.ProjectLatestScanOverviewApiView.as_view(),
         name="apiv1_project_overview"),

    path("<int:project_id>/codelint/", include("apps.codelint.api_urls.v1_project")),
]
