# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
基础 接口模块
"""

# 原生
import logging

# 第三方
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)


class BaseApiView(APIView):
    """基础接口，用于首页
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """获取基础页数据
        """
        return Response(data={"msg": "Weclome to CodeDog FTP Server"})


class HealthCheckAPIVIew(APIView):
    """服务状态探测接口
    """
    schema = None
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        logger.info("[FileServerHealthCheck] check db connection and orm operation")
        try:
            Group.objects.all()
        except Exception as e:
            logger.info("[FileServerHealthCheck] check db failed, err msg: %s" % e)
            return HttpResponse("DB connection or orm raise exception", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return HttpResponse("file server status check success", status=status.HTTP_200_OK)
