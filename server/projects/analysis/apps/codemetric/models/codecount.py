# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - codecount models
"""
from django.db import models

from apps.codeproj.models import Project, Scan


class ClocScan(models.Model):
    """Cloc扫描类
    """
    scan = models.OneToOneField(Scan, verbose_name="扫描记录", on_delete=models.CASCADE)
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

    def get_file_num(self):
        return ClocFile.objects.filter(scan=self, is_latest=True).count()

    def get_change_file_num(self):
        return ClocFile.objects.filter(scan=self, is_latest=True, change_type__in=[
            ClocFile.ChangeTypeEnum.ADDED, ClocFile.ChangeTypeEnum.MODIFIED, ClocFile.ChangeTypeEnum.DELETED]).count()


class _ClocBase(models.Model):
    """Cloc基础类
    """
    code_line_num = models.IntegerField(verbose_name="代码行数")
    comment_line_num = models.IntegerField(verbose_name="注释行数")
    blank_line_num = models.IntegerField(verbose_name="空白行数")
    total_line_num = models.IntegerField(verbose_name="总行数")

    add_code_line_num = models.IntegerField(verbose_name="新增代码行数")
    add_comment_line_num = models.IntegerField(verbose_name="新增注释行数")
    add_blank_line_num = models.IntegerField(verbose_name="新增空白行数")
    add_total_line_num = models.IntegerField(verbose_name="新增总行数")

    mod_code_line_num = models.IntegerField(verbose_name="修改代码行数")
    mod_comment_line_num = models.IntegerField(verbose_name="修改注释行数")
    mod_blank_line_num = models.IntegerField(verbose_name="修改空白行数")
    mod_total_line_num = models.IntegerField(verbose_name="修改总行数")

    del_code_line_num = models.IntegerField(verbose_name="删除代码行数")
    del_comment_line_num = models.IntegerField(verbose_name="删除注释行数")
    del_blank_line_num = models.IntegerField(verbose_name="删除空白行数")
    del_total_line_num = models.IntegerField(verbose_name="删除总行数")

    class Meta:
        abstract = True


class ClocBase(_ClocBase):
    """Cloc普通基础类
    """
    project = models.ForeignKey(Project, verbose_name="项目名称", blank=True, null=True,
                                on_delete=models.CASCADE)
    scan = models.ForeignKey(ClocScan, verbose_name="扫描", on_delete=models.CASCADE)
    is_latest = models.BooleanField(verbose_name="是否最新", default=True, blank=True)

    class Meta:
        abstract = True


class ClocFile(ClocBase):
    """Cloc文件表
    """

    class ChangeTypeEnum(object):
        ADDED = "add"
        DELETED = "del"
        MODIFIED = "mod"

    CHANGE_TYPE_CHOICES = (
        (ChangeTypeEnum.ADDED, "新增"),
        (ChangeTypeEnum.DELETED, "删除"),
        (ChangeTypeEnum.MODIFIED, "修改"))
    dir_path = models.CharField(max_length=512, verbose_name="目录地址")
    file_name = models.CharField(max_length=512, verbose_name="文件名")
    business_names = models.CharField(max_length=512, verbose_name="业务", null=True, blank=True)
    subscribers = models.CharField(max_length=512, verbose_name="关注人", null=True, blank=True)
    language = models.CharField(max_length=32, verbose_name="语言")
    change_type = models.CharField(max_length=64, choices=CHANGE_TYPE_CHOICES, verbose_name="更改类型", blank=True,
                                   null=True)

    class Meta:
        index_together = (
            ("project", "is_latest"),
        )


class ClocDir(ClocBase):
    """Cloc目录类
    """
    parent_path = models.CharField(max_length=512, verbose_name="父目录地址", null=True)
    dir_path = models.CharField(max_length=512, verbose_name="目录地址")
    file_num = models.IntegerField(verbose_name="文件数")


class ClocLanguage(ClocBase):
    """扫描语言类
    """
    name = models.CharField(max_length=64, verbose_name="语言名称")
    file_num = models.IntegerField(verbose_name="文件数")

    @classmethod
    def get_project_language_infos(cls, project_id, scan_id=None):
        """获取指定项目指定扫描的语言信息
        """
        language_infos = cls.objects.filter(project_id=project_id)
        if scan_id:
            return language_infos.filter(scan__scan_id=scan_id)
        else:
            return language_infos.filter(is_latest=True)
