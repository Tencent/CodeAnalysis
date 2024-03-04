# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
permissions - repoistory、project、scanscheme permissions
"""

import logging

from rest_framework import permissions
from django.shortcuts import get_object_or_404, Http404

from apps.codeproj.models import Project, Repository, ScanScheme, ScanSchemePerm
from apps.codeproj.core import ScanSchemePermManager


logger = logging.getLogger(__name__)


class RepositoryPermission(permissions.BasePermission):
    """代码库权限校验，通过url的repo_id来判定用户是否有权限访问
    """

    def has_permission(self, request, view):
        repo_id = view.kwargs.get("repo_id")
        if not repo_id:
            return False
        repo = get_object_or_404(Repository, id=repo_id)
        return (request.method in permissions.SAFE_METHODS
                and request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)) \
            or request.user.has_perm(repo.PermissionNameEnum.CHANGE_REPO_PERM, repo)


class RepositoryUserPermission(permissions.BasePermission):
    """代码库权限校验，通过url的repo_id来判定用户是否有权限访问
    """

    def has_permission(self, request, view):
        repo_id = view.kwargs.get("repo_id")
        if not repo_id:
            return False
        repo = get_object_or_404(Repository, id=repo_id)
        return request.user and request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)


class RepositorySchemePermission(permissions.BasePermission):
    """代码库扫描方案权限校验
    """

    def has_permission(self, request, view):
        repo_id = view.kwargs.get("repo_id")
        scheme_id = view.kwargs.get("scheme_id")
        if not repo_id or not scheme_id:
            return False
        repo = get_object_or_404(Repository, id=repo_id)
        scheme = get_object_or_404(ScanScheme, id=scheme_id)
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            # SAFE_METHODS
            return request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)
        schemeperm = ScanSchemePerm.objects.filter(scan_scheme=scheme).first()
        if schemeperm and schemeperm.edit_scope == ScanSchemePerm.ScopeEnum.PRIVATE:
            # 方案私有
            return schemeperm.check_user_edit_manager_perm(request.user)
        # 方案公开
        return request.user.has_perm(repo.PermissionNameEnum.CHANGE_REPO_PERM, repo)


class RepositoryProjectPermission(permissions.BasePermission):
    """代码库内项目管理员权限校验，通过url的project_id来判定用户是否有权限访问
    """

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id")
        if not project_id:
            return False
        project = get_object_or_404(Project, id=project_id)
        repo = project.repo
        return (request.method in permissions.SAFE_METHODS
                and request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)) \
            or request.user.has_perm(repo.PermissionNameEnum.CHANGE_REPO_PERM, repo)


class RepositoryProjectUserPermission(permissions.BasePermission):
    """代码库内项目用户权限校验，通过url的project_id来判定用户是否有权限访问
    """

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id")
        if not project_id:
            return False
        project = get_object_or_404(Project, id=project_id)
        repo = project.repo
        return request.user and request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)


class RepositoryProjectExecutePermission(permissions.BasePermission):
    """代码库内创建分支项目/启动分支项目扫描权限
    """

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id")
        if not project_id:
            return False
        project = get_object_or_404(Project, id=project_id)
        if request.user.is_superuser:
            return True
        schemeperm = ScanSchemePerm.objects.filter(scan_scheme=project.scan_scheme).first()
        if request.method not in permissions.SAFE_METHODS and schemeperm and \
                schemeperm.execute_scope == ScanSchemePerm.ScopeEnum.PRIVATE:
            return schemeperm.check_user_execute_manager_perm(request.user)
        repo = project.repo
        return request.user and request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo)


class ScanSchemePermission(permissions.BasePermission):
    """
    扫描方案权限校验，通过url的scheme_id来判断用户是否有权限访问
    """
    def has_permission(self, request, view):
        """权限判断
        """
        scheme_id = view.kwargs.get("scheme_id")
        if not scheme_id:
            return False
        if not request.user or not request.user.is_authenticated:
            return False
        scan_scheme = get_object_or_404(ScanScheme, id=scheme_id)
        if not request.user.is_superuser and not ScanSchemePermManager.check_user_view_perm(scan_scheme, request.user):
            logger.error("[User: %s] no permission to view scheme: %s" % (request.user, scan_scheme))
            raise Http404('No %s matches the given query.' % scan_scheme._meta.object_name)
        return request.user and request.user.is_authenticated and \
               (request.method in permissions.SAFE_METHODS or request.user.is_superuser or
                ScanSchemePermManager.check_user_edit_manager_perm(scan_scheme, request.user))
