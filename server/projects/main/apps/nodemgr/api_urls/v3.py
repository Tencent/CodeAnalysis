# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - v3 api urls
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.nodemgr.apis import v3

# 前缀 /api/v3/orgs/<org_sid>/nodes/
urlpatterns = [
    path("tags/", v3.OrgExecTagListAPIView.as_view(), name="apiv3_tag_list"),
    path("tags/<int:tag_id>/", v3.OrgExecTagDetailAPIView.as_view(), name="apiv3_tag_detail"),
    path("tags/<int:tag_id>/processes/", v3.OrgExecTagProcessesAPIView.as_view(),
         name="apiv3_tag_processes"),

    path("", v3.OrgNodeListAPIView.as_view(), name="apiv3_node_list"),
    path("<int:node_id>/", v3.OrgNodeDetailAPIView.as_view(), name="apiv3_node_detail"),
    path("<int:node_id>/processes/", v3.OrgNodeProcessesAPIView.as_view(), name="apiv3_node_processes"),
    path("<int:node_id>/tasks/", v3.OrgNodeTaskListAPIView.as_view(), name="apiv3_node_task_list"),
]
