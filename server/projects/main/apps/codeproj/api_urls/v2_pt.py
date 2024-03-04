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


# 前缀 /api/v2/teams/
urlpatterns = [
    path("",
         v2_apis.ProjectTeamListAPIView.as_view(),
         name="apiv2_team_list"),
]
