# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - v3 apis
"""

import logging

# 项目内 import
from apps.codelint.apis import v2
from apps.codeproj.apimixins import ProjectTeamBaseAPIView

logger = logging.getLogger(__name__)


class PTProjectIssueListView(v2.ProjectIssueListView, ProjectTeamBaseAPIView):
    """项目问题列表接口

    ### Get
    应用场景：查看问题列表数据
    """


class PTProjectIssueDownloadView(v2.ProjectIssueDownloadView, ProjectTeamBaseAPIView):
    """项目问题列表下载接口

    ### Get
    应用场景：下载问题列表数据
    """


class PTIssueResolutionBulkUpdateView(v2.IssueResolutionBulkUpdateView, ProjectTeamBaseAPIView):
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


class PTIssueAuthorBulkUpdateView(v2.IssueAuthorBulkUpdateView, ProjectTeamBaseAPIView):
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


class PTProjectIssueAuthorsView(v2.ProjectIssueAuthorsView, ProjectTeamBaseAPIView):
    """问题责任人列表

    ### get
    应用场景：获取项目问题全部责任人列表，用于issue责任人筛选
    """


class PTIssueDetailView(v2.IssueDetailView, ProjectTeamBaseAPIView):
    """问题详情接口

    ### GET
    应用场景：获取issue详情
    """


class PTProjectIssueCheckRuleNumView(v2.ProjectIssueCheckRuleNumView, ProjectTeamBaseAPIView):
    """项目问题规则数

    ### GET
    应用场景：获取活跃问题规则数
    """


class PTIssueCommentsView(v2.IssueCommentsView, ProjectTeamBaseAPIView):
    """问题评论列表接口

    ### GET
    应用场景：获取issue评论列表

    ### POST
    应用场景：创建issue评论
    """


class PTIssueAuthorUpdateView(v2.IssueAuthorUpdateView, ProjectTeamBaseAPIView):
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


class PTIssueSeverityUpdateView(v2.IssueSeverityUpdateView, ProjectTeamBaseAPIView):
    """问题严重级别更新接口

    ### POST
    应用场景：修改issue severity接口

    >### 参数：
    >* severity:指定问题严重级别，取值范围：1～4, FATAL=1/ERROR=2/WARNING=3/INFO=4

    >### 返回：
    >* issue serializer

    ******
    """


class PTIssueResolutionUpdateView(v2.IssueResolutionUpdateView, ProjectTeamBaseAPIView):
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


class PTInvalidIssueListView(v2.InvalidIssueListView, ProjectTeamBaseAPIView):
    """无效问题列表

    ### GET
    应用场景：查询指定代码库的无效问题列表
    """


class PTWontFixIssueListView(v2.WontFixIssueListView, ProjectTeamBaseAPIView):
    """无需修复问题列表

    ### GET
    应用场景：查询指定代码库的无效问题列表
    """
