# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1_pt 接口定义

URL前缀： /api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/jobs/
用途：体验版开放接口
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.job.apis import v1_pt as apis

# 前缀 /api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/jobs/
urlpatterns = [
    # 通用
    path("", apis.ProjectJobListAPIView.as_view(),
         name="apiv1_project_job_list"),
    path("<int:job_id>/", apis.ProjectJobDetailAPIView.as_view(),
         name="apiv1_project_job_detail"),
    path("init/", apis.ProjectScanJobInitAPIView.as_view(),
         name="apiv1_project_scan_job_init"),
    path("<int:job_id>/finish/", apis.ProjectJobFinishAPIView.as_view(),
         name="apiv1_project_job_finish"),
]
