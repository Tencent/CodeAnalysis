# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - v3 apis
"""

# 项目内 import
from apps.codemetric.apis import v2
from apps.codeproj.apimixins import ProjectTeamBaseAPIView


class PTCCFileListView(v2.CCFileListView, ProjectTeamBaseAPIView):
    """圈复杂度文件列表接口

    ### GET
    应用场景：获取代码度量 圈复杂度文件列表
    """


class PTCCFileDetailView(v2.CCFileDetailView, ProjectTeamBaseAPIView):
    """圈复杂度文件详情接口

    ### GET
    应用场景：获取代码度量 圈复杂度文件详情
    """


class PTCCFileFileIssueListView(v2.CCFileFileIssueListView, ProjectTeamBaseAPIView):
    """圈复杂度文件问题列表接口

    ### GET
    应用场景：获取代码度量 圈复杂度文件问题列表
    """


class PTCCIssueListView(v2.CCIssueListView, ProjectTeamBaseAPIView):
    """圈复杂度列表接口

    ### GET
    应用场景：获取代码度量 圈复杂度问题列表
    """


class PTCCIssueHistoryListView(v2.CCIssueHistoryListView, ProjectTeamBaseAPIView):
    """指定扫描的圈复杂度列表接口

    ### GET
    应用场景：获取代码度量 指定扫描的圈复杂度问题列表，需要指定scan_id进行查询
    """


class PTCCIssueDetailView(v2.CCIssueDetailView, ProjectTeamBaseAPIView):
    """圈复杂度详情接口

    ### GET
    应用场景：获取圈复杂度issue详情
    """


class PTCCIssueStatusBulkUpdateView(v2.CCIssueStatusBulkUpdateView, ProjectTeamBaseAPIView):
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


class PTCCIssueAuthorUpdateView(v2.CCIssueAuthorUpdateView, ProjectTeamBaseAPIView):
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


class PTDupFileListView(v2.DupFileListView, ProjectTeamBaseAPIView):
    """重复代码问题列表接口

    ### GET
    应用场景：获取代码度量 重复代码问题列表
    """


class PTDupFileDetailView(v2.DupFileDetailView, ProjectTeamBaseAPIView):
    """重复代码问题详情接口

    ### GET
    应用场景：获取代码度量 重复代码问题详情

    """


class PTDupFileHistoryListView(v2.DupFileHistoryListView, ProjectTeamBaseAPIView):
    """重复文件历史扫描记录列表接口

    ### GET
    应用场景：获取指定文件的历史扫描记录
    """


class PTDupBlockListView(v2.DupBlockListView, ProjectTeamBaseAPIView):
    """指定文件的重复块列表

    ### GET
    应用场景：获取指定文件的重复内容列表
    """


class PTDupBlockDetailView(v2.DupBlockDetailView, ProjectTeamBaseAPIView):
    """指定文件的重复块详情

    ### GET
    应用场景：获取指定文件的重复内容详情
    """


class PTRelatedDupBlockListView(v2.RelatedDupBlockListView, ProjectTeamBaseAPIView):
    """指定重复块的关联块列表

    ### GET
    应用场景：获取指定块相关的代码块列表
    """


class PTDupIssueCommentListView(v2.DupIssueCommentListView, ProjectTeamBaseAPIView):
    """指定重复问题的评论列表

    ### GET
    应用场景：获取指定重复问题的评论列表
    """


class PTDupIssueOwnerUpdateView(v2.DupIssueOwnerUpdateView, ProjectTeamBaseAPIView):
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


class PTDupIssueStateUpdateView(v2.DupIssueStateUpdateView, ProjectTeamBaseAPIView):
    """重复问题状态更新接口

    ### PUT
    应用场景：修改重复issue state接口

    >###参数：
    >* state:指定问题状态，取值区间1-3  1="未处理"/2="可忽略"/3="关闭"

    >###返回：
    >* issue serializer

    ******
    """


class PTClocFileListView(v2.ClocFileListView, ProjectTeamBaseAPIView):
    """文件统计信息列表接口

    ### GET
    应用场景：获取所有文件统计信息
    """


class PTClocFileDetailView(v2.ClocFileDetailView, ProjectTeamBaseAPIView):
    """文件统计信息详情接口

    ### GET
    应用场景：获取指定文件编号的统计信息
    """


class PTClocDirFileListView(v2.ClocDirFileListView, ProjectTeamBaseAPIView):
    """目录统计信息列表接口

    ### GET
    应用场景：获取指定路径的子目录和子文件信息，并统计该目录的所有文件信息

    参数：
    > path: 目录路径，为空时为根目录
    """


class PTClocLanguageListView(v2.ClocLanguageListView, ProjectTeamBaseAPIView):
    """语言统计信息列表接口

    ### GET
    应用场景：获取项目各个语言的行数信息
    """
