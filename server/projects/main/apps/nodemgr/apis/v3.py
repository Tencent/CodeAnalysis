# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - v3 apis
"""

# python 原生import
import logging

# 第三方 import
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

# 项目内 import
from apps.authen.permissions import OrganizationDefaultPermission
from apps.nodemgr import models
from apps.nodemgr.apis import v2 as api_v2
from apps.nodemgr.core import NodeManager
from apps.nodemgr.permissions import OrganizationNodeAdminPermission
from apps.nodemgr.serializers import v3 as serializers_v3

logger = logging.getLogger(__name__)


class OrgExecTagListAPIView(api_v2.ExecTagListAPIView):
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


class OrgExecTagDetailAPIView(generics.RetrieveUpdateAPIView):
    """团队标签详情

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


class OrgExecTagProcessesAPIView(api_v2.TagProcessesAPIView):
    """团队标签进程列表

    ### GET
    应用场景：获取指定标签的进程列表

    ### PUT
    应用场景：修改标签进程配置，参数为get所得参数格式，按需修改supported的值为true or false即可
    """
    permission_classes = [OrganizationDefaultPermission]

    def get_tag(self, request, **kwargs):
        """获取标签
        """
        org_sid = self.kwargs["org_sid"]
        tag_id = kwargs["tag_id"]
        tag = get_object_or_404(models.ExecTag, id=tag_id)
        if tag.org_sid == org_sid or tag.org_sid is None:
            return tag
        else:
            raise NotFound({"cd_error": "Tag-%s标签不存在" % tag_id})

    def put(self, request, **kwargs):
        """修改标签进程配置
        """
        tag = self.get_tag(request, **kwargs)
        if tag.org_sid is None:
            raise NotFound({"cd_error": "Tag-%s为公共标签，不能修改" % tag.display_name})
        data = request.data
        NodeManager.update_tag_processes(tag, data)
        return Response(data)


class OrgNodeListAPIView(api_v2.NodeListAPIView):
    """指定团队的节点列表

    ### GET
    应用场景：获取指定团队的节点列表
    """
    permission_classes = [OrganizationDefaultPermission]

    def get_queryset(self):
        org_sid = self.kwargs["org_sid"]
        return models.Node.objects.filter(org_sid=org_sid)


class OrgNodeDetailAPIView(api_v2.NodeDetailAPIView):
    """指定团队的节点详情

    ### GET
    应用场景：获取指定团队的节点详情
    """
    permission_classes = [OrganizationNodeAdminPermission]
    serializer_class = serializers_v3.OrgNodeSerializer

    def get_object(self):
        org_sid = self.kwargs["org_sid"]
        node_id = self.kwargs["node_id"]
        return get_object_or_404(models.Node, id=node_id, org_sid=org_sid)


class OrgNodeProcessesAPIView(api_v2.NodeProcessesAPIView):
    """指定团队的节点进程列表

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
    """指定团队的节点任务列表

    ### GET
    应用场景：获取节点任务列表
    """
    permission_classes = [OrganizationNodeAdminPermission]

    def get_queryset(self):
        org_sid = self.kwargs["org_sid"]
        node_id = self.kwargs["node_id"]
        node = get_object_or_404(models.Node, id=node_id, org_sid=org_sid)
        return node.task_set.all().order_by("-id")
