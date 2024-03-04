# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job - v1 apis
"""

# python 原生import
import json
import logging

# 第三方 import
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内 import
from apps.authen.backends import ServerAPIAuthentication, TCANodeTokenBackend
from apps.authen.core import UserManager
from apps.codeproj import core as codeproj_core
from apps.codeproj.apimixins import ProjectBaseAPIView
from apps.codeproj.models import ScanSchemePerm
from apps.codeproj.serializers.base import ScanJobCreateSerializer, ScanJobInitSerializer
from apps.job import core, models
from apps.job.api_filters import base as filters
from apps.job.serializers import base as serializers
from apps.nodemgr.models import Node
from util import errcode
from util.exceptions import CDErrorBase

logger = logging.getLogger(__name__)


class ProjectJobListApiView(generics.ListAPIView, ProjectBaseAPIView):
    """项目任务列表接口

    ### GET
    应用场景：获取指定项目任务列表详情
    """
    serializer_class = serializers.JobCodeLineSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.JobFilterSet

    def get_queryset(self):
        project = self.get_project()
        return models.Job.objects.select_related("project__repo").filter(project_id=project.id).order_by("-id")


class ProjectJobDetailApiView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目任务详情接口

    ### GET
    应用场景：获取指定项目指定任务详情
    """
    serializer_class = serializers.JobSerializer
    queryset = models.Job.objects.all()

    def get_object(self):
        project = self.get_project()
        job_id = self.kwargs["job_id"]
        return get_object_or_404(models.Job, id=job_id, project_id=project.id)


class ProjectJobApiView(generics.GenericAPIView):
    """任务关闭接口
    使用对象：服务内部

    ### PUT
    应用场景：Job JobClosed 的回调
    """
    schema = None
    authentication_classes = [ServerAPIAuthentication]
    serializer_class = serializers.JobClosedSerializer

    def put(self, request, **kwargs):
        get_object_or_404(models.Project, id=kwargs["project_id"])
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            logger.info("[Job: %d] 开始执行回调..." % kwargs["job_id"])
            try:
                core.JobCloseHandler.job_closed(
                    kwargs["job_id"], slz.validated_data["result_code"], slz.validated_data["result_msg"],
                    slz.validated_data["result_data"], slz.validated_data.get("result_path"))
                return Response("job_closed")
            except CDErrorBase as e:
                return Response(e.data, status=status.HTTP_400_BAD_REQUEST)


class ProjectScanJobInitApiView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目扫描初始化
    使用对象：节点

    ### GET
    应用场景：获取项目扫描配置的api，供节点端离线扫描使用

    ### POST
    应用场景：创建新的扫描任务，仅做初始化
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = ScanJobInitSerializer

    def post(self, request, **kwargs):
        project = self.get_project()
        if not request.user.is_superuser:
            schemeperm = ScanSchemePerm.objects.filter(scan_scheme=project.scan_scheme).first()
            if schemeperm and schemeperm.execute_scope == ScanSchemePerm.ScopeEnum.PRIVATE \
                    and not schemeperm.check_user_execute_manager_perm(request.user):
                logger.error("本地扫描/CI流水线，代码库内创建分支项目/启动分支项目扫描无权限：%s" % request.user)
                raise PermissionDenied("您没有执行该操作的权限，该扫描方案已私有化，您不在该方案权限配置的关联分支项目权限成员列表中！！！")
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            logger.info("[Project: %s] 参数校验通过，开始初始化任务，参数如下：" % project.id)
            logger.info(json.dumps(slz.validated_data))
            try:
                job_id, scan_id, task_infos = codeproj_core.create_local_scan(
                    project=project, creator=UserManager.get_username(request.user),
                    scan_data=slz.validated_data,
                    created_from=slz.validated_data.get("created_from", "codedog_client"))
                return Response({"job": job_id, "scan": scan_id, "tasks": task_infos})
            except CDErrorBase as e:
                return Response({"cd_error": e.data}, status=status.HTTP_400_BAD_REQUEST)


class ProjectJobFinishApiView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目本地扫描完成，上报结果
    使用对象：节点

    ### POST
    应用场景：上报本地扫描的任务结果
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = ScanJobCreateSerializer

    def post(self, request, **kwargs):
        project = self.get_project()
        job = get_object_or_404(models.Job, id=kwargs["job_id"], project_id=kwargs["project_id"])
        if not request.user.is_superuser:
            schemeperm = ScanSchemePerm.everything.filter(scan_scheme=project.scan_scheme).first()
            if schemeperm and schemeperm.execute_scope == ScanSchemePerm.ScopeEnum.PRIVATE \
                    and not schemeperm.check_user_execute_manager_perm(request.user):
                logger.error("本地扫描/CI流水线，代码库内创建分支项目/启动分支项目扫描无权限：%s" % request.user)
                raise PermissionDenied("您没有执行该操作的权限，该扫描方案已私有化，您不在该方案权限配置的关联分支项目权限成员列表中！！！")
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            logger.info("[Job: %s]参数校验通过，开始结束任务" % job.id)
            try:
                job_id, scan_id = codeproj_core.finish_job_from_client(
                    job, project, slz.validated_data, puppy_create=True)
                return Response({"job": job_id, "scan": scan_id})
            except CDErrorBase as e:
                return Response(e.data, status=status.HTTP_400_BAD_REQUEST)


class NodeTaskAckApiView(APIView):
    """指定节点的Task确认接口
    """

    # authentication_classes = [TCANodeTokenBackend]

    def post(self, request, node_id, task_id):
        """
        ### POST
        应用场景：更新指定节点注册的指定Task状态为执行中，表示Task已被节点正常获取
        """
        nrows = models.Task.objects.filter(id=task_id, node_id=node_id, state=models.Task.StateEnum.ACKING).update(
            state=models.Task.StateEnum.RUNNING)
        if nrows:
            core.NodeTaskRegisterManager.update_task_state_with_running(task_id, node_id)
            return Response({"msg": "Task-%s ack success" % task_id})
        else:
            logger.warning("[Node: %s] task-%s ack failed, release node" % (node_id, task_id))
            core.NodeTaskRegisterManager.release_node(node_id)
            return Response(None)


class NodeTaskRegisterApiView(APIView):
    """
    get: 获取节点的排队中的Task 或Process， 但不修改任务的执行状态，因为服务端不同步修改状态，所以不可以作为任务执行
    post: 获取节点的排队中的Task 或Process， 同时修改任务的执行状态
    """
    schema = None

    # authentication_classes = [TCANodeTokenBackend]

    def _get_task_request(self, task, processes):
        """获取任务执行参数
        """
        task_request = serializers.ExcutableTaskSerializer(instance=task).data
        task_request.update(
            {"execute_processes": [process.name for process in processes]})
        return task_request

    def _get_task(self, request, node_id, occupy=False):
        """注册可执行的任务

        1. 查询当前节点是否有待执行关闭任务
        2. 判断当前节点的状态是否忙碌
        3. 获取当前节点队列下待运行的Task列表
        """
        node = get_object_or_404(Node, id=node_id)
        if occupy:
            # 返回被终止的任务
            killed_task = core.NodeTaskRegisterManager.get_killed_task(node)
            if killed_task:
                return killed_task
            # 查询并占用节点，如果节点忙碌，则返回空
            if not core.NodeTaskRegisterManager.set_node_busy_state(node, **request.data):
                return None

        task, processes = core.NodeTaskRegisterManager.register_task(node, occupy)
        task_request = None
        if task:
            task_request = self._get_task_request(task, processes)
        return task_request

    def get(self, request, node_id):
        return Response(self._get_task(request, node_id, occupy=False))

    def post(self, request, node_id):
        return Response(self._get_task(request, node_id, occupy=True))


class TaskProgressApiView(generics.ListCreateAPIView):
    """指定task进度接口

    ### GET
    应用场景：获取指定task的进度

    ### POST
    应用场景：上报指定task的进度数据
    """
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.TaskProgressSerializer

    def get_queryset(self):
        return models.TaskProgress.objects.filter(task__id=self.kwargs["task_id"])


class TaskDetailApiView(generics.GenericAPIView):
    """指定task详情接口

    ### PUT
    应用场景：上报task结果
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.TaskResultSerializer

    def put(self, request, **kwargs):
        job_id = kwargs["job_id"]
        task_id = kwargs["task_id"]
        task = get_object_or_404(models.Task, id=task_id, job_id=job_id)
        logger.info("[Job: %s][Task: %s] 收到上报结果请求，执行节点: %s，执行参数: %s" % (
            job_id, task_id, task.node, json.dumps(request.data)))
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            core.JobCloseHandler.save_task_result(task_id, slz.validated_data["task_version"],
                                                  slz.validated_data["result_code"],
                                                  slz.validated_data["result_msg"],
                                                  slz.validated_data["result_data_url"],
                                                  slz.validated_data["log_url"],
                                                  slz.validated_data["processes"])
            if errcode.is_success(slz.validated_data["result_code"]):
                core.JobCloseHandler.close_job(task.job_id)
            else:
                core.JobCloseHandler.revoke_job(
                    task.job, slz.validated_data["result_code"], slz.validated_data["result_msg"])
            return Response(slz.data)


class ExcutePrivateTask(generics.GenericAPIView):
    """
    ### post
    应用场景：获取未执行的私有任务
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]

    def post(self, request, **kwargs):
        job = get_object_or_404(models.Job, id=kwargs["job_id"])
        result = core.PrivateTaskManager.get_private_task(job)
        state = result["state"]
        state_msg = result["state_msg"]
        tasks = result["tasks"]
        task_jsons = []
        for task_info in tasks.values():
            task = task_info["task"]
            execute_processes = task_info["execute_processes"]
            task_json = serializers.ExcutableTaskSerializer(instance=task).data
            task_json.update({"execute_processes": [process.name for process in execute_processes]})
            task_jsons.append(task_json)
        return Response({"state": state, "state_msg": state_msg, "tasks": task_jsons})


class JobTasksBeatApiView(generics.GenericAPIView):
    """指定Task的心跳上报接口

    ### POST
    应用场景：更新job下所有task的心跳时间
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]

    def post(self, request, **kwargs):
        job_id = kwargs["job_id"]
        task_ids = list(models.Task.objects.filter(job_id=job_id).exclude(
            state=models.Task.StateEnum.CLOSED).values_list("id", flat=True))
        task_num = models.Task.objects.filter(id__in=task_ids).update(last_beat_time=now())
        job_num = models.Job.objects.filter(id=job_id).exclude(
            state=models.Task.StateEnum.CLOSED).update(last_beat_time=now())
        return Response({"nrows": task_num, "job_nrows": job_num})


class JobApiView(generics.RetrieveUpdateAPIView):
    """指定Job详情接口

    ### GET
    应用场景：获取指定job的详情

    ###put
    应用场景：修改job的字段内容
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobCodeLineSerializer
    lookup_url_kwarg = "job_id"


class JobTasksApiView(generics.ListAPIView):
    """指定Job的task列表查询接口

    ### GET
    应用场景：获取Job的Task列表
    """
    schema = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.TaskFilterSet
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        return models.Task.objects.filter(job_id=self.kwargs["job_id"]).order_by("-id")
