# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - duplicate models
"""
from django.db import models

from apps.base.basemodel import CDBaseModel
from apps.codeproj.models import Project, Scan


class DuplicateScan(models.Model):
    """重复代码扫描
    """
    scan = models.OneToOneField(Scan, verbose_name="扫描记录", on_delete=models.CASCADE)
    last_revision = models.CharField(max_length=256, verbose_name="旧版本号", blank=True, null=True)
    duplicate_file_count = models.IntegerField(verbose_name="重复文件数", blank=True, null=True)
    duplicate_block_count = models.IntegerField(verbose_name="重复块数", blank=True, null=True)
    duplicate_line_count = models.IntegerField(verbose_name="重复行数", blank=True, null=True)
    diff_duplicate_block_count = models.IntegerField(verbose_name="差异重复块数", blank=True, null=True)
    diff_duplicate_line_count = models.IntegerField(verbose_name="差异重复行数", blank=True, null=True)
    close_issue_count = models.IntegerField(verbose_name="关闭历史issue数", blank=True, null=True)
    new_issue_count = models.IntegerField(verbose_name="新增issue数", blank=True, null=True)
    reopen_issue_count = models.IntegerField(verbose_name="重新打开issue数", blank=True, null=True)
    ignored_issue_count = models.IntegerField(verbose_name="入库忽略issue数", blank=True, null=True)
    duplicate_rate = models.FloatField(verbose_name="重复率", blank=True, null=True)
    default_summary = models.TextField(verbose_name="默认标准的总结", null=True, blank=True)
    custom_summary = models.TextField(verbose_name="自定义标准的总结", null=True, blank=True)
    unique_duplicate_line_count = models.IntegerField(verbose_name="上报数据去重后的重复行数", blank=True, null=True)
    total_duplicate_line_count = models.IntegerField(verbose_name="项目总的去重后的重复行数", blank=True, null=True)
    total_line_count = models.IntegerField(verbose_name="项目总的代码行数", blank=True, null=True)


class DuplicateIssue(CDBaseModel):
    """重复代码问题
    """

    class StateEnum(object):
        ACTIVE = 1
        IGNORED = 2
        CLOSED = 3

    STATE_CHOICES = (
        (StateEnum.ACTIVE, "未处理"),
        (StateEnum.IGNORED, "可忽略"),
        (StateEnum.CLOSED, "关闭"))

    STATE_CHOICES_DICT = dict(STATE_CHOICES)

    issue_hash = models.CharField(max_length=128, verbose_name="Issue Hash")
    state = models.IntegerField(choices=STATE_CHOICES, verbose_name="状态",
                                default=StateEnum.ACTIVE)
    owner = models.CharField(max_length=128, verbose_name="责任人", null=True, blank=True)
    project = models.ForeignKey(Project, verbose_name="项目名称", on_delete=models.CASCADE)
    dir_path = models.CharField(max_length=512, verbose_name="目录路径")
    file_name = models.CharField(max_length=512, verbose_name="文件名")
    file_path = models.CharField(max_length=1024, verbose_name="文件路径")


class DuplicateIssueComment(models.Model):
    """重复代码问题评论
    """
    project_id = models.IntegerField(verbose_name="项目 id", null=True, blank=True)
    issue_id = models.IntegerField(verbose_name="issue id")
    action = models.CharField(max_length=128, verbose_name="操作")
    message = models.CharField(max_length=512, verbose_name="信息", null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    creator = models.CharField(max_length=64, verbose_name="创建人")


class DuplicateFile(CDBaseModel):
    """重复代码文件
    """

    class ChangeTypeEnum(object):
        ADDED = "add"
        DELETED = "del"
        MODIFIED = "mod"

    CHANGE_TYPE_CHOICES = (
        (ChangeTypeEnum.ADDED, "新增"),
        (ChangeTypeEnum.DELETED, "删除"),
        (ChangeTypeEnum.MODIFIED, "修改"))
    project = models.ForeignKey(Project, verbose_name="项目名称", blank=True, null=True,
                                on_delete=models.CASCADE)
    issue = models.ForeignKey(DuplicateIssue, verbose_name="缺陷单", blank=True, null=True,
                              on_delete=models.CASCADE)
    issue_hash = models.CharField(max_length=128, verbose_name="Issue Hash", blank=True, null=True)
    scan = models.ForeignKey(DuplicateScan, verbose_name="扫描记录", on_delete=models.CASCADE)
    dir_path = models.CharField(max_length=512, verbose_name="目录路径")
    file_name = models.CharField(max_length=512, verbose_name="文件名")
    file_path = models.CharField(max_length=1024, verbose_name="文件路径")
    duplicate_rate = models.FloatField(verbose_name="重复率")
    total_line_count = models.IntegerField(verbose_name="总行数")
    total_duplicate_line_count = models.IntegerField(verbose_name="总重复行数")
    distinct_hash_num = models.IntegerField(verbose_name="重复代码块数（去重）", blank=True, null=True)
    block_num = models.IntegerField(verbose_name="重复代码块数")
    last_modifier = models.CharField(max_length=128, verbose_name="最近修改人", blank=True, null=True)
    change_type = models.CharField(max_length=64, choices=CHANGE_TYPE_CHOICES, verbose_name="更改类型", blank=True,
                                   null=True)
    scm_revision = models.CharField(max_length=512, verbose_name="版本号", null=True, blank=True)
    is_latest = models.BooleanField(verbose_name="是否最新", default=True, blank=True)

    @property
    def sorted_block_set(self):
        return self.duplicateblock_set.order_by("start_line_num")


class DuplicateBlock(models.Model):
    """重复代码文件块
    """

    class ChangeTypeEnum(object):
        ADDED = "add"
        DELETED = "del"
        MODIFIED = "mod"

    CHANGE_TYPE_CHOICES = (
        (ChangeTypeEnum.ADDED, "新增"),
        (ChangeTypeEnum.DELETED, "删除"),
        (ChangeTypeEnum.MODIFIED, "修改"))
    project_id = models.IntegerField(verbose_name="项目 id", blank=True, null=True)
    scan_id = models.IntegerField(verbose_name="扫描 id", blank=True, null=True)
    duplicate_file = models.ForeignKey(DuplicateFile, verbose_name="代码文件", on_delete=models.CASCADE)
    block_hash = models.CharField(max_length=512, verbose_name="区块标识", blank=True, null=True)
    token_num = models.IntegerField(verbose_name="代码块长度")
    duplicate_times = models.IntegerField(verbose_name="重复次数")
    duplicate_rate = models.FloatField(verbose_name="重复占比")
    start_line_num = models.IntegerField(verbose_name="起始行号")
    end_line_num = models.IntegerField(verbose_name="结束行号")
    duplicate_line_count = models.IntegerField(verbose_name="重复行数")
    last_modifier = models.CharField(max_length=128, verbose_name="最近修改人", blank=True, null=True)
    change_type = models.CharField(max_length=64, choices=CHANGE_TYPE_CHOICES, verbose_name="更改类型", blank=True,
                                   null=True)
    related_modifiers = models.CharField(max_length=512, verbose_name="代码相关人", null=True, blank=True)
