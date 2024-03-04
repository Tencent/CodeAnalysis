# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 api urls for projectteam

URL前缀： /api/orgs/<org_sid>/teams/
用途：体验版开放接口
"""
# 第三方 import
from django.urls import path, include

# 项目内 import
from apps.codeproj.apis import v1
from apps.codeproj.apis import v1_pt
from apps.codeproj.apis import v1_scheme

# 前缀 /api/orgs/<org_sid>/teams/<team_name>/repos/
repo_url_patterns = [
    # 节点使用
    path("defaultpaths/", v1.DefaultScanPathListApiView.as_view(),
         name="apiv1_pt_repo_defaultpath_list"),
    path("schemeinfo/", v1_pt.PTRepositorySchemeInfoAPIView.as_view(),
         name="apiv1_pt_repo_scheme_infos"),
    path("<int:repo_id>/projects/<int:project_id>/scans/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_scans"),
    path("<int:repo_id>/projects/<int:project_id>/scans/<int:scan_id>/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_repo_project_scan_info"),
    path("<int:repo_id>/projects/<int:project_id>/overview/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_overview"),
    path("<int:repo_id>/projects/<int:project_id>/overview/latestscan/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_latestscan_overview"),
    path("<int:repo_id>/projects/<int:project_id>/overview/lintscans/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_lintscans_overview"),
    path("<int:repo_id>/projects/<int:project_id>/overview/cycscans/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_cycscans_overview"),
    path("<int:repo_id>/projects/<int:project_id>/overview/dupscans/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_dupscans_overview"),
    path("<int:repo_id>/projects/<int:project_id>/overview/clocscans/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_clocscans_overview"),
    path("<int:repo_id>/projects/<int:project_id>/codelint/issues/", v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_codelint_issue"),
    path("<int:repo_id>/projects/<int:project_id>/codelint/issues/epreport/",
         v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_codelint_issue_epreport"),
    path("<int:repo_id>/projects/<int:project_id>/codelint/issues/summary/",
         v1_pt.PTAnalyseServerProxyAPIView.as_view(),
         name="apiv1_pt_project_codelint_summary"),
    path("<int:repo_id>/projects/<int:project_id>/scheme/defaultpaths/",
         v1_pt.PTProjectScanSchemeDefaultScanPathListAPIView.as_view(),
         name="apiv1_pt_project_scheme_defaultpaths"),
    path("<int:repo_id>/projects/<int:project_id>/scans/jobconfs/",
         v1_pt.PTProjectScanJobConfAPIView.as_view(),
         name="apiv1_pt_project_scan_jobconfs"),
    path("<int:repo_id>/projects/<int:project_id>/confs/",
         v1_pt.PTProjectConfAPIView.as_view(),
         name="apiv1_pt_project_scan_jobconfs"),

    # 对外开放
    path("", v1_pt.PTRepoListAPIView.as_view(),
         name="apiv1_pt_project_team_repo_list"),
    path("<int:repo_id>/", v1_pt.PTRepoDetailAPIView.as_view(),
         name="apiv1_pt_project_team_repo_list"),
    path("<int:repo_id>/branches/", v1_pt.PTRepoBranchListAPIView.as_view(),
         name="apiv1_pt_project_team_repo_branches"),
    path("<int:repo_id>/projects/", v1_pt.PTProjectListAPIView.as_view(),
         name="apiv1_pt_project_team_repo_project_list"),
    path("<int:repo_id>/projects/<int:project_id>/", v1_pt.PTProjectDetailAPIView.as_view(),
         name="apiv1_pt_project_team_repo_project_detail"),
    path("<int:repo_id>/projects/<int:project_id>/scheme/", v1_pt.PTProjectScanSchemeDetailApiView.as_view(),
         name="apiv1_pt_project_scheme_detail"),
    path("<int:repo_id>/projects/<int:project_id>/scans/create/",
         v1_pt.PTProjectScanCreateAPIView.as_view(),
         name="apiv1_pt_project_team_repo_project_scans"),
    path("<int:repo_id>/schemes/", v1_pt.PTScanSchemeListAPIView.as_view(),
         name="apiv1_pt_project_team_repo_scheme_list"),
    path("<int:repo_id>/copyscheme/", v1_pt.PTRepositorySchemeCopyApiView.as_view(),
         name="apiv1_pt_project_team_repo_scheme_copy"),
    path("<int:repo_id>/schemes/<int:scheme_id>/basicconf/", v1_pt.PTScanSchemeBasicConfAPIView.as_view(),
         name="apiv1_pt_project_team_repo_scheme_basicconf"),
    path("<int:repo_id>/schemes/<int:scheme_id>/lintconf/", v1_pt.PTScanSchemeLintConfAPIView.as_view(),
         name="apiv1_pt_project_team_scanscheme_lintconf"),
    path("<int:repo_id>/schemes/<int:scheme_id>/metricconf/", v1_pt.PTScanSchemeMetricConfAPIView.as_view(),
         name="apiv1_pt_project_team_scanscheme_metricconf"),
    path("<int:repo_id>/schemes/<int:scheme_id>/scandirs/", v1_pt.PTScanSchemeDirListAPIView.as_view(),
         name="apiv1_pt_project_team_scanscheme_scandirs"),
    path("<int:repo_id>/schemes/<int:scheme_id>/scandirs/<int:dir_id>/", v1_pt.PTScanSchemeDirDetailAPIView.as_view(),
         name="apiv1_pt_project_team_scanscheme_scandir"),
    path("<int:repo_id>/projects/<int:project_id>/jobs/", include("apps.job.api_urls.v1_pt")),

]

# 前缀 /api/orgs/<org_sid>/teams/<team_name>/projects/
project_url_patterns = [
    path("", v1_pt.PTProjectListCreateView.as_view(),
         name="apiv1_pt_project_list"),
]

# 前缀 /api/orgs/<org_sid>/schemes/
# 分析方案模板路由
global_scheme_urlpatterns = [
    path("",
         v1_scheme.OrgScanSchemeListAPIView.as_view(),
         name="apiv1_org_scheme_list"),
    path("<int:scheme_id>/",
         v1_scheme.OrgScanSchemeDetailAPIView.as_view(),
         name="apiv1_org_scheme_detail"),
    path("<int:scheme_id>/jobconfs/",
         v1_scheme.OrgScanSchemeScanJobConfAPIView.as_view(),
         name="apiv1_org_scheme_scan_jobconfs"),

]

# 前缀 /api/orgs/<org_sid>/
urlpatterns = [
    path("schemes/", include(global_scheme_urlpatterns)),
    path("teams/<str:team_name>/repos/", include(repo_url_patterns)),
    path("teams/<str:team_name>/projects/", include(project_url_patterns)),
]
