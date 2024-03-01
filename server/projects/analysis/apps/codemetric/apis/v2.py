# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - v2 apis
"""
# 原生 import
import logging
from urllib.parse import unquote

# 第三方 import
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import ParseError
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

# 项目内 import
from apps.codemetric import serializers, models, core, filters
from apps.codeproj.apimixins import ProjectBaseAPIView

logger = logging.getLogger(__name__)


class CCFileListView(generics.ListAPIView, ProjectBaseAPIView):
    """圈复杂度文件列表接口

    ### GET
    应用场景：获取代码度量 圈复杂度文件列表
    """
    serializer_class = serializers.CyclomaticComplexityFileSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = filters.MetricCCFileFilterSet

    ordering_fields = "__all__"

    def get_queryset(self):
        project = self.get_project()
        return models.CyclomaticComplexityFile.objects.select_related("project").filter(project_id=project.id)


class CCFileDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """圈复杂度文件详情接口

    ### GET
    应用场景：获取代码度量 圈复杂度文件详情
    """
    serializer_class = serializers.CyclomaticComplexityFileSerializer

    def get_queryset(self):
        project = self.get_project()
        return models.CyclomaticComplexityFile.objects.filter(project_id=project.id)

    def get_object(self):
        project = self.get_project()
        ccfile_id = self.kwargs.get("file_id")
        return get_object_or_404(models.CyclomaticComplexityFile, project_id=project.id, id=ccfile_id)


class CCFileFileIssueListView(generics.ListAPIView, ProjectBaseAPIView):
    """圈复杂度文件问题列表接口

    ### GET
    应用场景：获取代码度量 圈复杂度文件问题列表
    """
    serializer_class = serializers.DetailedCyclomaticComplexitySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = filters.MetricCCNIssueFilterSet

    ordering_fields = "__all__"

    def get_queryset(self):
        project = self.get_project()
        ccfile_id = self.kwargs.get("file_id")
        cc_file = get_object_or_404(models.CyclomaticComplexityFile, project_id=project.id, id=ccfile_id)
        return models.CyclomaticComplexity.everything.filter(
            project_id=project.id, file_hash=cc_file.file_hash, is_latest=True)


class CCIssueListView(generics.ListAPIView, ProjectBaseAPIView):
    """圈复杂度列表接口

    ### GET
    应用场景：获取代码度量 圈复杂度问题列表
    """
    serializer_class = serializers.CyclomaticComplexitySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.MetricCCNIssueFilterSet

    ordering_fields = "__all__"
    ordering = ["-id"]

    def get_queryset(self):
        project = self.get_project()
        return models.CyclomaticComplexity.everything.filter(project_id=project.id, is_latest=True)


class CCIssueHistoryListView(generics.ListAPIView, ProjectBaseAPIView):
    """指定扫描的圈复杂度列表接口

    ### GET
    应用场景：获取代码度量 指定扫描的圈复杂度问题列表，需要指定scan_id进行查询
    """
    serializer_class = serializers.CyclomaticComplexitySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = filters.MetricCCNIssueFilterSet

    ordering_fields = "__all__"
    ordering = ["-id"]

    def get_scan_id(self):
        """获取扫描编号
        """
        try:
            return int(self.request.query_params.get("scan_id"))
        except Exception:
            return None

    def get_queryset(self):
        project = self.get_project()
        scan_id = self.get_scan_id()
        if not scan_id:
            raise ParseError({"cd_error": "请指定扫描任务编号"})
        return models.CyclomaticComplexity.objects.filter(project_id=project.id, scan_open__scan_id=scan_id)


class CCIssueDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """圈复杂度详情接口

    ### GET
    应用场景：获取圈复杂度issue详情
    """
    serializer_class = serializers.DetailedCyclomaticComplexitySerializer
    lookup_url_kwarg = "issue_id"

    def get_queryset(self):
        project = self.get_project()
        return models.CyclomaticComplexity.objects.filter(project_id=project.id)


class CCIssueStatusBulkUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """圈复杂度问题状态批量更新接口

    ### PUT
    应用场景：批量更新圈复杂度问题状态
    > ### 参数:
    >* cc_issues: 圈复杂度问题编号
    >* status: 问题状态，1为需要关注，2为无需关注

    >### 格式：

    ```python
    {
        "ccissue_ids": [1,2],
        "status":  1 or 2
    }
    ```

    >### 返回：
    >* http200
    """

    def check_status_valid(self, status):
        """检查问题状态是否有效
        :param status: int，问题状态
        """
        if models.CyclomaticComplexity.STATUS_CHOICES_DICT.get(status) is None:
            raise ParseError("参数异常，`Status` 值[%s]错误" % status)

    def put(self, request, *args, **kwargs):
        project = self.get_project()
        issue_ids = request.data.get("ccissue_ids")
        new_status = request.data.get("status")
        if not isinstance(issue_ids, list):
            raise ParseError("参数异常, `issue_ids`不是list格式")
        self.check_status_valid(new_status)
        issues = models.CyclomaticComplexity.objects.filter(project_id=project.id, id__in=issue_ids)
        core.CCIssueManager.bulk_update_issues_status(request.user.username, issues, new_status)
        return Response(data={"msg": "success"})


class CCIssueAuthorUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """圈复杂度责任人修改

    ### PUT
    应用场景：修改圈复杂度issue 责任人

    >###参数：
    >* author:指定问题责任人

    >### 格式：

    ```python
     {
        "author": "xxx"
     }
    ```

    >###返回：

    ```pythoon

    ```

    ******

    应用场景：修改cc issue 的责任人
    """

    def put(self, request, *args, **kwargs):
        project_id = kwargs["project_id"]
        issue_id = kwargs["issue_id"]
        self.get_project()
        cc = get_object_or_404(models.CyclomaticComplexity, id=issue_id, project_id=project_id)
        cc = core.CCIssueManager.update_issue_author(cc, request.user.username, request.data['author'])
        serializer = serializers.CyclomaticComplexitySerializer(instance=cc)
        return Response(serializer.data)


class DupFileListView(generics.ListAPIView, ProjectBaseAPIView):
    """重复代码问题列表接口

    ### GET
    应用场景：获取代码度量 重复代码问题列表
    """
    serializer_class = serializers.DuplicateFileSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = filters.MetricDupFileFilterSet
    ordering_fields = [field.name for field in models.DuplicateFile._meta.fields] + ["issue_owner", "issue_state"]
    ordering = ["-id"]

    def get_queryset(self):
        project = self.get_project()
        return models.DuplicateFile.objects.filter(is_latest=True, project_id=project.id)


class DupFileDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """重复代码问题详情接口

    ### GET
    应用场景：获取代码度量 重复代码问题详情

    """
    serializer_class = serializers.DuplicateFileDetailSerializer
    lookup_url_kwarg = "file_id"

    def get_queryset(self):
        project = self.get_project()
        return models.DuplicateFile.objects.filter(project_id=project.id)


class DupFileHistoryListView(generics.ListAPIView, ProjectBaseAPIView):
    """重复文件历史扫描记录列表接口

    ### GET
    应用场景：获取指定文件的历史扫描记录
    """
    serializer_class = serializers.DuplicateFileSerializer

    def get_queryset(self):
        project = self.get_project()
        file_id = self.kwargs['file_id']
        dup_file = get_object_or_404(models.DuplicateFile, id=file_id)
        return models.DuplicateFile.objects.filter(
            project_id=project.id, issue_hash=dup_file.issue_hash).order_by("-id")[:10][::-1]  # 取最后10条记录


class DupBlockListView(generics.ListAPIView, ProjectBaseAPIView):
    """指定文件的重复块列表

    ### GET
    应用场景：获取指定文件的重复内容列表
    """
    serializer_class = serializers.DuplicateBlockSerializer

    def get_queryset(self):
        project = self.get_project()
        file_id = self.kwargs["file_id"]
        return models.DuplicateBlock.objects.filter(
            duplicate_file__project_id=project.id, duplicate_file_id=file_id
        ).order_by("start_line_num", "-end_line_num")


class DupBlockDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """指定文件的重复块详情

    ### GET
    应用场景：获取指定文件的重复内容详情
    """
    serializer_class = serializers.DuplicateBlockDetailSerializer

    def get_object(self):
        project = self.get_project()
        file_id = self.kwargs["file_id"]
        block_id = self.kwargs['block_id']

        return get_object_or_404(models.DuplicateBlock,
                                 duplicate_file__project_id=project.id,
                                 duplicate_file_id=file_id,
                                 id=block_id)


class RelatedDupBlockListView(generics.ListAPIView, ProjectBaseAPIView):
    """指定重复块的关联块列表

    ### GET
    应用场景：获取指定块相关的代码块列表
    """

    serializer_class = serializers.RelatedDuplicateBlockSerializer

    def get_queryset(self):
        project = self.get_project()
        file_id = self.kwargs["file_id"]
        block_id = self.kwargs['block_id']

        dup_block = get_object_or_404(
            models.DuplicateBlock, duplicate_file__project_id=project.id, duplicate_file_id=file_id, id=block_id)
        return models.DuplicateBlock.objects.filter(
            block_hash=dup_block.block_hash,
            duplicate_file__scan=dup_block.duplicate_file.scan
        ).exclude(id=dup_block.id)


class DupIssueCommentListView(generics.ListAPIView, ProjectBaseAPIView):
    """指定重复问题的评论列表

    ### GET
    应用场景：获取指定重复问题的评论列表
    """
    serializer_class = serializers.DuplicateIssueCommentSerializer

    def get_queryset(self):
        self.get_project()
        issue_id = self.kwargs['issue_id']
        return models.DuplicateIssueComment.objects.filter(issue_id=issue_id).order_by("-id")[:20]


class DupIssueOwnerUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """重复问题责任人更新接口

    ### PUT

    应用场景：修改重复issue owner接口

    >###参数：
    >* owner:指定问题责任人list，多人以英文;隔开
    >* all: true or false, 为true时批量修改责任人，默认为false

    >### 格式：
    ```python
     {
        "owner": "xxx",
        "all": true
     }
     ```

    >###返回：
    >* issue serializer

    ******
    """

    serializer_class = serializers.DuplicateIssueSerializer

    def check_author_valid(self, current_owner, new_owner):
        """检查责任人字段有效性
        :param current_owner: str，现有责任人
        :param new_owner: str，新责任人
        """
        if not new_owner:
            raise ParseError("责任人不可以为空")

        if current_owner == new_owner:
            raise ParseError("新责任人不可以与原责任人相同")

    def put(self, request, *args, **kwargs):
        project_id = kwargs["project_id"]
        issue_id = kwargs["issue_id"]
        self.get_project()
        new_owner = request.data["owner"]
        change_all = request.data.get("all", False) is True
        issue = get_object_or_404(models.DuplicateIssue, id=issue_id, project_id=project_id)
        self.check_author_valid(issue.owner, new_owner)
        issue = core.DuplicateIssueOwnerManager.update_issue_owner(
            models.DuplicateIssue, request.user.username, issue, new_owner, change_all)
        serializer = self.get_serializer(instance=issue)
        return Response(serializer.data)


class DupIssueStateUpdateView(generics.GenericAPIView, ProjectBaseAPIView):
    """重复问题状态更新接口

    ### PUT
    应用场景：修改重复issue state接口

    >###参数：
    >* state:指定问题状态，取值区间1-3  1="未处理"/2="可忽略"/3="关闭"

    >###返回：
    >* issue serializer

    ******
    """

    serializer_class = serializers.DuplicateIssueSerializer

    def check_state_valid(self, state):
        """检查状态值是否有效
        :param state: int，状态值
        """
        if models.DuplicateIssue.STATE_CHOICES_DICT.get(state) is None:
            raise ParseError("State 值错误")

    def put(self, request, *args, **kwargs):
        project_id = kwargs["project_id"]
        issue_id = kwargs["issue_id"]
        self.get_project()
        new_state = int(request.data["state"])
        self.check_state_valid(state=new_state)
        issue = get_object_or_404(models.DuplicateIssue, id=int(issue_id), project_id=project_id)
        core.DuplicateIssueStateManager.update_issue_state(request.user.username, issue, new_state)
        serializer = self.get_serializer(instance=issue)
        return Response(serializer.data)


class ClocFileListView(generics.ListAPIView, ProjectBaseAPIView):
    """文件统计信息列表接口

    ### GET
    应用场景：获取所有文件统计信息
    """
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.MetricClocFileFilterSet
    serializer_class = serializers.ClocFileSerializer

    def get_queryset(self):
        self.get_project()
        return models.ClocFile.objects.filter(project_id=self.kwargs["project_id"], is_latest=True)


class ClocFileDetailView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """文件统计信息详情接口

    ### GET
    应用场景：获取指定文件编号的统计信息
    """

    serializer_class = serializers.ClocFileSerializer

    def get_queryset(self):
        self.get_project()
        return models.ClocFile.objects.filter(project_id=self.kwargs["project_id"], is_latest=True)

    def get_object(self):
        project = self.get_project()
        file_id = self.kwargs["file_id"]
        return get_object_or_404(models.ClocFile, id=file_id, project_id=project.id, is_latest=True)


class ClocDirFileListView(generics.GenericAPIView, ProjectBaseAPIView):
    """目录统计信息列表接口

    ### GET
    应用场景：获取指定路径的子目录和子文件信息，并统计该目录的所有文件信息

    参数：
    > path: 目录路径，为空时为根目录
    """

    def get(self, request, *args, **kwargs):
        project_id = kwargs["project_id"]
        self.get_project()
        path = request.query_params.get('path') or ""
        path = unquote(path)
        cloc_dirs = core.ClocDirFileManager.filter_cloc_dirs_by_project_id_and_path(
            models.ClocDir, project_id=project_id, path=path)
        cloc_files = core.ClocDirFileManager.filter_cloc_files_by_project_id_and_path(
            models.ClocFile, project_id=project_id, path=path)
        cloc_dir_sum = core.ClocDirFileManager.get_cloc_dir_sum_by_project_id_and_path(
            models.ClocDir, project_id=project_id, start_path=path)
        return Response({"dirs": {
            "count": cloc_dirs.count(),
            "results": serializers.ClocDirSerializer(cloc_dirs, many=True).data
        },
            "files": {
                "count": cloc_files.count(),
                "results": serializers.ClocFileSerializer(cloc_files, many=True).data
            },
            "info": cloc_dir_sum
        })


class ClocLanguageListView(generics.ListAPIView, ProjectBaseAPIView):
    """语言统计信息列表接口

    ### GET
    应用场景：获取项目各个语言的行数信息
    """

    serializer_class = serializers.ClocLanguageSerializer

    def get_queryset(self):
        self.get_project()
        return models.ClocLanguage.objects.filter(project_id=self.kwargs["project_id"], is_latest=True)
