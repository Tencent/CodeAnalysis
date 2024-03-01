# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
自定义返回处理
"""

# 导入控制返回的JSON格式的类
from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):
    # 重构render方法
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code
        code = 0
        if renderer_context:
            msg = ""
            status = status_code
            if data:
                if isinstance(data, dict):
                    msg = data.pop("msg", None)
                    detail = data.pop("detail", None)
                    msg = msg or detail or "success"
                    status = data.pop("status", status_code)
                    code = 0
                elif isinstance(data, list):
                    # 需返回count字段来统计数组大小
                    msg = "success"
                    result = {
                        "count": len(data),
                        "results": data
                    }
                    data = result
                    code = 0
                else:
                    msg = "fail"
                    status = status_code
                    code = 400
                # 重新构建返回的JSON字典
                for key in data:
                    # 判断是否有自定义的异常的字段
                    if key == "exception_message":
                        msg = data[key]
                        code = 400
                        data = ""
            # 落在200-300范围内都是成功的，返回data
            ret = {
                "msg": msg,
                "status_code": status,
                "data": data,
                "code": code
            }

            # 返回JSON数据
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)
