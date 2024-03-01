# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v1 serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models

logger = logging.getLogger(__name__)


class CheckToolNameSimpleSerializer(serializers.ModelSerializer):
    """工具名称简单序列化
    """
    display_name = serializers.SerializerMethodField()

    def get_display_name(self, checktool):
        """获取工具展示名称
        """
        request = self.context.get("request")
        user = request.user if request else None
        return checktool.get_show_name(user=user)

    class Meta:
        model = models.CheckTool
        fields = ["id", "name", "display_name"]
