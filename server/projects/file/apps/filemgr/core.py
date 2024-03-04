# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
文件管理 核心模块
"""
import hashlib
import logging
import os

from django.db import IntegrityError
from django.utils import timezone

from apps.filemgr import models
from utils import error
from utils.file_storage import storage_client

logger = logging.getLogger(__name__)


class FileHandler(object):

    @classmethod
    def get_source_ip(cls, request_header):
        """从请求头部获取源IP
        """
        header_keys = ["HTTP_X_REAL_IP",
                       "HTTP_CLIENT_IP",
                       "HTTP_X_FORWARDED_FOR",
                       "HTTP_X_FORWARDED",
                       "HTTP_X_CLUSTER_CLIENT_IP",
                       "HTTP_FORWARDED_FOR",
                       "HTTP_FORWARDED",
                       "REMOTE_ADDR"]
        for header in header_keys:
            ip = request_header.get(header)
            if ip:
                return ip

    @classmethod
    def get_content_md5(cls, request_header):
        """获取文件md5值
        """
        return request_header.get("HTTP_FTP_MD5") or request_header.get("HTTP_CONTENT_MD5")

    @classmethod
    def get_content_sha256(cls, request_header):
        """获取文件sha256
        """
        return request_header.get("HTTP_FTP_SHA256") or request_header.get("HTTP_CONTENT_SHA256")

    @classmethod
    def get_app_unit(cls, bucket, dir_path):
        """获取AppUnit
        """
        return models.AppUnit.objects.get(name="%s/%s" % (bucket, dir_path))

    @classmethod
    def get_file(cls, app_unit, full_name):
        """获取文件
        """
        return models.File.shard(app_unit.bucket).objects.filter(
            unit=app_unit, full_name=full_name, is_file=True).first()

    @classmethod
    def delete_file(cls, app_unit, full_name):
        """删除文件
        """
        models.File.shard(app_unit.bucket).objects.filter(
            unit=app_unit, full_name=full_name).delete()

    @classmethod
    def check_content_md5(cls, request, content_md5):
        """检查文件的md5值与请求头部md5值是否一致
        """
        header_md5 = cls.get_content_md5(request.META)
        if header_md5 == content_md5:
            return True
        else:
            return False

    @classmethod
    def save_file(cls, app_unit, full_name, username, content_md5=None, content_sha256=None):
        """存储文件
        如果是上传文件，则文件上传成功后需要新增一条File记录
        """
        file_path = full_name.split("/")
        folders = []
        new_file = None
        file_model = models.File.shard(app_unit.bucket)
        for index, seg_name in enumerate(file_path):
            is_file = (index == len(file_path) - 1)
            if not is_file and index == 0:
                # bucket那级目录都不存储
                continue

            full_path = "/".join(file_path[:index + 1])
            parent = folders and folders[-1] or None

            # 计算full_path 的md5值，需转为utf-8
            name_hash = hashlib.md5(isinstance(full_path, str) and full_path.encode(
                "utf8") or full_path).hexdigest()

            data = {"full_name": full_path, "creator": username, "name_hash": name_hash}
            try:
                new_file, is_create = file_model.objects.get_or_create(
                    unit=app_unit,
                    name=seg_name,
                    is_file=is_file,
                    parent_id=parent.id if parent else None,
                    content_md5=content_md5 if is_file else None,
                    content_sha256=content_sha256 if is_file else None,
                    defaults=data)
            except IntegrityError:
                # 防止并发竞争，在parent,name,is_file上增加组合唯一索引
                new_file = file_model.objects.get(
                    unit=app_unit, name=seg_name, is_file=is_file, parent_id=parent.id if parent else None)
                is_create = False

            if not is_file:
                # 如果是目录，则插入到目录列表中，后面批量更新
                folders.append(new_file)
            elif not is_create:
                # 如果是文件，而且是覆盖旧文件，则更新时间
                new_file.__dict__.update(data)
                new_file.save()

        now = timezone.now()
        # 批量将目录的修改时间更新，将save_unit时间更新
        if folders:
            file_model.objects.filter(id__in=[a.id for a in folders]).update(
                modify_time=now)
        app_unit.modify_time = now
        app_unit.save()
        return new_file

    @classmethod
    def execute_file_action(cls, request, bucket, dir_path, file_name):
        """
        根据请求类型执行文件操作
        """
        username = request.user.username
        full_name = "%s/%s/%s" % (bucket, dir_path, file_name)
        app_unit = cls.get_app_unit(bucket, dir_path)

        method = request.method.lower()
        content_md5 = cls.get_content_md5(request.META)
        content_sha256 = cls.get_content_md5(request.META)
        source_ip = cls.get_source_ip(request.META)

        new_file = None
        if method == "put":
            new_file = cls.save_file(app_unit, full_name, username, content_md5, content_sha256)
        elif method == "get":
            new_file = cls.get_file(app_unit, full_name)
        elif method == "delete":
            # 如果是删除或者下载，则File里一定会有记录
            models.File.shard(app_unit.bucket).objects.filter(
                unit=app_unit, full_name=full_name).delete()

        action = models.FileLog.ACTION_TYPE_DICT.get(method)
        if action:
            models.FileLog.shard(app_unit.bucket).objects.create(
                unit=app_unit, full_name=full_name, action=method,
                creator=username, source_ip=source_ip)

        return new_file


class FileUploadHandler(object):
    """文件上传处理器
    """

    @classmethod
    def create_bucket(cls, bucket, client=None):
        """创建桶
        """
        if not client:
            client = storage_client
        bucket_count = models.AppUnit.objects.filter(bucket=bucket).count()
        if bucket_count == 0:
            result, msg = client.create_bucket(bucket)
            if not (result or 'bucket already exist' in msg):
                # 如果bucket已存在，也算创建成功，否者抛出异常
                raise error.QFSRequestError(msg, error.BUCKET_CREATE_FAIL)

    @classmethod
    def check_bucket_write_permission(cls, bucket, dir_path, username):
        """检查是否有读写权限
        """
        app_unit, is_create = None, True
        try:
            app_unit, is_create = models.AppUnit.objects.get_or_create(
                name='%s/%s' % (bucket, dir_path), bucket=bucket, defaults={'creator': username})
        except IntegrityError:
            # 防止并发竞争，在name上增加唯一索引
            pass

        if (not is_create) and (app_unit.creator != username and app_unit.other_permission != 'rw'):
            # 如果是已有的app/type，先检查权限看当前用户是否可以写
            raise error.QFSUnitForbidden('当前用户没有%s/%s目录下的写权限' % (bucket, dir_path))

    @classmethod
    def save_file_to_local(cls, file_obj, bucket, dir_path, file_name):
        """保存文件到本地
        :return: is_uploaded, msg, content_md5
        """
        logger.info("[Bucket %s] saving path: %s" % (bucket, file_obj.temporary_file_path()))
        return storage_client.upload_file(bucket, '%s/%s' % (dir_path, file_name), file_obj)


class FileDownloadHandler(object):
    """文件下载处理器
    """

    @classmethod
    def check_file_exist(cls, bucket, dir_path, file_name):
        """检查文件是否上传过
        """
        full_name = '%s/%s/%s' % (bucket, dir_path, file_name)
        app_unit = FileHandler.get_app_unit(bucket, dir_path)
        return FileHandler.get_file(app_unit, full_name)

    @classmethod
    def download_from_local(cls, bucket, dir_path, file_name):
        """检查本地是否存在
        """
        local_full_path = storage_client.format_real_file_name(bucket, '%s/%s' % (dir_path, file_name))
        if os.path.exists(local_full_path):
            return storage_client.download_file(bucket, '%s/%s' % (dir_path, file_name))
        else:
            return False, None, 0
