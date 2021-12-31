# -*- coding: utf-8 -*-
"""
job - base apis
"""
# python 原生import
import logging

# 第三方 import
from django.db.models import Count, Sum, Max
from django.utils.timezone import now, localtime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ParseError

# 项目内 import
from apps.job import models
from apps.job.api_filters import base as filters
from apps.job.serializers import base as serializers
from apps.job import core
from apps.job.permissions import JobUserPermission
from apps.authen.core import UserManager

from util import errcode


logger = logging.getLogger(__name__)


class JobsApiView(generics.ListAPIView):
    """任务列表接口

    ### GET
    应用场景：获取任务列表
    """
    schema = None
    serializer_class = serializers.JobSerializer
    queryset = models.Job.objects.all().order_by("-id")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.JobFilterSet
    permission_classes = [IsAdminUser]


class JobCancelApiView(generics.GenericAPIView):
    """任务取消接口

    ### POST
    应用场景：取消任务
    """

    schema = None
    permission_classes = [JobUserPermission]
    serializer_class = serializers.JobCancelSerializer

    def cancel_job(self, request, job, force, remarks):
        """取消任务
        """
        username = UserManager.get_username(request.user)
        if job.state not in [models.Job.StateEnum.CLOSED, models.Job.StateEnum.CLOSING]:
            """当前任务未关闭，可进行取消
            """
            core.revoke_job(job, errcode.E_CLIENT_CANCELED,
                            "User( %s ) Canceled: %s . " % (username, remarks))
            job.refresh_from_db()
            job.remarks = remarks
            job.remarked_by = request.user
            job.save()
        elif job.state == models.Job.StateEnum.CLOSING:
            """当前任务正在入库，强制取消
            """
            models.Job.objects.filter(id=job.id).update(
                result_code=errcode.E_CLIENT_CANCELED,
                result_msg="User( %s ) Canceled: %s.[Job is closing] " % (username, remarks),
                state=models.Job.StateEnum.CLOSED,
                expire_time=now(),
                remarks=remarks,
                remarked_by=request.user
            )
            core.close_scan(job.id)
        else:
            core.close_scan(job.id)

    def post(self, request, job_id):
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            job = get_object_or_404(models.Job, id=job_id)
            logger.info("User( %s ) cancel job %s" %
                        (request.user.username, job_id))
            try:
                remarks = slz.validated_data["remarks"]
                force = slz.validated_data["force"]
                self.cancel_job(request, job, force, remarks)
                return Response({"msg": "取消成功"})
            except Exception as e:
                logger.exception("Cancel job exception: %s" % e)
                raise ParseError({"cd_error": "取消任务异常"})

