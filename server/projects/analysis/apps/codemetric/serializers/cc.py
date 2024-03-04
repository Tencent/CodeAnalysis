# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - cc serializers
"""
import json
import logging

from rest_framework import serializers

from apps.codemetric import models

logger = logging.getLogger(__name__)


class CyclomaticComplexityScanSerializer(serializers.ModelSerializer):
    """圈复杂度扫描数据序列化
    """
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")
    default_summary = serializers.SerializerMethodField()
    custom_summary = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField(read_only=True)
    ccfile_url = serializers.SerializerMethodField(read_only=True)

    def get_default_summary(self, scan):
        return json.loads(scan.default_summary) if scan.default_summary else None

    def get_custom_summary(self, scan):
        return json.loads(scan.custom_summary) if scan.custom_summary else None

    def get_url(self, cycscan):
        return ""

    def get_ccfile_url(self, cycscan):
        return ""

    class Meta:
        model = models.CyclomaticComplexityScan
        fields = "__all__"


class CyclomaticComplexityScanClosedSerializer(serializers.ModelSerializer):
    """圈复杂度扫描关闭序列化
    """
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")

    class Meta:
        model = models.CyclomaticComplexityScan
        fields = "__all__"


class CyclomaticComplexityFileSerializer(serializers.ModelSerializer):
    """圈复杂度文件序列化
    """
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)

    class Meta:
        model = models.CyclomaticComplexityFile
        exclude = ["file_hash", "g_file_hash"]


class CyclomaticComplexityFileDetailSerializer(serializers.ModelSerializer):
    """圈复杂度文件详情序列化
    """
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)
    issues = serializers.SerializerMethodField()

    def get_issues(self, instance):
        issues = models.CyclomaticComplexity.objects.filter(file_hash=instance.file_hash, is_latest=True)
        slz = CyclomaticComplexitySerializer(issues, many=True)
        return slz.data

    class Meta:
        model = models.CyclomaticComplexityFile
        exclude = ["file_hash", "g_file_hash"]


class CyclomaticComplexitySerializer(serializers.ModelSerializer):
    """圈复杂度数据序列化
    """
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)

    class Meta:
        model = models.CyclomaticComplexity
        exclude = ["file_hash", "unique_cc_hash"]


class DetailedCyclomaticComplexitySerializer(serializers.ModelSerializer):
    """包含圈复杂度详情的圈复杂度序列化
    """
    detail = serializers.SerializerMethodField()

    def get_detail(self, ccissue):
        """提取详情，兼容处理
        """
        return {
            "token": ccissue.token,
            "line_num": ccissue.line_num,
            "code_line_num": ccissue.code_line_num,
            "start_line_no": ccissue.start_line_no,
            "end_line_no": ccissue.end_line_no,
            "scan_revision": ccissue.scan_revision
        }

    class Meta:
        model = models.CyclomaticComplexity
        fields = "__all__"
