# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================
"""
v2 api 接口url定义
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.authen.apis import v2

# 前缀/api/v2/orgs/
urlpatterns = [
    path("", v2.OrganizationListApiView.as_view(),
         name="apiv2_org_list"),
    path("<str:org_sid>/", v2.OrganizationDetailApiView.as_view(),
         name="apiv2_org_detail"),
    path("<str:org_sid>/status/", v2.OrganizationStatusApiView.as_view(),
         name="apiv2_org_status"),
]
