# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codemetric.api_urls.v3_pt

在codeproj子模块下的url

URL前缀：/api/v3/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codemetric/
"""

from django.urls import path

from apps.codemetric.apis import v3

urlpatterns = [
    path("ccfiles/", v3.PTCCFileListView.as_view(),
         name="apv3_codemetric_ccfiles"),
    path("ccfiles/<int:file_id>/", v3.PTCCFileDetailView.as_view(),
         name="apv3_codemetric_ccfile_detail"),
    path("ccfiles/<int:file_id>/ccissues/", v3.PTCCFileFileIssueListView.as_view(),
         name="apv3_codemetric_ccfile_issue_list"),
    path("ccissues/", v3.PTCCIssueListView.as_view(),
         name="apv3_codemetric_ccissues"),
    path("ccissues/history/", v3.PTCCIssueHistoryListView.as_view(),
         name="apv3_codemetric_ccissues_history"),
    path("ccissues/status/", v3.PTCCIssueStatusBulkUpdateView.as_view(),
         name="apv3_codemetric_ccissue_status_bulk_update"),
    path("ccissues/<int:issue_id>/", v3.PTCCIssueDetailView.as_view(),
         name="apv3_codemetric_ccissue"),
    path("ccissues/<int:issue_id>/author/", v3.PTCCIssueAuthorUpdateView.as_view(),
         name="apv3_codemetric_ccissue_update_author"),

    path("dupfiles/", v3.PTDupFileListView.as_view(),
         name="apv3_codemetric_dupfiles"),
    path("dupissues/<int:issue_id>/comments/", v3.PTDupIssueCommentListView.as_view(),
         name="apv3_codemetric_dupissue_comments"),
    path("dupissues/<int:issue_id>/owner/", v3.PTDupIssueOwnerUpdateView.as_view(),
         name="apv3_codemetric_dupissue_update_owner"),
    path("dupissues/<int:issue_id>/state/", v3.PTDupIssueStateUpdateView.as_view(),
         name="apv3_codemetric_dupissue_update_state"),
    path("dupfiles/<int:file_id>/", v3.PTDupFileDetailView.as_view(),
         name="apv3_codemetric_dupfile"),
    path("dupfiles/<int:file_id>/history/", v3.PTDupFileHistoryListView.as_view(),
         name="apv3_codemetric_dupfile_history"),
    path("dupfiles/<int:file_id>/blocks/", v3.PTDupBlockListView.as_view(),
         name="apv3_codemetric_dupblocks"),
    path("dupfiles/<int:file_id>/blocks/<int:block_id>/", v3.PTDupBlockDetailView.as_view(),
         name="apv3_codemetric_dupblock"),
    path("dupfiles/<int:file_id>/blocks/<int:block_id>/related/", v3.PTRelatedDupBlockListView.as_view(),
         name="apv3_codemetric_dupblock_related"),

    path("clocs/", v3.PTClocDirFileListView.as_view(),
         name="apv3_codemetric_clocs"),
    path("clocfiles/", v3.PTClocFileListView.as_view(),
         name="apv3_codemetric_cloc_files"),
    path("cloclangs/", v3.PTClocLanguageListView.as_view(),
         name="apv3_codemetric_cloc_lang_list"),

]
