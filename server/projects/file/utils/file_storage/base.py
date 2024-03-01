# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
"""
import os
import re
import hmac
import time
from hashlib import sha1
from urllib.parse import quote
from functools import wraps
from abc import ABC, abstractmethod


def retry(tries=3):
    """
    # 当返回值第一位为False时重试
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for _ in range(tries):
                result, data = f(*args, **kwargs)
                if result:
                    return result, data

                time.sleep(1)
            return f(*args, **kwargs)
        return wrapper
    return decorator


class StorageClient(ABC):

    def _check_bucket_name(self, name):
        """
        检查bucket名是否符合要求（1.长度不超过40，2.仅可以包含小写字母和数字的组合，包含大写字母会被转换为小写字母）
        :param name: str bucket名
        :return: (boolean, str) (是否符合要求，错误提示消息/name) 不符合要求时返回错误提示消息，符合要求时返回处理后的name
        """
        name = name.lower().strip()
        if len(name) > 40:
            return False, 'bucket长度不可超过40字符'

        match = re.search('^[0-9a-z]+$', name)
        if not match:
            return False, 'bucket仅可以包含小写字母和数字。'

        return True, name

    def _check_file_size(self, file):
        """检查文件大小
        """
        if isinstance(file, str):
            file_size = os.path.getsize(file)
        else:
            file_size = file.size

        if file_size > 5 * 1024 * 1024 * 1024:
            return False, '暂不支持上传大于5G的文件'
        return True, file_size

    def _format_file_name(self, file_name):
        """检查文件名
        """
        if not isinstance(file_name, str):
            file_name = file_name.decode('utf-8')
        file_name = file_name.lstrip('/')
        return file_name

    def format_auth(self, method, uri, params, headers, *args, **kwargs):
        """
        method: 该请求的 HTTP 操作行为，例如 PUT/GET/DELETE
        uri: 该请求中的 URI 部分，即除去 http:// 协议和域名的部分（通常以 / 开始），并且不包含 URL 中的参数部分。
              例如访问地址 http://testbucket-125000000.sztest.file.tencent-cloud.com/testfile 其 Format URI 为 /testfile
        params: 请求的参数，字典类型，在该函数内完成urlencode
        headers: 请求头，字典类型，在该函数内完成urlencode
        """
        return {}

    def format_host_path(self, app, type_, file_name):
        """
        针对COS存储，获取当前请求需要代理的host和path
        """
        return '', ''

    def quote_lower(self, s, safe='/'):
        """
        重写urllib中的quote方法，把多字节转成小写（quote为大写）但不影响其他单字节字符大小写
        """
        # fastpath
        always_safe = (b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                       b'abcdefghijklmnopqrstuvwxyz'
                       b'0123456789'
                       b'_.-~')

        _safe_map = {}
        for i in range(256):
            _safe_map[i] = chr(i) if (i < 128 and i in always_safe) else '%%%02x' % i
        _safe_quoters = {}
        if not s:
            if s is None:
                raise TypeError('None object cannot be quoted')
            return s

        if isinstance(safe, str):
            # Normalize 'safe' by converting to bytes and removing non-ASCII chars
            safe = safe.encode('ascii', 'ignore')
        else:
            safe = bytes([c for c in safe if c < 128])

        if isinstance(s, str):
            s = s.encode('utf-8')

        cachekey = (safe, always_safe)
        try:
            (quoter, safe) = _safe_quoters[cachekey]
        except KeyError:
            safe_map = _safe_map.copy()
            safe_map.update([(c, chr(c)) for c in safe])
            quoter = safe_map.__getitem__

            safe = always_safe + safe
            _safe_quoters[cachekey] = (quoter, safe)

        if not s.rstrip(safe):
            return s.decode("utf-8")

        return ''.join([quoter(char) for char in s])

    def urlencode_lower(self, params):
        data = []
        # key转小写，value里编码转小写，其他值保持一致
        for key, value in params.items():
            data.append("%s=%s" %
                        (quote(key).lower(), self.quote_lower(value, "")))

        return "&".join(data)

    def hmac_sha1(self, key, str):
        string_to_sign = str.encode('utf-8')
        key_to_sign = key.encode('utf-8')
        sign = hmac.new(key_to_sign, string_to_sign, sha1)
        return sign.hexdigest()

    @abstractmethod
    def create_bucket(self, name):
        """
        :param name: str bucket名，长度不可以超过40，仅可以包含小写字母和数字的组合。
        :return: (boolean，str) (是否创建成功，成功或错误消息)
        """
        pass

    @abstractmethod
    def list_bucket(self):
        """
        列出目前系统中的所有bucket.
        返回包含bucket名的生成器
        """
        pass

    @abstractmethod
    def delete_bucket(self, name):
        """
        删除bucket， 删除前bucket必须为空
        :param name: str bucket名，长度不可以超过40，仅可以包含小写字母和数字的组合。
        :return: (boolean，str) (是否删除成功，成功或错误消息)
        """
        pass

    @abstractmethod
    def upload_file(self, bucket, file_name, file):
        """
        上传单个文件至指定bucket，文件不能大于5G。
        :param bucket: str bucket名
        :param file_name: str 上传文件名，可以支持含目录结构（如/folder/file），建议使用简单的数字字母和!-_.这几个字符
        :param file: 文件本地保存路径，或django file对象
        :return: (boolean，str) (是否上传成功，成功或错误消息)
        """
        pass

    @abstractmethod
    def download_file(self, bucket, file_name):
        """
        下载指定文件。下载文件时，为防止文件内容过大，返回字节块生成器。
        :param bucket: str bucket名
        :param file_name: str 文件名，可以支持含目录结构（如/folder/file），建议使用简单的数字字母和!-_.这几个字符
        :return: (boolean，generator/str, size) (是否删除成功，成功或错误消息) 成功时返回响应，错误时返回错误信息。
        """
        pass

    @abstractmethod
    def delete_file(self, bucket, file_name):
        """
        删除指定文件。
        :param bucket: str bucket名
        :param file_name: str 文件名，可以支持含目录结构（如/folder/file），建议使用简单的数字字母和!-_.这几个字符
        :return: (boolean，str) (是否删除成功，成功或错误消息)
        """
        pass

    def batch_delete_file(self, bucket, file_list):
        """
        批量删除文件。
        :param bucket: str bucket名
        :param file_list: list/tuple/set 文件名列表，文件名为完整路径（包含bucket），因此在删除时，需留意避免重复拼接bucket
        :return: (boolean，str) (是否删除成功，失败列表或错误消息) 存在成功删除时，返回删除失败的文件列表。
        """
        if not isinstance(file_list, (list, tuple, set)):
            file_list = [file_list]

        if len(file_list) > 1000:
            return False, '不支持一次性删除1000个以上的文件'

        fail_info = []
        for file_name in file_list:
            if file_name.startswith("%s/" % bucket):
                file_name = file_name.split("/", 1)[-1]

            is_deleted, msg = self.delete_file(bucket, file_name)
            if not is_deleted:
                fail_info.append((file_name, msg))

        return True, fail_info
