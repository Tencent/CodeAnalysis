# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1_job 接口定义

URL前缀： /api/jobs/
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.job.apis import v1_pt as apis_v1_pt

# 前缀 /api/jobs/
urlpatterns = [
    path("taskqueue/nodes/<int:node_id>/tasks/register/", apis_v1_pt.NodeTaskRegisterAPIView.as_view(),
         name="apiv1_node_task_register"),
    path("taskqueue/nodes/<int:node_id>/tasks/<int:task_id>/ack/", apis_v1_pt.NodeTaskAckApiView.as_view(),
         name="apiv1_node_task_ack"),
]
