# -*- coding: utf-8 -*-
"""
job - v1 apsi for job
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.job.apis import v1_tiyan

# url前缀：/api/jobs/
urlpatterns = [

    path("<int:job_id>/", v1_tiyan.JobApiView.as_view(),
         name="apiv1_job_detail"),
    path("<int:job_id>/tasksbeat/", v1_tiyan.JobTasksBeatApiView.as_view(),
         name="apiv1_job_tasksbeat"),
    path("<int:job_id>/tasks/<int:task_id>/", v1_tiyan.TaskDetailApiView.as_view(),
         name="apiv1_job_task_detail"),
    path("<int:job_id>/tasks/<int:task_id>/progresses/", v1_tiyan.TaskProgressApiView.as_view(),
         name="apiv1_job_task_progresses"),
]
