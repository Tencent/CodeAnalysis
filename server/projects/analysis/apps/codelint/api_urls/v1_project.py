# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - v1 project url
"""

from django.urls import path

from apps.codelint.apis import v1

# url前缀： /api/projects/:project_id/codelint/
urlpatterns = [

    # 通用
    path("issues/report/", v1.ProjectLintIssueReport.as_view(),
         name="apiv1_project_issue_report"),
    path("issues/summary/", v1.ProjectScanIssueSummaryAPIView.as_view(),
         name="apiv1_project_issue_summary"),
    path("issues/", v1.ProjectIssueListView.as_view(),
         name="apiv1_issue_list"),
    path("issuedetails/", v1.ProjectIssueWithDetailListView.as_view(),
         name="apiv1_issue_list_with_issue_detail"),
    path("issues/<int:issue_id>/", v1.ProjectIssueDetailView.as_view(),
         name="apiv1_issue_detail"),
    path("issues/toolreports/", v1.ProjectIssueToolReportListAPIView.as_view(),
         name="apiv1_codelint_issue_tool_report_list"),
]
