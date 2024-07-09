# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - cc models
"""
import json

from django.db import models

from apps.base.basemodel import CDBaseModel
from apps.codeproj.models import Project, Scan


class CyclomaticComplexityScan(CDBaseModel):
    """CyclomaticComplexity Scan表
    """
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE)
    last_revision = models.CharField(max_length=256, verbose_name="旧版本号", blank=True, null=True)
    diff_cc_num = models.IntegerField(verbose_name="新增的数量", null=True, blank=True)
    cc_open_num = models.IntegerField(null=True, blank=True, help_text="打开的数量")
    cc_average_of_lines = models.FloatField(null=True, blank=True, help_text="千行代码平均圈复杂度")
    cc_fix_num = models.IntegerField(default=0, help_text="修复的数量")
    worse_cc_file_num = models.IntegerField(null=True, blank=True, help_text="圈复杂度恶化的文件数据")
    min_ccn = models.IntegerField(null=True, blank=True)
    code_line_num = models.IntegerField(null=True, blank=True, help_text="扫描代码行数")
    default_summary = models.TextField(verbose_name="默认标准的总结", null=True, blank=True)
    custom_summary = models.TextField(verbose_name="自定义标准的总结", null=True, blank=True)

    @classmethod
    def get_cc_scan_with_scan(cls, scan):
        """获取指定scan关联的圈复杂度scan记录
        """
        return cls.objects.filter(scan=scan).first()

    def get_custom_summary(self):
        """获取自定义的概览
        """
        return json.loads(self.custom_summary) if self.custom_summary else {}

    def get_default_summary(self):
        """获取默认的概览
        """
        return json.loads(self.default_summary) if self.default_summary else {}

    def get_summary(self):
        """获取概览结果

        如果存在自定义概览，则优先返回自定义概览，如果不存在，则返回默认概览
        """
        custom_summary = self.get_custom_summary()
        if custom_summary:
            return custom_summary
        else:
            return self.get_default_summary()


class CyclomaticComplexityFile(CDBaseModel):
    """圈复杂度文件维度表
    """

    class ChangeTypeEnum(object):
        DEFAULT = 0
        ADDED = 1
        DELETED = 2
        MODIFIED = 3

    CHANGEDTYPE_CHOICES = (
        (ChangeTypeEnum.DEFAULT, "无变化"),
        (ChangeTypeEnum.ADDED, "新增"),
        (ChangeTypeEnum.DELETED, "删除"),
        (ChangeTypeEnum.MODIFIED, "修改")
    )

    CHANGEDTYPE_MAP = {
        "add": ChangeTypeEnum.ADDED,
        "del": ChangeTypeEnum.DELETED,
        "mod": ChangeTypeEnum.MODIFIED
    }

    class StateEnum(object):
        ACTIVE = 1
        RESOLVED = 2
        CLOSED = 3

    STATE_CHOICES = (
        (StateEnum.ACTIVE, "未处理"),
        (StateEnum.RESOLVED, "已处理"),
        (StateEnum.CLOSED, "关闭")
    )

    STATE_CHOICES_DICT = dict(STATE_CHOICES)

    STATE_ENG_CHOICES = (
        (StateEnum.ACTIVE, "active"),
        (StateEnum.RESOLVED, "resolved"),
        (StateEnum.CLOSED, "closed")
    )

    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE)
    over_func_cc = models.IntegerField(default=0, verbose_name="自定义超标方法的圈复杂度总和")
    over_cc_sum = models.IntegerField(default=0, verbose_name="文件超标方法圈复杂度超过阈值的差值之和")
    over_cc_avg = models.IntegerField(default=0, verbose_name="文件超标方法圈复杂度平均数")
    over_cc_func_count = models.IntegerField(default=0, verbose_name="文件圈复杂度超标方法个数")
    diff_over_func_cc = models.IntegerField(default=0, verbose_name="自定义超标方法的圈复杂度总和增量值")
    diff_over_cc_sum = models.IntegerField(default=0, verbose_name="文件超标方法圈复杂度超过阈值的差值之和的增量值")
    diff_over_cc_avg = models.IntegerField(default=0, verbose_name="文件超标方法圈复杂度平均数增量值")
    diff_over_cc_func_count = models.IntegerField(default=0, verbose_name="文件圈复杂度超标方法个数增量值")
    worse = models.BooleanField(default=False, verbose_name="文件圈复杂度恶化标志，True表示进一步恶化，False表示没有恶化")
    file_hash = models.CharField(max_length=64, unique=True, verbose_name="文件唯一Hash码")
    g_file_hash = models.CharField(max_length=64, db_index=True, verbose_name="文件全局Hash码", null=True, blank=True)
    file_path = models.CharField(max_length=512, verbose_name="文件路径")
    state = models.IntegerField(default=StateEnum.ACTIVE, verbose_name="问题状态，1为未处理，2为已处理，3为已关闭")
    change_type = models.IntegerField(choices=CHANGEDTYPE_CHOICES, default=0, verbose_name="圈复杂度变化情况")
    last_modifier = models.CharField(max_length=64, verbose_name="最近修改人")
    last_modifier_email = models.CharField(max_length=128, verbose_name="最近修改人邮箱", null=True, blank=True)
    related_modifiers = models.CharField(max_length=256, verbose_name="代码相关人", null=True, blank=True)
    author = models.CharField(max_length=64, verbose_name="责任人", null=True, blank=True)
    most_weight_modifier = models.CharField(max_length=64, verbose_name="最大权重修改人", null=True, blank=True)
    most_weight_modifier_email = models.CharField(max_length=128, verbose_name="最大权重修改人的邮箱", null=True, blank=True)
    weight_modifiers = models.TextField(verbose_name="权重列表", null=True, blank=True)
    scan_open = models.ForeignKey(CyclomaticComplexityScan, related_name="file_scan_open", verbose_name="发现的扫描",
                                  null=True, on_delete=models.CASCADE)
    scan_close = models.ForeignKey(CyclomaticComplexityScan, related_name="file_scan_close",
                                   verbose_name="圈复杂度降低的扫描", null=True, on_delete=models.CASCADE)
    file_owners = models.CharField(max_length=256, verbose_name="文件负责人，多个时使用英文分号';'分隔",
                                   null=True, blank=True)
    language = models.CharField(max_length=64, verbose_name="文件所属语言", null=True, blank=True)
    tapd_ws_id = models.IntegerField(verbose_name="tapd项目id", blank=True, null=True, db_index=True)
    tapd_bug_id = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    revision = models.CharField(max_length=64, verbose_name="问题引入的版本号", blank=True, null=True)
    ci_time = models.DateTimeField(verbose_name="问题引入版本号的关联时间", blank=True, null=True, db_index=True)


class CyclomaticComplexity(CDBaseModel):
    """圈复杂度问题
    """

    class ChangeTypeEnum(object):
        DEFAULT = 0
        ADDED = 1
        DELETED = 2
        MODIFIED = 3

    CHANGEDTYPE_CHOICES = (
        (ChangeTypeEnum.DEFAULT, "无"),
        (ChangeTypeEnum.ADDED, "新增"),
        (ChangeTypeEnum.DELETED, "删除"),
        (ChangeTypeEnum.MODIFIED, "修改")
    )

    CHANGEDTYPE_MAP = {
        "add": ChangeTypeEnum.ADDED,
        "del": ChangeTypeEnum.DELETED,
        "mod": ChangeTypeEnum.MODIFIED
    }

    class StatusEnum(object):
        OPEN = 1
        CLOSED = 2

    STATUS_CHOICES = (
        (StatusEnum.OPEN, "需要关注"),
        (StatusEnum.CLOSED, "无须关注")
    )

    STATUS_CHOICES_DICT = dict(STATUS_CHOICES)

    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE)
    ccn = models.IntegerField(default=0, verbose_name="圈复杂度")
    g_cc_hash = models.CharField(max_length=64, db_index=True, verbose_name="全局Hash码，废弃", null=True, blank=True)
    cc_hash = models.CharField(max_length=64, db_index=True, verbose_name="Hash码，废弃", null=True, blank=True)
    unique_cc_hash = models.CharField(max_length=64, db_index=True, verbose_name="不连续Hash码", null=True, blank=True)
    file_path = models.CharField(max_length=512, verbose_name="文件路径")
    file_hash = models.CharField(max_length=40, verbose_name="所在文件hash值", null=True, db_index=True)
    func_name = models.CharField(max_length=512, verbose_name="函数名称")
    func_param_num = models.IntegerField(default=0, verbose_name="函数参数数量")
    long_name = models.CharField(max_length=1024, verbose_name="函数名称")
    change_type = models.IntegerField(choices=CHANGEDTYPE_CHOICES, default=0, verbose_name="圈复杂度变化情况")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="状态,废弃")
    last_modifier = models.CharField(max_length=16, verbose_name="最近修改人")
    author = models.CharField(max_length=16, verbose_name="责任人", null=True, blank=True)
    related_modifiers = models.CharField(max_length=256, verbose_name="代码相关人", null=True, blank=True)
    most_weight_modifier = models.CharField(max_length=64, verbose_name="最大权重修改人", null=True, blank=True)
    most_weight_modifier_email = models.CharField(max_length=128, verbose_name="最大权重修改人的邮箱", null=True, blank=True)
    weight_modifiers = models.TextField(verbose_name="权重列表", null=True, blank=True)
    scan_open = models.ForeignKey(CyclomaticComplexityScan, related_name="scan_open", verbose_name="发现的扫描",
                                  null=True, on_delete=models.CASCADE)
    scan_close = models.ForeignKey(CyclomaticComplexityScan, related_name="scan_close",
                                   verbose_name="圈复杂度降低的扫描,废弃", null=True, on_delete=models.CASCADE)
    is_tapdbug = models.BooleanField(default=False, verbose_name="是TAPD缺陷单，废弃")
    ignore_time = models.DateTimeField(null=True, verbose_name="忽略问题时间，废弃")
    is_latest = models.BooleanField(default=False, verbose_name="是否为最近一次扫描")
    language = models.CharField(max_length=64, verbose_name="文件所属语言", null=True, blank=True)
    revision = models.CharField(max_length=64, verbose_name="版本号", blank=True)
    ci_time = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name="问题引入的时间")
    diff_ccn = models.IntegerField(verbose_name="差异圈复杂度", blank=True, null=True)
    token = models.IntegerField(verbose_name="token数", null=True, blank=True)
    line_num = models.IntegerField(verbose_name="函数行数,包含空行和函数内部注释", null=True, blank=True)
    code_line_num = models.IntegerField(verbose_name="函数代码行数", null=True, blank=True)
    start_line_no = models.IntegerField(verbose_name="起始行号", null=True, blank=True)
    end_line_no = models.IntegerField(verbose_name="结束行号", null=True, blank=True)
    scan_revision = models.CharField(max_length=64, verbose_name="扫描版本号", null=True, blank=True)


class PersonCyclomaticComplexity(CDBaseModel):
    """项目圈复杂度个人维度
    """
    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.SET_NULL, null=True)
    scan = models.ForeignKey(CyclomaticComplexityScan, verbose_name="关联扫描", on_delete=models.SET_NULL, null=True)
    author = models.CharField(max_length=128, verbose_name="负责人名称")
    author_email = models.CharField(max_length=256, verbose_name="负责人邮箱")
    over_cc_func_count = models.IntegerField(verbose_name="函数超标数量")
    over_cc_sum = models.IntegerField(verbose_name="函数超标总和")
    ext_data = models.JSONField(verbose_name="扩展数据", null=True, blank=True)

    class Meta:
        unique_together = ("project", "scan", "author")
