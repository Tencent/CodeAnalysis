# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1 接口定义，供节点端调用

URL前缀：api/nodes/
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.nodemgr.apis import v1

urlpatterns = [
    path("<int:node_id>/heartbeat/", v1.NodeHeartBeatApiView.as_view(), name="apiv1_node_heart_beat"),
    path("<int:node_id>/status/", v1.NodeStatusApiView.as_view(), name="apiv1_node_status"),
    path("register/", v1.NodeRegisterApiView.as_view(), name="apiv1_node_register"),
    path("nodestate/metrics/", v1.NodeStateExporterApiView.as_view(), name="apiv1_node_state_metrics"),
]
