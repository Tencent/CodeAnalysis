# -*- coding: utf-8 -*-
# Copyright (c) 2021-2025 Tencent
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - api urls
"""

from django.urls import path

from apps.base import apis


# 前缀：/
urlpatterns = [
    path("", apis.BaseApiView.as_view(), name="index_view"),
    path("healthcheck/", apis.HealthCheckAPIVIew.as_view(), name="sever_health_check"),
]
