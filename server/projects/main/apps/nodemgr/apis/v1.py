# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
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
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from django.http import HttpResponse

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
        logger.debug("[Node: %s][User: %s] upload node heart" % (node, request.user))
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
        slz.is_valid(raise_exception=True)
        org_sid = slz.validated_data.get("org_sid")
        if not NodeManager.validate_node_org(request.user, org_sid):
            if org_sid:
                raise PermissionDenied("用户%s不是团队%s的成员，无法注册节点" % (
                    request.user, org_sid))
            else:
                raise ParseError("未指定团队org_sid，无法注册节点")
        data = NodeManager.register_node(request, slz.validated_data)
        return Response(data)


class NodeStateExporterApiView(APIView):
    """节点状态查询接口

    ### GET
    应用场景：查询所有节点池中的全部节点数、活跃节点数以及空闲节点数，为Prometheus节点状态监控提供metrics。
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        REGISTRY = CollectorRegistry()
        LABELS = ['tag']  # 标签定义

        # 指标定义
        nodes_total = Gauge('nodes_total', 'Total number of nodes', LABELS, registry=REGISTRY)
        nodes_active = Gauge('nodes_active', 'Number of active nodes', LABELS, registry=REGISTRY)
        nodes_free = Gauge('nodes_free', 'Number of free nodes', LABELS, registry=REGISTRY)

        try:
            # 先获取所有的tag
            tags = models.ExecTag.objects.all()
            for tag in tags:
                # 遍历tag，也就是每一个节点池，统计每个节点池的节点总数和空闲节点数,在filter添加tag过滤条件
                total = models.Node.objects.filter(exec_tags=tag.id).count()
                active = models.Node.objects.filter(exec_tags=tag.id, enabled=1).count()
                free = models.Node.objects.filter(exec_tags=tag.id, enabled=1, state=0).count()  # 获取state字段为0的数据的条数

                nodes_total.labels(tag.name).set(total)
                nodes_active.labels(tag.name).set(active)
                nodes_free.labels(tag.name).set(free)

            return HttpResponse(generate_latest(REGISTRY), status=200, content_type="text/plain")
        except Exception as e:
            logger.exception(e)
            return HttpResponse('# HELP Error occured', status=500, content_type="text/plain")
