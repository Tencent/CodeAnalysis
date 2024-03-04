# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
文件管理 权限模块
"""

from django.db import IntegrityError

from apps.filemgr import models
from apps.filemgr.utils import format_file

from utils import error


class PermissionCheckMixIn(object):
    """
    # 提供文件上传读写的一系列检测，包括URL格式检测，bucket检测，权限检测，文件存在检测
    """

    def _format_file_response(self, uri):
        """
        根据请求uri，解析出对应的bucket，dir_path和file_name。或者直接返回错误响应
        :param uri: str
        :return tuple(bucket, dir_path, file_name) 正确时返回解析结果，错误时抛 QFSRequestError 异常
        """
        return format_file(uri)

    def _format_app_unit_response(self, app, dir_path):
        """
        根据app和dir_path获取对应的app_unit记录，如果没有则返回错误响应
        :return: app_unit 正确时返回app_unit，错误时抛 QFSRequestError 异常
        """
        app_unit = None
        try:
            app_unit, _ = models.AppUnit.objects.get_or_create(name='%s/%s' % (app, dir_path))
        except models.AppUnit.DoesNotExist:
            raise error.QFSRequestError('当前文件不存在', error.BUCKET_NOT_EXIST)
        except IntegrityError:
            # 防止并发竞争，在name上增加唯一索引
            pass
        return app_unit

    def _format_user_permission_response(self, app_unit, username, permissions):
        """
        检查用户对于某个app_unit是否具有指定的权限，如果不具备则直接返回错误响应
        :param app_unit: .model.AppUnit
        :param username: str user.ename
        :param permissions: list(str)
        :return: boolean 有权限时返回True，无权限时抛 QFSRequestError 异常
        """
        if not isinstance(permissions, (set, tuple, list)):
            permissions = [permissions]
        if app_unit.creator != username and app_unit.other_permission not in permissions:
            msg = '当前用户没有{}目录下的{}权限'.format(app_unit.name, '读' if 'r' in permissions else '写')
            raise error.QFSRequestError(msg, error.BUCKET_FORBIDDEN)
        return True

    def _format_file_exist_response(self, app_unit, file_name):
        """
        检查文件是否存在。如果不存在，直接返回错误响应
        :param app_unit: model.AppUnit
        :param file_name: str
        :return: boolean 文件存在时返回True，错误时抛 QFSRequestError 异常
        """
        file_model = models.File.shard(app_unit.bucket)
        try:
            file_model.objects.get(
                unit=app_unit, full_name='%s/%s' % (app_unit.name, file_name), is_file=True)
        except file_model.DoesNotExist:
            raise error.QFSRequestError('当前文件不存在', error.FILE_NOT_EXIST)
        return True
