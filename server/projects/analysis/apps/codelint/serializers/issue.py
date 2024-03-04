# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - serializers for issue
"""

import json

from django.conf import settings
from django.db.models import Count
from rest_framework import serializers

from apps.codelint import models
from apps.codelint.core import CodeLintIssueDetailManager
from apps.codelint.job.utils import queryset_to_dict
from apps.codeproj.models import Scan


class ProjectIssueSerializer(serializers.ModelSerializer):
    """项目问题序列化
    """
    is_external = serializers.SerializerMethodField(read_only=True)
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)

    def get_is_external(self, issue):
        return True if issue.scm_url else False

    class Meta:
        model = models.Issue
        fields = ("id", "file_path", "project", "repo", "checkrule_real_name", "checkrule_display_name",
                  "checktool_name", "msg", "state", "resolution", "author", "severity", "revision", "ci_time",
                  "scan_open", "scan_fix", "fixed_time", "language", "file_owners", "is_external", "scm_url",
                  "real_file_path", "tapd_ws_id",)


class ProjectIssueFilterSerializer(serializers.Serializer):
    """项目问题过滤序列化
    """
    author = serializers.CharField(max_length=50, help_text="负责人")
    exclude_dirs = serializers.ListField(
        child=serializers.CharField(help_text="过滤的路径"), help_text="过滤的路径列表", allow_empty=True, allow_null=True)


class RepoIssueSerializer(ProjectIssueSerializer):
    """代码库问题序列化
    """
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)

    class Meta:
        model = models.Issue
        fields = ["id", "file_path", "project", "repo", "checkrule_real_name", "msg", "state", "resolution",
                  "author", "severity", "revision", "ci_time", "is_external", "scm_url", "real_file_path"]


class RepoIssueResolutionSerializer(serializers.Serializer):
    """代码库问题处理序列化
    """

    project_ids = serializers.ListField(child=serializers.IntegerField(help_text="项目编号"), help_text="项目编号列表")
    checkrule_gids = serializers.ListField(child=serializers.IntegerField(help_text="规则编号"),
                                           help_text="规则编号列表", allow_null=True, allow_empty=True, required=False)
    g_issue_hashes = serializers.ListField(child=serializers.CharField(help_text="问题值"),
                                           help_text="问题值列表", allow_null=True, allow_empty=True, required=False)
    resolution = serializers.ChoiceField(help_text="解决方式", allow_null=True, required=False,
                                         choices=models.Issue.RESOLUTION_CHOICES)
    author = serializers.CharField(help_text="操作人")


class IssueReferSerializer(serializers.ModelSerializer):
    """IssueRefer序列化
    """

    class Meta:
        model = models.IssueRefer
        fields = "__all__"


class IssueDetailSimpleSerializer(serializers.ModelSerializer):
    """IssueDetail简易版序列化
    """
    issue_refers = serializers.SerializerMethodField(read_only=True)

    def get_issue_refers(self, issue_detail):
        issue_refers = models.IssueRefer.objects.filter(
            issuedetail_uuid=issue_detail.issuedetail_uuid)
        return IssueReferSerializer(issue_refers, many=True).data

    class Meta:
        model = models.IssueDetail
        exclude = ("issue_hash",)


class IssueDetailWithIssueSerializer(IssueDetailSimpleSerializer):
    """包含Issue信息的IssueDetail序列化
    """
    issue = serializers.SerializerMethodField(read_only=True)

    def get_issue(self, issue_detail):
        """获取Issue信息
        """
        issue = issue_detail.issue_info
        if issue:
            return ProjectIssueSerializer(instance=issue).data
        else:
            return None

    class Meta:
        model = models.IssueDetail
        exclude = ("issue_hash",)


class DetailedIssueSerializer(serializers.ModelSerializer):
    """带IssueDetail的Issue序列化
    """
    issue_details = serializers.SerializerMethodField(read_only=True)
    is_external = serializers.SerializerMethodField(read_only=True)
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)

    def get_is_external(self, issue):
        return True if issue.scm_url else False

    def get_issue_details(self, issue):
        issue_details = CodeLintIssueDetailManager.get_issue_details(issue)
        return IssueDetailSimpleSerializer(issue_details, many=True).data

    class Meta:
        model = models.Issue
        exclude = ["issue_hash", "g_issue_hash", "o_issue_hash", "file_hash"]


class IssueCommentSerializer(serializers.ModelSerializer):
    """Issue评论序列化
    """

    class Meta:
        model = models.IssueComment
        fields = "__all__"


class _ScanSerializer(serializers.ModelSerializer):
    """Scan序列化
    """
    execute_time = serializers.DurationField(read_only=True)

    class Meta:
        model = Scan
        fields = ["id", "scan_time", "execute_time"]


class LintScanSerializer(serializers.ModelSerializer):
    """项目Lint扫描序列化
    """
    scan = _ScanSerializer()
    status = serializers.SerializerMethodField(read_only=True)
    text = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)

    current_scan = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    scan_summary = serializers.SerializerMethodField(read_only=True)
    total_summary = serializers.SerializerMethodField(read_only=True)

    def get_status(self, lintscan):
        return lintscan.scan.result_code

    def get_text(self, lintscan):
        return lintscan.scan.result_code_msg

    def get_url(self, lintscan):
        return "%s/repos/%d/projects/%d/codelint/issues?state=1&scan_open=%d" % (
            settings.LOCAL_DOMAIN, lintscan.scan.repo_id, lintscan.scan.project.id, lintscan.scan.id)

    def get_description(self, lintscan):
        return lintscan.scan.result_msg

    def get_current_scan(self, lintscan):
        return {
            "active_category_detail": json.loads(lintscan.active_category_detail or "{}"),
            "active_severity_detail": json.loads(lintscan.active_severity_detail or "{}"),
            "issue_open_num": lintscan.issue_open_num,
            "issue_fix_num": lintscan.issue_fix_num
        }

    def get_total(self, lintscan):
        return {
            "state_detail": json.loads(lintscan.total_state_detail or "{}"),
            "category_detail": json.loads(lintscan.total_category_detail or "{}"),
            "severity_detail": json.loads(lintscan.total_severity_detail or "{}")
        }

    def get_scan_summary(self, lintscan):
        return json.loads(lintscan.scan_summary) if lintscan.scan_summary else None

    def get_total_summary(self, lintscan):
        return json.loads(lintscan.total_summary) if lintscan.total_summary else None

    class Meta:
        model = models.LintScan
        fields = ["issue_open_num", "issue_fix_num", "issue_detail_num", "scan", "current_scan", "total",
                  "status", "text", "url", "description", "scan_summary", "total_summary"]


class LintScanLatestResultSerializer(serializers.ModelSerializer):
    """项目扫描概览实时数据序列化
    """
    url = serializers.SerializerMethodField(read_only=True)
    current_scan = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)

    def get_url(self, lintscan):
        return "%s/repos/%d/projects/%d/codelint/issues?state=1&scan_open=%d" % (
            settings.LOCAL_DOMAIN, lintscan.scan.repo_id, lintscan.scan.project.id, lintscan.scan.id)

    def get_current_scan(self, lintscan):
        """获取当前扫描的最新问题数据
        """
        scan = lintscan.scan
        project_id = scan.project_id
        project_issues = models.Issue.everything.filter(project_id=project_id)
        active_issues = project_issues.filter(
            scan_open=scan, scan_fix__isnull=True, state=models.Issue.StateEnum.ACTIVE)
        issue_open_num = active_issues.count()
        issue_fix_num = project_issues.filter(scan_fix=scan).count()
        active_severity_detail = dict([(models.Issue.SEVERITY_ENG_CHOICES_DICT.get(s, s), c) for (
            s, c) in active_issues.values_list("severity").annotate(count=Count("id"))])
        return {
            "issue_open_num": issue_open_num,
            "issue_fix_num": issue_fix_num,
            "active_severity_detail": active_severity_detail
        }

    def get_total(self, lintscan):
        """获取存量Issue数据
        """
        project_id = lintscan.scan.project_id
        project_issues = models.Issue.everything.filter(project_id=project_id)
        total_state_detail = dict([(models.Issue.STATE_ENG_CHOICES_DICT.get(field, field), count) for (field, count) in
                                   project_issues.values_list("state").annotate(count=Count("id"))])
        total_severity_detail = queryset_to_dict(
            project_issues.values_list(
                "severity", "state").annotate(count=Count("id")),
            models.Issue.SEVERITY_ENG_CHOICES_DICT,
            models.Issue.STATE_ENG_CHOICES_DICT)
        return {
            "state_detail": total_state_detail,
            "severity_detail": total_severity_detail
        }

    class Meta:
        model = models.LintScan
        fields = ["current_scan", "total", "url"]


class LintScanClosedSerializer(serializers.ModelSerializer):
    """Lint扫描关闭序列化
    """
    scan = _ScanSerializer()
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")

    class Meta:
        model = models.LintScan
        fields = "__all__"


class InvalidIssueSerializer(serializers.ModelSerializer):
    """无效问题序列化
    """
    issue = ProjectIssueSerializer(read_only=True)

    class Meta:
        model = models.InvalidIssue
        fields = "__all__"


class WontFixIssueSerializer(serializers.ModelSerializer):
    """无需修复问题序列化
    """
    issue = ProjectIssueSerializer(read_only=True)

    class Meta:
        model = models.WontFixIssue
        fields = "__all__"


class CheckToolScanSeriailizer(serializers.ModelSerializer):
    """代码扫描工具序列化
    """

    active_severity_detail = serializers.SerializerMethodField(read_only=True)
    total_state_detail = serializers.SerializerMethodField(read_only=True)
    total_severity_detail = serializers.SerializerMethodField(read_only=True)

    def get_active_severity_detail(self, instance):
        if instance.active_severity_detail:
            return json.loads(instance.active_severity_detail)
        else:
            return None

    def get_total_state_detail(self, instance):
        if instance.total_state_detail:
            return json.loads(instance.total_state_detail)
        else:
            return None

    def get_total_severity_detail(self, instance):
        if instance.total_severity_detail:
            return json.loads(instance.total_severity_detail)
        else:
            return None

    class Meta:
        model = models.CheckToolScan
        exclude = ["author_issue_detail"]


class IssueDownloadSerializer(serializers.ModelSerializer):
    """Issue下载序列化
    """

    class Meta:
        model = models.Issue
        fields = ["id", "file_path", "checkrule_display_name", "checkrule_real_name", "msg", "author",
                  "revision", "project", "ci_time", "scan_open", "get_state_display",
                  "get_resolution_display", "get_severity_display"]
