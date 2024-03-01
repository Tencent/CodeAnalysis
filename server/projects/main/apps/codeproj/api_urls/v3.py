# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 api urls

v3 api 接口url定义，供前端页面调用
"""

# 第三方 import
from django.urls import path, include

# 项目内 import
from apps.codeproj.apis import v3, v3_scheme

# 前缀 /api/v3/orgs/<str:org_sid>/teams/
# 项目路由
team_urlpatterns = [
    path("",
         v3.ProjectTeamListApiView.as_view(),
         name="apiv3_org_team_list"),
    path("<str:team_name>/",
         v3.ProjectTeamDetailApiView.as_view(),
         name="apiv3_org_team_detail"),
    path("<str:team_name>/status/",
         v3.ProjectTeamStatusApiView.as_view(),
         name="apiv3_org_team_status"),
    path("<str:team_name>/memberconf/",
         v3.ProjectTeamMemberConfApiView.as_view(),
         name="apiv3_org_team_member_conf"),
    path("<str:team_name>/memberconf/<int:role>/<str:username>/",
         v3.ProjectTeamMemberConfDeleteApiView.as_view(),
         name="apiv3_org_team_member_role_username"),
    path("<str:team_name>/labels/",
         v3.ProjectTeamLabelListApiView.as_view(),
         name="apiv3_org_team_label_list"),
    path("<str:team_name>/labels/tree/",
         v3.ProjectTeamLabelTreeApiView.as_view(),
         name="apiv3_org_team_label_tree"),
    path("<str:team_name>/labels/<int:label_id>/",
         v3.ProjectTeamLabelDetailApiView.as_view(),
         name="apiv3_org_team_label_detail"),
]

# 前缀 /api/v3/orgs/<str:org_sid>/schemes/
# 分析方案模板路由
global_scheme_urlpatterns = [
    path("",
         v3_scheme.ScanSchemeListApiView.as_view(),
         name="apiv3_org_scheme_list"),
    path("<int:scheme_id>/",
         v3_scheme.ScanSchemeDetailApiView.as_view(),
         name="apiv3_org_scheme_detail"),
    path("<int:scheme_id>/basicconf/",
         v3_scheme.ScanSchemeDetailApiView.as_view(),
         name="apiv3_org_scheme_basiconf"),
    path("<int:scheme_id>/lintconf/",
         v3.ScanSchemeLintConfApiView.as_view(),
         name="apiv3_org_scheme_lintconf"),
    path("<int:scheme_id>/metricconf/",
         v3.ScanSchemeMetricConfApiView.as_view(),
         name="apiv3_org_scheme_metricconf"),
    path("<int:scheme_id>/scandirs/",
         v3.ScanSchemeDirListApiView.as_view(),
         name="apiv3_org_scheme_scan_dirlist"),
    path("<int:scheme_id>/scandirs/bulkcreate/",
         v3.ScanSchemeDirBulkCreateApiView.as_view(),
         name="apiv3_org_scheme_scan_dir_bulkcreate"),
    path("<int:scheme_id>/scandirs/clear/",
         v3.ScanSchemeDirClearApiView.as_view(),
         name="apiv3_org_scheme_scan_dir_clear"),
    path("<int:scheme_id>/scandirs/<int:dir_id>/",
         v3.ScanSchemeDirDetailApiView.as_view(),
         name="apiv3_org_scheme_scan_dir_detail"),
    path("<int:scheme_id>/permconf/",
         v3_scheme.ScanSchemePermConfApiView.as_view(),
         name="apiv3_org_scheme_perm_conf"),
    path("<int:scheme_id>/childrens/",
         v3_scheme.ScanSchemeChildrenListApiView.as_view(),
         name="apiv3_org_scheme_children_list"),
    path("<int:scheme_id>/push/",
         v3_scheme.ScanSchemePushApiView.as_view(),
         name="apiv3_org_scheme_push"),

    # 加载 scan_conf 模块的 v3_scheme
    path("<int:scheme_id>/", include("apps.scan_conf.api_urls.v3_global_scheme")),
]

# 前缀 /api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repos/
# 代码库路由
repo_urlpatterns = [
    path("",
         v3.RepositoryListApiView.as_view(),
         name="apiv3_org_repo_list"),
    path("<int:repo_id>/",
         v3.RepositoryDetailApiView.as_view(),
         name="apiv3_org_repo_detail"),
    path("<int:repo_id>/auth/",
         v3.RepositoryAuthDetailApiView.as_view(),
         name="apiv3_org_repo_auth"),
    path("<int:repo_id>/memberconf/",
         v3.RepositoryMemberConfApiView.as_view(),
         name="apiv3_org_repo_memberconf"),
    path("<int:repo_id>/memberconf/<int:role>/<str:username>/",
         v3.RepositoryMemberConfDeleteApiView.as_view(),
         name="apiv3_org_repo_memberconf_username"),
    path("<int:repo_id>/subscribed/",
         v3.RepositorySubscribedApiView.as_view(),
         name="apiv3_org_repo_subscribed"),
    path("<int:repo_id>/init/",
         v3.RepositoryInitApiView.as_view(),
         name="apiv3_org_repo_init"),
    path("<int:repo_id>/initscheme/",
         v3.RepositorySchemeInitApiView.as_view(),
         name="apiv3_org_repo_team_scheme_init"),
    path("<int:repo_id>/copyscheme/",
         v3.RepositorySchemeCopyApiView.as_view(),
         name="apiv3_org_repo_team_scheme_copy"),
    path("<int:repo_id>/branchnames/",
         v3.ScanBranchNameListApiView.as_view(),
         name="apiv3_org_team_repo_branchname_list"),
    path("<int:repo_id>/branch/projects/",
         v3.ScanBranchProjectListApiView.as_view(),
         name="apiv3_org_team_repo_branch_project_list"),
]

# 前缀 /api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repos/<int:repo_id>/schemes/
# 代码库分析方案路由
scheme_urlpatterns = [
    path("",
         v3.ScanSchemeListApiView.as_view(),
         name="apiv3_org_repo_team_scheme_list", ),
    path("<int:scheme_id>/",
         v3.ScanSchemeBasicConfApiView.as_view(),
         name="apiv3_org_repo_team_scheme_detail"),
    path("<int:scheme_id>/basicconf/",
         v3.ScanSchemeBasicConfApiView.as_view(),
         name="apiv3_org_repo_team_scheme_basicconf"),
    path("<int:scheme_id>/lintconf/",
         v3.ScanSchemeLintConfApiView.as_view(),
         name="apiv3_org_repo_team_scheme_lintconf"),
    path("<int:scheme_id>/metricconf/",
         v3.ScanSchemeMetricConfApiView.as_view(),
         name="apiv3_org_repo_team_scheme_metricconf"),
    path("<int:scheme_id>/scandirs/",
         v3.ScanSchemeDirListApiView.as_view(),
         name="apiv3_org_repo_team_scheme_scandir_list"),
    path("<int:scheme_id>/scandirs/bulkcreate/",
         v3.ScanSchemeDirBulkCreateApiView.as_view(),
         name="apiv3_org_repo_team_scheme_scandir_bulkcreate"),
    path("<int:scheme_id>/scandirs/clear/",
         v3.ScanSchemeDirClearApiView.as_view(),
         name="apiv3_org_repo_team_scheme_scandir_clear"),
    path("<int:scheme_id>/scandirs/<int:dir_id>/",
         v3.ScanSchemeDirDetailApiView.as_view(),
         name="apiv3_org_repo_team_scheme_scandir_detail"),
    path("<int:scheme_id>/branchs/",
         v3.ScanSchemeBranchListApiView.as_view(),
         name="apiv3_org_repo_team_scheme_branch_list"),
    path("<int:scheme_id>/pull/",
         v3.ScanSchemePullApiView.as_view(),
         name="apiv3_org_repo_team_scheme_pull"),
    path("<int:scheme_id>/defaultpaths/",
         v3.ScanSchemeDefaultScanPathListApiView.as_view(),
         name="apiv3_org_repo_team_scheme_defaultpath_list"),
    path("<int:scheme_id>/defaultpaths/<int:path_id>/",
         v3.ScanSchemeDefaultScanPathDetailApiView.as_view(),
         name="apiv3_org_repo_team_scheme_defaultpath_detail"),
    # 加载 scan_conf 模块的 v3_scheme
    path("<int:scheme_id>/", include("apps.scan_conf.api_urls.v3_scheme")),
]

# 前缀 /api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repos/<int:repo_id>/projects/
# 代码库分支项目路由
project_urlpatterns = [
    path("",
         v3.ProjectListApiView.as_view(),
         name="apiv3_org_team_repo_project_list"),
    path("<int:project_id>/",
         v3.ProjectDetailApiView.as_view(),
         name="apiv3_org_team_repo_project_detail"),
    path("<int:project_id>/codefile/",
         v3.ProjectCodeFileApiView.as_view(),
         name="apiv3_org_team_repo_project_codefile"),
    path("<int:project_id>/scans/",
         v3.ProjectScanCreateApiView.as_view(),
         name="apiv3_org_team_repo_project_scan_create"),
    path("<int:project_id>/jobs/<int:job_id>/",
         v3.ProjectJobDetailApiView.as_view(),
         name="apiv3_org_team_repo_project_job_detail"),
    path("<int:project_id>/jobs/<int:job_id>/tasks/<int:task_id>/",
         v3.ProjectJobTaskDetailApiView.as_view(),
         name="apiv3_org_team_repo_project_job_task_detail"),
    path("<int:project_id>/jobs/<int:job_id>/cancel/",
         v3.ProjectJobCancelApiView.as_view(),
         name="apiv3_org_team_repo_project_job_cancel"),
    path("<int:project_id>/scans/puppyini/",
         v3.ProjectScanPuppyiniApiView.as_view(),
         name="apiv3_org_team_repo_project_scans_puppyini"),

]


urlpatterns = [
    path("orgs/<str:org_sid>/teams/", include(team_urlpatterns)),
    path("orgs/<str:org_sid>/teams/<str:team_name>/repos/", include(repo_urlpatterns)),
    path("orgs/<str:org_sid>/teams/<str:team_name>/repos/<int:repo_id>/schemes/", include(scheme_urlpatterns)),
    path("orgs/<str:org_sid>/teams/<str:team_name>/repos/<int:repo_id>/projects/", include(project_urlpatterns)),
    path("orgs/<str:org_sid>/repos/", v3.OrgRepositoryListApiView.as_view(), name="apiv3_org_repo_list"),
    path("orgs/<str:org_sid>/schemes/", include(global_scheme_urlpatterns)),
    path("orgs/<str:org_sid>/checktools/", include("apps.scan_conf.api_urls.v3_checktool")),
    path("orgs/<str:org_sid>/toollibs/", include("apps.scan_conf.api_urls.v3_toollib")),
    path("orgs/<str:org_sid>/nodes/", include("apps.nodemgr.api_urls.v3")),
]
