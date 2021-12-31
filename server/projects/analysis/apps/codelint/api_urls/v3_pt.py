# -*- coding: utf-8 -*-
"""
codelint - v3 apis for project team
"""

from django.urls import path

from apps.codelint.apis import v3

# url前缀： /api/v3/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codelint/
urlpatterns = [
    path("issues/", v3.PTProjectIssueListView.as_view(),
         name="apiv3_issue_list"),
    path("issues/download/", v3.PTProjectIssueDownloadView.as_view(),
         name="apiv3_issue_download"),
    path("issues/checkrules/", v3.PTProjectIssueCheckRuleNumView.as_view(),
         name="apiv3_issue_checkrule_num"),
    path("issues/resolution/", v3.PTIssueResolutionBulkUpdateView.as_view(),
         name="apiv3_issue_resolution_bulk_update"),
    path("issues/author/", v3.PTIssueAuthorBulkUpdateView.as_view(),
         name="apiv3_issue_author_bulk_update"),
    path("issues/<int:issue_id>/", v3.PTIssueDetailView.as_view(),
         name="apiv3_issue_detail"),
    path("issues/<int:issue_id>/comments/", v3.PTIssueCommentsView.as_view(),
         name="apiv3_issue_comments"),
    path("issues/<int:issue_id>/author/", v3.PTIssueAuthorUpdateView.as_view(),
         name="apiv3_issue_author_update"),
    path("issues/<int:issue_id>/severity/", v3.PTIssueSeverityUpdateView.as_view(),
         name="apiv3_issue_severity_update"),
    path("issues/<int:issue_id>/resolution/", v3.PTIssueResolutionUpdateView.as_view(),
         name="apiv3_issue_resolution_update"),
]
