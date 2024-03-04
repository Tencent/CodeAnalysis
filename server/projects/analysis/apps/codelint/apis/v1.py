# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - apis v1

OpenAPI
"""

# python 原生import
import json
import logging

# 第三方 import
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

# 项目内 import
from apps.codelint import serializers, models, filters
from apps.codelint.job.utils import queryset_to_dict
from apps.codeproj.apimixins import ProjectBaseAPIView
from util import errcode

logger = logging.getLogger(__name__)


class ProjectIssueListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目问题列表接口

    ### Get
    应用场景：查看指定项目的问题列表数据
    """
    serializer_class = serializers.ProjectIssueSerializer
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = "__all__"
    ordering = ["-id"]
    filterset_class = filters.LintIssueFilterSet

    def get_queryset(self):
        project = self.get_project()
        return models.Issue.everything.filter(project_id=project.id)


class ProjectIssueWithDetailListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目问题详情列表接口(Issue列表包含IssueDetail）

    ### Get
    应用场景：查看指定项目的问题列表数据（包含问题详情数据）
    """
    serializer_class = serializers.DetailedIssueSerializer
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = "__all__"
    ordering = ["-id"]
    filterset_class = filters.LintIssueFilterSet

    def get_queryset(self):
        project = self.get_project()
        return models.Issue.everything.filter(project_id=project.id)


class ProjectIssueDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目问题详情

    ### Get
    应用场景：查看指定项目的指定问题详情
    """
    serializer_class = serializers.DetailedIssueSerializer

    def get_object(self):
        project = self.get_project()
        issue_id = self.kwargs["issue_id"]
        return get_object_or_404(models.Issue, id=issue_id, project_id=project.id)


class ProjectLintIssueReport(generics.GenericAPIView, ProjectBaseAPIView):
    """项目问题数据报告接口

    ### Get
    应用场景：获取指定项目的数据报告
    """
    serializer_class = serializers.LintScanSerializer

    def get_scan_id(self, request):
        """从请求参数中获取scan_id
        """
        scan_id = request.query_params.get("scan_id")
        try:
            return int(scan_id)
        except Exception as err:
            logger.error("convert scan id exception, err: %s" % err)
            return None

    def get(self, request, **kwargs):
        project = self.get_project()
        scan_id = self.get_scan_id(request)
        if scan_id:
            scan = get_object_or_404(models.Scan, id=scan_id, lintscan__isnull=False)
        else:
            scan = models.Scan.objects.filter(
                result_code=errcode.OK, lintscan__isnull=False, project=project).order_by("-id").first()
        if scan:
            slz = serializers.LintScanSerializer(instance=scan.lintscan)
            return Response(slz.data)
        else:
            raise NotFound(detail={"err_msg": "找不到指定扫描的报告"})


class ProjectIssueToolReportListAPIView(generics.ListAPIView, ProjectBaseAPIView):
    """获取指定项目的工具报告接口
    """
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.CheckToolScanFilterSet
    serializer_class = serializers.CheckToolScanSeriailizer

    def get_scan_id(self):
        """从请求参数中获取scan_id
        """
        scan_id = self.request.query_params.get("scan_id")
        if not scan_id:
            return None
        try:
            return int(scan_id)
        except Exception as err:
            logger.warning("convert scan id exception, err: %s" % err)
            return None

    def get_scan_revision(self):
        """从请求参数中获取revision
        """
        scan_revision = self.request.query_params.get("scan_revision")
        return scan_revision

    def get_queryset(self):
        project = self.get_project()
        scan_id = self.get_scan_id()
        scan_revision = self.get_scan_revision()
        if scan_id:
            scan = get_object_or_404(models.Scan, id=scan_id, project=project)
        elif scan_revision:
            scans = models.Scan.objects.filter(project_id=project.id, current_revision=scan_revision,
                                               lintscan__isnull=False)
            scan = scans.order_by("-id").first()
        else:
            scan = models.Scan.objects.filter(
                result_code=errcode.OK, lintscan__isnull=False, project=project).order_by("-id").first()
        if not scan:
            raise NotFound(detail={"err_msg": "当前项目没有启动扫描或没有扫描成功"})
        return models.CheckToolScan.objects.filter(scan=scan)


class ProjectScanIssueSummaryAPIView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目扫描问题数据报告接口

    ### Get
    应用场景：获取指定项目的数据报告

    > 结果格式
    > {
        "current_scan": {  # 本次扫描
            "issue_open_num": 0,  # 新增问题量
            "issue_fix_num": 0,  # 关闭问题量
            "active_severity_detail": {  # 新增问题严重级别统计
                "fatal": 0,  # 致命
                "error": 0,  # 错误
                "warning": 0,  # 警告
                "info": 0  # 提示
            },
        },
        "total": {  # 存量问题
            "state_detail": {  # 总量统计
                "active": 0,
                "resolved": 0,
                "closed": 0
            },
            "severity_detail": {  # 按严重级别统计
                "fatal": {"active": 0, "resolved": 0, "closed": 0},  # 未处理，已处理，关闭
                "error": {"active": 0, "resolved": 0, "closed": 0},
                "warning": {"active": 0, "resolved": 0, "closed": 0},
                "info": {"active": 0, "resolved": 0, "closed": 0}
            },

        }
    }
    """

    def get_scan_id(self, request):
        """从请求参数中获取scan_id
        """
        scan_id = request.query_params.get("scan_id")
        if not scan_id:
            return None
        try:
            return int(scan_id)
        except Exception as err:
            logger.error("convert scan id exception, err: %s" % err)
            return None

    def get_scan_revision(self, request):
        """从请求参数中获取revision
        """
        scan_revision = request.query_params.get("scan_revision")
        return scan_revision

    def get_current_scan_issue(self, project_id, scan):
        """获取当前扫描的最新问题数据
        """
        project_issues = models.Issue.everything.filter(project_id=project_id)
        active_issues = project_issues.filter(scan_open=scan, scan_fix__isnull=True,
                                              state=models.Issue.StateEnum.ACTIVE)
        issue_open_num = active_issues.count()
        issue_fix_num = project_issues.filter(scan_fix=scan).count()
        active_severity_detail = dict([(models.Issue.SEVERITY_ENG_CHOICES_DICT.get(s, s), c) for (s, c)
                                       in active_issues.values_list("severity").annotate(count=Count('id'))])
        return {
            "issue_open_num": issue_open_num,
            "issue_fix_num": issue_fix_num,
            "active_severity_detail": active_severity_detail
        }

    def get_total_issue(self, project_id):
        """获取存量Issue数据
        """
        project_issues = models.Issue.everything.filter(project_id=project_id)
        total_state_detail = dict([(models.Issue.STATE_ENG_CHOICES_DICT.get(field, field), count) for (field, count) in
                                   project_issues.values_list("state").annotate(count=Count('id'))])
        total_severity_detail = queryset_to_dict(
            project_issues.values_list("severity", "state").annotate(count=Count('id')),
            models.Issue.SEVERITY_ENG_CHOICES_DICT,
            models.Issue.STATE_ENG_CHOICES_DICT)
        return {
            "state_detail": total_state_detail,
            "severity_detail": total_severity_detail
        }

    def get_current_project_issue_summary(self, project_id, scan):
        """获取当前项目的问题数
        """
        project_issues = models.Issue.everything.filter(project_id=project_id)
        # 注意：问题数超过1000的不进行实时计算 -- 20201218 暂时调整为 1000000
        if project_issues.count() < 1000000:
            return {
                "current_scan": self.get_current_scan_issue(project_id, scan),
                "total": self.get_total_issue(project_id)
            }
        else:
            logger.info("[Project: %s][Scan: %s] use default summary" % (project_id, scan.id))
            lint_scan = models.LintScan.objects.get(scan=scan)
            return {
                "current_scan": {
                    "active_severity_detail": json.loads(lint_scan.active_severity_detail or '{}'),
                    "issue_open_num": lint_scan.issue_open_num,
                    "issue_fix_num": lint_scan.issue_fix_num
                },
                "total": {
                    "state_detail": json.loads(lint_scan.total_state_detail or '{}'),
                    "severity_detail": json.loads(lint_scan.total_severity_detail or '{}')
                }
            }

    def get(self, request, **kwargs):
        project = self.get_project()
        scan_id = self.get_scan_id(request)
        scan_revision = self.get_scan_revision(request)
        scan = None
        if scan_id:
            scan = get_object_or_404(models.Scan, id=scan_id, project_id=project.id, lintscan__isnull=False)
        elif scan_revision:
            scans = models.Scan.objects.filter(project_id=project.id, current_revision=scan_revision,
                                               lintscan__isnull=False)
            scan = scans.order_by("-id").first()
        if not scan:
            raise NotFound()
        summary = self.get_current_project_issue_summary(project.id, scan)
        return Response(data=summary)
