# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - v1 apis for project team
"""

from django.urls import path

from apps.codemetric.apis import v3

# 前缀 /api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codemetric/
urlpatterns = [
    path("ccfiles/", v3.PTCCFileListView.as_view(),
         name="apiv1_pt_codemetric_ccfiles"),
    path("ccfiles/<int:file_id>/ccissues/", v3.PTCCFileFileIssueListView.as_view(),
         name="apiv1_pt_codemetric_ccfile_issue_list"),
    path("ccissues/", v3.PTCCIssueListView.as_view(),
         name="apiv1_pt_codemetric_ccissues"),
    path("ccissues/history/", v3.PTCCIssueHistoryListView.as_view(),
         name="apiv1_pt_codemetric_ccissues_history"),
    path("ccissues/<int:issue_id>/", v3.PTCCIssueDetailView.as_view(),
         name="apiv1_pt_codemetric_ccissue"),
    path("ccissues/<int:issue_id>/author/", v3.PTCCIssueAuthorUpdateView.as_view(),
         name="apiv1_pt_codemetric_ccissue_update_author"),
    path("dupfiles/", v3.PTDupFileListView.as_view(),
         name="apiv1_pt_codemetric_dupfiles"),
    path("dupissues/<int:issue_id>/comments/", v3.PTDupIssueCommentListView.as_view(),
         name="apiv1_pt_codemetric_dupissue_comments"),
    path("dupissues/<int:issue_id>/owner/", v3.PTDupIssueOwnerUpdateView.as_view(),
         name="apiv1_pt_codemetric_dupissue_update_owner"),
    path("dupissues/<int:issue_id>/state/", v3.PTDupIssueStateUpdateView.as_view(),
         name="apiv1_pt_codemetric_dupissue_update_state"),
    path("dupfiles/<int:file_id>/", v3.PTDupFileDetailView.as_view(),
         name="apiv1_pt_codemetric_dupfile"),
    path("dupfiles/<int:file_id>/history/", v3.PTDupFileHistoryListView.as_view(),
         name="apiv1_pt_codemetric_dupfile_history"),
    path("dupfiles/<int:file_id>/blocks/", v3.PTDupBlockListView.as_view(),
         name="apiv1_pt_codemetric_dupblocks"),
    path("dupfiles/<int:file_id>/blocks/<int:block_id>/", v3.PTDupBlockDetailView.as_view(),
         name="apiv1_pt_codemetric_dupblock"),
    path("dupfiles/<int:file_id>/blocks/<int:block_id>/related/", v3.PTRelatedDupBlockListView.as_view(),
         name="apiv1_pt_codemetric_dupblock_related"),
    path("clocs/", v3.PTClocDirFileListView.as_view(),
         name="apiv1_pt_codemetric_clocs"),
    path("clocfiles/", v3.PTClocFileListView.as_view(),
         name="apiv1_pt_codemetric_cloc_files"),
    path("clocfiles/<int:file_id>/", v3.PTClocFileDetailView.as_view(),
         name="apiv1_pt_codemetric_cloc_file_detail"),
    path("cloclangs/", v3.PTClocLanguageListView.as_view(),
         name="apiv1_pt_codemetric_cloc_lang_list"),
]
