# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - scan models
"""

from django.db import models
from django.utils import timezone

from apps.base.basemodel import CDBaseModel
from util import errcode


class Project(CDBaseModel):
    """关联Main服务的分支项目
    """

    class ScmEnum(object):
        GIT = "git"
        SVN = "svn"

    SCM_TYPE_CHOICES = (
        (ScmEnum.GIT, "Git"),
        (ScmEnum.SVN, "SVN")
    )
    id = models.BigIntegerField(primary_key=True, unique=True, verbose_name="项目全局id")
    repo_id = models.BigIntegerField(verbose_name="代码库全局id", db_index=True)
    scan_scheme_id = models.BigIntegerField(verbose_name="扫描方案全局id", null=True, blank=True)
    scm_type = models.CharField(max_length=8, choices=SCM_TYPE_CHOICES, verbose_name="代码库类型")
    scm_url = models.CharField(max_length=512, verbose_name="代码库地址")
    org_sid = models.CharField(max_length=64, verbose_name="团队编号", null=True, blank=True)
    team_name = models.CharField(max_length=64, verbose_name="项目组名称", null=True, blank=True)

    def get_scm_url(self):
        """分支信息
        """
        items = self.scm_url.split("#", 1)
        return items[0]

    def get_branch(self):
        """分支信息
        """
        items = self.scm_url.split("#", 1)
        if len(items) > 1:
            branch = items[1]
        else:
            branch = "master"
        return branch


class Scan(models.Model):
    """项目扫描列表，保存项目每次扫描的基本信息，与Main服务的Job关联
    """

    class StateEnum(object):
        WAITING = 0
        RUNNING = 1
        CLOSED = 2
        CLOSING = 3

    STATE_CHOICES = (
        (StateEnum.WAITING, "Waiting"),
        (StateEnum.RUNNING, "Running"),
        (StateEnum.CLOSED, "Closed"),
        (StateEnum.CLOSING, "Closing")
    )

    STATE_CHOICES_DICT = dict(STATE_CHOICES)

    repo_id = models.BigIntegerField(verbose_name="代码库全局id")
    state = models.IntegerField(default=StateEnum.RUNNING, choices=STATE_CHOICES, verbose_name="状态")
    project = models.ForeignKey(Project, verbose_name="产品名称", on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name="扫描创建时间", null=True, blank=True)
    scan_time = models.DateTimeField(auto_now_add=True, verbose_name="扫描起始时间")
    closing_time = models.DateTimeField(verbose_name="结果入库时间", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="扫描结束时间", null=True, blank=True)
    current_revision = models.CharField(max_length=512, verbose_name="扫描版本号", null=True, blank=True)
    scm_time = models.DateTimeField(verbose_name="扫描版本时间", null=True, blank=True)
    result_code = models.IntegerField(verbose_name="结果状态码", null=True, blank=True)
    result_msg = models.TextField(verbose_name="结果详细信息", null=True, blank=True)
    job_gid = models.IntegerField(null=True, blank=True)
    job_archived = models.BooleanField(verbose_name="job是否已归档", null=True, blank=True)
    type = models.IntegerField(verbose_name="扫描类型", null=True, blank=True)
    creator = models.CharField(max_length=128, blank=True, null=True, verbose_name="启动人")
    daily_save = models.BooleanField(default=False, verbose_name="扫描结果数据保存开关，默认为False")

    @property
    def result_code_msg(self):
        return errcode.interpret_code(self.result_code)

    @property
    def execute_time(self):
        """执行时间
        """
        if not self.scan_time:
            return None
        if self.end_time:  # 正常结束
            return self.end_time - self.scan_time
        else:  # 正在执行中
            return timezone.now().replace(microsecond=0) - self.scan_time

    @property
    def save_time(self):
        """结果保存时间
        """
        if not self.closing_time:
            return None
        if self.end_time:
            return self.end_time - self.closing_time
        else:
            return timezone.now().replace(microsecond=0) - self.closing_time

    @property
    def waiting_time(self):
        if self.scan_time and self.create_time:  # 已经启动
            return self.scan_time - self.create_time
        elif self.create_time:  # 仍在等待
            return timezone.now().replace(microsecond=0) - self.create_time
        else:
            return None
