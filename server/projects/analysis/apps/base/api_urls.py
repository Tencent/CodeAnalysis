# -*- coding: utf-8 -*-
# Copyright (c) 2021-2025 Tencent
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""基础接口
"""
from django.urls import path

from . import apis

# 前缀：/
urlpatterns = [
    path('', apis.BaseApiView.as_view(), name="index_view"),
    path("healthcheck/", apis.HealthCheckAPIVIew.as_view(), name="sever_health_check"),
]
