# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
文件管理 API路由
"""
from django.urls import re_path, path

from apps.filemgr import apis

# 前缀: /api/files/
urlpatterns = [
    re_path(r"^auth/files/(?P<uri>[^?]+)$", apis.AuthAPIView.as_view()),
    re_path(r"options/(?P<bucket>[a-zA-Z0-9]+)/(?P<dir_path>[^?/]+)", apis.AppUnitConfigAPIView.as_view()),
    path("logs", apis.FileLogAPIView.as_view()),
    path("error", apis.ErrorCallbackAPIView.as_view()),

    re_path(r'(?P<uri>[^?]+)$', apis.CDLocalStorageView.as_view()),  # 本地存储
]
