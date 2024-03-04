# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - rule models
"""
# 第三方
from django.db import models

# 项目内
from apps.scan_conf.models.base import Language, Label
from apps.scan_conf.models.tool import CheckTool
from apps.base.basemodel import CDBaseModel


class CheckRule(CDBaseModel):
    """规则表
    """

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
        (CategoryEnum.CORRECTNESS, '功能'),
        (CategoryEnum.SECURITY, '安全'),
        (CategoryEnum.PERFORMANCE, '性能'),
        (CategoryEnum.USABILITY, '可用性'),
        (CategoryEnum.ACCESSIBILITY, '无障碍化'),
        (CategoryEnum.I18N, '国际化'),
        (CategoryEnum.CONVENTION, '代码风格'),
        (CategoryEnum.OTHER, '其他')
    )

    CATEGORY_ENG_CHOICES = (
        (CategoryEnum.CORRECTNESS, 'correctness'),
        (CategoryEnum.SECURITY, 'security'),
        (CategoryEnum.PERFORMANCE, 'performance'),
        (CategoryEnum.USABILITY, 'usability'),
        (CategoryEnum.ACCESSIBILITY, 'accessibility'),
        (CategoryEnum.I18N, 'i18n'),
        (CategoryEnum.CONVENTION, 'convention'),
        (CategoryEnum.OTHER, 'other')
    )

    # 优先级选项
    class SeverityEnum(object):
        FATAL = 1
        ERROR = 2
        WARNING = 3
        INFO = 4

    SEVERITY_CHOICES = (
        (SeverityEnum.FATAL, '致命'),
        (SeverityEnum.ERROR, '错误'),
        (SeverityEnum.WARNING, '警告'),
        (SeverityEnum.INFO, '提示')
    )

    SEVERITY_ENG_CHOICES = (
        (SeverityEnum.FATAL, 'fatal'),
        (SeverityEnum.ERROR, 'error'),
        (SeverityEnum.WARNING, 'warning'),
        (SeverityEnum.INFO, 'info')
    )

    class SelectStateTypeEnum:
        UNSELECT = 0  # 未选中
        CUSTOMSELECT = 1  # 自定义包规则已选中
        OFFICIALSELECT = 2  # 官方包规则已选中

    checktool = models.ForeignKey(CheckTool, null=True, blank=True, on_delete=models.CASCADE, help_text='分析工具')
    display_name = models.CharField(max_length=64, help_text='规则展示名称')
    real_name = models.CharField(max_length=128, help_text='规则真实名称')
    rule_title = models.CharField(max_length=512, null=True, blank=True, help_text='规则标题')
    category = models.IntegerField(choices=CATEGORY_CHOICES, blank=True, null=True,
                                   default=CategoryEnum.OTHER, help_text='规则类别')
    severity = models.IntegerField(choices=SEVERITY_CHOICES, blank=True, null=True,
                                   default=SeverityEnum.INFO, help_text='严重级别')
    rule_params = models.TextField(null=True, blank=True, help_text='规则参数')
    custom = models.BooleanField(default=False, blank=True, help_text='是否为自定义规则')
    disable = models.BooleanField(default=False, blank=True, help_text='规则失效')
    disabled_time = models.DateTimeField(blank=True, null=True)
    disabled_reason = models.CharField(max_length=64, blank=True, null=True, help_text='失效原因')
    owner = models.CharField(max_length=32, blank=True, null=True, help_text='规则负责人')
    solution = models.TextField(blank=True, null=True, help_text='解决方法')
    labels = models.ManyToManyField(Label, help_text='标签')
    languages = models.ManyToManyField(Language, help_text='适用语言')
    tool_key = models.CharField(max_length=64, null=True, help_text="工具key值, org_'<org_id>'")

    def __str__(self):
        return "%s" % self.display_name

    class Meta:
        unique_together = ('checktool', 'real_name')


class CheckRuleDesc(models.Model):
    """规则详细描述表
    """

    class Desctype(object):
        PLAIN = 0
        MARKDOWN = 1

    DESCTYPE = (
        (Desctype.PLAIN, '无格式'),
        (Desctype.MARKDOWN, 'markdown'),
    )

    checkrule = models.OneToOneField(CheckRule, on_delete=models.CASCADE, help_text='规则')
    desc_type = models.IntegerField(choices=DESCTYPE, help_text='规则描述类型')
    desc = models.TextField(blank=True, null=True, help_text='规则详细描述')
