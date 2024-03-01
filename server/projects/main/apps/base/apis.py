# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - apis
"""

# 原生引用
import logging

# 第三方 import
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# 项目内 import
from apps.authen.models import User
from apps.base.tasks import server_health_check


logger = logging.getLogger(__name__)


class BaseApiView(APIView):
    """基础接口，用于首页
    """
    schema = None
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"msg": "Weclome to CodeDog Server"})


class HealthCheckAPIVIew(APIView):
    """服务状态探测接口
    """
    schema = None
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        logger.info("[MainServerHealthCheck] Step 1: check db connection and orm operation")
        try:
            User.objects.all()
        except Exception as e:  # NOCA:broad-except(可能存在多种异常)
            logger.error("[MainServerHealthCheck] step 1 failed, err msg: %s" % e)
            return HttpResponse("DB connection or orm raise exception", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info("[MainServerHealthCheck] Step 2: check celery status and asynchronous tasks")
        file_name = request.GET.get("file_name", None)
        if file_name:
            server_health_check.delay(file_name)

        return HttpResponse("main server status check success", status=status.HTTP_200_OK)
