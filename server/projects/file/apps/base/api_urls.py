# -*- coding: utf-8 -*-
"""
基础 接口路由
"""

from django.urls import path

from apps.base import apis

urlpatterns = [
    path("", apis.BaseApiView.as_view(), name="api_base_view"),
]
