# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - v1 apis for project team
"""

from apps.codelint.apis import v1
from apps.codeproj.apimixins import ProjectTeamBaseAPIView


class PTProjectIssueListView(v1.ProjectIssueListView, ProjectTeamBaseAPIView):
    """项目问题列表接口

    ### Get
    应用场景：查看指定项目的问题列表数据
    """


class PTProjectIssueWithDetailListView(v1.ProjectIssueWithDetailListView, ProjectTeamBaseAPIView):
    """项目问题详情列表接口(Issue列表包含IssueDetail）

    ### Get
    应用场景：查看指定项目的问题列表数据（包含问题详情数据）
    """


class PTProjectIssueDetailView(v1.ProjectIssueDetailView, ProjectTeamBaseAPIView):
    """项目问题详情

    ### Get
    应用场景：查看指定项目的指定问题详情
    """


class PTProjectLintIssueReport(v1.ProjectLintIssueReport, ProjectTeamBaseAPIView):
    """项目问题数据报告接口

    ### Get
    应用场景：获取指定项目的数据报告
    """


class PTProjectScanIssueSummaryAPIView(v1.ProjectScanIssueSummaryAPIView, ProjectTeamBaseAPIView):
    """项目扫描问题数据报告接口

    ### Get
    应用场景：获取指定项目的数据报告

    > 结果格式
    > {
        "current_scan": {  # 本次扫描
            "issue_open_num": 0,  # 新增问题量
            "issue_fix_num": 0,  # 关闭问题量
            "active_severity_detail": {  # 新增问题严重级别统计
                "fatal": 0,  # 致命
                "error": 0,  # 错误
                "warning": 0,  # 警告
                "info": 0  # 提示
            },
        },
        "total": {  # 存量问题
            "state_detail": {  # 总量统计
                "active": 0,
                "resolved": 0,
                "closed": 0
            },
            "severity_detail": {  # 按严重级别统计
                "fatal": {"active": 0, "resolved": 0, "closed": 0},  # 未处理，已处理，关闭
                "error": {"active": 0, "resolved": 0, "closed": 0},
                "warning": {"active": 0, "resolved": 0, "closed": 0},
                "info": {"active": 0, "resolved": 0, "closed": 0}
            },

        }
    }
    """
