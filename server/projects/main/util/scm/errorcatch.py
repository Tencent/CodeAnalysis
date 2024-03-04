# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
wrap object for catching all error
"""


class ErrorCatcher(object):
    """Catch an object method"s exception and handle the exception with custom error handler.

    The custom error handler is a callable accept an argument ``error``::

       def my_error_handler(error):
           if isinstance(error, Exception):
               #return Exception subclass instance if want to raise
               #else just return a value to caller
           else:
               #do else thing
    """

    def __init__(self, obj, error_handler):
        """
        :param obj: object to catch error
        :param error_handler: custom error handler
        """

        self._obj = obj
        self._err_handler = error_handler

    def __getattr__(self, name):
        try:
            value = getattr(self._obj, name)
        except Exception as err:  # NOCA:broad-except(可能存在多种异常)
            rst = self._err_handler(err)
            if isinstance(rst, Exception):
                raise rst
            else:
                return rst
        else:
            if not hasattr(value, "__call__"):
                return value
            else:
                def _callwrap(*args, **kwargs):
                    try:
                        return value(*args, **kwargs)
                    except Exception as err:  # NOCA:broad-except(可能存在多种异常)
                        rst = self._err_handler(err)
                        if isinstance(rst, Exception):
                            raise rst
                        else:
                            return rst

                return _callwrap
