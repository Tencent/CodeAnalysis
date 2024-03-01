# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util.permissions
"""


from rest_framework import permissions
from django.shortcuts import get_object_or_404

from apps.job.models import Job


class JobPermission(permissions.BasePermission):
    """任务关联代码库管理员权限

    通过Job编号获取关联的代码库编号，查询当前用户是否有管理员权限
    """

    def has_permission(self, request, view):
        """检查当前用户是否审批通过
        """
        job_id = view.kwargs.get("job_id")
        if not job_id:
            return False
        job = get_object_or_404(Job, id=job_id)
        repo = job.project.repo
        return request.user and (
            request.method in permissions.SAFE_METHODS and
            request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)) \
            or request.user.has_perm(repo.PermissionNameEnum.CHANGE_REPO_PERM, repo)


class JobUserPermission(permissions.BasePermission):
    """任务关联代码库用户权限

    通过Job编号获取关联的代码库编号，查询当前用户是否有普通成员权限
    """

    def has_permission(self, request, view):
        """检查当前用户是否审批通过
        """
        job_id = view.kwargs.get("job_id")
        if not job_id:
            return False
        job = get_object_or_404(Job, id=job_id)
        repo = job.project.repo
        return request.user and request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)

