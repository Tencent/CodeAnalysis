# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - codecount serializers
"""
import logging

from rest_framework import serializers

from apps.codemetric import models


logger = logging.getLogger(__name__)


class ClocScanSerializer(serializers.ModelSerializer):
    """代码统计扫描数据序列化
    """
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, clocscan):
        return ""

    class Meta:
        model = models.ClocScan
        fields = '__all__'


class ClocScanClosedSerializer(serializers.ModelSerializer):
    """代码统计扫描关闭序列化
    """
    scan_revision = serializers.CharField(source="scan.current_revision")
    scan_time = serializers.DateTimeField(source="scan.scan_time")

    class Meta:
        model = models.ClocScan
        fields = '__all__'


class ClocFileSerializer(serializers.ModelSerializer):
    """代码统计文件数据序列化
    """
    class Meta:
        model = models.ClocFile
        fields = '__all__'


class ClocDirSerializer(serializers.ModelSerializer):
    """代码统计目录数据序列化
    """
    class Meta:
        model = models.ClocDir
        fields = '__all__'


class ClocLanguageSerializer(serializers.ModelSerializer):
    """代码统计语言数据序列化
    """
    class Meta:
        model = models.ClocLanguage
        fields = '__all__'
