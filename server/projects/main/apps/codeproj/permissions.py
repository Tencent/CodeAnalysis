# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - permission 模块
"""
# 原生 import
import logging

# 第三方 import
from django.shortcuts import get_object_or_404
from rest_framework import permissions

# 项目内 import
from apps.authen.permissions import CodeDogUserPermission
from apps.codeproj.core import ScanSchemePermManager
from apps.codeproj.models import Organization, Project, ProjectTeam, Repository, ScanScheme

logger = logging.getLogger(__name__)


class ProjectTeamDefaultPermission(CodeDogUserPermission):
    """项目组默认权限判断

    适用于非管理员只能查看的接口

    > 需团队验证通过，当前用户如果是团队管理员则都可操作，否则仅项目管理员可操作，普通成员可查看
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(ProjectTeamDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        team_name = view.kwargs.get("team_name")
        if not org_sid or not team_name:
            return False
        project_team = get_object_or_404(ProjectTeam.active_pts, name=team_name, organization__org_sid=org_sid)
        if not project_team.organization.validate_org_checked():
            return False
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS and
                   request.user.has_perm(ProjectTeam.PermissionNameEnum.VIEW_TEAM_PERM, project_team)) \
               or request.user.has_perm(ProjectTeam.PermissionNameEnum.CHANGE_TEAM_PERM, project_team) \
               or request.user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, project_team.organization)


class ProjectTeamOperationPermission(CodeDogUserPermission):
    """项目组操作权限判断

    适用于非管理员需要创建代码库的接口

    > 需团队验证通过，当前用户如果是团队管理员、项目管理员、项目成员均可操作
      适用于项目成员创建代码库，开启扫描的接口
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(ProjectTeamOperationPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        team_name = view.kwargs.get("team_name")
        if not org_sid or not team_name:
            return False
        project_team = get_object_or_404(ProjectTeam.active_pts, name=team_name, organization__org_sid=org_sid)
        if not project_team.organization.validate_org_checked():
            return False
        return self.is_check_adminuser(request.user) \
               or request.user.has_perm(ProjectTeam.PermissionNameEnum.VIEW_TEAM_PERM, project_team) \
               or request.user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, project_team.organization)


class RepositoryDefaultPermission(CodeDogUserPermission):
    """代码库默认权限判断

    适用于更新、配置代码库等操作

    > 需团队验证通过，当前用户如果是团队管理员、项目管理员、代码库创建者或管理员可操作，项目普通成员可查看
    """

    def has_permission(self, request, view):
        result = super(RepositoryDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        team_name = view.kwargs.get("team_name")
        repo_id = view.kwargs.get("repo_id")
        if not org_sid or not team_name or not repo_id:
            return False
        project_team = get_object_or_404(ProjectTeam.active_pts, name=team_name, organization__org_sid=org_sid)
        if not project_team.organization.validate_org_checked():
            return False
        repo = get_object_or_404(Repository, id=repo_id, project_team=project_team)
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS and
                   request.user.has_perm(ProjectTeam.PermissionNameEnum.VIEW_TEAM_PERM, project_team)) \
               or request.user == repo.creator \
               or request.user.has_perm(Repository.PermissionNameEnum.CHANGE_REPO_PERM, repo) \
               or request.user.has_perm(ProjectTeam.PermissionNameEnum.CHANGE_TEAM_PERM, project_team) \
               or request.user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, project_team.organization)


class RepositorySchemeDefaultPermission(CodeDogUserPermission):
    """代码库扫描方案默认权限判断

    适用于更新、配置扫描方案操作

    > 需团队验证通过，当前用户如果是团队管理员、项目管理员、代码库创建者或管理员、扫描方案创建者可操作，项目普通成员可查看
    """

    def has_permission(self, request, view):
        result = super(RepositorySchemeDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        team_name = view.kwargs.get("team_name")
        repo_id = view.kwargs.get("repo_id")
        scheme_id = view.kwargs.get("scheme_id")
        return self.has_repo_scheme_permission(request, org_sid, team_name, repo_id, scheme_id)

    def has_repo_scheme_permission(self, request, org_sid, team_name, repo_id, scheme_id):
        """代码库扫描方案默认权限判断
        """
        if not org_sid or not team_name or not repo_id or not scheme_id:
            return False
        project_team = get_object_or_404(ProjectTeam.active_pts, name=team_name, organization__org_sid=org_sid)
        if not project_team.organization.validate_org_checked():
            return False
        scheme = get_object_or_404(ScanScheme, id=scheme_id, repo_id=repo_id, repo__project_team=project_team)
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS and
                   request.user.has_perm(ProjectTeam.PermissionNameEnum.VIEW_TEAM_PERM, project_team)) \
               or request.user == scheme.creator \
               or request.user == scheme.repo.creator \
               or request.user.has_perm(Repository.PermissionNameEnum.CHANGE_REPO_PERM, scheme.repo) \
               or request.user.has_perm(ProjectTeam.PermissionNameEnum.CHANGE_TEAM_PERM, project_team) \
               or request.user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, project_team.organization)


class RepositoryProjectDefaultPermission(CodeDogUserPermission):
    """代码库分支项目默认权限判断

    适用于更新、配置分支项目操作

    > 需团队验证通过，当前用户如果是团队管理员、项目管理员、代码库创建者或管理员、分支项目创建者可操作，项目普通成员可查看
    """

    def has_permission(self, request, view):
        result = super(RepositoryProjectDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        team_name = view.kwargs.get("team_name")
        repo_id = view.kwargs.get("repo_id")
        project_id = view.kwargs.get("project_id")
        logger.info(project_id)
        if not org_sid or not team_name or not repo_id or not project_id:
            return False
        project_team = get_object_or_404(ProjectTeam.active_pts, name=team_name, organization__org_sid=org_sid)
        if not project_team.organization.validate_org_checked():
            return False
        project = get_object_or_404(Project, id=project_id, repo_id=repo_id, repo__project_team=project_team)
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS
                   and request.user.has_perm(ProjectTeam.PermissionNameEnum.VIEW_TEAM_PERM, project_team)) \
               or request.user == project.creator \
               or request.user == project.repo.creator \
               or request.user.has_perm(Repository.PermissionNameEnum.CHANGE_REPO_PERM, project.repo) \
               or request.user.has_perm(ProjectTeam.PermissionNameEnum.CHANGE_TEAM_PERM, project_team) \
               or request.user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, project_team.organization)


class GlobalSchemeDefaultPermission(CodeDogUserPermission):
    """分析方案模板默认权限判断

    适用于更新、配置分析方案模板操作

    > 需团队验证通过，如果当前用户是方案模板管理员可操作，否则团队内成员可查看
    """

    def has_permission(self, request, view):
        result = super(GlobalSchemeDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        scheme_id = view.kwargs.get("scheme_id")
        if not org_sid or not scheme_id:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        scheme = ScanScheme.objects.filter(id=scheme_id, repo__isnull=True,
                                           scheme_key=ScanScheme.SchemeKey.PUBLIC).first()
        if not scheme:
            scheme = get_object_or_404(ScanScheme, id=scheme_id, repo__isnull=True, scheme_key='org_%s' % org_sid)
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS and
                   ScanSchemePermManager.check_user_view_perm(scheme, request.user, org_sid)) \
               or (scheme.scheme_key != ScanScheme.SchemeKey.PUBLIC and
                   ScanSchemePermManager.check_user_edit_manager_perm(scheme, request.user))


class SchemeDefaultPermission(RepositorySchemeDefaultPermission):
    """分析方案模板权限判断
    根据不同调用接口，进行不同的权限判断

    > 代码块分析方案：需团队验证通过，当前用户如果是团队管理员、项目管理员、代码库创建者或管理员、扫描方案创建者可操作，项目普通成员可查看

    > 分析方案模板：需团队验证通过，如果当前用户是方案模板管理员可操作，否则团队内成员可查看
    """
    def has_repo_scheme_permission(self, request, org_sid, team_name, repo_id, scheme_id):
        """代码库扫描方案默认权限判断

        适用于更新、配置扫描方案操作

        > 需团队验证通过，当前用户如果是团队管理员、项目管理员、代码库创建者或管理员、扫描方案创建者可操作，项目普通成员可查看
        """
        project_team = get_object_or_404(ProjectTeam.active_pts, name=team_name, organization__org_sid=org_sid)
        if not project_team.organization.validate_org_checked():
            return False
        scheme = get_object_or_404(ScanScheme, id=scheme_id, repo_id=repo_id, repo__project_team=project_team)
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS
                   and request.user.has_perm("view_projectteam", project_team)) \
               or request.user == scheme.creator \
               or request.user == scheme.repo.creator or request.user.has_perm("change_repository", scheme.repo) \
               or request.user.has_perm("change_projectteam", project_team) \
               or request.user.has_perm('change_organization', project_team.organization)

    def has_global_scheme_permission(self, request, org_sid, scheme_id):
        """分析方案模板默认权限判断

        适用于更新、配置分析方案模板操作

        > 需团队验证通过，如果当前用户是方案模板管理员可操作，否则团队内成员可查看
        """
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        scheme = ScanScheme.objects.filter(id=scheme_id, repo__isnull=True,
                                           scheme_key=ScanScheme.SchemeKey.PUBLIC).first()
        if not scheme:
            scheme = get_object_or_404(ScanScheme, id=scheme_id, repo__isnull=True, scheme_key='org_%s' % org_sid)
        return self.is_check_adminuser(request.user) \
               or (request.method in permissions.SAFE_METHODS
                   and ScanSchemePermManager.check_user_view_perm(scheme, request.user, org_sid)) \
               or (scheme.scheme_key != ScanScheme.SchemeKey.PUBLIC
                   and ScanSchemePermManager.check_user_edit_manager_perm(scheme, request.user))

    def has_permission(self, request, view):
        result = CodeDogUserPermission.has_permission(self, request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        team_name = view.kwargs.get("team_name")
        repo_id = view.kwargs.get("repo_id")
        scheme_id = view.kwargs.get("scheme_id")
        if org_sid and team_name and repo_id and scheme_id:
            # 代码库分析方案相关接口
            return self.has_repo_scheme_permission(request, org_sid, team_name, repo_id, scheme_id)
        elif org_sid and scheme_id:
            # 分析方案模板相关接口
            return self.has_global_scheme_permission(request, org_sid, scheme_id)
        return False
