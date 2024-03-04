# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util - exceptions
Server异常类定义
"""

from rest_framework import status

from util import errcode


class CDErrorBase(Exception):
    """
    CodeDog Server异常错误类型。遇到异常时，需要抛出ServerError，指定code和msg::
    
        raise ServerError(100, "server error msg")
    """

    def __init__(self, code, msg, data=None):
        """
        :param code: 异常代码
        :param msg: 异常消息
        """
        self.code = code
        self.msg = msg
        self.data = data

    def __str__(self):
        return "[%d]%s" % (self.code, self.msg)


class ServerError(CDErrorBase):
    """
    CodeDog Server异常错误类型。遇到异常时，需要抛出ServerError，指定code和msg::
    
        raise ServerError(100, "server error msg")
    """
    pass


class BaseServerError(Exception):
    """Server错误
    """
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, code=None, msg=None, data=None):
        """
        :param code: 异常代码
        :param msg: 异常消息
        """
        self.code = code or errcode.E_SERVER
        self.msg = msg or 'server error'
        self.data = data

    def __str__(self):
        return "[%s]%s" % (self.code, self.msg)

    def __repr__(self):
        return self.__str__()


class ClientError(CDErrorBase):
    """
    CodeDog Client异常错误类型。遇到异常时，需要抛出ClientError，指定code和msg::
    
        raise ClientError(300, "invalid param")
    """
    pass
