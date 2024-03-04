# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
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
    path("tags/", v2.ExecTagListAPIView.as_view(),
         name="apiv2_tag_list"),
    path("tags/<int:tag_id>/", v2.ExecTagDetailAPIView.as_view(),
         name="apiv2_tag_detail"),
    path("tags/<int:tag_id>/processes/", v2.TagProcessesAPIView.as_view(),
         name="apiv2_tag_processes"),
    path("nodes/", v2.NodeListAPIView.as_view(),
         name="apiv2_node_list"),
    path("nodes/options/", v2.NodeOptionAPIView.as_view(),
         name="apiv2_node_option_list"),
    path("nodes/<int:node_id>/", v2.NodeDetailAPIView.as_view(),
         name="apiv2_node_detail"),
    path("nodes/<int:node_id>/processes/", v2.NodeProcessesAPIView.as_view(),
         name="apiv2_node_processes"),
    path("nodes/<int:node_id>/tasks/", v2.NodeTaskListAPIView.as_view(),
         name="apiv2_node_task_list"),
    path("nodes/processes/", v2.AllProcessesAPIView.as_view(),
         name="apiv2_all_processes"),
    path("nodes/processes/batchupdate/", v2.NodeProcessesBatchUpdateAPIView.as_view(),
         name="apiv2_node_process_batchupdate"),
    path("nodes/batchupdate/", v2.NodeBatchUpdateAPIView.as_view(),
         name="apiv2_node_info_batchupdate"),
]
