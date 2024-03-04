# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job - base apis
"""
# python 原生import
import logging

# 第三方 import
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

# 项目内 import
from apps.authen.core import UserManager
from apps.codeproj.apimixins import ProjectBaseAPIView
from apps.job import core
from apps.job import models
from apps.job.api_filters import base as filters
from apps.job.permissions import JobUserPermission
from apps.job.serializers import base as serializers
from util import errcode
from util.permissions import RepositoryUserPermission

logger = logging.getLogger(__name__)


class RepoJobListApiView(generics.ListAPIView, ProjectBaseAPIView):
    """指定代码库任务列表接口

    ### Get
    应用场景：获取指定项目任务列表详情
    """
    serializer_class = serializers.JobSerializer
    permission_classes = [RepositoryUserPermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.JobFilterSet

    def get_queryset(self):
        repo = self.get_repo()
        return models.Job.objects.select_related("project__repo").filter(project__repo_id=repo.id).order_by("-id")


class RepoJobDetailApiView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """指定代码库任务详情接口

    ### Get
    应用场景：获取项目指定扫描job的详情
    """
    serializer_class = serializers.JobSerializer
    permission_classes = [RepositoryUserPermission]

    def get_object(self):
        repo = self.get_repo()
        job_id = self.kwargs["job_id"]
        return get_object_or_404(models.Job, id=job_id, project__repo_id=repo.id)


class JobListApiView(generics.ListAPIView):
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


class TaskListApiView(generics.ListAPIView):
    """子任务列表接口

    ### GET
    应用场景：获取子任务列表
    """
    schema = None
    serializer_class = serializers.TaskSerializer
    queryset = models.Task.objects.all().order_by("-id")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.TaskFilterSet
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
            core.JobCloseHandler.revoke_job(job, errcode.E_CLIENT_CANCELED,
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
            core.JobCloseHandler.close_scan(job.id)
        else:
            core.JobCloseHandler.close_scan(job.id, force=True)

    def post(self, request, **kwargs):
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            job_id = kwargs["job_id"]
            job = get_object_or_404(models.Job, id=job_id)
            logger.info("User( %s ) cancel job %s" % (request.user.username, job_id))
            try:
                remarks = slz.validated_data["remarks"]
                force = slz.validated_data["force"]
                self.cancel_job(request, job, force, remarks)
                return Response({"msg": "取消成功"})
            except Exception as e:
                logger.exception("Cancel job exception: %s" % e)
                raise ParseError({"cd_error": "取消任务异常"})
