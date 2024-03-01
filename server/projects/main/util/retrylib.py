# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""重试模块
"""

import time
import logging

from functools import wraps


logger = logging.getLogger(__name__)


class RetryDecor(object):
    """重试装饰器类
    """
    def __init__(self, total=3, interval=5, ignore_errors=None):
        """初始化函数
        :param total: int，重试次数
        :param interval: int，重试间隔时间，单位为秒
        :param ignore_errors: list，可忽略的错误类型
        """
        self._total = total
        self._interval = interval
        self._ignore_errors = ignore_errors

    def __call__(self, func):
        """执行重试处理
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            cnt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    logger.warning("method <%s> exception: %s", func.__name__, err)
                    if self._check_error_ignore(err):
                        raise
                    if cnt >= self._total:
                        logger.exception("method <%s> exception: %s", func.__name__, err)
                        raise
                    else:
                        cnt += 1
                        logger.info("retrying method <%s> on %d time", func.__name__, cnt)
                    if self._interval:
                        time.sleep(self._interval)
        return wrapper

    def _check_error_ignore(self, err):
        """检查错误是否需要忽略
        """
        if not self._ignore_errors:
            return False
        if not isinstance(self._ignore_errors, list):
            self._ignore_errors = [self._ignore_errors]
        for item in self._ignore_errors:
            if isinstance(err, item):
                logger.debug("<error: %s> match ignore_error: %s, ignored", err, self._ignore_errors)
                return True
        return False
