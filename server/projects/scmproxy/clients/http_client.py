# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" http client
"""

import json
import logging

from urllib3 import poolmanager, util

logger = logging.getLogger(__name__)


class HttpClient(object):
    """请求客户端
    """

    def __init__(self):
        """初始化方法
        """
        _retries = util.Retry(total=3, backoff_factor=2.0, status_forcelist=(500, 502, 504))
        self._http_client = poolmanager.PoolManager(retries=_retries)

    def get_content_type_from_headers(self, headers):
        """获取请求头部的内容类型
        """
        if not headers:
            return None
        for key in headers:
            if key.upper() == "CONTENT-TYPE":
                return headers[key]
        return None

    def set_content_type_with_headers(self, headers, content_type):
        """设置请求头部的内容类型
        """
        if not headers:
            return {"Content-Type": content_type}
        for key in headers:
            if key.upper() == "CONTENT-TYPE":
                headers[key] = content_type

    def session(self, method, path, params=None, data=None, json_data=None, headers=None):
        """请求基础方法

        注意：
        1. 参数获取顺序：params > data > json_data
        2. 当同时指定params和data时，会尝试合并两者，如果data不是dict格式，则不会合并，如果同时指定
        """
        kwargs = {}
        if params:
            if data and isinstance(data, dict):
                params.update(data)
            else:
                logger.warning("data is not 'dict' type, only get params")
            if self.get_content_type_from_headers(headers) == "application/x-www-form-urlencoded":
                kwargs["encode_multipart"] = False
        elif data:
            kwargs["body"] = data if type(data) == bytes else str(data).encode("utf-8")
        elif json_data:
            kwargs["body"] = json.dumps(json_data).encode("utf-8")
            self.set_content_type_with_headers(headers, "application/json")

        return self._http_client.request(method, path, fields=params, headers=headers, **kwargs)

    def get(self, path, params=None, headers=None):
        result = self.session("GET", path, params=params, headers=headers)
        return result

    def post(self, path, params=None, data=None, json_data=None, headers=None):
        result = self.session("POST", path, params=params, data=data, json_data=json_data, headers=headers)
        return result

    def put(self, path, params=None, data=None, json_data=None, headers=None):
        result = self.session("PUT", path, params=params, data=data, json_data=json_data, headers=headers)
        return result

    def patch(self, path, params=None, data=None, json_data=None, headers=None):
        result = self.session("PATCH", path, params=params, data=data, json_data=json_data, headers=headers)
        return result

    def delete(self, path, params=None, data=None, json_data=None, headers=None):
        result = self.session("DELETE", path, params=params, data=data, json_data=json_data, headers=headers)
        return result
