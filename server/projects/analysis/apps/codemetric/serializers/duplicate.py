# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - duplicate serializers
"""

import json
import logging

from rest_framework import serializers

from apps.codemetric import models

logger = logging.getLogger(__name__)


class DuplicateScanSerializer(serializers.ModelSerializer):
    """重复代码扫描数据序列化
    """
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")
    default_summary = serializers.SerializerMethodField()
    custom_summary = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField(read_only=True)

    def get_default_summary(self, scan):
        return json.loads(scan.default_summary) if scan.default_summary else None

    def get_custom_summary(self, scan):
        return json.loads(scan.custom_summary) if scan.custom_summary else None

    def get_url(self, dupscan):
        return ""

    class Meta:
        model = models.DuplicateScan
        fields = '__all__'


class DuplicateScanClosedSerializer(serializers.ModelSerializer):
    """重复代码扫描关闭
    """
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")

    class Meta:
        model = models.DuplicateScan
        fields = '__all__'


class DuplicateIssueSerializer(serializers.ModelSerializer):
    """重复代码问题序列化
    """
    class Meta:
        model = models.DuplicateIssue
        fields = ('id', 'state', 'owner')


class DuplicateIssueCommentSerializer(serializers.ModelSerializer):
    """重复代码问题评论序列化
    """
    class Meta:
        model = models.DuplicateIssueComment
        fields = '__all__'


class DuplicateFileSerializer(serializers.ModelSerializer):
    """重复代码文件序列化
    """
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)
    issue = DuplicateIssueSerializer()

    class Meta:
        model = models.DuplicateFile
        exclude = ("issue_hash",)


class RelatedDuplicateBlockSerializer(serializers.ModelSerializer):
    """关联的重复代码块序列化
    """
    duplicate_file = DuplicateFileSerializer()

    class Meta:
        model = models.DuplicateBlock
        fields = '__all__'


class DuplicateBlockDetailSerializer(serializers.ModelSerializer):
    """重复代码块详情序列化
    """
    duplicate_file = DuplicateFileSerializer()
    related_blocks = serializers.SerializerMethodField()

    def get_related_blocks(self, block):
        # 注：避免数据量较大，只拉取100个，获取全部相关的代码块可以通过另一个接口拉取
        blocks = models.DuplicateBlock.objects.filter(
            block_hash=block.block_hash, duplicate_file__scan=block.duplicate_file.scan
        ).exclude(id=block.id)[:100]
        return RelatedDuplicateBlockSerializer(blocks, many=True).data

    class Meta:
        model = models.DuplicateBlock
        exclude = ("block_hash",)


class DuplicateBlockSerializer(serializers.ModelSerializer):
    """重复代码块序列化
    """
    class Meta:
        model = models.DuplicateBlock
        exclude = ("block_hash",)


class DuplicateFileDetailSerializer(serializers.ModelSerializer):
    """重复代码文件详情序列化
    """
    repo = serializers.IntegerField(source="project.repo_id", read_only=True)
    issue = DuplicateIssueSerializer()
    blocks = serializers.SerializerMethodField()
    duplicate_rate_trend = serializers.SerializerMethodField()

    def get_duplicate_rate_trend(self, dupfile):
        last_dupfile = models.DuplicateFile.objects.filter(project=dupfile.project, id__lt=dupfile.id,
                                                           issue_hash=dupfile.issue_hash).last()
        if last_dupfile:
            return dupfile.duplicate_rate - last_dupfile.duplicate_rate
        else:
            return None

    def get_blocks(self, dupfile):
        # 注：避免数据量较大，只拉取100个，获取全部相关的代码块可以通过另一个接口拉取
        blocks = dupfile.duplicateblock_set.all().order_by(
            "start_line_num", "-end_line_num")[:100]
        return DuplicateBlockSerializer(blocks, many=True).data

    class Meta:
        model = models.DuplicateFile
        exclude = ("issue_hash",)
