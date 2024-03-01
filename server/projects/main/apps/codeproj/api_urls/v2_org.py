# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================
"""
v2 api 接口url定义，v2系列接口均供前端页面调用
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.codeproj.apis import v2 as v2_apis


# 前缀 /api/orgs/<org_sid>/teams/
urlpatterns = [
    path("",
         v2_apis.OrgProjectTeamListAPIView.as_view(),
         name="apiv2_org_team_list"),
    path("<str:team_name>/",
         v2_apis.OrgProjectTeamDetailAPIView.as_view(),
         name="apiv2_org_team_detail"),
    path("<str:team_name>/status/",
         v2_apis.OrgProjectTeamStatusAPIView.as_view(),
         name="apiv2_org_team_status"),
]
