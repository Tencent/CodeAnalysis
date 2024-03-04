# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - apis
"""

import logging

# 第三方 import
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from celery.result import AsyncResult
from django.contrib.auth.models import User

# 项目内 import
from apps.base.tasks import server_health_check
from codedog.celery import celery_app

logger = logging.getLogger(__name__)


class BaseApiView(APIView):
    """基础接口，用于首页
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """获取基础页数据
        """
        return Response(data={"msg": "Weclome to CodeDog Server"})


class HealthCheckAPIVIew(APIView):
    """服务状态探测接口
    """
    schema = None
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        logger.info("[AnalysisServerHealthCheck] Step 1: check db connection and orm operation")
        try:
            User.objects.all()
        except Exception as e:
            logger.info("[AnalysisServerHealthCheck] step 1 failed, err msg: %s" % e)
            return HttpResponse("DB connection or orm raise exception", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info("[AnalysisServerHealthCheck] Step 2: check celery status and asynchronous tasks")
        file_name = request.GET.get("file_name", None)
        if file_name:
            server_health_check.delay(file_name)

        return HttpResponse("analysis server status check success", status=status.HTTP_200_OK)
