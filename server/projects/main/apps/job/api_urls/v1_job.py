# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1 接口定义，供节点端调用
"""
# 第三方 import
from django.urls import path
from django.conf import settings

# 项目内 import
from apps.job.apis import base as apis
from apps.job.apis import v1 as apis_v1

# url前缀：/api/jobs/
urlpatterns = [
    path("", apis.JobsApiView.as_view(),
         name="apiv1_jobs"),
    path("<int:job_id>/", apis_v1.JobApiView.as_view(),
         name="apiv1_job_detail"),
    path("<int:job_id>/tasks/", apis_v1.JobTasksApiView.as_view(),
         name="apiv1_job_tasks"),
    path("<int:job_id>/tasksbeat/", apis_v1.JobTasksBeatApiView.as_view(),
         name="apiv1_job_tasksbeat"),
    path("<int:job_id>/tasks/<int:task_id>/", apis_v1.TaskDetailApiView.as_view(),
         name="apiv1_job_task_detail"),
    path("<int:job_id>/tasks/<int:task_id>/progresses/", apis_v1.TaskProgressApiView.as_view(),
         name="apiv1_job_task_progresses"),
]
