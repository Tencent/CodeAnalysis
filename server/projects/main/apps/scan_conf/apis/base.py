# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

import logging

# 第三方
from rest_framework import generics

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers import base as serializers

logger = logging.getLogger(__name__)


class LanguageListAPIView(generics.ListAPIView):
    """平台语言列表接口

    ### GET
    应用场景：获取支持代码扫描的语言列表
    """

    serializer_class = serializers.LanguageSerializer
    queryset = models.Language.objects.all()



class LabelListAPIView(generics.ListAPIView):
    """标签列表接口

    ### get
    应用场景：获取平台标签列表。
    """
    serializer_class = serializers.LabelSerializer
    queryset = models.Label.objects.all()
