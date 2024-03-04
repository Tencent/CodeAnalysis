# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

import os

import urllib3
from django.conf import settings
from minio import Minio
from minio.api import sign_v4_s3, StaticProvider, time
from minio.error import InvalidResponseError

from .base import StorageClient


class MinioStorageClient(StorageClient):
    """
    基于Minio进行存储
    """

    def __init__(self, options=None):

        if options is None:
            options = settings.STORAGE['OPTIONS']

        self.entrypoint = options['MINIO_ENTRYPOINT']
        self.access_key = options['MINIO_ACCESS_KEY']
        self.secret_key = options['MINIO_SECRET_KEY']
        self.secure = options.get('MINIO_SECURE', None)
        self.region = options.get('MINIO_REGION', None)
        self.secret_token = options.get('MINIO_SECRET_TOKEN', None)
        self.root_bucket = options.get('MINIO_ROOT_BUCKET', None)

        http = urllib3.PoolManager(retries=urllib3.Retry(total=3, backoff_factor=0.2))

        self.client = Minio(self.entrypoint,
                            access_key=self.access_key,
                            secret_key=self.secret_key,
                            secure=self.secure,
                            region=self.region,
                            http_client=http)
        self.credentials = StaticProvider(self.access_key, self.secret_key, self.secret_token)

    def format_real_bucket_and_file_name(self, bucket, file_name):
        """
        返回实际的bucket名和file_name
        :param bucket: str 项目中要创建的bucket名
        :param file_name: str 项目中要上传的文件路径
        :return: str 实际存储时的bucket名和file_name
        """
        # 当前根存储为整个COS
        if self.root_bucket is None:
            return bucket, file_name
        # 当前根存储为COS下的某个BUCKET
        else:
            return self.root_bucket, '%s/%s' % (bucket, file_name)

    def format_host_path(self, bucket, type_, file_name):
        """
        针对COS存储，获取当前请求需要代理的host和path
        """
        if self.root_bucket is None:
            path = '/'.join(['', bucket, type_, file_name])
        # 当前根存储为COS下的某个BUCKET
        else:
            path = '/'.join(['', self.root_bucket, bucket, type_, file_name])

        return self.entrypoint, path

    def format_auth(self, method, uri, params, headers, *args, **kwargs):
        """
        使用minio库中的sign_v4函数，完成S3兼容的签名逻辑
        """
        bucket, file_name = uri.strip('/').split('/', 1)
        region = self.client._get_region(bucket, None)
        url = self.client._base_url.build(
            method.upper(), region, bucket_name=bucket, object_name=file_name,
            query_params=params)
        headers, date = self.client._build_headers(url.netloc, headers, None, self.credentials.retrieve())
        
        if kwargs.get("content_sha256"):
            headers["x-amz-content-sha256"] = kwargs["content_sha256"]
        headers = sign_v4_s3(method.upper(), url, region,
                             headers, self.credentials.retrieve(),
                             headers.get("x-amz-content-sha256"), date)
        return headers

    def download_auth(self, bucket, file_name):
        """
        使用minio库中的sign_v4函数，完成S3兼容的签名逻辑
        """
        region = self.client._get_region(bucket, None)
        # Construct target url.
        url = self.client._base_url.build(
            "GET", region, bucket_name=bucket, object_name=file_name,
            query_params=None)
        # Get signature headers if any.
        date = time.utcnow()
        headers = {"x-amz-date": time.to_amz_date(date)}
        headers = sign_v4_s3("GET", url, region,
                             headers, self.credentials.retrieve(),
                             None, date)
        return headers

    def create_bucket(self, name):
        """
        doc见.storage.StorageClient.create_bucket
        当前根存储为COS下的某个BUCKET时，不会实际创建请求的name。所以list_bucket的结果中不会包含该name。
        只有在发生实际的上传操作时，才会在list_bucket的结果中展示出该name对应的bucket。
        """
        is_valid, msg = self._check_bucket_name(name)
        if not is_valid:
            return False, msg
        else:
            name = msg

        # 当前根存储为COS下的某个BUCKET
        if self.root_bucket is not None:
            name = self.root_bucket

        if not self.client.bucket_exists(name):
            self.client.make_bucket(name)
            return True, ''
        else:
            return True, 'bucket already exist'

    def list_bucket(self):
        """
        doc见.storage.StorageClient.list_bucket
        """
        buckets = set()
        # 当前根存储为整个COS
        if self.root_bucket is None:
            results = self.client.list_buckets()
            for item in results:
                if item.name not in buckets:
                    buckets.add(item.name)
                    yield item.name
        # 当前根存储为COS下的某个BUCKET
        else:
            results = self.client.list_objects(self.root_bucket)
            for item in results:
                temp = item.object_name.split('/')
                if len(temp) > 1 and temp[0] not in buckets:
                    buckets.add(temp[0])
                    yield temp[0]

    def delete_bucket(self, name):
        """
        doc见.storage.StorageClient.delete_bucket
        """
        is_valid, msg = self._check_bucket_name(name)
        if not is_valid:
            return False, msg
        else:
            name = msg

        def is_bucket_empty(name):
            """
            判断bucket是否为空
            """
            results = self.client.list_objects(name)
            return len(results) != 0

        # 当前根存储为整个COS
        if self.root_bucket is None:
            if self.client.bucket_exists(name) and not is_bucket_empty(name):
                return False, 'bucket %s 非空，删除bucket内部文件后再试。' % name
            else:
                self.client.remove_bucket(name)
                return True, ''
        # 当前根存储为COS下的某个BUCKET
        else:
            results = self.client.list_objects(self.root_bucket)
            object_list = [item.object_name for item in results]
            if object_list:
                r = self.client.remove_objects(self.root_bucket, object_list)
                if r == {}:
                    return True, ''
                else:
                    return False, '删除bucket %s 错误' % name
            else:
                return True, ''

    def upload_file(self, bucket, file_name, file):
        """
        doc见.storage.StorageClient.upload_file
        如果已经存在同名文件，会直接覆盖
        """
        is_valid, msg = self._check_bucket_name(bucket)
        if not is_valid:
            return False, msg, None
        else:
            bucket = msg
        is_valid, msg = self._check_file_size(file)
        if not is_valid:
            return False, msg
        else:
            file_size = msg
        file_name = self._format_file_name(file_name)
        bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)
        try:
            if isinstance(file, str):
                result = self.client.fput_object(bucket, file_name, file)
            else:
                result = self.client.put_object(bucket, file_name, file, file_size)
        except InvalidResponseError as err:
            return False, repr(err), None
        return True, '', result

    def list_file(self, bucket):
        """
        doc见.storage.StorageClient.list_file
        """
        # 当前根存储为整个COS
        if self.root_bucket is None:
            results = self.client.list_objects(bucket)
            for item in results:
                yield item

        # 当前根存储为COS下的某个BUCKET
        else:
            results = self.client.list_objects(self.root_bucket, '%s/' % bucket)
            for item in results:
                yield item.object_name.split('/', maxsplit=1)[-1]

    def delete_file(self, bucket, file_name):
        """
        doc见.storage.StorageClient.delete_file
        """
        is_valid, msg = self._check_bucket_name(bucket)
        if not is_valid:
            return False, msg
        else:
            bucket = msg

        bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)

        try:
            self.client.remove_object(bucket, file_name)
        except InvalidResponseError as err:
            return False, repr(err)

        return True, ''

    def download_file(self, bucket, file_name):
        """
        doc见.storage.StorageClient.download_file
        下载文件时，为防止文件内容过大，使用stream模式进行下载，且返回值为response，而非请求内容
        """
        is_valid, msg = self._check_bucket_name(bucket)
        if not is_valid:
            return False, msg, 0
        else:
            bucket = msg

        bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)

        data = self.client.get_object(bucket, file_name)
        return True, data.stream(1024 * 1024), data.headers.get("Content-Length", 0)

    def batch_delete_file(self, bucket, file_list):
        """
        批量删除文件
        """
        real_bucket = self.root_bucket
        object_list = []
        for file_name in file_list:
            # 文件名为完整路径（包含bucket），避免重复拼接bucket
            if file_name.startswith("%s/" % bucket):
                file_name = file_name.split("/", 1)[-1]

            real_bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)

            object_list.append(file_name)

        result = self.client.remove_objects(real_bucket, object_list)
        failed_list = [a['object_name'] for a in result if a.get('object_name')]
        return True, failed_list
