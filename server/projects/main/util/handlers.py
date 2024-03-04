# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util.drfexceptionhandler RPC接口异常处理模块
"""

import logging

from rest_framework.status import HTTP_200_OK
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from util.exceptions import BaseServerError, errcode


logger = logging.getLogger(__name__)


def format_exception_handler(exc, context):
    """DRF框架自定义异常信息处理
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    request = context.get("request")
    if not request:
        return response
    api_type = request.META.get("HTTP_API_TYPE")
    if api_type != "coding":
        if isinstance(exc, BaseServerError):
            return Response({'code': exc.code, 'msg': exc.msg}, status=exc.status_code)
        else:
            return response

    if response is not None:
        logger.warning("exception response: %s" % response.data)
        custom_response_data = {"status_code": response.status_code, "code": -1}
        # 异常数据为字符串，则直接使用
        if isinstance(response.data, str):
            custom_response_data["cd_error"] = response.data
        # 异常数据为list，将其连接成为字符串
        elif isinstance(response.data, list):
            custom_response_data["cd_error"] = ";".join(response.data)
        # 异常数据为dict，且包含 detail字段，则将其detail替换为 cd_error
        elif isinstance(response.data, dict) and response.data.get("detail"):
            custom_response_data["cd_error"] = response.data.pop("detail")
            custom_response_data.update(**response.data)
        # 异常类型为 ValidationError 时，补充err_msg，并按固定格式存放数据
        elif isinstance(exc, ValidationError):
            invalid_fields = []
            for field, value in response.data.items():
                invalid_fields.append({"field": field, "message": value})
            custom_response_data["invalid_fields"] = invalid_fields
            custom_response_data["cd_error"] = "数据格式不准确"
        else:
            custom_response_data = response.data
        response.data = custom_response_data
        response.status_code = HTTP_200_OK
        logger.info("coding error response data: %s" % custom_response_data)
    return response


def custom_exception_handler(exc, context):
    """
    用于平台自定义error处理
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, BaseServerError):
        return Response({'code': exc.code, 'msg': exc.msg}, status=exc.status_code)

    return None


def get_error_message(msg, is_validation_error=False):
    """获取错误信息
    """
    if isinstance(msg, str):
        return msg
    elif isinstance(msg, list) and len(msg) > 0:
        return "%s" % msg[0]
    elif isinstance(msg, dict):
        keys = list(msg)
        if len(keys) > 0:
            key = keys[0]
            err_msg = msg[key]
            if is_validation_error:
                err_msg = "%s %s" % (key, get_error_message(msg[key], is_validation_error))
            return get_error_message(err_msg)
    return '未知错误，请联系系统管理员'


def tiyan_format_exception_handler(exc, context):
    """DRF框架自定义异常信息处理
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    request = context.get("request")
    if not request:
        return response

    # 处理自定义异常
    if not response:
        response = custom_exception_handler(exc, context)

    if response is not None:
        logger.warning("exception response: %s" % response.data)
        code = response.data.pop("code", errcode.E_SERVER_BASE) if isinstance(response.data, dict) \
            else errcode.E_SERVER_BASE
        custom_response_data = { 
          "status_code": response.status_code, 
          "code": code, 
          "msg": get_error_message(response.data, isinstance(exc, ValidationError)),
        }
        # 异常类型为 ValidationError 时，补充invalid_fields，并按固定格式存放数据
        if isinstance(exc, ValidationError) and isinstance(response.data, dict):
            invalid_fields = []
            for field, value in response.data.items():
                invalid_fields.append({"field": field, "message": value})
            custom_response_data["invalid_fields"] = invalid_fields
        response.data = custom_response_data
        logger.info("custom error response data: %s" % custom_response_data)
    return response
