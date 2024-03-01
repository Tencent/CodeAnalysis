# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1 接口定义，供节点端、服务内部、外界调用
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.job.apis import v1 as apis

# 前缀 /api/projects/<project_id>/jobs/
urlpatterns = [
    # 服务内部专用
    path("<int:job_id>/", apis.ProjectJobApiView.as_view(),
         name="apiv1_project_job_detail"),
]
