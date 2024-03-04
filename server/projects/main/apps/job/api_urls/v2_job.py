# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v2 api 接口url定义，v2系列接口均供前端页面调用
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.job.apis import base as apis

# 前缀 /api/v2/jobs/
urlpatterns = [
    path("", apis.JobListApiView.as_view(), name="apiv2_job_list"),
    path("<int:job_id>/cancel/", apis.JobCancelApiView.as_view(),
         name="apiv2_job_cancel"),
    path("tasks/", apis.TaskListApiView.as_view(), name="apiv2_task_list"),
]
