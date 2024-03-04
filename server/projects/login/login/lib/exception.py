# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

# 自定义异常处理

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response({
            "message": "服务器错误"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception=True)

    else:
        message = ""
        # 这个循环是取第一个错误的提示用于渲染
        for index, value in enumerate(response.data):
            if index == 0:
                key = value
                value = response.data[key]

                if isinstance(value, str):
                    message = value
                else:
                    message = key + value[0]
        return Response({
            "message": message,
        }, status=response.status_code, exception=True)
