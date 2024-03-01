# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1_pt 接口定义

URL前缀： /api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/jobs/
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.job.apis import v1_pt as apis_v1_pt

# 前缀 /api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/jobs/
urlpatterns = [
    # 通用
    path("", apis_v1_pt.ProjectJobListAPIView.as_view(),
         name="apiv1_project_job_list"),
    path("init/", apis_v1_pt.ProjectScanJobInitAPIView.as_view(),
         name="apiv1_project_scan_job_init"),
    path("<int:job_id>/finish/", apis_v1_pt.ProjectJobFinishAPIView.as_view(),
         name="apiv1_project_job_finish"),

    path("<int:job_id>/detail/", apis_v1_pt.ProjectJobDetailAPIView.as_view(),
         name="apiv1_job_detail"),
    path("<int:job_id>/codeline/", apis_v1_pt.JobCodeLineAPIView.as_view(),
         name="apiv1_job_code_info"),
    path("<int:job_id>/tasks/", apis_v1_pt.JobTasksAPIView.as_view(),
         name="apiv1_job_tasks"),
    path("<int:job_id>/tasksbeat/", apis_v1_pt.JobTasksBeatAPIView.as_view(),
         name="apiv1_job_tasksbeat"),
    path("<int:job_id>/privatetasks/", apis_v1_pt.ExcutePrivateTaskAPIView.as_view(),
         name="apiv1_job_private_tasks_execute"),
    path("<int:job_id>/tasks/<int:task_id>/", apis_v1_pt.TaskDetailAPIView.as_view(),
         name="apiv1_job_task_detail"),
    path("<int:job_id>/tasks/<int:task_id>/progresses/", apis_v1_pt.TaskProgressAPIView.as_view(),
         name="apiv1_job_task_progresses"),
]
