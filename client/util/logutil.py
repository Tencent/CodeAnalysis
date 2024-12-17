# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
日志打印工具类，封装到统一的工具类进行打印输出，避免日志中保留原模块名信息
"""

import logging

logger = logging.getLogger(__name__)


class LogPrinter(object):
    """日志打印类"""
    @staticmethod
    def info(msg, *args, **kwargs):
        logger.info(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        logger.debug(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        logger.warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        logger.error(msg, *args, **kwargs)

    @staticmethod
    def exception(msg, *args, **kwargs):
        logger.exception(msg, *args, exc_info=True, **kwargs)
