# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codemetric.core.duplicatemgr
DuplicateCode core logic
"""

from django.db.models import Q
from apps.codemetric import models


class DuplicateIssueOwnerManager(object):
    """重复文件责任人管理
    """
    @classmethod
    def update_issue_owner(cls, issue_model, operator, issue, new_owner, change_all):
        """更新Issue的责任人
        :return:
        """
        old_owner = issue.owner
        if not change_all:
            issue.owner = new_owner
            issue.save()
            action = '修改责任人'
            message = '%s -> %s' % (old_owner, new_owner)
            DuplicateIssueCommentManager.create_issue_comment(
                creator=operator, project_id=issue.project_id, issue_id=issue.id, message=message, action=action)
            cls.update_project_dup_file_owner(issue.project_id, [issue.id], new_owner)
        else:
            issues = issue_model.objects.filter(
                Q(project=issue.project, owner=old_owner, state=models.DuplicateIssue.StateEnum.ACTIVE) | Q(id=issue.id)
            )
            issues.update(author=new_owner)
            issue_ids = issues.values_list('id', flat=True)
            action = '批量修改责任人'
            message = '%s -> %s (源issue id:%d)' % (old_owner, new_owner, issue.id)
            DuplicateIssueCommentManager.bulk_create_issue_comment(
                creator=operator, project_id=issue.project_id, issue_ids=issue_ids, message=message, action=action)
            cls.update_project_dup_file_owner(issue.project_id, [issue_ids], new_owner)
        issue.refresh_from_db()
        return issue

    @classmethod
    def update_project_dup_file_owner(cls, project_id, issue_ids, new_owner):
        """修改指定项目指定问题的重复文件负责人
        """
        models.ProjectDuplicateFileFactory.shard(project_id).objects.filter(
            project_id=project_id, issue_id__in=issue_ids).update(issue_owner=new_owner)


class DuplicateIssueStateManager(object):
    """重复文件状态管理
    """
    @classmethod
    def update_issue_state(cls, operator, issue, new_state):
        """更新Issue的状态值
        :param operator: str，操作人
        :param issue: DuplicateIssue，待调整的Issue
        :param new_state: int，状态值
        :return: DuplicateIssue
        """
        old_state = issue.state
        issue.state = new_state
        issue.save()
        cls.update_project_dup_file_state(issue.project_id, [issue.id], new_state)
        action = '修改状态'
        message = '%s -> %s' % (models.DuplicateIssue.STATE_CHOICES_DICT[old_state],
                                models.DuplicateIssue.STATE_CHOICES_DICT[new_state])
        DuplicateIssueCommentManager.create_issue_comment(
            operator, issue.project_id, issue.id, action=action, message=message)
        return issue

    @classmethod
    def update_project_dup_file_state(cls, project_id, issue_ids, state):
        """修改指定项目指定问题的重复文件状态
        """
        models.ProjectDuplicateFileFactory.shard(project_id).objects.filter(
            project_id=project_id, issue_id__in=issue_ids).update(issue_state=state)


class DuplicateIssueCommentManager(object):
    """重复文件评论管理
    """

    @classmethod
    def create_issue_comment(cls, creator, project_id, issue_id, action, message):
        """创建Issue评论
        :param creator: str，创建人
        :param project_id: int, 项目编号
        :param issue_id: int，Issue编号
        :param action: str，操作
        :param message: str，描述
        :return: DuplicateIssueComment
        """

        models.ProjectDuplicateIssueCommentFactory.shard(project_id).objects.create(
            creator=creator, project_id=project_id, issue_id=issue_id, action=action, message=message
        )

    @classmethod
    def bulk_create_issue_comment(cls, creator, project_id, issue_ids, action, message):
        """批量创建Issue评论
        :param creator: str，创建人
        :param project_id: int, 项目编号
        :param issue_ids: list，Issue列表
        :param action: str，操作
        :param message: str，描述
        :return:
        """
        issue_comment_model = models.ProjectDuplicateIssueCommentFactory.shard(project_id)
        comments = [issue_comment_model(project_id=project_id, issue_id=issue_id,
                                        action=action, message=message, creator=creator)
            for issue_id in issue_ids
        ]
        issue_comment_model.objects.bulk_create(comments, 1000)
