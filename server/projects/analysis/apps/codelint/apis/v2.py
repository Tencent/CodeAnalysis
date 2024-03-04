# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - v2 apis
"""

# python 原生import
import logging

# 第三方 import
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import ParseError
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内 import
from apps.base.apimixins import ExportMixin
from apps.codelint import serializers, models, resources, core, filters
from apps.codeproj.apimixins import ProjectBaseAPIView
from util.ordering import OrderingWithPKFilter

logger = logging.getLogger(__name__)


class ProjectIssueListView(generics.ListAPIView, ProjectBaseAPIView):
    """项目问题列表接口

    ### Get
    应用场景：查看问题列表数据
    """
    serializer_class = serializers.ProjectIssueSerializer
    filter_backends = (DjangoFilterBackend, OrderingWithPKFilter,)
    ordering_fields = "__all__"
    filterset_class = filters.LintIssueFilterSet

    def get_queryset(self):
        project = self.get_project()
        return models.Issue.everything.filter(project_id=project.id)


class ProjectIssueDownloadView(ExportMixin, generics.GenericAPIView, ProjectBaseAPIView):
    """项目问题列表下载接口

    ### Get
    应用场景：下载问题列表数据
    """
    serializer_class = serializers.IssueDownloadSerializer
    resource_class = resources.IssueResource
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    ordering_fields = "__all__"
    ordering = ["-ci_time"]
    filterset_class = filters.LintIssueFilterSet

    def get_queryset(self):
        project = self.get_project()
        return models.Issue.everything.select_related("project").filter(project_id=project.id)

    def get_export_filename(self):
        """获取下载的文件名
        """
        project_id = self.kwargs['project_id']
        return "Project_%s_issue_data" % project_id


class IssueResolutionBulkUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """问题解决方式批量更新接口

    ### PUT
    应用场景：批量修改issue resolution接口

    >### 参数：
    >* issue_ids: 需要修改的id列表，需要在project下
    >* resolution: 指定问题解决方式，取值范围：0~6, 无=0/修复=1/无需修复=2/误报=3/重复单过滤=4/路径过滤=5/规则移除=6
    >* scope: 指定处理方式的影响范围(仅对无需修复、误报的处理方式有效），取值范围：1为当前项目级别，2为代码库级别

    >### 格式：
    ```python
     {
        "issue_ids": [1, 2],
        "resolution": 0,
        "scope": 0
     }
     ```

    >### 返回：
    >* http200

    ******
    """

    def check_resolution_valid(self, resolution):
        """检查解决方式是否有效
        :param resolution: int，解决方式
        """
        if models.Issue.RESOLUTION_CHOICES_DICT.get(resolution) is None:
            raise ParseError("参数异常，`Resolution` 值[%s]错误" % resolution)

    def check_scope_valid(self, scope):
        """判断影响范围是否有效
        """
        if scope and models.InvalidIssue.SCOPEENUM_CHOICES_DICT.get(scope) is None:
            raise ParseError("参数异常，`Scope` 值[%s]错误" % scope)

    def put(self, request, **kwargs):
        project = self.get_project()
        issue_ids = request.data.get("issue_ids")
        new_resolution = request.data.get("resolution")
        scope = request.data.get("scope")
        ignore_reason = request.data.get("ignore_reason")
        if not isinstance(issue_ids, list):
            raise ParseError("参数异常, `issue_ids`不是list格式")
        self.check_resolution_valid(new_resolution)
        self.check_scope_valid(scope)
        issues = models.Issue.everything.filter(project_id=project.id, id__in=issue_ids)
        core.CodeLintIssueResolutionManager.update_issues_resolution(
            request.user.username, issues, new_resolution, scope, ignore_reason)
        return Response(data={"msg": "success"})


class IssueAuthorBulkUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """问题责任人批量更新接口

    ### PUT
    应用场景：批量修改issue author接口

    >### 参数：
    >* issue_ids: 需要修改的id列表，需要在project下
    >* author: 新责任人

    >### 格式：
    ```python
     {
        "issue_ids": [1, 2],
        "author": "xxx"
     }
     ```

    >### 返回：
    >* http200

    ******
    """

    def put(self, request, **kwargs):
        project = self.get_project()
        issue_ids = request.data.get("issue_ids")
        new_author = request.data.get("author")
        if not isinstance(issue_ids, list):
            raise ParseError("参数异常, `issue_ids`不是list格式")
        issues = models.Issue.everything.filter(project_id=project.id, id__in=issue_ids)
        core.CodeLintIssueAuthorManager.update_issues_author(request.user.username, issues, new_author)
        return Response(data={"msg": "success"})


class ProjectIssueAuthorsView(APIView, ProjectBaseAPIView):
    """问题责任人列表

    ### get
    应用场景：获取项目问题全部责任人列表，用于issue责任人筛选
    """
    
    def get(self, request, *args, **kwargs):
        project = self.get_project()
        authors = list(models.Issue.everything.filter(project=project, author__isnull=False) \
            .exclude(author='').values_list('author', flat=True).order_by('author').distinct())
        return Response(data=authors)


class IssueDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """问题详情接口

    ### GET
    应用场景：获取issue详情
    """
    serializer_class = serializers.DetailedIssueSerializer

    def get_object(self):
        project = self.get_project()
        issue_id = self.kwargs["issue_id"]
        return get_object_or_404(models.Issue, id=issue_id, project_id=project.id)


class ProjectIssueCheckRuleNumView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目问题规则数

    ### GET
    应用场景：获取活跃问题规则数
    """

    def get(self, request, **kwargs):
        project = self.get_project()
        active_checkrule_nums = {item["checkrule_display_name"]: item["num"] for item in models.Issue.everything.filter(
            project_id=project.id, state=models.Issue.StateEnum.ACTIVE
        ).values("checkrule_display_name").annotate(num=Count("id"))}
        checkrule_nums = {item["checkrule_display_name"]: item["num"] for item in models.Issue.everything.filter(
            project_id=project.id
        ).values("checkrule_display_name").annotate(num=Count("id"))}
        checkrule_result = []
        for name, num in checkrule_nums.items():
            active_num = active_checkrule_nums.get(name, 0)
            checkrule_result.append({"checkrule_display_name": name, "num": num, "active_num": active_num})
        return Response(data=checkrule_result)


class IssueCommentsView(generics.ListCreateAPIView, ProjectBaseAPIView):
    """问题评论列表接口

    ### GET
    应用场景：获取issue评论列表

    ### POST
    应用场景：创建issue评论
    """
    serializer_class = serializers.IssueCommentSerializer
    queryset = models.IssueComment.objects.all()

    def get_queryset(self):
        self.get_project()
        issue_id = self.kwargs["issue_id"]
        return models.IssueComment.objects.filter(issue_id=issue_id).order_by("-id")[:20]


class IssueAuthorUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """问题责任人更新接口

    ### POST
    应用场景：修改issue author接口

    >### 参数：
    >* author:指定问题责任人list，多人以英文;隔开
    >* all: true or false, 为true时批量修改责任人，默认为false

    >### 格式：
    ```python
     {
        "author": "xxx",
        "all": true
     }
     ```

    >### 返回：
    >* issue serializer

    ******
    """

    def check_author_valid(self, current_author, new_author):
        """检查责任人字段有效性
        :param current_author: str，现有责任人
        :param new_author: str，新责任人
        """
        if not new_author:
            raise ParseError("参数异常，责任人不可以为空")

        if current_author == new_author:
            raise ParseError("参数异常，新责任人不可以与原责任人相同")

    def put(self, request, *args, **kwargs):
        issue_id = kwargs["issue_id"]
        project = self.get_project()
        new_author = request.data.get("author", "").strip()
        change_all = request.data.get("all", False) is True
        issue = get_object_or_404(models.Issue, project_id=project.id, id=issue_id)
        self.check_author_valid(issue.author, new_author)
        issue = core.CodeLintIssueAuthorManager.update_issue_author(request.user.username, issue, new_author,
                                                                    change_all)
        serializer = serializers.DetailedIssueSerializer(instance=issue)
        return Response(serializer.data)


class IssueSeverityUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """问题严重级别更新接口

    ### POST
    应用场景：修改issue severity接口

    >### 参数：
    >* severity:指定问题严重级别，取值范围：1～4, FATAL=1/ERROR=2/WARNING=3/INFO=4

    >### 返回：
    >* issue serializer

    ******
    """

    def check_severity_valid(self, severity):
        """检查优先级有效性
        :param severity: int, 问题优先级
        """
        if models.Issue.SEVERITY_CHOICES_DICT.get(severity) is None:
            raise ParseError("参数异常，`Severity` 值[%s]错误" % severity)

    def put(self, request, *args, **kwargs):
        issue_id = kwargs["issue_id"]
        project = self.get_project()
        new_severity = request.data.get("severity")
        self.check_severity_valid(new_severity)
        issue = get_object_or_404(models.Issue, project_id=project.id, id=issue_id)
        core.CodeLintIssueSeverityManager.update_issue_severity(request.user.username, issue, new_severity)
        serializer = serializers.DetailedIssueSerializer(instance=issue)
        return Response(serializer.data)


class IssueResolutionUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """问题解决解决方式更新接口

    ### POST
    应用场景：修改issue resolution接口

    >### 参数：
    >* resolution:指定问题解决方式，取值范围：0~6, 无=0/修复=1/无需修复=2/误报=3/重复单过滤=4/路径过滤=5/规则移除=6
    >* scope: 指定处理方式的影响范围(仅对无需修复、误报的处理方式有效），取值范围：1为当前项目级别，2为代码库级别

    >### 返回：
    >* issue serializer

    ******
    """

    def check_resolution_valid(self, resolution):
        """检查解决方式是否有效
        :param resolution: int，解决方式
        """
        if models.Issue.RESOLUTION_CHOICES_DICT.get(resolution) is None:
            raise ParseError("参数异常，`Resolution` 值[%s]错误" % resolution)

    def check_scope_valid(self, scope):
        """判断影响范围是否有效
        """
        if scope and models.InvalidIssue.SCOPEENUM_CHOICES_DICT.get(scope) is None:
            raise ParseError("参数异常，`Scope` 值[%s]错误" % scope)

    def put(self, request, *args, **kwargs):
        issue_id = kwargs["issue_id"]
        project = self.get_project()
        new_resolution = request.data.get("resolution")
        scope = request.data.get("scope")
        ignore_reason = request.data.get("ignore_reason")
        self.check_resolution_valid(new_resolution)
        self.check_scope_valid(scope)
        issue = get_object_or_404(models.Issue, project_id=project.id, id=issue_id)
        issue = core.CodeLintIssueResolutionManager.update_one_issue_resolution(
            request.user.username, issue, new_resolution, scope, ignore_reason)
        serializer = serializers.DetailedIssueSerializer(instance=issue)
        return Response(serializer.data)


class InvalidIssueListView(generics.ListAPIView, ProjectBaseAPIView):
    """无效问题列表

    ### GET
    应用场景：查询指定代码库的无效问题列表
    """
    serializer_class = serializers.InvalidIssueSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.InvalidIssueFilterSet

    def get_queryset(self):
        repo_id = self.get_repo_id()
        return models.InvalidIssue.objects.filter(project__repo_id=repo_id)


class WontFixIssueListView(generics.ListAPIView, ProjectBaseAPIView):
    """无需修复问题列表

    ### GET
    应用场景：查询指定代码库的无效问题列表
    """
    serializer_class = serializers.WontFixIssueSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.WontFixIssueFilterSet

    def get_queryset(self):
        repo_id = self.get_repo_id()
        return models.WontFixIssue.objects.filter(project__repo_id=repo_id)
