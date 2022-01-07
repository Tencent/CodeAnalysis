# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - tag model
"""
from django.db import models

from apps.base.basemodel import CDBaseModel


class ExecTag(models.Model):
    """
    执行标签列表，表示所有可以被执行的标签类型，用户不可修改
    """
    class TypeEnum(object):
        PUBLIC = 1
        PRIVATE = 2
        DISABLED = 99

    TYPE_CHOICES = (
        (TypeEnum.PUBLIC, "公共标签"),
        (TypeEnum.PRIVATE, "非公共标签"),
        (TypeEnum.DISABLED, "已停用标签"),
    )

    name = models.CharField(verbose_name="标签名称", max_length=64, unique=True)
    desc = models.CharField(verbose_name="描述", max_length=256, null=True, blank=True)
    public = models.BooleanField(verbose_name="是否可用", default=False)
    official = models.BooleanField(verbose_name="是否官方标签", null=True, blank=True)
    tag_type = models.IntegerField(verbose_name="标签状态", null=True, blank=True, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class Node(CDBaseModel):
    """
    节点表
    """

    class EnabledEnum(object):
        DISABLED = 0
        ACTIVE = 1
        OFFLINE = 2

    ENABLED_CHOICES = (
        (EnabledEnum.DISABLED, "Disabled"),
        (EnabledEnum.ACTIVE, "Active"),
        (EnabledEnum.OFFLINE, "Offline")
    )

    class StateEnum(object):
        FREE = 0
        BUSY = 1

    State_CHOICES = (
        (StateEnum.FREE, "Free"),
        (StateEnum.BUSY, "Busy")
    )
    name = models.CharField(verbose_name="节点名称", max_length=64, unique=True)
    addr = models.GenericIPAddressField(verbose_name="IP地址", default="0.0.0.0")
    enabled = models.IntegerField(verbose_name="是否可用", choices=ENABLED_CHOICES, default=0,
                                  help_text="置为非Active会回收正在执行的Task。")
    last_beat_time = models.DateTimeField(verbose_name="心跳时间", null=True, blank=True)
    exec_tags = models.ManyToManyField(ExecTag, blank=True, verbose_name="最大执行标签集",
                                       help_text="（可多选）节点可执行标签的最大集合。")
    # 废弃字段，待移除
    min_exec_tags = models.ManyToManyField(ExecTag, blank=True, related_name="min_exec_tags",
                                           verbose_name="最小执行标签集",
                                           help_text="（可多选）节点可执行标签的最小集合。")
    # 废弃字段，待移除
    tag = models.ForeignKey(ExecTag, on_delete=models.SET_NULL, verbose_name="唯一执行标签", null=True, blank=True,
                            related_name="nodes")  # 执行标签
    executor_num = models.IntegerField(verbose_name="执行器数", default=1)
    executor_used_num = models.IntegerField(verbose_name="已被使用的执行器数", default=0)
    state = models.IntegerField(verbose_name="状态", choices=State_CHOICES, default=0)
    uuid = models.CharField(verbose_name="节点唯一标志", max_length=64, unique=True)
    manager = models.ForeignKey("auth.User", verbose_name="节点管理员", blank=True, null=True, related_name="+",
                                on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
