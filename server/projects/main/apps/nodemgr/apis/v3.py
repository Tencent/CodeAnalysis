# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - v2 apis
"""

# python 原生import
import logging

# 第三方 import
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics

# 项目内 import
from apps.authen.permissions import OrganizationDefaultPermission
from apps.nodemgr import models
from apps.nodemgr.apis import v2 as api_v2
from apps.nodemgr.permissions import OrganizationNodeAdminPermission
from apps.nodemgr.serializers import v3 as serializers_v3

logger = logging.getLogger(__name__)


class OrgExecTagListView(generics.ListCreateAPIView):
    """标签列表

    ### GET
    应用场景：获取标签列表

    ### POST
    应用场景：创建标签，仅团队管理员
    """
    permission_classes = [OrganizationDefaultPermission]
    serializer_class = serializers_v3.OrgExecTagSerializer

    def get_queryset(self):
        org_sid = self.kwargs["org_sid"]
        return models.ExecTag.objects.filter(Q(org_sid=org_sid) | Q(org_sid__isnull=True))


class OrgExecTagDetailView(generics.RetrieveUpdateAPIView):
    """标签详情

    ### GET
    应用场景：获取标签详情

    ### PUT
    应用场景：更新标签，仅团队管理员
    """
    permission_classes = [OrganizationDefaultPermission]
    serializer_class = serializers_v3.OrgExecTagSerializer

    def get_object(self):
        org_sid = self.kwargs["org_sid"]
        tag_id = self.kwargs["tag_id"]
        return get_object_or_404(models.ExecTag, id=tag_id, org_sid=org_sid)


class OrgNodeListAPIView(api_v2.NodeListAPIView):
    permission_classes = [OrganizationDefaultPermission]

    def get_queryset(self):
        org_sid = self.kwargs["org_sid"]
        return models.Node.objects.filter(org_sid=org_sid)


class OrgNodeDetailAPIView(api_v2.NodeDetailAPIView):
    permission_classes = [OrganizationNodeAdminPermission]
    serializer_class = serializers_v3.OrgNodeSerializer

    def get_object(self):
        org_sid = self.kwargs["org_sid"]
        node_id = self.kwargs["node_id"]
        return get_object_or_404(models.Node, id=node_id, org_sid=org_sid)


class OrgNodeProcessesAPIView(api_v2.NodeProcessesAPIView):
    """
    ### GET
    应用场景：获取节点进程配置情况

    ### PUT
    应用场景：修改节点进程配置，参数为get所得参数格式，按需修改supported的值为true or false即可
    """
    permission_classes = [OrganizationNodeAdminPermission]

    def get_node(self, request, **kwargs):
        """获取节点
        """
        org_sid = kwargs["org_sid"]
        node_id = kwargs["node_id"]
        return get_object_or_404(models.Node, id=node_id, org_sid=org_sid)


class OrgNodeTaskListAPIView(api_v2.NodeTaskListAPIView):
    """
    ### GET
    应用场景：获取节点任务列表
    """
    permission_classes = [OrganizationNodeAdminPermission]

    def get_queryset(self):
        org_sid = self.kwargs["org_sid"]
        node_id = self.kwargs["node_id"]
        node = get_object_or_404(models.Node, id=node_id, org_sid=org_sid)
        return node.task_set.all().order_by("-id")
