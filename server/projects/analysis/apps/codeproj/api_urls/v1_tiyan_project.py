# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 apis for tiyan
"""

from django.urls import path

from apps.codeproj.apis import v1 as apis

# 服务内部调用，显式采用 MainServerInternalAuthentication 鉴权
# 前缀： /api/projects/
urlpatterns = [
    path("", apis.ProjectCreateApiView.as_view(),
         name="apiv1_project_create"),
    path("<int:project_id>/", apis.ProjectDetailApiView.as_view(),
         name="apiv1_project_detail"),
    path("<int:project_id>/scans/", apis.ProjectScanListCreateApiView.as_view(),
         name="apiv1_project_scan_list"),
    path("<int:project_id>/scans/<int:scan_id>/", apis.ProjectScanResultDetailApiView.as_view(),
         name="apiv1_project_scan_result_detail"),
    path("<int:project_id>/scans/<int:scan_id>/info/", apis.ProjectScanDetailApiView.as_view(),
         name="apiv1_project_scan_detail"),
]
