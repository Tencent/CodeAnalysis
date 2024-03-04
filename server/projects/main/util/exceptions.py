# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Server异常类定义
"""

# 第三方
from rest_framework import status

# 项目内
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
        super(CDErrorBase, self).__init__(msg)

    def __str__(self):
        return "[%d]%s" % (self.code, self.msg)

    def __repr__(self):
        return self.__str__()


class CDScmError(CDErrorBase):
    """
    CodeDog Server Scm异常错误类型。遇到异常时，需要抛出CDScmError，指定code和msg::

        raise CDScmError(11x, "scm error msg")
    """


class ServerError(CDErrorBase):
    """
    CodeDog Server异常错误类型。遇到异常时，需要抛出ServerError，指定code和msg::
    
        raise ServerError(100, "server error msg")
    """
    pass


class ServerConfigError(ServerError):
    """
    CodeDog Server异常错误类型。遇到配置异常时，需要抛出ServerConfigError，指定msg
    """

    def __init__(self, msg, data=None):
        """
        :param msg: 异常数据
        :param data: 异常详细数据
        """
        self.code = 100
        super(ServerConfigError, self).__init__(self.code, msg, data)


class ServerOperationError(ServerError):
    """
    CodeDog Server异常错误类型。遇到操作异常时，需要抛出ServerOperationError，指定msg
    """

    def __init__(self, msg, data=None):
        """
        :param msg: 异常数据
        :param data: 异常详细数据
        """
        self.code = 100
        super(ServerOperationError, self).__init__(self.code, msg, data)


class ClientError(CDErrorBase):
    """
    CodeDog Client异常错误类型。遇到异常时，需要抛出ClientError，指定code和msg::
    
        raise ClientError(300, "invalid param")
    """
    pass


class BaseServerError(Exception):
    """Server错误
    """
    status_code = status.HTTP_400_BAD_REQUEST
    code = errcode.E_SERVER_BASE

    def __init__(self, code=None, msg=None, data=None):
        """
        :param code: 异常代码
        :param msg: 异常消息
        """
        self.code = code or self.code
        self.msg = msg or 'server error'
        self.data = data

    def __str__(self):
        return "[%s]%s" % (self.code, self.msg)

    def __repr__(self):
        return self.__str__()


class OrganizationCreateError(BaseServerError):
    """创建团队错误
    """


class ProjectTeamCreateError(BaseServerError):
    """创建项目错误
    """
    pass


class ProjectTeamUpdateError(BaseServerError):
    """更新项目错误
    """
    pass


class InviteCodeError(BaseServerError):
    """邀请码错误
    """

    def __init__(self, code=errcode.E_SERVER_INVITE_CODE):
        if code == errcode.E_SERVER_INVITE_CODE:
            self.code = code
            self.msg = "邀请码错误"
        elif code == errcode.E_SERVER_INVITE_CODE_EXPIRED:
            self.code = code
            self.msg = "邀请码已过期"


class ProjectTeamLabelCreateError(BaseServerError):
    """项目标签创建错误
    """
    pass


class ProjectTeamLabelUpdateError(BaseServerError):
    """项目标签更新错误
    """
    pass


class RepositoryCreateError(BaseServerError):
    """代码库创建错误
    """
    pass


class RepositoryUpdateError(BaseServerError):
    """代码库更新错误
    """
    pass


class ProjectCreateError(BaseServerError):
    """项目创建错误
    """

    def __init__(self, msg=None, data=None):
        """初始化函数
        """
        super().__init__(errcode.E_SERVER_PROJECT_CREATE, msg, data)


class ProjectScanCreateError(BaseServerError):
    """分析任务创建扫描错误
    """
    pass


class ProjectArchiveStartError(BaseServerError):
    """分析任务启动归档错误
    """
    pass


class ProjectScanConfigError(BaseServerError):
    """分析任务创建扫描配置错误
    """
    code = errcode.E_CLIENT_CONFIG_ERROR


class NodeRegisterError(BaseServerError):
    """节点注册错误
    """

    def __init__(self, msg=None, data=None):
        """初始化函数
        """
        super().__init__(errcode.E_SERVER_NODE_REGISTER, msg, data)


class ScmInfoError(BaseServerError):
    """scm info校验error
    """
    pass


class UserNoOAuthError(BaseServerError):
    """未授权error
    """

    def __init__(self, msg=None, data=None):
        """初始化函数
        """
        super().__init__(errcode.E_USER_CONFIG_NO_OAUTH, msg, data)


class DragSortError(BaseServerError):
    """排序失败
    """
    pass


class CheckToolLibAddError(BaseServerError):
    """工具添加依赖错误
    """
    pass
