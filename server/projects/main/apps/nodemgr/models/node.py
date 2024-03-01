# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - node model
"""

# 第三方 import
from django.db import models

# 项目内 import
from apps.base.models import CDBaseModel
from apps.authen.models import Organization
from apps.nodemgr.models.tag import ExecTag
from apps.scan_conf.models import CheckTool, Process


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
                            related_name="nodes")
    executor_num = models.IntegerField(verbose_name="执行器数", default=1)
    executor_used_num = models.IntegerField(verbose_name="已被使用的执行器数", default=0)
    state = models.IntegerField(verbose_name="状态", choices=State_CHOICES, default=0)
    uuid = models.CharField(verbose_name="节点唯一标志", max_length=64, unique=True)
    manager = models.ForeignKey("auth.User", verbose_name="节点管理员", blank=True, null=True, related_name="+",
                                on_delete=models.SET_NULL)
    related_managers = models.ManyToManyField("auth.User", blank=True, related_name="related_managers",
                                              verbose_name="节点关注人员列表")
    org_sid = models.CharField(verbose_name="组织编号", max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def org_info(self):
        """团队信息
        """
        if self.org_sid:
            return Organization.objects.filter(org_sid=self.org_sid).first()
        else:
            return None

    def query_executor(self, occupy=False):
        if self.enabled != self.EnabledEnum.ACTIVE or self.executor_used_num >= self.executor_num:
            return False
        else:
            if occupy:
                self.executor_used_num += 1
                self.save()
            return True

    def free_executor(self):
        self.executor_used_num = self.executor_used_num - 1 if self.executor_used_num > 0 else 0
        self.save()

    def check_user_admin_permission(self, user):
        """检查指定用户是否有节点管理权限
        """
        if user == self.manager or user in self.related_managers.all():
            return True
        else:
            return False


class NodeToolProcessRelation(models.Model):
    """
    节点工具进程关联表
    """
    node = models.ForeignKey(Node, verbose_name="节点", on_delete=models.CASCADE)
    checktool = models.ForeignKey(CheckTool, verbose_name="工具", on_delete=models.CASCADE)
    process = models.ForeignKey(Process, verbose_name="进程", on_delete=models.CASCADE)


class NodeStatus(models.Model):
    """
    节点状态表
    """
    node = models.ForeignKey(Node, verbose_name="节点名称", on_delete=models.CASCADE)
    cpu_num = models.IntegerField(verbose_name="CPU数量", default=0)
    cpu_usage = models.IntegerField(verbose_name="CPU使用率", default=0)
    mem_space = models.BigIntegerField(verbose_name="内存空间", default=0)
    mem_free_space = models.BigIntegerField(verbose_name="内存可用空间", default=0)
    hdrive_space = models.BigIntegerField(verbose_name="磁盘空间", default=0)
    hdrive_free_space = models.BigIntegerField(verbose_name="磁盘可用空间", default=0)
    network_latency = models.BigIntegerField(verbose_name="网络延迟", default=0)
    timestamp = models.DateTimeField(verbose_name="记录时间", auto_now=True)
    os = models.CharField(verbose_name="操作系统", max_length=128)
