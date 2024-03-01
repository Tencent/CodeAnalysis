# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""clients.excepiton
异常类型
"""


class HTTPBaseException(Exception):
    """基本异常
    """

    def __init__(self, code=None, msg=None):
        """初始化函数

        :param code: int - 错误码
        :param msg: str - 异常信息
        """
        if code:
            self.code = code
        if msg:
            self.message = msg

    def __unicode__(self):
        return "[%s] %s" % (self.code, self.message)

    def __str__(self):
        return "[%s] %s" % (self.code, self.message)


class BadRequestException(HTTPBaseException):
    """参数错误异常
    """
    code = 400
    message = "Bad Request"


class AuthorizationException(HTTPBaseException):
    """认证异常
    """
    code = 401
    message = "Authentication failed"


class ForbiddenException(HTTPBaseException):
    """权限异常
    """
    code = 403
    message = "remote error: Git:Project not found"


class NotFoundException(HTTPBaseException):
    """不存在异常，也可能是账号没有权限异常
    """
    code = 404
    message = "remote error: Git:Project not found"


class ServerException(HTTPBaseException):
    """服务器异常
    """
    code = 500
    message = "The requested URL returned error: 500"
