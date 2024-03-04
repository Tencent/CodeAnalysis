# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - tag model
"""
from django.db import models

from apps.authen.models import Organization
from apps.base.basemodel import CDBaseModel
from apps.scan_conf.models import CheckTool, Process


class ExecTag(CDBaseModel):
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
    display_name = models.CharField(verbose_name="标签展示名称", max_length=128, null=True, blank=True)
    org_sid = models.CharField(verbose_name="组织编号", max_length=64, null=True, blank=True)
    desc = models.CharField(verbose_name="描述", max_length=256, null=True, blank=True)
    public = models.BooleanField(verbose_name="是否可用", default=False)
    official = models.BooleanField(verbose_name="是否官方标签", null=True, blank=True)
    tag_type = models.IntegerField(verbose_name="标签状态", null=True, blank=True, choices=TYPE_CHOICES)

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


class TagToolProcessRelation(models.Model):
    """
    标签工具进程关联表
    """
    tag = models.ForeignKey(ExecTag, verbose_name="标签", on_delete=models.CASCADE)
    checktool = models.ForeignKey(CheckTool, verbose_name="工具", on_delete=models.CASCADE)
    process = models.ForeignKey(Process, verbose_name="进程", on_delete=models.CASCADE)
