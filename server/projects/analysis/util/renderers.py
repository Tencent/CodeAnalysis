# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util - renderers
自定义响应
"""
# 原生
import logging

# 第三方
from rest_framework.renderers import JSONRenderer

# 项目内
from util import errcode


logger = logging.getLogger(__name__)


class DefaultJSONRenderer(JSONRenderer):
    """默认 json响应体

    {
        "code": "",
        "status_code": "",
        "data": "",
        "msg": ""
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return bytes()
        renderer_context = renderer_context or {}
        response = renderer_context["response"]

        if response and 200 <= response.status_code < 400:
            msg = "请求成功"
            if isinstance(data, dict):
                msg = data.get("msg", "请求成功")
            custom_data = {
                "data": data,
                "code": errcode.OK,
                "msg": msg,
                "status_code": response.status_code
            }
        else:
            custom_data = data
        return super().render(custom_data, accepted_media_type, renderer_context)
