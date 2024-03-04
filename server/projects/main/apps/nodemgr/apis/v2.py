# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
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
from util.permissions import IsSuperUserOrReadOnly

logger = logging.getLogger(__name__)


class ExecTagListAPIView(generics.ListCreateAPIView):
    """标签列表

    ### GET
    应用场景：获取标签列表

    ### POST
    应用场景：创建标签，仅superuser
    """
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = serializers.ExecTagSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.TagFilter
    queryset = models.ExecTag.objects.all()


class ExecTagDetailAPIView(generics.RetrieveUpdateAPIView):
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


class NodeListAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.NodeSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filterset_class = filters.NodeFilter

    def get_queryset(self):
        if self.request.user.is_superuser is True:
            return models.Node.objects.all().order_by("name")
        else:
            return models.Node.objects.filter(
                Q(manager=self.request.user) | Q(related_managers=self.request.user)
            ).order_by("name")


class NodeOptionAPIView(APIView):
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


class NodeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
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


class NodeBatchUpdateAPIView(generics.GenericAPIView):
    """节点批量更新接口
    ### PUT
    应用场景：修改节点详情
    """
    serializer_class = serializers.NodeBatchUpdateSerializer

    def put(self, request, **kwargs):
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        nodes = slz.validated_data.get("node_ids")
        NodeManager.batch_update_node_detail(nodes, slz.validated_data)
        return Response({"msg": "update success"})


class NodeProcessesAPIView(generics.GenericAPIView):
    """
    ### GET
    应用场景：获取节点进程配置情况

    ### PUT
    应用场景：修改节点进程配置，参数为get所得参数格式，按需修改supported的值为true or false即可
    """

    def get_node(self, request, **kwargs):
        """获取节点
        """
        node_id = kwargs["node_id"]
        if request.user.is_superuser is True:
            return get_object_or_404(models.Node, id=node_id)
        else:
            return get_object_or_404(models.Node, id=node_id, manager=request.user)

    def get(self, request, **kwargs):
        node = self.get_node(request, **kwargs)
        all_processes = NodeManager.get_all_processes()
        all_processes = NodeManager.get_support_process_relations(all_processes, node)
        return Response(all_processes)

    def put(self, request, **kwargs):
        node = self.get_node(request, **kwargs)
        data = request.data
        NodeManager.update_node_processes(node, data)
        return Response(data)


class NodeProcessesBatchUpdateAPIView(generics.GenericAPIView):
    """
    ### PUT
    应用场景：修改节点进程配置，参数为get所得参数格式，按需修改supported的值为true or false即可
    """
    serializer_class = serializers.NodeProcessesBatchUpdateSerializer

    def put(self, request, **kwargs):
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        nodes = slz.validated_data.get("node_ids")
        processes = slz.validated_data.get("processes")
        NodeManager.batch_update_node_processes(nodes, processes)
        return Response(processes)


class NodeTaskListAPIView(generics.ListAPIView):
    """
    ### GET
    应用场景：获取节点任务列表
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.NodeTaskSerializer

    def get_queryset(self):
        node_id = self.kwargs["node_id"]
        node = get_object_or_404(models.Node, id=node_id)
        return node.task_set.all().order_by("-id")


class AllProcessesAPIView(generics.GenericAPIView):
    """
    ### GET
    应用场景：获取节点可配置进程列表
    """

    def get(self, request, **kwargs):
        all_processes = NodeManager.get_all_processes()
        return Response(all_processes)


class TagProcessesAPIView(APIView):
    """
    ### GET
    应用场景：获取标签进程配置情况

    ### PUT
    应用场景：修改标签进程配置，参数为get所得参数格式，按需修改supported的值为true or false即可
    """
    permission_classes = [IsAdminUser]

    def get_tag(self, request, **kwargs):
        """获取标签
        """
        tag_id = kwargs["tag_id"]
        return get_object_or_404(models.ExecTag, id=tag_id)

    def get(self, request, **kwargs):
        tag = self.get_tag(request, **kwargs)
        all_processes = NodeManager.get_all_processes()
        all_processes = NodeManager.get_support_process_relations(all_processes, tag)
        return Response(all_processes)

    def put(self, request, **kwargs):
        tag = self.get_tag(request, **kwargs)
        data = request.data
        NodeManager.update_tag_processes(tag, data)
        return Response(data)
