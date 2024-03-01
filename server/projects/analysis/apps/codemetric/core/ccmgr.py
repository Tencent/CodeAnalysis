# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codemetric.core.ccmgr

CyclomaticComplexity core logic
"""


class CCIssueManager(object):
    """CCIssue管理
    """

    @classmethod
    def update_issue_author(cls, cc_issue, operator, author):
        """修改Issue责任人
        :param cc_issue: CyclomaticComplexity
        :param operator: str, 操作人
        :param author: str，责任人
        :return: CyclomaticComplexity
        """
        cc_issue.author = author
        cc_issue.save(user=operator)
        return cc_issue

    @classmethod
    def update_issue_status(cls, operator, cc_issue, status):
        """修改Issue状态
        :param operator: str，责任人
        :param cc_issue: CyclomaticComplexity
        :param status: int，新状态
        :return: CyclomaticComplexity
        """
        cc_issue.status = status
        cc_issue.save(user=operator)
        return cc_issue

    @classmethod
    def bulk_update_issues_status(cls, operator, cc_issues, status):
        """批量修改Issue状态
        :param operator: str，责任人
        :param cc_issues: CyclomaticComplexity
        :param status: int，新状态
        :return: list，CyclomaticComplexity
        """
        updated_cc_issues = []
        for cc_issue in cc_issues:
            updated_cc_issues.append(cls.update_issue_status(cc_issue=cc_issue, status=status, operator=operator))
        return updated_cc_issues
