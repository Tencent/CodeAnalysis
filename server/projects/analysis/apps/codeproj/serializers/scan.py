# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - scan serializers
"""
# python 原生import
import logging

# 第三方 import
from rest_framework import serializers

# 项目内 import
from apps.codeproj import models
from apps.base.serializers import CDBaseModelSerializer
from apps.codelint.serializers import LintScanSerializer, LintScanLatestResultSerializer
from apps.codemetric.serializers import CyclomaticComplexityScanSerializer, DuplicateScanSerializer, ClocScanSerializer

logger = logging.getLogger(__name__)


class ProjectSerializer(CDBaseModelSerializer):
    """项目序列化
    """
    class Meta:
        model = models.Project
        fields = "__all__"


class ScanSimpleSerializer(serializers.ModelSerializer):
    """扫描序列化
    """
    class Meta:
        model = models.Scan
        fields = "__all__"


class _ScanTaskSerializer(serializers.Serializer):
    """扫描Task序列化
    task result定义，将作为参数传递给on_job_end
    """
    module = serializers.CharField(max_length=32, help_text="任务所属模块")
    name = serializers.CharField(max_length=32, help_text="任务所属模块")
    execute_version = serializers.CharField(max_length=56, help_text="任务的执行版本", allow_blank=True, allow_null=True)
    params_url = serializers.CharField(help_text="参数路径", allow_null=True, allow_blank=True)
    result_code = serializers.IntegerField(help_text="结果码")
    result_msg = serializers.CharField(help_text="结果信息", allow_blank=True, allow_null=True)
    result_data_url = serializers.CharField(help_text="结果路径", allow_blank=True, allow_null=True)
    log_url = serializers.CharField(help_text="日志链接", allow_blank=True, allow_null=True)


class _ScanJobSerializer(serializers.Serializer):
    """扫描任务参数序列化
    """
    context_url = serializers.CharField(help_text="参数路径", allow_blank=True, allow_null=True)
    result_code = serializers.IntegerField(help_text="结果码")
    result_msg = serializers.CharField(help_text="结果信息", allow_blank=True, allow_null=True)


class ScanLatestResultSerializer(serializers.ModelSerializer):
    """实时扫描报告序列化
    """
    url = serializers.SerializerMethodField(read_only=True)
    lintscan = LintScanLatestResultSerializer(read_only=True)
    duplicatescan = DuplicateScanSerializer(read_only=True)
    cyclomaticcomplexityscan = CyclomaticComplexityScanSerializer(read_only=True)
    clocscan = ClocScanSerializer(read_only=True)

    def get_url(self, scan):
        return ""

    class Meta:
        model = models.Scan
        fields = ["id", "repo_id", "project_id", "job_gid", "scan_time", "current_revision", "result_code",
                  "result_code_msg", "result_msg", "url", "lintscan", "duplicatescan", "cyclomaticcomplexityscan",
                  "clocscan", "job_archived"]


class ScanSerializer(serializers.ModelSerializer):
    """扫描报告序列化
    """
    status = serializers.SerializerMethodField(read_only=True)
    text = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)

    lintscan = LintScanSerializer(read_only=True)
    duplicatescan = DuplicateScanSerializer(read_only=True)
    cyclomaticcomplexityscan = CyclomaticComplexityScanSerializer(read_only=True)
    clocscan = ClocScanSerializer(read_only=True)
    total_time = serializers.SerializerMethodField(read_only=True)

    def get_status(self, scan):
        return scan.result_code

    def get_text(self, scan):
        return scan.result_code_msg

    def get_url(self, scan):
        return ""

    def get_description(self, scan):
        return scan.result_msg

    def get_total_time(self, scan):
        if scan.execute_time and scan.waiting_time:
            return scan.waiting_time + scan.execute_time
        elif scan.waiting_time:
            return scan.waiting_time
        else:
            return None

    class Meta:
        model = models.Scan
        fields = ["id", "repo_id", "project_id", "job_gid", "scan_time", "state", "type", "current_revision",
                  "result_code", "result_msg", "create_time", "creator", "execute_time", "waiting_time", "total_time",
                  "status", "text", "url", "description", "lintscan", "duplicatescan", "cyclomaticcomplexityscan",
                  "clocscan", "result_code_msg", "daily_save", "job_archived"]


class ProjectScanPutResultsSerializer(serializers.Serializer):
    """上报扫描结果序列化
    """
    job = _ScanJobSerializer(help_text="Job 信息", required=False)
    tasks = _ScanTaskSerializer(many=True, help_text="Tasks 列表信息", allow_null=True, required=False)
    reset = serializers.BooleanField(help_text="重新入库", required=False, allow_null=True, default=False)
    sync_flag = serializers.BooleanField(help_text="同步入库", required=False, allow_null=True, default=False)


class ProjectScanSerializer(serializers.ModelSerializer):
    """项目扫描序列化
    """
    result_code_msg = serializers.ReadOnlyField(help_text="结果码信息")

    lintscan = LintScanSerializer(read_only=True)
    duplicatescan = DuplicateScanSerializer(read_only=True)
    cyclomaticcomplexityscan = CyclomaticComplexityScanSerializer(read_only=True)
    clocscan = ClocScanSerializer(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, scan):
        return ""

    class Meta:
        model = models.Scan
        fields = "__all__"
        read_only_fields = ["project", "scan_time", "result_code", "result_msg", "url"]
