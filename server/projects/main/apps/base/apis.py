# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
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

# 项目内 import
from apps.authen.models import User
from apps.base.tasks import server_health_check
from codedog.celery import celery_app

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
        except Exception as e:
            logger.info("[MainServerHealthCheck] step 1 failed, err msg: %s" % e)
            return HttpResponse("DB connection or orm raise exception", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info("[MainServerHealthCheck] Step 2: check celery status and asynchronous tasks")
        try:
            res = server_health_check.delay()
            cycle_time = 10
            while cycle_time >= 0:
                async_task = AsyncResult(id=res.id, app=celery_app)
                if async_task.successful():
                    return HttpResponse("main server status check success", status=status.HTTP_200_OK)
                elif cycle_time == 0:
                    return HttpResponse("celery and asynchronous task raise exception",
                                        status=status.HTTP_424_FAILED_DEPENDENCY)
                cycle_time -= 1
            return HttpResponse("celery and asynchronous task raise exception",
                                status=status.HTTP_424_FAILED_DEPENDENCY)
        except Exception as e:
            logger.info("[MainServerHealthCheck] step 2 failed, err msg: %s" % e)
            return HttpResponse("celery and asynchronous task raise exception", status=status.HTTP_424_FAILED_DEPENDENCY)
