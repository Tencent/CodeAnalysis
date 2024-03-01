# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""错误模块
"""

from rest_framework import status

BUCKET_NOT_EXIST = 'bucket_not_exist'
BUCKET_CREATE_FAIL = 'cos_bucket_create_fail'
BUCKET_FORBIDDEN = 'bucket_forbidden'
FILE_NOT_EXIST = 'file_not_exist'
FILE_EXIST = 'file_exist'
URL_NOT_MATCH = 'url_not_match'
OPTION_NOT_SUPPORT = 'option_not_support'
PARAM_ERROR = 'param_error'
URL_INVALID = 'url_invalid'
UPLOAD_ERROR = 'upload_error'
DELETE_ERROR = 'delete_error'
DOWNLOAD_ERROR = 'download_error'


ERROR_CODE = {
    BUCKET_NOT_EXIST: status.HTTP_404_NOT_FOUND,
    BUCKET_CREATE_FAIL: status.HTTP_500_INTERNAL_SERVER_ERROR,
    BUCKET_FORBIDDEN: status.HTTP_403_FORBIDDEN,
    FILE_NOT_EXIST: status.HTTP_404_NOT_FOUND,
    OPTION_NOT_SUPPORT: status.HTTP_400_BAD_REQUEST,
    PARAM_ERROR: status.HTTP_400_BAD_REQUEST,
    URL_INVALID: status.HTTP_400_BAD_REQUEST,
}


class QFSRequestError(Exception):
    """请求异常
    """

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code


class QFSURLInvalid(QFSRequestError):
    """请求链接无效
    """

    def __init__(self, detail=None):
        self.code = URL_INVALID
        self.detail = detail


class QFSUnitCreateFailed(QFSRequestError):
    """存储单元创建失败
    """
    def __init__(self, detail=None):
        self.code = BUCKET_CREATE_FAIL
        self.detail = detail


class QFSUnitNotFound(QFSRequestError):
    """存储单元不存在
    """
    def __init__(self, detail=None):
        self.code = BUCKET_NOT_EXIST
        self.detail = detail


class QFSUnitForbidden(QFSRequestError):
    """存储单元没有权限
    """
    def __init__(self, detail=None):
        self.code = BUCKET_FORBIDDEN
        self.detail = detail


class QFSParamConfigError(QFSRequestError):
    """存储单元参数配置异常
    """

    def __init__(self, detail=None):
        self.code = PARAM_ERROR
        self.detail = detail


class QFSFileUploadError(QFSRequestError):
    """文件上传异常
    """
    def __init__(self, detail=None):
        self.code = UPLOAD_ERROR
        self.detail = detail


class QFSFileDeleteError(QFSRequestError):
    """文件删除异常
    """

    def __init__(self, detail=None):
        self.code = DELETE_ERROR
        self.detail = detail


class QFSFileDownloadError(QFSRequestError):
    """文件下载异常
    """

    def __init__(self, detail):
        self.code = DOWNLOAD_ERROR
        self.detail = detail


class QFSFileNotExistdError(QFSRequestError):
    """文件下载异常
    """

    def __init__(self, detail):
        self.code = FILE_NOT_EXIST
        self.detail = detail
