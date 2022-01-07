# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 api urls for project

URL前缀： /api/projects/
用途：节点端、服务内部、开放接口

"""
# 第三方 import
from django.urls import path, include
from django.conf import settings

# 项目内 import
from apps.codeproj.apis import v1 as apis
from apps.scan_conf.apis import v1 as scan_conf_apis

# /api/projects/
urlpatterns = [
    # 转发到相应的模块
    path("<int:project_id>/jobs/", include('apps.job.api_urls.v1_project')),
]
