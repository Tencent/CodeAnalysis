# -*- encoding: utf-8 -*-
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

    def session(self, method, path, params, data=None, json_data=None, headers=None, **kwargs):
        """请求基础方法
        """
        if data and type(data) != bytes:
            data = str(data).encode("utf-8")
        elif json_data:
            data = json.dumps(json_data).encode("utf-8")
        if kwargs.get("stream") is True:
            return self._http_client.request(method, path, fields=params, headers=headers, preload_content=False)

        else:
            return self._http_client.request(method, path, fields=params, headers=headers, body=data, **kwargs)

    def get(self, path, params=None, headers=None, **kwargs):
        result = self.session("GET", path, params=params, headers=headers, **kwargs)
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
