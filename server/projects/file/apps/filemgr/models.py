# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
文件管理 模型模块
"""

from django.db import models

from apps.base.dynamic_models import AppShardMixin


class AppUnit(models.Model):
    """
    # 以app/type作为一个唯一的存储单元，其中app对应的是COS的bucket
    """

    PERMISSIONS = (
        ("",   "没有权限"),
        ("r",  "只读权限"),
        ("rw", "读写权限"),
    )

    name = models.CharField(max_length=200, unique=True, help_text="app/type，小写字母")
    bucket = models.CharField(max_length=40, db_index=True, help_text="COS bucket")
    creator = models.CharField(max_length=30, help_text="创建人")
    create_time = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    modify_time = models.DateTimeField(auto_now=True, help_text="更新时间")
    expired = models.IntegerField(default=7, help_text="该单元下文件保存期限")
    ext_fields = models.JSONField(help_text="扩展字段", null=True, blank=True)
    other_permission = models.CharField(
        default="", max_length=2, choices=PERMISSIONS, help_text="其他用户是否有可写权限")

    class Meta:
        db_table = "t_app_unit"


class File(models.Model, AppShardMixin):
    unit = models.ForeignKey(AppUnit, null=True, on_delete=models.SET_NULL, db_constraint=False)
    name = models.CharField(max_length=255, help_text="文件名或目录名，只包含当前级")
    full_name = models.CharField(max_length=2048, help_text="上传文件名，包含app/type")
    name_hash = models.CharField(max_length=255, db_index=True, help_text="文件全路径的hash值")
    content_md5 = models.CharField(max_length=128, help_text="文件MD5值", null=True, blank=True)
    content_sha256 = models.CharField(max_length=128, help_text="文件sha256值", null=True, blank=True)
    parent_id = models.IntegerField(help_text="父目录编号", null=True, blank=True)
    creator = models.CharField(max_length=30, help_text="最终的上传者，要查看历史可见FileLog")
    create_time = models.DateTimeField(auto_now_add=True, help_text="上传时间")
    modify_time = models.DateTimeField(auto_now=True, help_text="更新时间")
    remote_saved = models.BooleanField(default=False, help_text="是否已经保存在远程服务器", null=True, blank=True)
    is_file = models.BooleanField(default=True, help_text="是否为文件，不是则为目录")
    ext_fields = models.JSONField(help_text="扩展字段", null=True, blank=True)

    class Meta:
        unique_together = (
            ("parent_id", "name"),
        )
        db_table = "t_file"
        abstract = True


class FileLog(models.Model, AppShardMixin):
    """文件操作日志
    按App分表存储，定期删除超过30天的日志
    """

    class ActionTypeEnum:
        GET = 'get'
        PUT = 'put'
        DELETE = 'delete'

    ACTION_TYPE = (
        (ActionTypeEnum.GET, "下载文件"),
        (ActionTypeEnum.PUT, "上传文件"),
        (ActionTypeEnum.DELETE, "删除文件"),
    )

    ACTION_TYPE_DICT = dict(ACTION_TYPE)

    unit = models.ForeignKey(AppUnit, null=True, on_delete=models.SET_NULL, db_constraint=False)
    full_name = models.CharField(max_length=2048, help_text="文件全名，等同于file.name，冗余数据便于查看")
    action = models.CharField(max_length=20, choices=ACTION_TYPE, help_text="文件操作类型")
    creator = models.CharField(max_length=30, help_text="操作人")
    create_time = models.DateTimeField(auto_now_add=True, help_text="操作时间")
    source_ip = models.CharField(max_length=256, help_text="请求源IP")
    ext_fields = models.JSONField(help_text="扩展字段", null=True, blank=True)

    class Meta:
        db_table = "t_file_log"
        abstract = True
