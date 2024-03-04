# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - config models
"""

# 原生 import
import json
import logging

# 第三方 import
from django.db import models
from django.contrib.auth.models import User

# 项目内 import
from apps.codeproj.models.base import Project, Repository, ScanScheme
from apps.base.basemodel import CDBaseModel
from apps.scan_conf.models import CheckProfile, Label as ScanConfLabel
from apps.nodemgr.models import ExecTag

logger = logging.getLogger(__name__)


class ScanSchemeTemplate(CDBaseModel):
    """扫描方案模版
    """
    name = models.CharField(max_length=128, help_text="扫描方案模版名称")
    display_name = models.CharField(max_length=128, help_text="扫描方案展示名称", null=True, blank=True)
    short_desc = models.CharField(max_length=128, help_text="扫描方案模板简短描述", null=True, blank=True)
    description = models.TextField(help_text="详细描述", null=True, blank=True)
    tag = models.ForeignKey(ExecTag, on_delete=models.SET_NULL, verbose_name="执行环境", null=True, blank=True)
    labels = models.ManyToManyField(ScanConfLabel, related_name="label_schemetemplate", help_text="标签")
    basic_conf = models.TextField(help_text="基础配置")
    lint_conf = models.TextField(help_text="扫描配置")
    metric_conf = models.TextField(help_text="度量配置")
    public = models.BooleanField(help_text="是否开放", default=False)
    hidden = models.BooleanField(help_text="是否隐藏", default=False)
    recommend = models.BooleanField(help_text="是否推荐", default=False)
    need_compile = models.BooleanField(help_text="是否依赖编译", default=False)
    checkprofile = models.ForeignKey(CheckProfile, on_delete=models.SET_NULL, verbose_name="检测检测集",
                                     blank=True, null=True)
    owners = models.ManyToManyField(User, related_name="own_schemetemplate", help_text="负责人")

    def to_dict(self):
        """字典格式
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "short_desc": self.short_desc,
            "description": self.description,
            "tag": self.tag,
            "labels": list(self.labels.all().values_list("name", flat=True)),
            "basic_conf": json.loads(self.basic_conf),
            "lint_conf": json.loads(self.lint_conf),
            "metric_conf": json.loads(self.metric_conf),
            "profile_conf": self.profile_conf
        }

    @property
    def profile_conf(self):
        """规则集配置
        """
        return self.checkprofile.get_custom_checkpackage_content()

    def __str__(self):
        return self.name


class ScanSchemePerm(CDBaseModel):
    """扫描方案权限

    针对方案模板，execute_scope用于表示组织的公开范围，OPEN表示组织内公开，PRIVATE表示组织内不公开
    针对方案，execute_scope用于表示方案的执行权限，OPEN表示权限开放，PRIVATE表示权限仅指定成员可用
    """

    class ScopeEnum(object):
        OPEN = 1
        PRIVATE = 2

    SCOPE_CHOICES = (
        (ScopeEnum.OPEN, "公开"),
        (ScopeEnum.PRIVATE, "私有"),
    )

    scan_scheme = models.OneToOneField(ScanScheme, on_delete=models.CASCADE, help_text="扫描方案")
    edit_scope = models.IntegerField(choices=SCOPE_CHOICES, default=ScopeEnum.OPEN, help_text="方案编辑权限范围")
    execute_scope = models.IntegerField(choices=SCOPE_CHOICES, default=ScopeEnum.OPEN, help_text="关联项目启动权限范围")
    edit_managers = models.ManyToManyField(User, help_text="方案可编辑成员列表", blank=True, related_name="+")
    execute_managers = models.ManyToManyField(User, help_text="方案可执行成员列表", blank=True, related_name="+")

    def get_edit_managers(self):
        """获取可编辑成员列表
        """
        return self.edit_managers.all()

    def get_execute_managers(self):
        """获取可执行成员列表
        """
        return self.execute_managers.all()

    def check_user_edit_manager_perm(self, user):
        """检查指定用户是否有可编辑的维护权限
        """
        if self.scan_scheme.creator == user:
            return True
        elif self.edit_managers.filter(username=user.username).first():
            return True
        else:
            return False

    def check_user_execute_manager_perm(self, user):
        """检查指定用户是否有可执行的维护权限
        """
        if self.scan_scheme.creator == user:
            return True
        elif self.execute_managers.filter(username=user.username).first():
            return True
        else:
            return False


# ****************************
# * 项目扫描结果信息
# ****************************
class ProjectScanInfoBase(models.Model):
    """
    上次成功扫描信息 - 整体信息
    """
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    scan_revision = models.CharField(max_length=64, verbose_name="扫描版本号", null=True, blank=True)
    scan_time = models.DateTimeField(verbose_name="扫描时间", null=True, blank=True)

    class Meta:
        abstract = True


class CodeLintInfo(ProjectScanInfoBase):
    """上次成功扫描信息 - codelint
    """
    issue_open_num = models.IntegerField("新增缺陷数", null=True, blank=True)
    issue_fix_num = models.IntegerField("修复缺陷数", null=True, blank=True)
    active_severity_detail = models.CharField(max_length=512, verbose_name="严重级别详情", null=True, blank=True)
    active_category_detail = models.CharField(max_length=512, verbose_name="类别详情", null=True, blank=True)
    total_state_detail = models.CharField(max_length=512, verbose_name="状态详情", null=True, blank=True)
    total_severity_detail = models.CharField(max_length=512, verbose_name="严重级别详情", null=True, blank=True)
    total_category_detail = models.CharField(max_length=512, verbose_name="类别详情", null=True, blank=True)
    scan_summary = models.TextField(verbose_name="本次扫描总结报告", null=True, blank=True)
    total_summary = models.TextField(verbose_name="累计总结报告", null=True, blank=True)


class CodeMetricCCInfo(ProjectScanInfoBase):
    """上次成功扫描信息 - codemetric cc圈复杂度
    """
    # cc scan
    last_revision = models.CharField(max_length=256, verbose_name="旧版本号", blank=True, null=True)
    cc_open_num = models.IntegerField(null=True, blank=True)
    cc_fix_num = models.IntegerField(default=0)
    default_summary = models.TextField(verbose_name="默认标准的总结", null=True, blank=True)
    custom_summary = models.TextField(verbose_name="自定义标准的总结", null=True, blank=True)


class CodeMetricDupInfo(ProjectScanInfoBase):
    """上次成功扫描信息 - codemetric dup重复代码
    """
    # dup scan
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


class CodeMetricClocInfo(ProjectScanInfoBase):
    """上次成功扫描信息 - codemetric codecount代码统计
    """
    last_revision = models.CharField(max_length=256, verbose_name="旧版本号", blank=True, null=True)
    code_line_num = models.IntegerField(verbose_name="代码行数", blank=True, null=True)
    comment_line_num = models.IntegerField(verbose_name="注释行数", blank=True, null=True)
    blank_line_num = models.IntegerField(verbose_name="空白行数", blank=True, null=True)
    total_line_num = models.IntegerField(verbose_name="总行数", blank=True, null=True)
    add_code_line_num = models.IntegerField(verbose_name="新增代码行数", blank=True, null=True)
    add_comment_line_num = models.IntegerField(verbose_name="新增注释行数", blank=True, null=True)
    add_blank_line_num = models.IntegerField(verbose_name="新增空白行数", blank=True, null=True)
    add_total_line_num = models.IntegerField(verbose_name="新增总行数", blank=True, null=True)
    mod_code_line_num = models.IntegerField(verbose_name="修改代码行数", blank=True, null=True)
    mod_comment_line_num = models.IntegerField(verbose_name="修改注释行数", blank=True, null=True)
    mod_blank_line_num = models.IntegerField(verbose_name="修改空白行数", blank=True, null=True)
    mod_total_line_num = models.IntegerField(verbose_name="修改总行数", blank=True, null=True)
    del_code_line_num = models.IntegerField(verbose_name="删除代码行数", blank=True, null=True)
    del_comment_line_num = models.IntegerField(verbose_name="删除注释行数", blank=True, null=True)
    del_blank_line_num = models.IntegerField(verbose_name="删除空白行数", blank=True, null=True)
    del_total_line_num = models.IntegerField(verbose_name="删除总行数", blank=True, null=True)


# ****************************
# * 项目扫描相关配置
# ****************************


class CommonSetting(models.Model):
    """代码扫描共用的设置
    """
    project = models.OneToOneField(Project, on_delete=models.CASCADE)


class LintBaseSetting(CDBaseModel):
    """codelint 设置
    """
    scan_scheme = models.OneToOneField(ScanScheme, on_delete=models.CASCADE, help_text="扫描方案")
    enabled = models.BooleanField(help_text="是否开启", default=False)
    checkprofile = models.ForeignKey(CheckProfile, on_delete=models.SET_NULL, verbose_name="检测检测集",
                                     blank=True, null=True)
    default_author = models.CharField(max_length=64, verbose_name="缺省责任人", null=True, blank=True,
                                      help_text="当获取不到问题代码提交人时的缺省提单人，如不设置则默认为空")
    build_cmd = models.TextField(verbose_name="编译命令", blank=True, null=True,
                                 help_text="咨询项目的开发,如果还有问题联系bensonqin或yalechen")
    envs = models.TextField(verbose_name="环境变量", blank=True, null=True, help_text="环境变量")
    pre_cmd = models.CharField(max_length=512, verbose_name="前置命令", blank=True, null=True,
                               help_text="项目编译前需要执行的命令")

    @classmethod
    def get_lint_conf_template(cls):
        """获取扫描配置模板
        """
        lint_conf_template = {
            "enabled": True
        }
        return lint_conf_template

    @classmethod
    def merge_lint_conf_template(cls, lint_conf_1, lint_conf_2):
        """合并基础配置模板
        """
        for item in lint_conf_1:
            if lint_conf_2.pop(item, False) is True:
                lint_conf_1[item] = True
        lint_conf_1.update(**lint_conf_2)
        return lint_conf_1


class MetricSetting(CDBaseModel):
    """代码度量配置
    """
    scan_scheme = models.OneToOneField(ScanScheme, on_delete=models.CASCADE, help_text="扫描方案")
    # 废弃字段
    codediff_scan_enabled = models.BooleanField(default=False, help_text="旧版代码统计开关，默认关闭")
    # 圈复杂度配置
    cc_scan_enabled = models.BooleanField(default=False, help_text="圈复杂度开关，默认关闭")
    min_ccn = models.IntegerField(default=20, help_text="圈复杂度检测最小值")
    cc_ref_project_id = models.IntegerField(help_text="参考阈值的项目编号", null=True, blank=True)
    cc_ref_setting_time = models.DateTimeField(help_text="参考阈值设定的时间", null=True, blank=True)
    cc_ref_value_flag = models.BooleanField(default=False,
                                            help_text="圈复杂度文件参考阈值标识位，如果设定了即为True，默认为False")
    cc = models.CharField(max_length=16, help_text="提单抄送人", null=True, blank=True)
    # 重复代码
    dup_scan_enabled = models.BooleanField(default=False, help_text="重复代码开关，默认关闭")
    dup_block_length_min = models.IntegerField(default=120, help_text="重复代码长度最小值")  # 单位是单词
    dup_block_length_max = models.IntegerField(blank=True, null=True, help_text="重复代码长度最大值")  # 为空时表示无限大
    dup_min_dup_times = models.IntegerField(default=2, help_text="重复最小次数")
    dup_max_dup_times = models.IntegerField(blank=True, null=True, help_text="重复最大次数")  # 为空时表示无限大
    dup_min_midd_rate = models.IntegerField(default=5, help_text="中风险最小重复率")
    dup_min_high_rate = models.IntegerField(default=11, help_text="高风险最小重复率")
    dup_min_exhi_rate = models.IntegerField(default=20, help_text="极高风险风险最小重复率")
    dup_issue_limit = models.IntegerField(default=1000, help_text="上报重复代码块数上限")
    # 代码统计
    cloc_scan_enabled = models.BooleanField(default=True, help_text="新版代码统计，默认关闭")
    use_lang = models.BooleanField(default=False, help_text="只统计方案指定语言，默认关闭")
    # 废弃字段
    core_file_path = models.CharField(verbose_name="核心文件配置路径", max_length=256,
                                      help_text="兼容已有配置文件corefiles.xml，供代码统计使用", null=True, blank=True)
    file_mon_path = models.CharField(verbose_name="文件监控配置路径", max_length=256,
                                     help_text="兼容已有配置文件filemon.xml，供代码统计使用", null=True, blank=True)

    @classmethod
    def get_metric_conf_template(cls):
        """获取度量配置模板
        """
        metric_conf_template = {
            "cc_scan_enabled": False,
            "min_ccn": 20,
            "dup_scan_enabled": False,
            "dup_block_length_min": 120,
            "dup_block_length_max": None,
            "dup_min_dup_times": 2,
            "dup_max_dup_times": None,
            "dup_min_midd_rate": 5,
            "dup_min_high_rate": 11,
            "dup_min_exhi_rate": 20,
            "dup_issue_limit": 1000,
            "cloc_scan_enabled": False
        }
        return metric_conf_template

    @classmethod
    def merge_metric_conf_template(cls, metric_conf_1, metric_conf_2):
        """合并度量配置模板
        """
        for item in metric_conf_1:
            value = metric_conf_2.pop(item) if item in metric_conf_2 else None
            if type(metric_conf_1[item]) == int \
                    and value is not None \
                    and metric_conf_1[item] > value:
                metric_conf_1[item] = value
            elif type(metric_conf_1[item]) == bool \
                    and value is True:
                metric_conf_1[item] = True
            elif type(metric_conf_1[item]) is None and value is not None:
                metric_conf_1[item] = value
        metric_conf_1.update(**metric_conf_2)
        return metric_conf_1


class ScanDir(models.Model):
    """项目扫描仅扫描/过滤目录
    """

    class ScanTypeEnum(object):
        DEFAULT = 0
        INCLUDE = 1
        EXCLUDE = 2

    SCAN_TYPE_CHOICES = (
        (ScanTypeEnum.DEFAULT, ""),
        (ScanTypeEnum.INCLUDE, "Include"),
        (ScanTypeEnum.EXCLUDE, "Exclude"),)

    class PathTypeEnum(object):
        WILDCARD = 1
        REGULAR = 2

    PATH_TYPE_CHOICES = (
        (PathTypeEnum.WILDCARD, "通配符格式"),
        (PathTypeEnum.REGULAR, "正则表达式格式"),
    )

    scan_scheme = models.ForeignKey(ScanScheme, on_delete=models.SET_NULL, help_text="扫描方案", null=True)
    dir_path = models.CharField(max_length=512, help_text="名称")
    path_type = models.IntegerField(default=PathTypeEnum.WILDCARD, choices=PATH_TYPE_CHOICES, null=True, blank=True,
                                    help_text="路径格式类型，1为通配符，2为正则表达式，默认为通配符", )
    scan_type = models.IntegerField(default=0, choices=SCAN_TYPE_CHOICES, help_text="扫描类型")

    @classmethod
    def get_path_list_with_scheme(cls, scan_scheme, path_type, scan_type):
        """获取指定扫描方案指定类型的路径列表
        """
        return list(cls.objects.filter(
            scan_scheme=scan_scheme, scan_type=scan_type, path_type=path_type
        ).values_list("dir_path", flat=True))


class DefaultScanPath(CDBaseModel):
    """扫描默认过滤路径
    """

    class PathTypeEnum(object):
        WILDCARD = 1
        REGULAR = 2

    PATH_TYPE_CHOICES = (
        (PathTypeEnum.WILDCARD, "通配符格式"),
        (PathTypeEnum.REGULAR, "正则表达式格式"),
    )

    dir_path = models.CharField(max_length=255, help_text="过滤路径名称", unique=True)
    path_type = models.IntegerField(default=PathTypeEnum.WILDCARD, null=True, blank=True,
                                    help_text="路径格式类型，1为通配符，2为正则表达式，默认为通配符")
    category = models.CharField(max_length=20, help_text="过滤路径类别", default="默认")
    description = models.CharField(max_length=255, help_text="路径描述", null=True, blank=True)

    def __str__(self):
        return "[%s]%s-%s" % (self.category, self.path_type, self.dir_path)


class SchemeDefaultScanPathExcludeMap(models.Model):
    """扫描方案默认过滤路径映射表（记录屏蔽哪些过滤路径）
    """
    scan_scheme = models.ForeignKey(ScanScheme, on_delete=models.SET_NULL, help_text="扫描方案", null=True)
    default_scan_path = models.ForeignKey(DefaultScanPath, on_delete=models.SET_NULL, help_text="过滤路径", null=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="创建人")

    class Meta:
        unique_together = ("scan_scheme", "default_scan_path")


# ****************************
# * 项目成员相关配置
# ****************************
class NonProjectUser(CDBaseModel):
    """非项目成员名单
    """
    project = models.ForeignKey(Project, verbose_name="产品名称", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    replace_user = models.ForeignKey(User, verbose_name="对接人", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="replace_user")


class NonRepoUser(CDBaseModel):
    """非代码库成员名单
    """
    repo = models.ForeignKey(Repository, verbose_name="代码库", on_delete=models.CASCADE)
    users = models.ManyToManyField(User, verbose_name="用户", blank=True)
    replace_user = models.ForeignKey(User, verbose_name="对接人", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="replace_username")
