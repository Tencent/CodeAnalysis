# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""codeLint的db模块
"""

import json
import uuid

from django.core.cache import cache
from django.db import models

from apps.base.basemodel import CDBaseModel, utcnow
from apps.codeproj.models import Project, Scan


class LintScan(models.Model):
    """CodeLint的Scan表"""
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE)
    issue_open_num = models.IntegerField(verbose_name="新增缺陷数", blank=True, null=True)
    issue_fix_num = models.IntegerField(verbose_name="修复缺陷数", blank=True, null=True)
    active_issue_num = models.IntegerField(verbose_name="所有未解决的缺陷数量", blank=True, null=True)
    issue_detail_num = models.IntegerField(verbose_name="问题详情数量", blank=True, null=True)
    author_num = models.IntegerField(verbose_name="发现问题的人数", blank=True, null=True)
    active_severity_detail = models.CharField(max_length=512, verbose_name="严重级别详情", blank=True, null=True)
    active_category_detail = models.CharField(max_length=512, verbose_name="类别详情", blank=True, null=True)
    total_state_detail = models.CharField(max_length=512, verbose_name="状态详情", blank=True, null=True)
    total_severity_detail = models.CharField(max_length=512, verbose_name="严重级别详情", blank=True, null=True)
    total_category_detail = models.CharField(max_length=512, verbose_name="类别详情", blank=True, null=True)
    scan_summary = models.TextField(verbose_name="本次扫描总结报告", blank=True, null=True)
    total_summary = models.TextField(verbose_name="累计总结报告", blank=True, null=True)

    @property
    def active_severity_detail_dict(self):
        return json.loads(self.active_severity_detail or "{}")

    @property
    def active_category_detail_dict(self):
        return json.loads(self.active_category_detail or "{}")

    @property
    def total_state_detail_dict(self):
        return json.loads(self.total_state_detail or "{}")

    @property
    def total_severity_detail_dict(self):
        return json.loads(self.total_severity_detail or "{}")

    @property
    def total_category_detail_dict(self):
        return json.loads(self.total_category_detail or "{}")

    @property
    def scan_summary_dict(self):
        return json.loads(self.scan_summary or "{}")

    @property
    def total_summary_dict(self):
        return json.loads(self.total_summary or "{}")


class CheckToolScan(models.Model):
    """代码扫描 - 工具数据
    """
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=64, help_text="工具名称")
    issue_open_num = models.IntegerField(help_text="工具本次扫描新发现的问题数", blank=True, null=True)
    issue_fix_num = models.IntegerField(help_text="工具本次扫描关闭的问题数", blank=True, null=True)
    active_severity_detail = models.TextField(help_text="本次工具新发现不同级别的问题数", blank=True, null=True)
    total_state_detail = models.TextField(help_text="工具发现的问题状态详情", blank=True, null=True)
    total_severity_detail = models.TextField(help_text="本次工具发现不同级别的问题数", blank=True, null=True)
    author_issue_detail = models.TextField(help_text="本次工具问题的负责人分布情况", blank=True, null=True)

    class Meta:
        unique_together = ("scan", "name")

    @property
    def active_severity_detail_dict(self):
        return json.loads(self.active_severity_detail or "{}")

    @property
    def total_state_detail_dict(self):
        return json.loads(self.total_state_detail or "{}")

    @property
    def total_severity_detail_dict(self):
        return json.loads(self.total_severity_detail or "{}")

    @property
    def author_issue_detail_dict(self):
        return json.loads(self.author_issue_detail or "{}")


class Issue(CDBaseModel):
    """静态代码扫描发现的问题列表
    """

    class Meta:
        index_together = (
            ("id", "project"),
            ("project", "file_hash"),
            ("project", "ci_time"),
            ("project", "state", "ci_time"),
            ("project", "state", "resolution"),
            ("project", "state", "author"),
            ("project", "state", "severity", "ci_time"),
            ("project", "checktool_name"),
            ("checkrule_display_name", "resolution"),
            ("checkrule_gid", "state"),
        )

    class StateEnum(object):
        ACTIVE = 1
        RESOLVED = 2
        CLOSED = 3

    class ResolutionEnum(object):
        DONOTHING = 0
        FIXED = 1
        WONTFIX = 2
        INVALID = 3
        FILTER = 4
        BLACKLIST = 5
        RULEREMOVE = 6
        HISTORY = 7
        COMMENTIGNORE = 8

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

    STATE_ENG_CHOICES_DICT = dict(STATE_ENG_CHOICES)

    RESOLUTION_CHOICES = (
        (ResolutionEnum.DONOTHING, "无"),
        (ResolutionEnum.FIXED, "修复"),
        (ResolutionEnum.WONTFIX, "无须修复"),
        (ResolutionEnum.INVALID, "误报"),
        (ResolutionEnum.FILTER, "重复单过滤"),
        (ResolutionEnum.BLACKLIST, "路径过滤"),
        (ResolutionEnum.RULEREMOVE, "规则移除"),
        (ResolutionEnum.HISTORY, "历史问题"),
        (ResolutionEnum.COMMENTIGNORE, "注释忽略"),
    )

    RESOLUTION_CHOICES_DICT = dict(RESOLUTION_CHOICES)

    class CategoryEnum(object):
        CORRECTNESS = 1
        SECURITY = 2
        PERFORMANCE = 3
        USABILITY = 4
        ACCESSIBILITY = 5
        I18N = 6
        CONVENTION = 7
        OTHER = 8

    CATEGORY_CHOICES = (
        (CategoryEnum.CORRECTNESS, "功能"),
        (CategoryEnum.SECURITY, "安全"),
        (CategoryEnum.PERFORMANCE, "性能"),
        (CategoryEnum.USABILITY, "可用性"),
        (CategoryEnum.ACCESSIBILITY, "无障碍化"),
        (CategoryEnum.I18N, "国际化"),
        (CategoryEnum.CONVENTION, "代码风格"),
        (CategoryEnum.OTHER, "其他")
    )

    CATEGORY_CHOICES_DICT = dict(CATEGORY_CHOICES)

    CATEGORY_ENG_CHOICES = (
        (CategoryEnum.CORRECTNESS, "correctness"),
        (CategoryEnum.SECURITY, "security"),
        (CategoryEnum.PERFORMANCE, "performance"),
        (CategoryEnum.USABILITY, "usability"),
        (CategoryEnum.ACCESSIBILITY, "accessibility"),
        (CategoryEnum.I18N, "i18n"),
        (CategoryEnum.CONVENTION, "convention"),
        (CategoryEnum.OTHER, "other")
    )

    CATEGORY_ENG_CHOICES_DICT = dict(CATEGORY_ENG_CHOICES)

    # 优先级选项
    class SeverityEnum(object):
        FATAL = 1
        ERROR = 2
        WARNING = 3
        INFO = 4

    SEVERITY_CHOICES = (
        (SeverityEnum.FATAL, "致命"),
        (SeverityEnum.ERROR, "错误"),
        (SeverityEnum.WARNING, "警告"),
        (SeverityEnum.INFO, "提示")
    )

    SEVERITY_CHOICES_DICT = dict(SEVERITY_CHOICES)

    SEVERITY_ENG_CHOICES = (
        (SeverityEnum.FATAL, "fatal"),
        (SeverityEnum.ERROR, "error"),
        (SeverityEnum.WARNING, "warning"),
        (SeverityEnum.INFO, "info")
    )

    SEVERITY_ENG_CHOICES_DICT = dict(SEVERITY_ENG_CHOICES)

    g_issue_hash = models.CharField(max_length=40, verbose_name="全局hash值", blank=True, null=True)
    issue_hash = models.CharField(max_length=40, verbose_name="hash值", unique=True)
    o_issue_hash = models.CharField(max_length=40, verbose_name="旧版hash值", blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file_path = models.CharField(verbose_name="所属文件", max_length=512)
    file_hash = models.CharField(max_length=40, verbose_name="所在文件hash值", null=True)
    scm_url = models.CharField(max_length=512, verbose_name="子库代码库地址")
    real_file_path = models.CharField(verbose_name="子库文件路径", max_length=512)
    checkrule_gid = models.IntegerField(verbose_name="规则id", null=True, blank=True)
    checkrule_real_name = models.CharField(max_length=254, verbose_name="工具使用名称")
    checkrule_display_name = models.CharField(max_length=254, verbose_name="规则显示名称", blank=True, null=True)
    checkrule_rule_title = models.CharField(max_length=254, verbose_name="规则详情", blank=True, null=True)
    checktool_name = models.CharField(max_length=64, verbose_name="工具名称")
    category = models.IntegerField(choices=CATEGORY_CHOICES, verbose_name="规则类别", default=CategoryEnum.OTHER)
    msg = models.CharField(max_length=512, verbose_name="问题描述")
    state = models.IntegerField(db_index=True, choices=STATE_CHOICES, verbose_name="状态")
    resolution = models.IntegerField(choices=RESOLUTION_CHOICES, blank=True, null=True, verbose_name="解决方法")
    author = models.CharField(max_length=256, verbose_name="责任人", null=True)
    scan_open = models.ForeignKey(Scan, related_name="scan_open", null=True, verbose_name="发现扫描",
                                  on_delete=models.CASCADE)
    scan_fix = models.ForeignKey(Scan, related_name="scan_fix", null=True, verbose_name="关闭扫描",
                                 on_delete=models.CASCADE)
    scan_revision = models.CharField(max_length=64, verbose_name="扫描版本号", null=True)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, verbose_name="严重级别", default=SeverityEnum.INFO)
    language = models.CharField(max_length=64, verbose_name="文件所属的代码语言", null=True, blank=True)
    revision = models.CharField(max_length=64, verbose_name="问题引入的版本号", blank=True)
    ci_time = models.DateTimeField(blank=True, null=True, db_index=True)  # 问题引入的时间
    file_owners = models.CharField(max_length=256, verbose_name="文件负责人，多个时使用英文分号';'分隔",
                                   null=True, blank=True)
    fixed_time = models.DateTimeField(null=True)

    # tapd相关字段，可以为空
    tapd_ws_id = models.IntegerField(verbose_name="tapd项目id", blank=True, null=True, db_index=True)
    tapd_bug_id = models.CharField(max_length=32, blank=True, null=True, db_index=True)

    # 覆盖CDBaseModel的字段，去除索引
    modified_time = models.DateTimeField(default=utcnow, verbose_name="最近修改时间")


class IssueComment(models.Model):
    project_id = models.IntegerField(verbose_name="项目编号", null=True, blank=True)
    issue_id = models.IntegerField(verbose_name="issue编号，不使用外键，以防止被删除后无记录")
    issue_hash = models.CharField(max_length=128, verbose_name="问题标记值", db_index=True, blank=True, null=True)
    action = models.CharField(max_length=128, verbose_name="执行操作")
    message = models.CharField(max_length=512, verbose_name="执行信息", blank=True, null=True)

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    creator = models.CharField(max_length=64, verbose_name="创建人")


class BaseIgnoreIssue(CDBaseModel):
    """用户忽略的issue
    """
    class Meta:
        abstract = True

    class ScopeEnum:
        """范围
        """
        PROJECT = 1
        REPO = 2

    SCOPEENUM_CHOICES = (
        (ScopeEnum.PROJECT, "项目级别"),
        (ScopeEnum.REPO, "代码库级别")
    )

    SCOPEENUM_CHOICES_DICT = dict(SCOPEENUM_CHOICES)
    issue = models.ForeignKey(Issue, verbose_name="关联issue", on_delete=models.SET_NULL,
                              blank=True, null=True, db_constraint=False)
    issue_hash = models.CharField(max_length=128, verbose_name="问题标记值", db_index=True, blank=True, null=True)
    g_issue_hash = models.CharField(max_length=128, verbose_name="全局hash值", blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True)
    scope = models.IntegerField(default=ScopeEnum.PROJECT, verbose_name="影响范围，默认为项目级别")
    ext_field = models.JSONField(verbose_name="扩展字段", null=True, blank=True)


class InvalidIssue(BaseIgnoreIssue):
    """用户标记为误报的issue
    """
    pass


class WontFixIssue(BaseIgnoreIssue):
    """用户标记为无需处理的issue
    """
    pass


class IssueDetail(CDBaseModel):
    """Issue的详细信息
    """
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True)
    issue_hash = models.CharField(db_index=True, max_length=40, verbose_name="hash值", null=True)
    issuedetail_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.CharField(max_length=256, verbose_name="责任人", null=True)
    line = models.IntegerField(verbose_name="行号")
    column = models.IntegerField(verbose_name="列号", blank=True, null=True)
    scan_revision = models.CharField(max_length=64, verbose_name="问题当前版本")
    real_revision = models.CharField(max_length=64, verbose_name="问题代码子库版本")
    is_latest = models.BooleanField(default=True, verbose_name="是否为最近一次扫描")

    # 覆盖CDBaseModel的字段，去除索引
    created_time = models.DateTimeField(default=utcnow, verbose_name="最近修改时间")
    modified_time = models.DateTimeField(default=utcnow, verbose_name="最近修改时间")

    @property
    def issue_info(self):
        """IssueDetail所属的Issue信息
        """
        key = "issue-%s" % self.issue_hash
        if cache.get(key):
            return cache.get(key)
        else:
            issue = Issue.everything.filter(issue_hash=self.issue_hash).first()
            cache.set(key, issue, timeout=60)
            return issue


class IssueRefer(CDBaseModel):
    """Issue的参考信息，issue产生的路径
    """
    project_id = models.IntegerField(verbose_name="项目编号", null=True, blank=True)
    issuedetail_uuid = models.UUIDField(verbose_name="issuedetail uuid hex", null=True, db_index=True)
    issue_hash = models.CharField(db_index=True, max_length=40, verbose_name="hash值", null=True)
    file_path = models.CharField(verbose_name="产生issue的文件路径", max_length=512)
    line = models.IntegerField(verbose_name="行号")
    column = models.IntegerField(verbose_name="列号", null=True)
    msg = models.CharField(max_length=512, verbose_name="问题描述")
    seq = models.IntegerField(verbose_name="issue发生的原因序号")


class PackageRuleMap(models.Model):
    """规则包与规则映射
    """
    checkpackage_gid = models.IntegerField(verbose_name="规则包编号")
    checkrule_gid = models.IntegerField(verbose_name="规则编号")

    class Meta:
        unique_together = ("checkpackage_gid", "checkrule_gid")
