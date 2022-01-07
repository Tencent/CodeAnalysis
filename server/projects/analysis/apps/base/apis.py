# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - apis
"""

import logging

# 第三方 import
from rest_framework.views import APIView
from rest_framework.response import Response


logger = logging.getLogger(__name__)


class BaseApiView(APIView):
    """基础接口，用于首页
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """获取基础页数据
        """
        return Response(data={"msg": "Weclome to CodeDog Server"})
