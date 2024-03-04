# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

import os
from hashlib import md5
from wsgiref.util import FileWrapper

from django.conf import settings

from .base import StorageClient


class CustomFileWrapper(FileWrapper):

    def __init__(self, file_path, blksize=8192):
        self.file_size = os.path.getsize(file_path)
        super(CustomFileWrapper, self).__init__(open(file_path, 'rb'), blksize)


class LocalFilesystemStorageClient(StorageClient):
    """
    文件存储方案：某个文件的路径(full_name)为att/demo/test/1.png，其中att为bucket名，demo为type名，test/1.png为预期的文件路径。
               对full_name计算md5值为 b81dbb8eb01fff2d3d6fc891daac5225。
               文件存储的根目录为root_dir，则文件在服务器上的保存路径为root_dir/att/b8/1d/b81dbb8eb01fff2d3d6fc891daac5225.png。
               b8和1d目录分别为md5值最高两位和md5值次高两位。
    """

    def __init__(self, options=None):
        """
        :param options: dict
        """
        if options is None:
            options = settings.STORAGE['OPTIONS']

        self.root_dir = options['DEFAULT_STORAGE_ROOT_DIR']

    def format_real_file_name(self, bucket, file_name):
        """
        按照文件存储方案，根据声明的包含路径的文件名，给出实际存储时的包含路径的文件名。
        :param bucket: str bucket名
        :param file_name: str 包含路径的文件名
        :return: str 实际存储时的包含路径的文件名
        """
        if not isinstance(file_name, str):
            file_name = file_name.decode('utf-8')
        file_name = file_name.lstrip('/')

        name_hash = md5(os.path.join(bucket, file_name).encode('utf-8')).hexdigest()
        suffix = os.path.splitext(file_name)[1]

        return os.path.join(self.root_dir, bucket, '%s' % name_hash[:2], '%s' % name_hash[2:4],
                            '%s%s' % (name_hash, suffix))

    def create_bucket(self, name):
        """
        doc见.storage.StorageClient.create_bucket
        """
        is_valid, msg = self._check_bucket_name(name)
        if not is_valid:
            return False, msg
        else:
            name = msg

        full_name = os.path.join(self.root_dir, name)
        if not os.path.exists(full_name):
            os.makedirs(full_name, exist_ok=True)
            return True, ''
        else:
            return True, 'bucket already exist'

    def list_bucket(self):
        """
        doc见.storage.StorageClient.list_bucket
        """
        for item in os.listdir(self.root_dir):
            full_name = os.path.join(self.root_dir, item)
            if os.path.isdir(full_name):
                yield item

    def delete_bucket(self, name):
        """
        doc见.storage.StorageClient.delete_bucket
        """
        is_valid, msg = self._check_bucket_name(name)
        if not is_valid:
            return False, msg
        else:
            name = msg

        full_name = os.path.join(self.root_dir, name)
        if os.path.exists(full_name):
            try:
                os.rmdir(full_name)
            except OSError:
                return False, 'bucket %s 非空，删除bucket内部文件后再试。' % name
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
        full_name = self.format_real_file_name(bucket, file_name)

        # 如果父目录不存在，则创建
        parent_folder = os.path.dirname(full_name)
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder, exist_ok=True)

        file_md5 = md5()
        with open(full_name, 'wb') as des:
            if isinstance(file, str):
                with open(file, 'rb') as src:
                    data = src.read()
                    file_md5.update(data)
                    des.write(data)

            else:
                data = file.read()
                file_md5.update(data)
                des.write(data)

        return True, '', file_md5.hexdigest()

    def delete_file(self, bucket, file_name):
        """
        doc见.storage.StorageClient.delete_file
        """
        is_valid, msg = self._check_bucket_name(bucket)
        if not is_valid:
            return False, msg
        else:
            bucket = msg

        full_name = self.format_real_file_name(bucket, file_name)

        if os.path.exists(full_name):
            os.remove(full_name)

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

        full_name = self.format_real_file_name(bucket, file_name)

        return True, CustomFileWrapper(full_name), os.path.getsize(full_name)

    def batch_delete_file(self, bucket, file_list):
        """
        批量删除文件
        doc见.storage.StorageClient.batch_delete_file
        """
        return super().batch_delete_file(bucket, file_list)
