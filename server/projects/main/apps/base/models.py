# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - models
"""

from django.db import models
from .basemodel import CDBaseModel  # 让CDBaseModel被引入


class OperationRecord(models.Model):
    scenario_key = models.CharField(max_length=128, verbose_name='场景Key',
                                    db_index=True)  # 用来表示一类操作，建议以 project_1 来表示项目相关的操作，以便前端展示使用
    action = models.CharField(max_length=128, verbose_name='操作')  # 用来表示一类操作
    message = models.TextField(verbose_name="信息", null=True, blank=True)  # 具体操作详情

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    creator = models.CharField(max_length=64, verbose_name='创建人')


class Origin(models.Model):
    name = models.CharField(max_length=64, verbose_name="渠道", primary_key=True)

    def __str__(self):
        return "%s" % self.name
