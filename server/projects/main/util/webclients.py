# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util.webclients 访问第三方平台的客户端
"""
import json
import logging

from django.conf import settings

from util import errcode
from util.httpclient import HttpClient
from util.exceptions import CDErrorBase
from util.authticket import ServerInternalTicket
from util.exceptions import CDErrorBase
from util.httpclient import HttpClient

logger = logging.getLogger(__name__)


def ActionWarpper(func):
    """装饰器
    """
    def __deco(*args, **kwargs):
        rsp = func(*args, **kwargs)
        result = rsp.data.decode("utf-8")
        # 正常返回
        if 200 <= rsp.status < 300:
            if result:
                return json.loads(result)
            else:
                return result
        else:
            # 其他错误，如请求参数错误
            logger.error(result)
            # 系统错误
            if rsp.status >= 500:
                raise CDErrorBase(errcode.E_SERVER, "server return code[%d] %s with params %s" % (
                    rsp.status, result, str(args)))
            else:
                raise CDErrorBase(errcode.E_CLIENT, "server return code[%d] %s with params %s" % (
                    rsp.status, result, str(args)), data=result)

    return __deco


class BaseClient(object):
    """基础客户端
    """

    def __init__(self):
        self._session = HttpClient()
        self._server_url = None
        self._headers = {
            "SERVER-TICKET": ServerInternalTicket.generate_ticket(),
            "CONTENT-TYPE": "application/json"
        }
        self._apis = {}

    def _get_url(self, path):
        return "%s/%s" % (self._server_url, path)

    @ActionWarpper
    def get(self, path, query_params):
        return self._session.get(self._get_url(path), params=query_params, headers=self._headers)

    @ActionWarpper
    def post(self, path, data):
        return self._session.post(self._get_url(path), json_data=data, headers=self._headers)

    @ActionWarpper
    def patch(self, path, data):
        return self._session.patch(self._get_url(path), json_data=data, headers=self._headers)

    @ActionWarpper
    def put(self, path, data):
        return self._session.put(self._get_url(path), json_data=data, headers=self._headers)

    @ActionWarpper
    def delete(self, path, data):
        return self._session.delete(self._get_url(path), json_data=data, headers=self._headers)

    def api(self, name, data, path_params=None):
        api_def = self._apis.get(name)
        if not api_def:
            raise CDErrorBase(code=errcode.E_SERVER,
                              msg="调用错误，未知 server api: %s" % name)
        path = api_def["path"] % path_params if path_params else api_def["path"]
        logger.info("调用 server接口：%s，参数如下：" % path)
        logger.debug(data)
        if api_def["method"] == "get":
            return self.get(path, query_params=data)
        elif api_def["method"] == "post":
            return self.post(path, data=data)
        elif api_def["method"] == "put":
            return self.put(path, data=data)
        elif api_def["method"] == "patch":
            return self.patch(path, data=data)
        elif api_def["method"] == "delete":
            return self.delete(path, data=data)


class AnalyseClient(BaseClient):
    """Analysis访问客户端
    """
    def __init__(self):
        """
        初始化需要授权，访问地址等
        """
        super(AnalyseClient, self).__init__()
        self._server_url = settings.ANALYSE_SERVER_URL

        self._apis = {
            "sync_pkg_rule_map": {
                "path": "api/base/pkgrulemapsync/",
                "method": "post",
            },
            "create_project": {
                "path": "api/projects/",
                "method": "post",
            },
            "delete_project": {
                "path": "api/projects/%d/",
                "method": "delete",
            },
            "create_scan": {
                "path": "api/projects/%d/scans/",
                "method": "post",
            },
            "get_overview": {
                "path": "api/projects/%d/overview/",
                "method": "get",
            },
            'scan_check': {
                'path': 'api/projects/%d/scans/%d/check/',
                'method': 'get',
            },
            'update_scan': {
                'path': 'api/projects/%d/scans/%d/info/',
                'method': 'patch',
            },
            "get_scans": {
                "path": "api/projects/%d/scans/",
                "method": "get",
            },
            "get_scan": {
                "path": "api/projects/%d/scans/%d/",
                "method": "get",
            },
            "update_scan": {
                "path": "api/projects/%d/scans/%d/info/",
                "method": "patch",
            },
            "close_scan": {
                "path": "api/projects/%d/scans/%d/",
                "method": "put",
            },
            "get_cloc_languages": {
                "path": "api/projects/%d/codemetric/cloclangs/",
                "method": "get",
            }
        }

    def get_data_from_result(self, result):
        """
        Analysis返回格式调整，不具备通用性，需要特殊适配
        """
        if isinstance(result, dict):
            if result.get("data") is not None and result.get("code") is not None and result.get(
                    "status_code") is not None:
                return result["data"]
        return result

    def api(self, name, data, path_params=None):
        api_def = self._apis.get(name)
        if not api_def:
            raise CDErrorBase(code=errcode.E_SERVER,
                              msg="调用错误，未知analyse server api: %s" % name)
        path = api_def["path"] % path_params if path_params else api_def["path"]
        logger.info("调用analyse server接口：%s，参数如下：" % path)
        logger.info(json.dumps(data, indent=2))
        if api_def["method"] == "get":
            result = self.get(path, query_params=data)
        elif api_def["method"] == "post":
            result = self.post(path, data=data)
        elif api_def["method"] == "put":
            result = self.put(path, data=data)
        elif api_def["method"] == "patch":
            result = self.patch(path, data=data)
        elif api_def["method"] == "delete":
            return self.delete(path, data=data)
        else:
            return None
        return self.get_data_from_result(result)


class LoginProxyClient(BaseClient):
    """Login登录服务客户端
    """

    def __init__(self):
        """初始化需要授权，访问地址等
        """
        super(LoginProxyClient, self).__init__()
        self._server_url = settings.LOGIN_SERVER_URL
        self._apis = {
            "create_user_task": {
                "path": "api/v1/login/users/",
                "method": "post"
            },
            "update_user_task": {
                "path": "api/v1/login/users/%s/",
                "method": "put"
            }
        }
