# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 apis for project team
"""

from django.urls import path, include

from apps.codeproj.apis import v1_pt

project_urlpatterns = [

    path("<int:project_id>/scans/", v1_pt.PTProjectScanListCreateApiView.as_view(),
         name="apiv1_pt_project_scan_list"),
    path("<int:project_id>/scans/<int:scan_id>/", v1_pt.PTProjectScanResultDetailApiView.as_view(),
         name="apiv1_project_scan_result_detail"),
    path("<int:project_id>/overview/", v1_pt.PTProjectOverviewApiView.as_view(),
         name="apiv1_pt_project_overview"),
    path("<int:project_id>/overview/lintscans/", v1_pt.PTProjectOverviewLintScanListView.as_view(),
         name="apiv1_pt_project_lintscan_overview"),
    path("<int:project_id>/overview/cycscans/", v1_pt.PTProjectOverviewCycScanListView.as_view(),
         name="apiv1_pt_project_cycscan_overview"),
    path("<int:project_id>/overview/dupscans/", v1_pt.PTProjectOverviewDupScanListView.as_view(),
         name="apiv1_pt_project_dupscan_overview"),
    path("<int:project_id>/overview/clocscans/", v1_pt.PTProjectOverviewClocScanListView.as_view(),
         name="apiv1_pt_project_clocscan_overview"),
    path("<int:project_id>/overview/latestscan/", v1_pt.PTProjectLatestScanOverviewApiView.as_view(),
         name="apiv1_pt_project_latest_overview"),

    path("<int:project_id>/codelint/", include("apps.codelint.api_urls.v1_pt")),
    path("<int:project_id>/codemetric/", include("apps.codemetric.api_urls.v1_pt")),

]

# 服务外部调用，采用 MainProxyAuthentication 鉴权
# 前缀：/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/
urlpatterns = [
    path("<int:repo_id>/projects/", include(project_urlpatterns))
]
