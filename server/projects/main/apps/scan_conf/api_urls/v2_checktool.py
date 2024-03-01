# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v2 api urls for checktool
"""
# 第三方
from django.urls import path

# 项目内
from apps.scan_conf.apis import v2 as apis

# 前缀/api/v2/checktools/
urlpatterns = [
    path("",
         apis.CheckToolListAPIView.as_view(),
         name="apiv2_checktool_list"),
    path("<int:checktool_id>/open/",
         apis.CheckToolOpenUpdateAPIView.as_view(),
         name="apiv2_checktool_open")
]
