# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""codedog URL Configuration
"""
from django.conf import settings
from django.urls import path, include

from rest_framework.documentation import include_docs_urls

# 注意
urlpatterns = [
    path("", include("apps.base.api_urls")),
    path("prometheus/", include("django_prometheus.urls")),
]

# V1 API
urlpatterns += [
    # 服务内部调用
    path("api/base/", include("apps.codeproj.api_urls.v1_base")),
    path("api/projects/", include("apps.codeproj.api_urls.v1_tiyan_project")),

    # 开放接口
    path("api/orgs/<str:org_sid>/teams/<str:team_name>/repos/", include("apps.codeproj.api_urls.v1_pt")),  # 从库

    # V3 API
    path("api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repos/", include("apps.codeproj.api_urls.v3_pt")),
]

# 根据DEBUG状态显示接口文档
if settings.DEBUG is True:
    urlpatterns += [
        path("api/docs/", include_docs_urls(
            title="CODEDOG ANALYSE API",
            public=True,
            authentication_classes=[],
            permission_classes=[]
        ))]
