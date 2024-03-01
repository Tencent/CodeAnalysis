# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

import os

from django.conf import settings
from qcloud_cos import CosConfig, CosS3Client

from .base import StorageClient


class TencentCosStorageClient(StorageClient):
    """
    目前使用的是众测的腾讯云公共COS，实际上所有内容都存放在同一个BUCKET。
    但文件服务器对外的逻辑依然是将文件分bucket存放。
    """

    def __init__(self, options=None):

        if options is None:
            options = settings.STORAGE['OPTIONS']

        self.app_id = options['TENCENT_COS_APPID']
        self.secret_id = options['TENCENT_COS_SECRETID']
        self.secret_key = options['TENCENT_COS_SECRETKEY']
        self.region = options['TENCENT_COS_REGION']
        self.root_bucket = options['TENCENT_COS_ROOT_BUCKET']

        config = CosConfig(Appid=self.app_id, Secret_id=self.secret_id, Secret_key=self.secret_key, Region=self.region)
        self.client = CosS3Client(conf=config, retry=3)

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
            host = '%s.cos.%s.myqcloud.com' % (bucket, self.region)
            path = '/'.join(['', type_, file_name])
            return host, path
        else:
            host = '%s.cos.%s.myqcloud.com' % (self.root_bucket, self.region)
            path = '/'.join(['', bucket, type_, file_name])
            return host, path

    def format_auth(self, method, uri, params, headers, *args, **kwargs):
        """
        原则上应该与内部cos一致，但可直接调用SDK中的get_auth方法，文档见：
        https://cloud.tencent.com/document/product/436/35153
        """
        bucket, file_name = uri.strip('/').split('/', 1)
        bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)

        auth = self.client.get_auth(Method=method, Bucket=bucket, Key=file_name,
                                    Expired=300, Headers=headers, Params=params)

        return {'authorization': auth}

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
            self.client.create_bucket(name)
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
            for item in results['Buckets']['Bucket']:
                if item['Name'] not in buckets:
                    buckets.add(item['Name'])
                    yield item['Name']
        # 当前根存储为COS下的某个BUCKET
        else:
            results = self.client.list_objects(Bucket=self.root_bucket)
            if 'Contents' in results:
                for item in results['Contents']:
                    temp = item['Key'].split('/')
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
            if 'Contents' in results and len(results['Contents']) > 0:
                return True
            return False

        # 当前根存储为整个COS
        if self.root_bucket is None:
            if self.client.bucket_exists(name) and is_bucket_empty(name):
                return False, 'bucket %s 非空，删除bucket内部文件后再试。' % name
            else:
                self.client.delete_bucket(name)
                return True, ''
        # 当前根存储为COS下的某个BUCKET
        else:
            objects = {
                'Quiet': 'true',
                'Object': [],
            }
            results = self.client.list_objects(self.root_bucket)
            if 'Contents' in results:
                for item in results['Contents']:
                    temp = item['Key'].split('/')
                    # 项目中使用到的BUCKET为实际存储的BUCKET下的文件名的前缀
                    if temp[0] == name:
                        objects['Object'].append({'Key': item['Key']})
                r = self.client.delete_objects(Bucket=self.root_bucket, Delete=objects)
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
        file_name = self._format_file_name(file_name)
        bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)
        if isinstance(file, str):
            result = self.client.upload_file(Bucket=bucket, Key=file_name, LocalFilePath=file)
        else:
            result = self.client.put_object(Bucket=bucket, Body=file, Key=file_name)
        return True, '', result.get("Content-MD5")

    def list_file(self, bucket):
        """
        doc见.storage.StorageClient.list_file
        """
        # 当前根存储为整个COS
        if self.root_bucket is None:
            results = self.client.list_objects(Bucket=bucket)
        # 当前根存储为COS下的某个BUCKET
        else:
            results = self.client.list_objects(Bucket=self.root_bucket, Prefix='%s/' % bucket)

        if 'Contents' in results:
            for item in results['Contents']:
                yield item['Key'].split('/', maxsplit=1)[1]

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

        self.client.delete_object(Bucket=bucket, Key=file_name)

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

        response = self.client.get_object(Bucket=bucket, Key=file_name)
        fp = response['Body']

        return True, fp.get_stream(512), response.get("Content-Length", 0)

    def batch_delete_file(self, bucket, file_list):
        """
        批量删除文件
        """
        real_bucket = self.root_bucket
        delete_info = {
            'Object': [],
            'Quiet': 'true'
        }

        for file_name in file_list:
            # 文件名为完整路径（包含bucket），避免重复拼接bucket
            if file_name.startswith("%s/" % bucket):
                file_name = file_name.split("/", 1)[-1]

            real_bucket, file_name = self.format_real_bucket_and_file_name(bucket, file_name)

            delete_info['Object'].append({'Key': file_name})

        response = self.client.delete_objects(Bucket=self.root_bucket or bucket, Delete=delete_info)
        failed_list = [a['Key'] for a in response.get('Error', []) if a.get('Key')]
        return True, failed_list
