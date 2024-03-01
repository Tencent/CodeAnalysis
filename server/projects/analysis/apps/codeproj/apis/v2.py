# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v2 apis
"""

# python 原生import
import logging

# 第三方 import
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

# 项目内 import
from apps.codeproj import serializers, models, filters
from apps.codeproj.apimixins import ProjectBaseAPIView
from apps.codelint import models as lint_models
from apps.codelint import core as lint_core
from apps.codelint import serializers as lint_serializers
from apps.codemetric import models as metric_models
from apps.codemetric import serializers as metric_serializers

from util import errcode

logger = logging.getLogger(__name__)


class ProjectDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目详情接口

    ### Get
    应用场景：获取项目详情
    """
    serializer_class = serializers.ProjectSerializer
    lookup_url_kwarg = "scan_id"

    def get_object(self):
        project = self.get_project()
        return get_object_or_404(models.Project, id=project.id)


class ProjectScanListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目扫描列表接口

    ### Get
    应用场景：获取项目扫描列表
    """
    queryset = models.Scan.objects.all()
    serializer_class = serializers.ScanSerializer
    filter_backends = (OrderingFilter,)
    ordering = ["-id"]

    def get_queryset(self):
        project = self.get_project()
        return models.Scan.objects.filter(project_id=project.id)


class ProjectScanDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目扫描详情接口

    ### GET
    应用场景：获取指定的项目扫描详情
    """
    serializer_class = serializers.ScanSerializer
    lookup_url_kwarg = "scan_id"

    def get_object(self):
        project = self.get_project()
        return get_object_or_404(models.Scan, project_id=project.id,
                                 id=self.kwargs["scan_id"])


class ProjectScanLatestDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目扫描最新一次的详情接口

    ### GET
    应用场景：获取项目最新扫描详情
    """
    serializer_class = serializers.ScanSerializer

    def get_object(self):
        project = self.get_project()
        return models.Scan.objects.filter(project_id=project.id).order_by("-scan_time").first()


class ProjectMyOverviewDetailView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目概览信息 - 与我相关的信息

    ### GET
    应用场景：获取项目概览信息 - 与我相关的信息
    """

    def get(self, request, **kwargs):
        """获取当前项目与我相关的概览信息
        """
        project = self.get_project()
        my_overview = {
            "lint_issue_num": lint_models.Issue.everything.filter(
                project_id=project.id,
                state=lint_models.Issue.StateEnum.ACTIVE,
                author=request.user.username
            ).count(),
            "cyc_issue_num": metric_models.CyclomaticComplexity.objects.filter(
                project_id=project.id,
                is_latest=True,
                status=metric_models.CyclomaticComplexity.StatusEnum.OPEN,
                author=request.user.username
            ).count(),
            "dup_issue_num": metric_models.DuplicateIssue.objects.filter(
                project_id=project.id,
                state=metric_models.DuplicateIssue.StateEnum.ACTIVE,
                owner=request.user.username
            ).count()
        }
        return Response(my_overview)


class ProjectOverviewLintScanLatestDetailView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目概览信息 - 代码检查最新扫描详情

    ### GET
    应用场景：获取项目概览信息 - 代码检查最新扫描详情
    """

    def get(self, request, **kwargs):
        """获取当前项目最新的问题信息
        > 严重值(severity)描述: 1=致命/2=错误/3=警告/4=提示

        """
        project = self.get_project()
        lint_issues = lint_models.Issue.everything.filter(
            project_id=project.id,
            state=lint_models.Issue.StateEnum.ACTIVE
        )
        result = {
            "lint_issue_num": lint_issues.count(),
            "lint_issue_severity_list": lint_issues.values("severity").annotate(num=Count("id")).order_by("severity")
        }
        return Response(result)


class ProjectOverviewLintScanListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目概览信息 - 代码检查列表

    ### GET
    应用场景：获取项目概览信息 - 代码检查列表
    """
    serializer_class = lint_serializers.LintScanSerializer
    filterset_class = filters.ProjectOverviewLintScanFilter

    def get_queryset(self):
        project = self.get_project()
        return lint_models.LintScan.objects.filter(
            scan__project_id=project.id,
            total_summary__isnull=False
        ).order_by("-id")


class ProjectOverviewCycScanListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目概览信息 - 圈复杂度扫描列表

    ### GET
    应用场景：获取项目概览信息 - 圈复杂度扫描列表
    """
    serializer_class = metric_serializers.CyclomaticComplexityScanSerializer
    filterset_class = filters.ProjectOverviewCycScanFilter

    def get_queryset(self):
        project = self.get_project()
        return metric_models.CyclomaticComplexityScan.objects.filter(
            scan__project_id=project.id,
            default_summary__isnull=False
        ).order_by("-id")


class ProjectOverviewDupScanListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目概览信息 - 重复代码扫描列表

    ### GET
    应用场景：获取项目概览信息 - 重复代码扫描列表
    """
    serializer_class = metric_serializers.DuplicateScanSerializer
    filterset_class = filters.ProjectOverviewDupScanFilter

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return metric_models.DuplicateScan.objects.filter(
            scan__project_id=project_id,
            default_summary__isnull=False
        ).order_by("-id")


class ProjectOverviewClocScanListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目概览信息 - 代码统计扫描列表

    ### GET
    应用场景：获取项目概览信息 - 代码统计扫描列表
    """
    serializer_class = metric_serializers.ClocScanSerializer
    filterset_class = filters.ProjectOverviewClocScanFilter

    def get_queryset(self):
        project = self.get_project()
        return metric_models.ClocScan.objects.filter(
            scan__project_id=project.id
        ).order_by("-id")


class ProjectOverviewCheckToolScanView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目不同工具的问题概览数据

    ### GET
    应用场景：获取最新扫描或指定扫描中不同工具的问题数据
    """

    def get_codelint_scan_data(self, project, scan=None):
        """获取扫描工具检查数据
        """
        if not scan:
            scan = models.Scan.objects.filter(
                result_code=errcode.OK, lintscan__isnull=False, project=project
            ).order_by("-id").first()
        checktool_scan = lint_models.CheckToolScan.objects.filter(scan=scan)
        if not checktool_scan:
            return None
        tool_names = list(checktool_scan.values_list("name", flat=True))
        tool_infos = lint_core.CodelintToolManager.get_codelint_toolinfos(tool_names)

        checktool_scan_data = []
        for item in checktool_scan:
            tool_info = tool_infos.get(item.name)
            if tool_info:
                tool_name = tool_info["display_name"]
            else:
                tool_name = item.name
            tool_data = dict(lint_serializers.CheckToolScanSeriailizer(item).data)
            tool_data.update({"name": tool_name})
            checktool_scan_data.append({tool_name: tool_data})
        return checktool_scan_data

    def get_codemetric_scan_data(self, project, scan=None):
        """获取度量工具检查数据
        """
        if not scan:
            cc_scan = metric_models.CyclomaticComplexityScan.objects.filter(
                scan__project=project).order_by("-id").first()
            dup_scan = metric_models.DuplicateScan.objects.filter(scan__project=project).order_by("-id").first()
            cloc_scan = metric_models.ClocScan.objects.filter(scan__project=project).order_by("-id").first()
            cc_data = metric_serializers.CyclomaticComplexityScanSerializer(cc_scan).data if cc_scan else None
            dup_data = metric_serializers.DuplicateScanSerializer(dup_scan).data if dup_scan else None
            cloc_data = metric_serializers.ClocScanSerializer(cloc_scan).data if cloc_scan else None
        else:
            cc_data = metric_serializers.CyclomaticComplexityScanSerializer(
                scan.cyclomaticcomplexityscan).data if scan.cyclomaticcomplexityscan else None
            dup_data = metric_serializers.DuplicateScanSerializer(
                scan.duplicatescan).data if scan.duplicatescan else None
            cloc_data = metric_serializers.ClocScanSerializer(scan.clocscan).data if scan.clocscan else None
        return [{"圈复杂度": cc_data}, {"重复代码": dup_data}, {"代码统计": cloc_data}]

    def get(self, request, **kwargs):
        project = self.get_project()
        scan_id = self.request.query_params.get("scan_id")
        scan = None
        if scan_id:
            scan = get_object_or_404(models.Scan, id=scan_id)
        tool_overview = dict()
        tool_overview["codelint"] = self.get_codelint_scan_data(project, scan)
        tool_overview["codemetric"] = self.get_codemetric_scan_data(project, scan)
        return Response(tool_overview)
