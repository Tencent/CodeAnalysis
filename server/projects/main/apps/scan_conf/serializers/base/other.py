# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - other serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models

logger = logging.getLogger(__name__)


class LanguageSerializer(serializers.ModelSerializer):
    """语言序列化
    """
    display_name = serializers.CharField(source="get_name_display")

    class Meta:
        model = models.Language
        fields = "__all__"


class LabelSerializer(serializers.ModelSerializer):
    """标签序列化
    """
    checked = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    def get_checked(self, label):
        return "基础" in label.name

    def get_display_name(self, label):
        return "%s扫描" % label.name

    class Meta:
        model = models.Label
        fields = "__all__"


class ScanAppSerializer(serializers.ModelSerializer):
    """扫描应用序列化
    """

    class Meta:
        model = models.ScanApp
        fields = ["id", "name", "label", "desc"]


class ProcessSerailizer(serializers.ModelSerializer):
    """进程序列化
    """

    class Meta:
        model = models.Process
        fields = "__all__"
