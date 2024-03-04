# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""Scm Proxy Server
"""

import logging
import logging.handlers
import os
import socketserver
from xmlrpc.server import SimpleXMLRPCServer, resolve_dotted_attribute

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

import apis
import settings
from sourcemgr import SourceManager
from utils import ScmError

logger = logging.getLogger("proxyserver")


class ScmProxyServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    """多线程 ScmProxy Server
    """

    def __init__(self, addr):
        """
        初始化函数

        :param addr: tuple - (host, port)
        """
        SimpleXMLRPCServer.__init__(
            self, addr=addr, encoding="UTF-8")
        self.allow_none = True
        self.register_introspection_functions()
        self.register_apis()

    def register_apis(self):
        """注册api，这里的apis可以作为一个模块，也可以作为一个包
        """
        apis.register_apis(self)

    def _dispatch(self, method, params):
        """重写SimpleRPCServer的 _dispatch，修改返回的异常信息
        其中针对权限验证的错误，直接返回 Authentication failed，避免返回带有帐号和密码的URL

        :param method: 方法名称
        :param params: 方法参数
        :return: 响应数据，可能为方法正常返回结果或者Fault对象
        """
        func = None
        try:
            func = self.funcs[method]
        except KeyError:
            if self.instance is not None:
                if hasattr(self.instance, "_dispatch"):
                    return self.instance._dispatch(method, params)
                else:
                    try:
                        func = resolve_dotted_attribute(self.instance, method, True)
                    except AttributeError as err:
                        logger.exception("resolve dotted attribute: %s" % err)
                        pass
        if func is not None:
            scm_type = params[0]["scm_type"]
            try:
                if isinstance(params, list) or isinstance(params, tuple):
                    response = func(*params)
                else:
                    response = func(**params)
                return response
            except Exception as err:
                logger.exception("Error info:")
                err_msg = ScmError.handler_msg(scm_type, str(err))
                trace_string = "{method: %s, error_message: %s}" % (func.__name__, err_msg)
                logger.error(trace_string)
                raise Exception(trace_string)
        else:
            raise Exception("Method %s not supported." % method)

    def process_request(self, request, client_address):
        """重写 ThreadingMixIn 的 process_request方法

        当线程停止时，移除线程，避免内存泄漏

        :param request: dict，请求数据
        :param client_address: 客户端地址
        """
        super().process_request(request, client_address)
        for thread in self._threads:
            if not thread.is_alive():
                self._threads.remove(thread)


def main():
    """ScmProxyServer 主入口
    """
    # 配置PROXY环境变量
    os.environ.update(settings.PROXY_ENVS)
    # 创建源码目录
    os.makedirs(settings.SOURCE_DIR, exist_ok=True)
    # 创建临时目录
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    # 创建日志目录
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    # scmproxy Log 配置
    formater = logging.Formatter(
        "%(asctime)-15s PID:%(process)d %(filename)s-line:%(lineno)d | %(levelname)s - %(message)s")
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=os.path.join("logs", "scmproxy.log"),
                                                             when="d", backupCount=15)

    if settings.SENTRY_URL:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        sentry_sdk.init(
            dsn=settings.SENTRY_URL,
            integrations=[sentry_logging]
        )
    console_hanlder = logging.StreamHandler()
    file_handler.setLevel("DEBUG")
    file_handler.setFormatter(formater)
    console_hanlder.setFormatter(formater)
    console_hanlder.setLevel("INFO")
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_hanlder)
    logger.setLevel(logging.DEBUG)
    # 启动源码和临时文件定时清理线程
    logger.info("Source Manager - Start")
    SourceManager(settings.SOURCE_DIR).start()
    SourceManager(settings.TEMP_DIR).start()
    # 启动Scmproxy服务
    server = ScmProxyServer((settings.HOST, settings.PORT))
    logger.info("Server[%s:%s] - Start" % (settings.HOST, settings.PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    logger.info("Server[%s:%s] - Stop" % (settings.HOST, settings.PORT))


if __name__ == "__main__":
    main()
