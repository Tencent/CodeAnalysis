# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
文件管理 通用模块
"""
import io
import os
import logging
from urllib.parse import urlparse, unquote

from rest_framework.parsers import FileUploadParser

from utils import error

logger = logging.getLogger(__name__)


def format_file(uri, check_valid=True):
    """
    根据请求uri，解析出bucket/app，dirpath，filename
    """
    if not isinstance(uri, str):
        uri = uri.decode('utf-8')

    parse_result = urlparse(uri.strip('/'))
    paths = parse_result.path.split('/')

    # 处理URL中出现连续斜杠的场景
    file_info = [a for a in paths if a]
    file_info = [a.lower() for a in file_info[:2]] + file_info[2:]   # 把bucket和type转为小写

    if not check_valid:
        return file_info

    if len(file_info) < 3:
        raise error.QFSURLInvalid('url必须包含app/type/filename三部分')

    bucket, dirpath = file_info[:2]
    if len(bucket) > 40 or not bucket.isalnum():
        raise error.QFSURLInvalid('app只允许为数字和字母，且长度不允许超过40')

    # bucket和dirpath的总长度不能超过200
    if (len(bucket) + len(dirpath)) > 200:
        raise error.QFSURLInvalid('存储单元名字过长，请不要超过200字符。%s/%s' % (bucket, dirpath))

    file_name = '/'.join(file_info[2:])
    return [bucket, dirpath, file_name]


class CDFileUploadParser(FileUploadParser):
    """
    Parser for file upload data.
    """
    media_type = '*/*'
    errors = {
    }

    def get_filename(self, stream, media_type, parser_context):
        """
        Detects the uploaded file name. First searches a 'filename' url kwarg.
        Then tries to parse Content-Disposition header.
        """
        path_info = parser_context["request"].path_info
        file_name = path_info.split("/")[-1]
        return unquote(file_name)


class TempFile(io.BytesIO):

    @property
    def size(self):
        size = self.seek(0, os.SEEK_END)
        self.seek(0, os.SEEK_SET)
        return size
