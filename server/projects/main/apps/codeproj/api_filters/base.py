# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base filters
"""
# 原生
import logging

# 第三方
from django.db.models import Q
from django_filters import rest_framework as filters

# 项目内
from apps.codeproj import models
from util.scm import ScmClient

logger = logging.getLogger(__name__)


class ProjectTeamFilter(filters.FilterSet):
    """项目组筛选项

    ```python
    display_name: str, 项目显示名称, 包含
    status: int, 项目状态
    ```
    """
    display_name = filters.CharFilter(help_text="项目显示名称", lookup_expr="icontains")
    organization_name = filters.CharFilter(help_text="团队名称", field_name="organization__name",
                                           lookup_expr="icontains")
    organization_sid = filters.CharFilter(help_text="团队编号", field_name="organization__org_sid",
                                          lookup_expr="icontains")

    class Meta:
        model = models.ProjectTeam
        fields = ["status", "display_name", "organization_name", "organization_sid"]


class ApiProjectFilter(filters.FilterSet):
    """项目筛选
    """
    scm_url = filters.CharFilter(label="代码库#分支地址", help_text="会根据仓库地址及分支进行匹配，代码库与分支使用#间隔",
                                 method="scm_url_branch_filter")
    branch = filters.CharFilter(label="代码库分支", help_text="代码库分支筛选", lookup_expr="exact")
    scan_path = filters.CharFilter(label="扫描路径", help_text="扫描路径筛选", lookup_expr="icontains")
    scm_url__exact = filters.CharFilter(label="代码库地址精准匹配", help_text="会根据仓库地址进行匹配",
                                        method="scm_url_filter")
    created_time__lte = filters.DateTimeFilter(field_name="created_time",
                                               help_text="指定时间之前创建的项目", lookup_expr="lte")
    created_time__gte = filters.DateTimeFilter(field_name="created_time",
                                               help_text="指定时间之后创建的项目", lookup_expr="gte")
    scan_scheme_id = filters.NumberFilter(label="扫描方案编号",
                                          help_text="如需指定扫描方案，请输入扫描方案编号", lookup_expr="exact")
    scan_scheme__name = filters.CharFilter(label="扫描方案名称",
                                           help_text="如需指定扫描方案，请输入扫描方案名称", lookup_expr="exact")
    scan_scheme__default_flag = filters.BooleanFilter(label="默认方案", help_text="是否使用默认方案", lookup_expr="exact")

    def scm_url_branch_filter(self, queryset, name, value):
        """项目代码库地址、分支筛选，地址与分支通过#符号分割
        """
        if "svn" in value:
            svn_client = ScmClient(models.Repository.ScmTypeEnum.SVN, value,
                                   models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
            git_client = ScmClient(models.Repository.ScmTypeEnum.GIT, value,
                                   models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
            return queryset.filter(repo__scm_url__in=[git_client.get_repository(), svn_client.get_repository()],
                                   branch__in=[git_client.branch, svn_client.branch])
        else:
            git_client = ScmClient(models.Repository.ScmTypeEnum.GIT, value,
                                   models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
            queryset = queryset.filter(repo__scm_url=git_client.get_repository(), branch=git_client.branch)
            return queryset

    def scm_url_filter(self, queryset, name, value):
        """项目代码库地址筛选
        """
        git_client = ScmClient(models.Repository.ScmTypeEnum.GIT, value,
                               models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
        svn_client = ScmClient(models.Repository.ScmTypeEnum.SVN, value,
                               models.ScmAuth.ScmAuthTypeEnum.PASSWORD)
        return queryset.filter(repo__scm_url__in=[git_client.get_repository(), svn_client.get_repository()])

    class Meta:
        model = models.Project
        fields = ["scm_url", "scm_url__exact", "scan_scheme__name", "scan_scheme__default_flag",
                  "scan_scheme_id", "branch", "created_time__gte", "created_time__lte", "scan_path"]


class ScanSchemeFilter(filters.FilterSet):
    """扫描方案筛选
    """
    default_flag = filters.BooleanFilter(help_text="默认标志")
    name = filters.CharFilter(help_text="扫描方案名称", lookup_expr="icontains")
    status = filters.NumberFilter(help_text="扫描方案状态，1为活跃，2为废弃")
    include_branch = filters.CharFilter(label="include_branch", help_text="包含的分支名称，多个分支使用,分隔",
                                        method="include_branch_filter")
    exclude_branch = filters.CharFilter(label="exclude_branch", help_text="不包含的分支名称，多个分支使用,分隔",
                                        method="exclude_branch_filter")
    refer_template_ids = filters.CharFilter(help_text="参考方案ID组合，查询前请排序，精准匹配通过参考方案ID组合创建的扫描方案",
                                            method="refer_template_ids_filter")

    def include_branch_filter(self, queryset, name, value):
        """包含分支筛选
        """
        if not value:
            return queryset
        branches = value.split(",")
        return queryset.filter(project__branch__in=branches)

    def exclude_branch_filter(self, queryset, name, value):
        """不包含分支筛选
        """
        if not value:
            return queryset
        branches = value.split(",")
        return queryset.exclude(project__branch__in=branches)

    def refer_template_ids_filter(self, queryset, name, value):
        """参照模板编号筛选
        """
        if not value:
            return queryset
        try:
            refer_template_ids = sorted([int(item) for item in value.split(",")])
        except ValueError as err:
            logger.exception("query with template id format error: %s" % err)
            return queryset
        logger.info("template_ids: %s" % refer_template_ids)
        return queryset.filter(refer_template_ids=refer_template_ids)

    class Meta:
        model = models.ScanScheme
        fields = ["name", "status", "include_branch", "exclude_branch", "refer_template_ids", "default_flag"]


class GlobalScanSchemeTemplateFilter(filters.FilterSet):
    """扫描方案模板筛选

    ```python
    name: str, 方案模板名称，包含
    scope: str, 过滤范围，all全部，system系统模板，not_system非系统模板，editable有权限编辑模板
    ```
    """

    class ScopeEnum:
        ALL = "all"
        SYSTEM = "system"
        NOT_SYSTEM = "not_system"
        EDITABLE = "editable"

    SCOPE_CHOICES = (
        (ScopeEnum.ALL, "全部"),
        (ScopeEnum.SYSTEM, "系统模板"),
        (ScopeEnum.NOT_SYSTEM, "非系统模板"),
        (ScopeEnum.EDITABLE, "可编辑模板"),
    )

    name = filters.CharFilter(help_text="方案模板名称", lookup_expr="icontains")
    scope = filters.ChoiceFilter(label="scope", help_text="过滤范围", method="scope_filter", choices=SCOPE_CHOICES)

    def scope_filter(self, queryset, name, value):
        user = self.request.user
        if value == self.ScopeEnum.SYSTEM:
            return queryset.filter(scheme_key=models.ScanScheme.SchemeKey.PUBLIC)
        elif value == self.ScopeEnum.NOT_SYSTEM:
            return queryset.exclude(scheme_key=models.ScanScheme.SchemeKey.PUBLIC)
        elif value == self.ScopeEnum.EDITABLE:
            scheme_ids = models.ScanSchemePerm.objects.filter(edit_managers__in=[user]) \
                .values_list("scan_scheme_id", flat=True)
            return queryset.exclude(scheme_key=models.ScanScheme.SchemeKey.PUBLIC).filter(id__in=scheme_ids)
        return queryset

    class Meta:
        model = models.ScanScheme
        fields = ["name", "scope"]


class GlobalScanSchemeTemplateChildrenFilter(filters.FilterSet):
    """方案模板子分析方案筛选
    """
    name = filters.CharFilter(help_text="分析方案名称", lookup_expr="icontains")
    repo__scm_url = filters.CharFilter(help_text="代码库地址", lookup_expr="icontains")

    class Meta:
        model = models.ScanScheme
        fields = ["name", "repo__scm_url"]


class ProjectFilter(filters.FilterSet):
    """项目筛选
    """
    branch = filters.CharFilter(help_text="分支名称")
    scan_path = filters.CharFilter(help_text="扫描路径筛选", lookup_expr="icontains")
    scan_scheme = filters.NumberFilter(help_text="扫描方案编号")
    scan_scheme__name = filters.CharFilter(help_text="扫描方案名称")
    scan_scheme__status = filters.NumberFilter(help_text="扫描方案状态，1为活跃，2为废弃")
    branch_or_scheme = filters.CharFilter(label="分支名称/扫描方案名称", help_text="分支名称/扫描方案名称",
                                          method="branch_or_scheme_or_path_filter")

    def branch_or_scheme_or_path_filter(self, queryset, name, value):
        return queryset.filter(
            Q(branch__icontains=value) |
            Q(scan_scheme__name__icontains=value) |
            Q(scan_path__icontains=value))

    class Meta:
        model = models.Project
        fields = ["branch", "scan_scheme", "scan_path", "branch_or_scheme", "scan_scheme__status", "status",
                  "scan_scheme__default_flag", "scan_scheme__name"]


class ProjectBranchNameFilter(filters.FilterSet):
    """分支项目分支名称筛选
    """
    branch = filters.CharFilter(help_text="分支名称，包含", lookup_expr="icontains")

    class Meta:
        model = models.Project
        fields = ["branch"]
