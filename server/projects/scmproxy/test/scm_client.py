# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""测试脚本
"""

import re
import logging
import http.client
import xmlrpc.client
import xmlrpc.server
from datetime import datetime


logger = logging.getLogger(__file__)


ScmProxy = "http://127.0.0.1:8001"


class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout):
        xmlrpc.client.Transport.__init__(self)
        self._timeout = timeout or 20

    def make_connection(self, host):
        # return an existing connection if possible.  This allows
        # HTTP/1.1 keep-alive.
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        # create a HTTP connection object from a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        # store the host argument along with the connection object
        self._connection = host, http.client.HTTPConnection(chost, timeout=self._timeout)
        return self._connection[1]


class TimeoutServerProxy(xmlrpc.client.ServerProxy):
    def __init__(self, uri, transport=None, encoding=None,
                 verbose=False, timeout=None):
        if transport is None:
            transport = TimeoutTransport(timeout)
        xmlrpc.client.ServerProxy.__init__(self, uri=uri, transport=transport, encoding=encoding,
                                           verbose=verbose, allow_none=True)


TimeoutServer = TimeoutServerProxy


class ScmError(Exception):
    """Scm错误基类, 并提供下面的参数

    :param msg(unicode): 错误消息
    """

    def __init__(self, msg):
        super(ScmError, self).__init__(msg)
        self.msg = msg


class ScmConnectionError(ScmError):
    """Scm链接错误
    """
    pass


class ScmClientError(ScmError):
    """Scm用户输入错误
    """
    pass


class ScmAccessDeniedError(ScmClientError):
    """Scm访问权限被拒
    """
    pass


class ScmNotFoundError(ScmClientError):
    """访问不存在的文件
    """
    pass


class ErrorCatcher(object):
    """Catch an object method's exception and handle the exception with custom error handler.

    The custom error handler is a callable accept an argument ``error``::

       def my_error_handler(error):
           if isinstance(error, Exception):
               #return Exception subclass instance if want to raise
               #else just return a value to caller
           else:
               #do else thing
    """

    def __init__(self, obj, error_handler):
        '''
        :param obj: object to catch error
        :param error_handler: custom error handler
        '''

        self._obj = obj
        self._err_handler = error_handler

    def __getattr__(self, name):
        try:
            value = getattr(self._obj, name)
        except Exception as err:
            rst = self._err_handler(err)
            if isinstance(rst, Exception):
                raise rst
            else:
                return rst
        else:
            if not hasattr(value, '__call__'):
                return value
            else:
                def _callwrap(*args, **kwargs):
                    try:
                        return value(*args, **kwargs)
                    except Exception as err:
                        rst = self._err_handler(err)
                        if isinstance(rst, Exception):
                            raise rst
                        else:
                            return rst

                return _callwrap


def _git_error_handler(error):
    """Git 错误处理

    :param error: jsonrpclib.jsonrpc.ProtocolError - 错误信息
    :return:
    """
    # err_msg 可能为 tuple - (status code, error msg)，也可能为字符串
    if type(error.message) != str:
        err_msg = error.message[1]
    else:
        err_msg = error.message
    logger.error("gitproxy error message: %s" % err_msg)
    if re.search(r"Revision doesn't exist", err_msg):
        return ScmNotFoundError(u"Git版本号不存在: %s" % err_msg)
    elif re.search(r"File doesn't exist", err_msg):
        return ScmNotFoundError(u"文件不存在: %s" % err_msg)
    elif re.search(r"Branch doesn't exist", err_msg):
        return ScmNotFoundError(u"分支不存在: %s" % err_msg)
    elif re.search(r"Authentication failed", err_msg):
        return ScmClientError(u"帐号密码错误: %s" % err_msg)
    elif re.search(r"Project doesn't exist or no project code access permission", err_msg):
        return ScmAccessDeniedError(u"项目可能不存在或没有项目访问权限: %s" % err_msg)
    # 2018-03-21 jerolin updated -- 增加scm url中使用git协议的异常信息捕获
    elif re.search(r"Submodule scm url was wrong with git format", err_msg):
        return ScmConnectionError(u"项目子模块的代码库地址暂不支持使用Git协议")
    elif re.search(r"Scm url was wrong with git format", err_msg):
        return ScmConnectionError(u"项目的代码库地址暂不支持使用Git协议")
    elif re.search(r"Git server error", err_msg):
        return ScmConnectionError(u"Git Code平台服务异常，请稍后再试")
    elif re.search(r"timed out", err_msg):
        return ScmConnectionError(u"正在获取代码信息，请稍后再试")
    else:
        logger.exception(err_msg)
        return ScmError(u"未知错误，请联系管理员")


class GitRemoteClient():
    """Git 远程客户端 - 通过 GitProxy 获取项目信息"""

    def __init__(self, scm_url, username=None, password=None, scm_type="git"):
        """
        初始化函数

        :param scm_url: scm库地址
        :param username: 域帐号
        :param password: 密码
        """
        # scm_info 作为参数传给GitProxy
        self._scm_info = {
            'scm_type': scm_type,
            'scm_url': scm_url.strip(),
            'username': username,
            'password': password
        }
        self._git_proxy = TimeoutServer(ScmProxy, timeout=20)

    @property
    def latest_revision(self):
        """最新版本号
        """
        return self._git_proxy.latest_revision(self._scm_info)

    @property
    def start_revision(self):
        """最初版本号
        """
        return self._git_proxy.start_revision(self._scm_info)

    def cat(self, path, revision):
        """获取文件内容

        :param path: 文件路径
        :param revision: 文件版本
        :type revision: str
        :return: 文件内容
        """
        content = self._git_proxy.cat(self._scm_info, path, revision)
        return content

    def get_revision_datetime(self, revision):
        """获取指定版本的创建时间

        :param revision: 文件版本
        :return: datetime对象
        """
        revision_datetime = datetime.strptime(self._git_proxy.get_revision_datetime(self._scm_info, revision),
                                              '%Y-%m-%d %H:%M:%S')
        return revision_datetime

    def log(self, revision_start=None, revision_end=None):
        """获取指定版本区间的提交日志

        :param revision_start: 起始版本
        :param revision_end: 结束版本
        :return: dict数据
            author - string - the name of the author who committed the revision
            date - datetime - the date of the commit
            message - string - the text of the log message for the commit
            revision - string - the revision of the commit
        """
        logs = self._git_proxy.log(self._scm_info, revision_start, revision_end)
        for log_info in logs:
            log_info['date'] = datetime.fromtimestamp(log_info["timestamp"])
        return logs

    def revision_lt(self, revision_start, revision_end):
        """比较版本大小

        :param revision_start: 起始版本
        :param revision_end: 结束版本
        :return: Boolean值
            False 表示revision_start >= revision_end
            True 表示revision_start < revision_end
        """
        return self._git_proxy.revision_lt(self._scm_info, revision_start, revision_end)

    def revisions_range(self, revision_start, revision_end):
        """返回指定版本号之间（包括指定的版本号）的版本列表

        :param revision_start: 起始版本，为空表示初始版本
        :param revision_end: 结束版本，为空表示最新版本
        :return: list: 包含start_revision和end_revision之间的版本号
        """
        revision_start = revision_start or self.start_revision
        revision_end = revision_end or self.latest_revision
        return self._git_proxy.revisions_range(self._scm_info, revision_start, revision_end)

    def list(self, path, revision=None):
        """返回指定路径下的子目录和文件列表

        :param path: 需要查询的列表，如果为空，则列出根目录下的目录和文件
        :param revision: 需要查询的版本，为空时表示最新版本
        :return: list: 包含start_revision和end_revision之间的版本号
        [{
            "name": "filename or directory name",
            "type": "file or dir",
        }]
        """
        return self._git_proxy.list(self._scm_info, path, revision)
