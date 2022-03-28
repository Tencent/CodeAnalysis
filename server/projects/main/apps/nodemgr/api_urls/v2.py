# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - v2 api urls
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.nodemgr.apis import v2

# 前缀 /api/v2/
urlpatterns = [
    path("tags/", v2.ExecTagListView.as_view(), name="apiv2_tag_list"),
    path("tags/<int:tag_id>/", v2.ExecTagDetailView.as_view(), name="apiv1_tag_detail"),
    path("nodes/", v2.NodeListView.as_view(), name="apiv2_node_list"),
    path("nodes/options/", v2.NodeOptionApiView.as_view(), name="apiv2_node_option_list"),
    path("nodes/<int:node_id>/", v2.NodeApiView.as_view(), name="apiv2_node_detail"),
    path("nodes/<int:node_id>/processes/", v2.NodeProcessesApiView.as_view(), name="apiv2_node_processes"),
    path("nodes/<int:node_id>/tasks/", v2.NodeTaskListApiView.as_view(), name="apiv2_node_task_list"),
]
