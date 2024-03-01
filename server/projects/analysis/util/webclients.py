# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util - webclient
访问第三方平台的客户端
"""
import json
import logging

from django.conf import settings

from util import errcode
from util.authticket import MainServerTicket
from util.exceptions import CDErrorBase
from util.httpclient import HttpClient

logger = logging.getLogger(__name__)


def ActionWarpper(func):
    def __deco(*args, **kwargs):
        rsp = func(*args, **kwargs)
        result = rsp.data.decode("utf-8")
        if 200 <= rsp.status < 300:  # 正常返回
            return json.loads(result)
        else:
            logger.error(result)  # 其他错误，如请求参数错误
            if rsp.status >= 500:  # 系统错误
                raise CDErrorBase(errcode.E_SERVER, 'Main server return code %d with params %s' % (
                    rsp.status, str(args)))
            else:
                raise CDErrorBase(errcode.E_CLIENT, 'Main server return code %d with params %s' % (
                    rsp.status, str(args)), data=result)

    return __deco


class MainClient:
    def __init__(self):
        """
        初始化需要授权，访问地址等
        """
        self._server_url = settings.MAIN_SERVER_URL
        self._headers = {"SERVER-TICKET": MainServerTicket.generate_ticket(), "CONTENT-TYPE": "application/json"}
        self._session = HttpClient()

        self._apis = {
            'job_closed': {
                'path': 'api/projects/%d/jobs/%d/',
                'method': 'put',
            },
            'project_detail': {
                'path': 'api/projects/%s/',
                'method': 'get',
            },
            'toolname_list': {
                'path': 'api/conf/toolnames/',
                'method': 'get',
            },
            'get_package_rule_ids': {
                'path': 'api/conf/checkpackages/%s/checkruleids/',
                'method': 'get',
            },
            'scheme_detail': {
                'path': 'api/projects/%s/scheme/',
                'method': 'get',
            },
            'scheme_checkprofile': {
                'path': 'api/projects/%s/scheme/checkprofile/',
                'method': 'get',
            },
            'report_closed': {
                'path': 'api/personstat/reports/%d/',
                'method': 'put',
            },
            'project_permission': {
                'path': 'api/projects/%s/permissions/',
                'method': 'get'
            },
            'repo_permission': {
                'path': 'api/repos/%s/permissions/',
                'method': 'get'
            },
            'repoinfo_summary': {
                'path': 'api/personstat/repoinfos/summary/',
                'method': 'post'
            }
        }

    def _get_url(self, path):
        return "%s/%s" % (self._server_url, path)

    @ActionWarpper
    def get(self, path, query_params):
        return self._session.get(self._get_url(path), params=query_params, headers=self._headers)

    @ActionWarpper
    def post(self, path, data):
        return self._session.post(self._get_url(path), json_data=data, headers=self._headers)

    @ActionWarpper
    def put(self, path, data):
        return self._session.put(self._get_url(path), json_data=data, headers=self._headers)

    def get_data_from_result(self, result):
        """
        Analysis返回格式调整，不具备通用性，需要特殊适配
        """
        if isinstance(result, dict) and result.get("data") is not None and \
                result.get("code") is not None and result.get("status_code") is not None:
            return result["data"]
        else:
            return result

    def api(self, name, data, path_params=None):
        api_def = self._apis.get(name)
        if not api_def:
            raise CDErrorBase(code=errcode.E_SERVER,
                              msg="调用错误，未知Main server api: %s" % name)
        path = api_def["path"] % path_params if path_params else api_def["path"]
        if api_def["method"] == 'get':
            result = self.get(path, query_params=data)
        elif api_def["method"] == 'post':
            result = self.post(path, data=data)
        elif api_def["method"] == 'put':
            result = self.put(path, data=data)
        else:
            return None
        return self.get_data_from_result(result)
