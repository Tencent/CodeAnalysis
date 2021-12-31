# -*- coding: utf-8 -*-
"""
file_storage
根据settings配置初始化client
"""

from django.conf import settings

from .local_storage import LocalFilesystemStorageClient
from .qcloud_cos import TencentCosStorageClient
from .minio import MinioStorageClient


def get_storage_class(client_mode=None):
    if client_mode is None:
        client_mode = settings.STORAGE['CLIENT']
    storage_cls_dict = {
        "LOCAL": LocalFilesystemStorageClient,
        "COS": TencentCosStorageClient,
        "MINIO": MinioStorageClient
    }
    return storage_cls_dict.get(client_mode, LocalFilesystemStorageClient)


storage_client = get_storage_class()(settings.STORAGE['OPTIONS'])
