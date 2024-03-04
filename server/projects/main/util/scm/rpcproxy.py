# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""定制化支持超时设置、鉴权头部的RpcServer
"""

from http import client
from xmlrpc.client import Transport, ServerProxy


class CustomTransport(Transport):
    """自定义传输
    """

    def __init__(self, timeout, headers=None):
        Transport.__init__(self)
        self._timeout = timeout or 20
        self._custom_headers = headers

    def make_connection(self, host):
        # return an existing connection if possible.  This allows
        # HTTP/1.1 keep-alive.
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        # create a HTTP connection object from a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        # store the host argument along with the connection object
        self._connection = host, client.HTTPConnection(chost, timeout=self._timeout)
        return self._connection[1]

    def send_headers(self, connection, headers):
        if self._custom_headers:
            for key, val in self._custom_headers.items():
                connection.putheader(key, val)
        for key, val in headers:
            connection.putheader(key, val)


class CustomServerProxy(ServerProxy):
    """自定义服务代理
    """

    def __init__(self, uri, transport=None, encoding=None,
                 verbose=0, timeout=None, headers=None):
        if transport is None:
            transport = CustomTransport(timeout, headers)
        ServerProxy.__init__(self, uri, transport, encoding, verbose, allow_none=True)
