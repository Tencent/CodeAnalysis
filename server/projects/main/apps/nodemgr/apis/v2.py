# -*- coding: utf-8 -*-
"""
nodemgr - v2 apis
"""

# python 原生import
import logging

# 第三方 import
from rest_framework import generics

# 项目内 import
from apps.nodemgr import models
from apps.nodemgr.serializers import base as serializers
from util.permissions import IsSuperUserOrReadOnly

logger = logging.getLogger(__name__)


class ExecTagListView(generics.ListCreateAPIView):
    """标签列表

    ### get
    应用场景：获取标签列表

    ### post
    应用场景：创建标签，仅superuser
    """
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = serializers.ExecTagSerializer
    queryset = models.ExecTag.objects.all()


class ExecTagDetailView(generics.RetrieveUpdateAPIView):
    """标签详情

    ### get
    应用场景：获取标签详情

    ### put
    应用场景：更新标签，仅superuser
    """
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = serializers.ExecTagSerializer
    queryset = models.ExecTag.objects.all()
    lookup_url_kwarg = "tag_id"
