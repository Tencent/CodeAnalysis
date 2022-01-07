# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - base serializer
"""
# python 原生import
import logging

# 第三方 import
from rest_framework import serializers

# 项目内 import
from apps.nodemgr import models

logger = logging.getLogger(__name__)


class ExecTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecTag
        fields = '__all__'
