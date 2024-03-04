# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""codedog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r"^$", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r"^$", Home.as_view(), name="home")
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r"^blog/", include(blog_urls))
"""
import logging

from django.contrib import admin
from django.conf import settings
from django.urls import include, path

from rest_framework.documentation import include_docs_urls

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator

logger = logging.getLogger(__name__)


# 自定义URL路径前缀
class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema.base_path = settings.SWAGGER_SETTINGS["API_PREFIX"] + schema.base_path
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="CodeDog API",
        default_version="v1",
        description="CodeDog Server API Docs，该接口文档包含代码库信息、项目配置等数据",
        contact=openapi.Contact(email="codedog@tencent.com"),
    ),
    url=settings.SWAGGER_SETTINGS["API_URL"],
    patterns=[
        path("api/orgs/<str:org_sid>/", include("apps.codeproj.api_urls.v1_org")),
        path("api/conf/", include("apps.scan_conf.api_urls.v1")),

    ],
    public=True,
    authentication_classes=(),
    permission_classes=(),
    generator_class=CustomOpenAPISchemaGenerator,
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include("apps.base.api_urls.base")),
    path("prometheus/", include("django_prometheus.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

urlpatterns += [
    # V1 APIs
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger"),
    path("api/authen/", include("apps.authen.api_urls.v1")),  # 内部调用专用
    path("api/projects/", include("apps.codeproj.api_urls.v1_project")),
    path("api/conf/", include("apps.scan_conf.api_urls.v1")),
    path("api/jobs/", include("apps.job.api_urls.v1_job")),
    path("api/nodes/", include("apps.nodemgr.api_urls.v1")),
    path("api/orgs/<str:org_sid>/", include("apps.codeproj.api_urls.v1_org")),

    # V2 APIs
    path("api/v2/authen/", include("apps.authen.api_urls.v2")),
    path('api/v2/orgs/', include('apps.authen.api_urls.v2_org')),
    path("api/v2/orgs/<str:org_sid>/teams/", include("apps.codeproj.api_urls.v2_org")),
    path('api/v2/teams/', include('apps.codeproj.api_urls.v2_pt')),
    path("api/v2/jobs/", include("apps.job.api_urls.v2_job")),
    path("api/v2/checktools/", include("apps.scan_conf.api_urls.v2_checktool")),
    path("api/v2/", include("apps.nodemgr.api_urls.v2")),

    # V3 APIs
    path("api/v3/", include("apps.base.api_urls.v3")),
    path("api/v3/authen/", include("apps.authen.api_urls.v3")),
    path("api/v3/", include("apps.authen.api_urls.v3_org")),
    path("api/v3/", include("apps.codeproj.api_urls.v3")),
]

# 根据DEBUG状态显示接口文档和管理页面
if settings.DEBUG is True:
    urlpatterns += [
        path("api/docs/", include_docs_urls(
            title="CODEDOG MAIN API",
            public=True,
            permission_classes=[],
            authentication_classes=[]
        )),
        path("admin/", admin.site.urls),
    ]
