# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - v1 apis for project team
"""

from django.urls import path

from apps.codelint.apis import v1_pt

# 前缀： /api/orgs/<str:org_sid>/teams/<str:team_name>/repos/<int:repo_id>/projects/<int:project_id>/codelint/
urlpatterns = [
    # 通用
    path("issues/report/", v1_pt.PTProjectLintIssueReport.as_view(),
         name="apiv1_pt_project_issue_report"),
    path("issues/summary/", v1_pt.PTProjectScanIssueSummaryAPIView.as_view(),
         name="apiv1_pt_project_issue_summary"),
    path("issues/", v1_pt.PTProjectIssueListView.as_view(),
         name="apiv1_pt_project_issue_list"),
    path("issues/<int:issue_id>/", v1_pt.PTProjectIssueDetailView.as_view(),
         name="apiv1_pt_project_issue_detail"),
]
