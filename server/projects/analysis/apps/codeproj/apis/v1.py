# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 apis
"""

# python 原生import
import json
import logging

# 第三方 import
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAdminUser

# 项目内 import
from apps.codeproj import core
from apps.codeproj import models
from apps.codeproj import serializers
from apps.codeproj import tasks
from apps.codeproj.apimixins import ProjectBaseAPIView
from apps.codelint import models as lint_models
from apps.codelint import serializers as lint_serializers
from apps.codelint import tasks as codelint_tasks
from apps.codemetric import models as metric_models
from apps.codemetric import serializers as metric_serializers
from apps.authen.backends import MainServerInternalAuthentication

from util import errcode

logger = logging.getLogger(__name__)


class ProjectCreateApiView(APIView):
    """项目创建接口
    使用对象：服务内部

    ### Post
    应用场景：创建项目
    """
    schema = None
    authentication_classes = (MainServerInternalAuthentication,)

    def post(self, request):
        """创建项目
        """
        project_id = request.data.get("id")
        repo_id = request.data.get("repo_id")
        if not project_id:
            raise ParseError(detail={"msg": "project id missed"})
        if not repo_id:
            raise ParseError(detail={"msg": "repo id missed"})
        try:
            core.ProjectController.create_project(**request.data)
            return Response(data={"msg": "project %s create success" % project_id}, status=status.HTTP_201_CREATED)
        except IntegrityError as err:
            logger.error("create project exception: %s" % err)
            return Response(data={"msg": "project %s has exist" % project_id}, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailApiView(generics.DestroyAPIView):
    """软删除项目
    使用对象：服务内部

    ### Delete
    应用场景：在analysis服务中，软删除main服务已被删除且过期的project

    """

    schema = None
    serializer_class = serializers.ProjectSerializer
    authentication_classes = (MainServerInternalAuthentication,)

    def get_object(self):
        return get_object_or_404(models.Project, id=self.kwargs["project_id"])


class ProjectScanListCreateApiView(generics.ListCreateAPIView, ProjectBaseAPIView):
    """项目扫描列表接口
    使用对象：服务内部

    ### Get
    应用场景：获取项目扫描历史列表

    ### Post
    应用场景：在指定项目创建一个扫描记录，如果项目不存在，则返回404
    """

    schema = None
    serializer_class = serializers.ProjectScanSerializer
    authentication_classes = (MainServerInternalAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = {"result_code": ("gte", "lt"), }

    def get_queryset(self):
        project = self.get_project()
        order_by = self.request.GET.get("order_by")
        order_by = order_by.split(",") if order_by else ["-id"]
        return models.Scan.objects.filter(project_id=project.id).order_by(*order_by)

    def perform_create(self, serializer):
        project_id = int(self.kwargs["project_id"])
        project = get_object_or_404(models.Project, id=project_id)
        instance = serializer.save(project=project)
        logger.info("[Project: %s] 创建代码扫描: %s" % (project_id, instance.id))


class ProjectScanDetailApiView(generics.UpdateAPIView):
    """项目扫描详情接口
    使用对象：服务内部

    ### put
    应用场景：更新任务的扫描信息
    """
    schema = None
    serializer_class = serializers.ScanSerializer
    authentication_classes = (MainServerInternalAuthentication,)
    lookup_field = "id"
    lookup_url_kwarg = "scan_id"

    def get_object(self):
        return get_object_or_404(models.Scan,
                                 id=self.kwargs["scan_id"],
                                 project_id=self.kwargs["project_id"])


class ProjectScanResultDetailApiView(generics.RetrieveUpdateAPIView, ProjectBaseAPIView):
    """项目扫描结果详情接口
    使用对象：服务内部

    ### Get
    应用场景：获取Scan详情，包括关联的各个功能模块的Scan信息

    ### put
    应用场景：任务完成后，将任务执行结果保存到扫描中
    """
    schema = None
    serializer_class = serializers.ScanSerializer
    create_serializer_class = serializers.ProjectScanPutResultsSerializer
    authentication_classes = (MainServerInternalAuthentication,)
    lookup_field = "id"
    lookup_url_kwarg = "scan_id"

    def get_serializer_class(self):
        if self.request and self.request.method == "PUT":
            if hasattr(self, "create_serializer_class"):
                return self.create_serializer_class
        return generics.GenericAPIView.get_serializer_class(self)

    def get_queryset(self):
        project = self.get_project()
        return models.Scan.objects.filter(project_id=project.id).order_by("-id")

    def put(self, request, *args, **kwargs):
        project = self.get_project()
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        get_object_or_404(models.Project, id=kwargs["project_id"])
        get_object_or_404(models.Scan, id=kwargs["scan_id"], project_id=kwargs["project_id"])
        logger.info("Scan数据入库参数校验通过，开始入库，参数如下：")
        logger.info(json.dumps(request.data))
        if slz.validated_data.get("sync_flag") is True:
            tasks.put_scan_result(kwargs["project_id"], kwargs["scan_id"], slz.validated_data)
        else:
            tasks.put_scan_result.delay(kwargs["project_id"], kwargs["scan_id"], slz.validated_data)
        return Response("OK")


class ProjectOverviewApiView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目扫描概览接口

    ### Get
    应用场景：获取指定项目的扫描概览
    > query_params: scan_revision: 指定查询的扫描版本号，如不指定则为最新的；latest_scan_time: 指定截止的查询时间
    """

    def _get_last_scan(self, cls, slz, project_id, scan_revision=None, latest_scan_time=None):
        """
        获取指定cls的最近一次扫描
        """
        scans = cls.objects.filter(scan__project_id=project_id, scan__result_code=errcode.OK)
        if scan_revision:
            scans = scans.filter(scan__current_revision=scan_revision)
        if latest_scan_time:
            scans = scans.filter(scan__scan_time__lte=latest_scan_time)

        if cls == lint_models.LintScan:
            scans = scans.filter(scan_summary__isnull=False)
        elif cls == metric_models.CyclomaticComplexityScan:
            scans = scans.filter(default_summary__isnull=False)
        elif cls == metric_models.DuplicateScan:
            scans = scans.filter(default_summary__isnull=False)
        elif cls == metric_models.ClocScan:
            scans = scans.filter(code_line_num__isnull=False)
        # 结合 id 和 scm_time 倒序筛选第一个
        scan = scans.order_by("-id", "-scan__scm_time").first()
        return slz(instance=scan).data if scan else None

    def get(self, request, **kwargs):
        project = self.get_project()
        scan_revision = request.GET.get("scan_revision")
        lint_scan = self._get_last_scan(lint_models.LintScan,
                                        lint_serializers.LintScanSerializer, project.id, scan_revision)
        cyc_scan = self._get_last_scan(metric_models.CyclomaticComplexityScan,
                                       metric_serializers.CyclomaticComplexityScanSerializer, project.id, scan_revision)
        dup_scan = self._get_last_scan(metric_models.DuplicateScan,
                                       metric_serializers.DuplicateScanSerializer, project.id, scan_revision)
        cloc_scan = self._get_last_scan(metric_models.ClocScan,
                                        metric_serializers.ClocScanSerializer, project.id, scan_revision)
        result = {
            "lintscan": lint_scan,
            "cyclomaticcomplexityscan": cyc_scan,
            "duplicatescan": dup_scan,
            "clocscan": cloc_scan,
        }
        return Response(result)


class ProjectLatestScanOverviewApiView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目最新扫描概览接口

    ### Get
    应用场景：获取指定项目指定版本的最新一次扫描
    > scan_revision: 指定查询的扫描版本号，如不指定则为当前项目最新的一次扫描
    """

    def _get_scan(self, project_id, scan_revision=None):
        """获取指定扫描
        """
        if scan_revision:
            scan = models.Scan.objects.filter(
                project_id=project_id, current_revision=scan_revision).order_by("-id").first()
        else:
            scan = models.Scan.objects.filter(project_id=project_id).order_by("-id").first()
        return scan

    def get(self, request, **kwargs):
        project = self.get_project()
        scan_revision = request.query_params.get("scan_revision")
        scan = self._get_scan(project.id, scan_revision)
        if not scan:
            if scan_revision:
                raise NotFound({"cd_error": "项目%s的%s扫描结果不存在" % (project.id, scan_revision)})
            else:
                raise NotFound({"cd_error": "项目%s未启动扫描" % project.id})
        slz = serializers.ScanLatestResultSerializer(instance=scan)
        return Response(slz.data)


class CheckPackageRuleMapSyncApiView(generics.GenericAPIView):
    """规则包与规则映射关系同步接口

    ### POST
    应用场景：触发规则包与规则映射关系任务
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        codelint_tasks.sync_checkpackage_rule_map.delay()
        return Response(data={"msg": "start checkpackage rule sync task success"})
