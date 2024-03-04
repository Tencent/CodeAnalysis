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
from apps.scan_conf import models, tasks
from apps.scan_conf.serializers import base
from apps.scan_conf.core import CheckToolManager

logger = logging.getLogger(__name__)


class CheckToolSerializer(base.CheckToolSerializer):
    """工具序列化
    """

    class Meta:
        model = models.CheckTool
        exclude = ["open_saas", "users", "co_owners", "owners"]


class CheckToolOpenUpdateSerializer(serializers.Serializer):
    """用于更新工具公有/私有
    """
    open_maintain = serializers.BooleanField(label="启用所有人可协同", help_text="启用所有人可协同", default=False)
    open_user = serializers.BooleanField(label="启用所有人可使用", help_text="启用所有人可使用", default=False)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        open_maintain = validated_data.get("open_maintain")
        open_user = validated_data.get("open_user")
        checktool, old_public, new_public = CheckToolManager.update_open_status(instance, open_maintain,
                                                                                open_user, user)
        if old_public and not new_public:
            username = user.username if user else None
            tasks.checktool_to_private.delay(checktool.id, username)
        return checktool
