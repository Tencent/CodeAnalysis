# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 api urls for toollib
"""
# 第三方
from django.urls import path

# 项目内
from apps.scan_conf.apis import v3 as apis

# 前缀/api/v3/orgs/<str:org_sid>/toollibs/
urlpatterns = [
    path("",
         apis.ToolLibListAPIView.as_view()),
    path("<int:toollib_id>/",
         apis.ToolLibDetailAPIView.as_view()),
]
