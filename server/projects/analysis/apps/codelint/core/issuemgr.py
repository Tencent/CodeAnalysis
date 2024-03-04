# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint issuemgr
"""

import logging

from django.db.models import Q
from django.utils import timezone

from apps.codelint import models
from util.webclients import MainClient

logger = logging.getLogger(__name__)


class CodeLintIssueDetailManager(object):
    """Codelint问题管理
    """

    @classmethod
    def get_issue_details(cls, issue):
        first_issue_detail = models.IssueDetail.objects.filter(issue_hash=issue.issue_hash).first()
        scan_revision = first_issue_detail.scan_revision if first_issue_detail else None
        issue_details = models.IssueDetail.objects.filter(
            issue_hash=issue.issue_hash, scan_revision=scan_revision)
        return issue_details

    @classmethod
    def get_current_issue_details(cls, issue):
        return cls.get_issue_details(issue)


class CodeLintIssueResolutionManager(object):
    """Codelint问题解决方式管理
    """

    @classmethod
    def get_scope_msg(cls, scope):
        """获取范围数据
        """
        if scope == models.InvalidIssue.ScopeEnum.REPO:
            return "[全局范围]"
        else:
            return ""

    @classmethod
    def update_issues_resolution(cls, operator, issues, new_resolution, scope, ignore_reason=None):
        """批量更新指定Issue列表的解决方式
        :param operator: str，操作者名称
        :param issues: list, Issue列表
        :param new_resolution: int，新的解决方式
        :param scope: int，作用范围
        :param ignore_reason: str，忽略理由
        :return: int，更新个数
        """
        for issue in issues:
            cls.update_one_issue_resolution(
                operator, issue, new_resolution, scope, action="批量处理", ignore_reason=ignore_reason)

    @classmethod
    def update_one_issue_resolution(cls, operator, issue, new_resolution, scope, action=None, ignore_reason=None):
        """更新Issue解决方式
        :param operator: str，操作者名称
        :param issue: Issue
        :param new_resolution: int，解决方式
        :param scope: int，作用范围
        :param action: str, 描述
        :param ignore_reason: str，忽略理由
        :return: Issue
        """
        old_resolution = issue.resolution
        old_state = issue.state
        issue.resolution = new_resolution
        scope = scope if scope else models.InvalidIssue.ScopeEnum.PROJECT
        scope_msg = cls.get_scope_msg(scope)

        # 增删invalid / wontfix issue 记录
        invalidissue = models.InvalidIssue.everything.filter(issue=issue).first()
        wontfixissue = models.WontFixIssue.everything.filter(issue=issue).first()
        if old_resolution != models.Issue.ResolutionEnum.INVALID and \
                new_resolution == models.Issue.ResolutionEnum.INVALID:
            # add to invalid form, save modifier(including creator if created)
            if invalidissue:
                invalidissue.ext_field.update({"ignore_reason": ignore_reason})
                invalidissue.undelete(user=operator)
                invalidissue.scope = scope
                invalidissue.save(user=operator)
            else:
                invalidissue = models.InvalidIssue(
                    issue=issue, g_issue_hash=issue.g_issue_hash, scope=scope, project=issue.project,
                    ext_field={"ignore_reason": ignore_reason})
                invalidissue.save(user=operator)
        elif old_resolution == models.Issue.ResolutionEnum.INVALID and \
                new_resolution != models.Issue.ResolutionEnum.INVALID:
            # soft delete from invalid form
            if invalidissue:
                invalidissue.delete(user=operator)

        if old_resolution != models.Issue.ResolutionEnum.WONTFIX and \
                new_resolution == models.Issue.ResolutionEnum.WONTFIX:
            # add to invalid form, save modifier(including creator if created)
            if wontfixissue:
                wontfixissue.ext_field.update({"ignore_reason": ignore_reason})
                wontfixissue.undelete(user=operator)
                wontfixissue.scope = scope
                wontfixissue.save(user=operator)
            else:
                wontfixissue = models.WontFixIssue(
                    issue=issue, g_issue_hash=issue.g_issue_hash, scope=scope, project=issue.project,
                    ext_field={"ignore_reason": ignore_reason})
                wontfixissue.save(user=operator)
        elif old_resolution == models.Issue.ResolutionEnum.WONTFIX and \
                new_resolution != models.Issue.ResolutionEnum.WONTFIX:
            # soft delete from invalid form
            if wontfixissue:
                wontfixissue.delete(user=operator)

        # 同步修改state
        if new_resolution == models.Issue.ResolutionEnum.DONOTHING:
            issue.state = models.Issue.StateEnum.ACTIVE
            issue.resolution = None
        elif new_resolution in [models.Issue.ResolutionEnum.FIXED, models.Issue.ResolutionEnum.WONTFIX,
                                models.Issue.ResolutionEnum.INVALID, models.Issue.ResolutionEnum.FILTER,
                                models.Issue.ResolutionEnum.HISTORY]:
            issue.state = models.Issue.StateEnum.RESOLVED
            issue.fixed_time = timezone.now()
        issue.save(user=operator)

        action = action if action is not None else "处理"
        message = "状态 %s -> %s，解决办法 %s -> %s，理由 %s" % (
            models.Issue.STATE_CHOICES_DICT.get(old_state),
            models.Issue.STATE_CHOICES_DICT[issue.state],
            models.Issue.RESOLUTION_CHOICES_DICT.get(old_resolution),
            models.Issue.RESOLUTION_CHOICES_DICT[new_resolution],
            ignore_reason
        )
        message += scope_msg
        CodeLintIssueCommentManager.create_issue_comment(operator, issue_id=issue.id, action=action,
                                                         message=message, project_id=issue.project_id)
        return issue


class CodeLintIssueAuthorManager(object):
    """Issue责任人管理
    """

    @classmethod
    def update_issue_author(cls, operator, issue, new_author, change_all, action=None):
        """更新Issue的责任人
        :return:
        """
        old_author = issue.author
        if not change_all:
            issue.author = new_author
            issue.save(user=operator)
            action = action or "修改责任人"
            message = "%s -> %s" % (old_author, new_author)
            CodeLintIssueCommentManager.create_issue_comment(
                creator=operator, issue_id=issue.id, message=message, action=action, project_id=issue.project_id)
        else:
            issues = models.Issue.everything.filter(
                Q(project=issue.project, author=old_author,
                  state=models.Issue.StateEnum.ACTIVE) | Q(id=issue.id)
            )
            issues.update(author=new_author)
            issue_ids = issues.values_list("id", flat=True)
            action = "批量修改责任人"
            message = "%s -> %s (源issue id:%d)" % (old_author,
                                                   new_author, issue.id)
            CodeLintIssueCommentManager.bulk_create_issue_comment(
                creator=operator, issue_ids=issue_ids, message=message, action=action, project_id=issue.project_id)
        issue.refresh_from_db()
        return issue

    @classmethod
    def update_issues_author(cls, operator, issues, new_author):
        """批量更新指定Issue列表的解决方式
        :param operator: str，操作者名称
        :param issues: list, Issue列表
        :param new_author: int，新的责任人
        :return: int，更新个数
        """
        for issue in issues:
            cls.update_issue_author(
                operator, issue, new_author, change_all=False, action="批量修改责任人")


class CodeLintIssueSeverityManager(object):
    """Issue优先级管理
    """

    @classmethod
    def update_issue_severity(cls, operator, issue, new_severity):
        """调整问题优先级
        :param operator: str
        :param issue: Issue
        :param new_severity: int，问题优先级
        :return: Issue
        """
        old_severity = issue.severity
        issue.severity = new_severity
        issue.save(user=operator)
        message = "%s -> %s" % (models.Issue.SEVERITY_CHOICES_DICT.get(old_severity),
                                models.Issue.SEVERITY_CHOICES_DICT[new_severity])
        CodeLintIssueCommentManager.create_issue_comment(
            operator, issue.id, action="修改优先级", message=message, project_id=issue.project_id)
        return issue


class CodeLintIssueCommentManager(object):
    @classmethod
    def create_issue_comment(cls, creator, issue_id, action, message, project_id):
        """创建Issue评论
        :param creator: str，创建人
        :param issue_id: int，Issue编号
        :param action: str，操作
        :param message: str，描述
        :param project_id: int，项目编号
        """
        models.IssueComment.objects.create(
            creator=creator, issue_id=issue_id, project_id=project_id, action=action, message=message)

    @classmethod
    def bulk_create_issue_comment(cls, creator, issue_ids, action, message, project_id):
        """批量创建Issue评论
        :param creator: str，创建人
        :param issue_ids: list，Issue列表
        :param action: str，操作
        :param message: str，描述
        :param project_id: int，项目编号
        :return:
        """
        comments = [models.IssueComment(
            issue_id=issue_id, action=action, project_id=project_id, message=message, creator=creator)
            for issue_id in issue_ids
        ]
        models.IssueComment.objects.bulk_create(comments, 1000)


class CodelintToolManager(object):
    """代码扫描工具管理
    """

    @classmethod
    def get_codelint_toolinfos(cls, tool_names):
        """获取工具列表
        """
        try:
            tools = MainClient().api("toolname_list", data={"tools": ",".join(tool_names)})
            tools = {tool["name"]: tool for tool in tools}
            return tools
        except Exception as err:
            logger.exception("get tool name list exception, error: %s" % err)
            return {}
