# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job - v1 apis for project team
"""

# 第三方 import
from django.shortcuts import get_object_or_404

# 项目内 import
from apps.authen.backends import TCANodeTokenBackend
from apps.codeproj.apimixins import ProjectTeamBaseAPIView
from apps.codeproj.permissions import RepositoryProjectDefaultPermission
from apps.job import models
from apps.job.api_filters import v3 as v3_filters
from apps.job.apis import v1
from apps.job.serializers import v3 as v3_serializers


class ProjectJobListAPIView(v1.ProjectJobListApiView, ProjectTeamBaseAPIView):
    """项目任务列表接口

    ### GET
    应用场景：获取指定项目任务列表详情
    """
    filterset_class = v3_filters.JobFilterSetV3
    permission_classes = [RepositoryProjectDefaultPermission]


class ProjectJobDetailAPIView(v1.ProjectJobDetailApiView, ProjectTeamBaseAPIView):
    """项目任务详情接口

    ### GET
    应用场景：获取指定项目指定任务详情
    """
    serializer_class = v3_serializers.JobSerializerV3
    permission_classes = [RepositoryProjectDefaultPermission]


class ProjectScanJobInitAPIView(v1.ProjectScanJobInitApiView, ProjectTeamBaseAPIView):
    """项目扫描初始化
    使用对象：节点

    ### GET
    应用场景：获取项目扫描配置的api，供节点端离线扫描使用

    ### POST
    应用场景：创建新的扫描任务，仅做初始化
    """
    permission_classes = [RepositoryProjectDefaultPermission]


class ProjectJobFinishAPIView(v1.ProjectJobFinishApiView, ProjectTeamBaseAPIView):
    """项目本地扫描完成，上报结果
    使用对象：节点

    ### POST
    应用场景：上报本地扫描的任务结果
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]


class JobCodeLineAPIView(v1.JobApiView, ProjectTeamBaseAPIView):
    """任务代码行数信息接口

    ### GET
    应用场景：获取指定job的代码行数详情

    ### PUT
    应用场景：修改job的代码行数字段内容
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]

    def get_object(self):
        project = self.get_project()
        return models.Job.objects.get(id=self.kwargs["job_id"], project=project)


class JobTasksAPIView(v1.JobTasksApiView, ProjectTeamBaseAPIView):
    """指定Job的task列表查询接口

    ### GET
    应用场景：获取Job的Task列表
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]

    def get_queryset(self):
        project = self.get_project()
        job = get_object_or_404(models.Job, id=self.kwargs["job_id"], project=project)
        return models.Task.objects.filter(job_id=job.id).order_by("-id")


class JobTasksBeatAPIView(v1.JobTasksBeatApiView, ProjectTeamBaseAPIView):
    """指定Task的心跳上报接口

    ### POST
    应用场景：更新job下所有task的心跳时间
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]

    def post(self, request, **kwargs):
        project = self.get_project()
        get_object_or_404(models.Job, id=kwargs["job_id"], project=project)
        return super().post(request, **kwargs)


class ExcutePrivateTaskAPIView(v1.ExcutePrivateTask, ProjectTeamBaseAPIView):
    """私有化任务执行接口

    ### GET
    应用场景：获取未执行的私有任务
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]

    def post(self, request, **kwargs):
        project = self.get_project()
        get_object_or_404(models.Job, id=kwargs["job_id"], project=project)
        return super().post(request, **kwargs)


class TaskDetailAPIView(v1.TaskDetailApiView, ProjectTeamBaseAPIView):
    """任务结果上报接口

    ### POST
    应用场景：上报任务结果
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]

    def put(self, request, **kwargs):
        project = self.get_project()
        get_object_or_404(models.Job, id=kwargs["job_id"], project=project)
        return super().put(request, **kwargs)


class TaskProgressAPIView(v1.TaskProgressApiView, ProjectTeamBaseAPIView):
    """任务进程上报接口

    ### POST
    应用场景：上报任务进度
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]

    def get_queryset(self):
        project = self.get_project()
        job = get_object_or_404(models.Job, id=self.kwargs["job_id"], project=project)
        return models.TaskProgress.objects.filter(task__id=self.kwargs["task_id"], task__job_id=job.id)


class NodeTaskRegisterAPIView(v1.NodeTaskRegisterApiView):
    """节点任务注册接口

    ### GET
    应用场景：获取节点的排队中的Task 或Process， 但不修改任务的执行状态，因为服务端不同步修改状态，所以不可以作为任务执行

    ### POST
    应用场景：获取节点的排队中的Task 或Process， 同时修改任务的执行状态
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]


class NodeTaskAckApiView(v1.NodeTaskAckApiView):
    """指定节点的Task确认接口
    使用对象：节点

    ### POST
    应用场景：上报本地扫描的任务结果
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
