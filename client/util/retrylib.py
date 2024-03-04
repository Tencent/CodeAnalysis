# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
异常重试类
"""


import logging

logger = logging.getLogger(__name__)


class RetryOnError(object):
    '''wrapper class to retry call.

    ``error_handler`` is a callable accepts three arguments, ``error`` and `` count`` and ``name``
    ``error`` is the Exception instance.
    ``count`` is the retry count starting from 0.
    ``name`` is the attribute name or function name.
    Exception raise inside error_handler will not be catched.

    :param obj_or_func: the object to wrapper
    :param error_handler: error handler
    '''

    def __init__(self, obj_or_func, error_handler):
        self._obj_or_func = obj_or_func
        self._error_handler = error_handler

    def __getattr__(self, name):
        cnt = 0
        while True:
            try:
                val = getattr(self._obj_or_func, name)
            except Exception as err:
                logger.error('encounter exception: %s', str(err))
                self._error_handler(err, cnt, name)
                cnt += 1
                logger.info('retrying get attribute "%s" on %d time', name, cnt)
            else:
                if callable(val):
                    return RetryOnError(val, self._error_handler)
                else:
                    return val

    def __call__(self, *args, **kwargs):
        cnt = 0
        while True:
            try:
                return self._obj_or_func(*args, **kwargs)
            except Exception as err:
                logger.error('encounter exception: %s', str(err))
                self._error_handler(err, cnt, self._obj_or_func.__name__)
                cnt += 1
                logger.info('retrying method "%s" on %d time', self._obj_or_func.__name__, cnt)
