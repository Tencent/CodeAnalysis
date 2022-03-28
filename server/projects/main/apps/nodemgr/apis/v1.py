# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

# -*- coding: utf8 -*-
"""
Node Restful Api实现
"""
# python 原生import
import logging

# 第三方 import
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import exceptions
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内 import
from apps.authen.backends import TCANodeTokenBackend
from apps.nodemgr import filters, models
from apps.nodemgr import serializers
from apps.nodemgr.core import NodeManager

logger = logging.getLogger(__name__)


class NodesApiView(generics.ListAPIView):
    """节点列表接口

    ### GET
    应用场景：获取当前用户管理的节点列表

    ### POST
    应用场景：根据uuid查询或新建一个节点
    """
    authentication_classes = [TCANodeTokenBackend]
    permission_classes = [IsAdminUser]
    serializer_class = serializers.NodeSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    filterset_class = filters.NodeFilter

    def get_queryset(self):
        return models.Node.objects.all()


class NodeHeartBeatApiView(APIView):
    """节点心跳接口
    
    ### POST
    应用场景：上报心跳接口
    """
    authentication_classes = [TCANodeTokenBackend]

    def post(self, request, node_id):
        node = get_object_or_404(models.Node, id=node_id)
        logger.debug("[Node: %s][User: %s] upload node heart" % (node_id, request.user))
        if request.user != node.manager:
            raise exceptions.PermissionDenied("非节点管理员无权操作")
        if node.enabled == models.Node.EnabledEnum.DISABLED:
            raise exceptions.ValidationError("节点处于不可用状态")
        result = NodeManager.refresh_active_node_hb(request, node)
        return Response(result)


class NodeStatusApiView(generics.GenericAPIView):
    """节点状态接口

    ### GET
    应用场景：获取节点最近的一次状态信息

    ### POST
    应用场景：更新或新建一个节点最近的状态信息
    """
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.NodeStatusSerializer

    def get(self, request, node_id):
        ns = models.NodeStatus.objects.filter(node_id=node_id).order_by("-id").first()
        status_slz = self.get_serializer(ns)
        return Response(status_slz.data)

    def post(self, request, node_id):
        node = get_object_or_404(models.Node, id=node_id)
        ns = models.NodeStatus.objects.filter(node=node).order_by("-id").first() or models.NodeStatus(node=node)
        status_slz = self.get_serializer(ns, data=request.data)
        if status_slz.is_valid():
            status_slz.save()
            return Response(status_slz.data)
        else:
            return Response(status_slz.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeRegisterApiView(generics.GenericAPIView):
    """节点注册接口

    ### POST
    应用场景：根据uuid查询或新建一个节点，并回收节点正在执行的任务。
    支持 执行环境标签参数，如果是新建或未配置标签，可以将其置为指定的标签，否则维持原有标签。
    """
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.NodeRegisterSerializer

    def post(self, request):
        slz = self.get_serializer(data=request.data)
        if slz.is_valid():
            data = NodeManager.register_node(request, slz.validated_data)
            return Response(data)
        else:
            return Response(slz.errors, status=status.HTTP_400_BAD_REQUEST)
