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
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内 import
from apps.nodemgr import filters, models
from apps.nodemgr.core import NodeManager
from apps.nodemgr.serializers import base as serializers
from apps.scan_conf.models import ToolProcessRelation
from util.permissions import IsSuperUserOrReadOnly

logger = logging.getLogger(__name__)


class ExecTagListView(generics.ListCreateAPIView):
    """标签列表

    ### GET
    应用场景：获取标签列表

    ### POST
    应用场景：创建标签，仅superuser
    """
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = serializers.ExecTagSerializer
    queryset = models.ExecTag.objects.all()


class ExecTagDetailView(generics.RetrieveUpdateAPIView):
    """标签详情

    ### GET
    应用场景：获取标签详情

    ### PUT
    应用场景：更新标签，仅superuser
    """
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = serializers.ExecTagSerializer
    queryset = models.ExecTag.objects.all()
    lookup_url_kwarg = "tag_id"


class NodeListView(generics.ListCreateAPIView):
    serializer_class = serializers.NodeSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filterset_class = filters.NodeFilter

    def get_queryset(self):
        if self.request.user.is_superuser is True:
            return models.Node.objects.all().order_by("name")
        else:
            return models.Node.objects.filter(manager=self.request.user).order_by("name")


class NodeOptionApiView(APIView):
    """node optionsj接口

    ### GET
    应用场景：获取节点的options数据
    """

    def get(self, request):
        name_or_ip = request.query_params.get("name_or_ip", None)
        queryset = models.Node.objects.all()
        node_option_list = (
            queryset.filter(Q(name__icontains=name_or_ip) |
                            Q(addr__icontains=name_or_ip)) if name_or_ip else queryset
        ).values("id", "addr", "name")
        return Response(node_option_list)


class NodeApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    ### GET
    应用场景：获取节点详情

    ### PUT
    应用场景：修改节点详情

    ### DELETE
    应用场景：删除节点
    """
    serializer_class = serializers.NodeSerializer
    queryset = models.Node.objects.all()
    lookup_url_kwarg = "node_id"

    def get_object(self):
        if self.request.user.is_superuser is True:
            return get_object_or_404(models.Node, id=self.kwargs["node_id"])
        else:
            return get_object_or_404(models.Node, id=self.kwargs["node_id"], manager=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_superuser is True:
            instance.delete()
        else:
            raise PermissionDenied()


class NodeProcessesApiView(APIView):
    """
    ### GET
    应用场景：获取节点进程配置情况

    ### PUT
    应用场景：修改节点进程配置，参数为get所得参数格式，按需修改supported的值为true or false即可
    """

    def get_node(self, request, node_id):
        """获取节点
        """
        if request.user.is_superuser is True:
            return get_object_or_404(models.Node, id=int(node_id))
        else:
            return get_object_or_404(models.Node, id=int(node_id), manager=request.user)

    def get(self, request, node_id):
        node = self.get_node(request, node_id)
        result = {}
        for tool_process in ToolProcessRelation.objects.all():
            processes = result.get(tool_process.checktool.name, {})
            processes.update({tool_process.process.name: {"supported": False}})
            result.update({tool_process.checktool.name: processes})
        for node_tool_process in models.NodeToolProcessRelation.objects.filter(node=node):
            try:
                result[node_tool_process.checktool.name][node_tool_process.process.name]["supported"] = True
                result[node_tool_process.checktool.name][node_tool_process.process.name]["id"] = node_tool_process.id
            except Exception as e:
                logger.exception("[Tool: %s][Process: %s] err: %s" % (
                    node_tool_process.checktool.name, node_tool_process.process.name, e))
        return Response(result)

    def put(self, request, node_id):
        data = request.data
        node = self.get_node(request, node_id)
        NodeManager.update_node_processes(node, data)
        return Response(data)


class NodeTaskListApiView(generics.ListAPIView):
    """
    ### GET
    应用场景：获取节点任务列表
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.NodeTaskSerializer

    def get_queryset(self):
        node_id = self.kwargs["node_id"]
        node = get_object_or_404(models.Node, id=int(node_id))
        return node.task_set.all().order_by("-id")
