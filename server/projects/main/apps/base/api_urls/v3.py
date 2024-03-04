# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - api urls
"""

from django.urls import path

# 项目内 import
from apps.nodemgr.apis import v2 as node_v2
from apps.scan_conf.apis import base as scan_base_apis

# 前缀：/api/v3
urlpatterns = [
    path("tags/", node_v2.ExecTagListAPIView.as_view(), name="apiv3_tag_list"),
    path("languages/", scan_base_apis.LanguageListAPIView.as_view(), name="apiv3_language_list"),
    path("labels/", scan_base_apis.LabelListAPIView.as_view(), name="apiv3_label_list"),
]
