# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 apis for project team
"""

from django.urls import path, include

from apps.codeproj.apis import v3


# 前缀: /api/v3/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/
project_urlpatterns = [
    # 项目接口
    path("<int:project_id>/", v3.PTProjectDetailView.as_view(),
         name="apiv3_project_detail"),

    # 扫描接口
    path("<int:project_id>/scans/", v3.PTProjectScanListView.as_view(),
         name="apiv3_scan_list"),
    path("<int:project_id>/scans/<int:scan_id>/", v3.PTProjectScanDetailView.as_view(),
         name="apiv3_scan_detail"),
    path("<int:project_id>/scans/latest/", v3.PTProjectScanLatestDetailView.as_view(),
         name="apiv3_scan_latest_detail"),

    # 概览接口
    path("<int:project_id>/overview/mine/", v3.PTProjectMyOverviewDetailView.as_view(),
         name="apiv3_project_my_overview_detail"),
    path("<int:project_id>/overview/lintscans/", v3.PTProjectOverviewLintScanListView.as_view(),
         name="apiv3_project_overview_lintscan_list"),
    path("<int:project_id>/overview/lintscans/latest/", v3.PTProjectOverviewLintScanLatestDetailView.as_view(),
         name="apiv3_project_overview_lintscan_latest"),
    path("<int:project_id>/overview/cycscans/", v3.PTProjectOverviewCycScanListView.as_view(),
         name="apiv3_project_overview_lintscans"),
    path("<int:project_id>/overview/dupscans/", v3.PTProjectOverviewDupScanListView.as_view(),
         name="apiv3_project_overview_dupscans"),
    path("<int:project_id>/overview/clocscans/", v3.PTProjectOverviewClocScanListView.as_view(),
         name="apiv3_project_overview_clocscans"),
    path("<int:project_id>/overview/checktoolscans/", v3.PTProjectOverviewCheckToolScanView.as_view(),
         name="apiv3_project_overview_checktoolscan"),

    # 转发到相应的模块
    path(r"<int:project_id>/codelint/", include("apps.codelint.api_urls.v3_pt")),
    path(r"<int:project_id>/codemetric/", include("apps.codemetric.api_urls.v3_pt")),

]

# 前缀: /api/v3/orgs/<org_sid>/teams/<team_name>/repos/
urlpatterns = [
    path("<int:repo_id>/projects/", include(project_urlpatterns))
]
