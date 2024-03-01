# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.authen.permission 模块
"""

import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from apps.authen.core import CodeDogUserManager
from apps.authen.models import CodeDogUser, Organization

logger = logging.getLogger(__name__)


class CodeDogUserPermission(permissions.BasePermission):
    """CodeDog用户鉴权权限判断
    """

    def has_permission(self, request, view):
        """检查当前用户是否审批通过
        """
        authenticated = bool(request.user and request.user.is_authenticated)
        if not authenticated:
            return authenticated
        codedog_user = CodeDogUserManager.get_codedog_user(request.user)
        if not codedog_user.validate_codedog_user_checked():
            logger.error("[User: %s] 没有权限访问CodeDog，当前用户状态：%s" % (
                request.user, codedog_user.get_status_display()))
            return False
        else:
            return True

    def is_check_adminuser(self, user):
        """校验是否是超管
        """
        return bool(user and user.is_staff and user.is_superuser)


class CodeDogSuperVipUserLevelPermission(CodeDogUserPermission):
    """IPT用户鉴权权限判断
    """

    def has_permission(self, request, view):
        result = super(CodeDogSuperVipUserLevelPermission, self).has_permission(request, view)
        if result and request.user.codedoguser.level == CodeDogUser.LevelEnum.SUPER_VIP:
            return True
        return False


class OrganizationDetailUpdatePermission(CodeDogUserPermission):
    """团队详情更新权限判断

    适用于团队更新接口

    > 无需团队验证通过，当前用户仅团队管理员可操作
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(OrganizationDetailUpdatePermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        if not org_sid:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        return self.is_check_adminuser(request.user) \
            or (request.method in permissions.SAFE_METHODS
                and request.user.has_perm(org.PermissionNameEnum.VIEW_ORG_PERM, org)) \
            or request.user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org)


class OrganizationDefaultPermission(CodeDogUserPermission):
    """团队默认权限判断

    适用于非管理员只能查看的接口

    > 需团队验证通过，当前用户仅团队管理员可操作，普通成员可查看
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(OrganizationDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        if not org_sid:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        return self.is_check_adminuser(request.user) \
            or (request.method in permissions.SAFE_METHODS and
                request.user.has_perm(org.PermissionNameEnum.VIEW_ORG_PERM, org)) \
            or request.user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org)


class OrganizationAdminPermission(CodeDogUserPermission):
    """团队管理员权限判断

    仅适用于管理员可操作接口

    > 需团队验证通过，当前用户仅团队管理员可操作
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(OrganizationAdminPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        if not org_sid:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        return self.is_check_adminuser(request.user) or \
            request.user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org)


class OrganizationOperationPermission(CodeDogUserPermission):
    """团队操作权限判断

    适用于非管理员需要创建项目组的接口

    > 需团队验证通过，当前用户团队管理员、普通成员均可操作，适用于创建项目组接口
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(OrganizationOperationPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        if not org_sid:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        return self.is_check_adminuser(request.user) or \
            request.user.has_perm(org.PermissionNameEnum.VIEW_ORG_PERM, org)


class OrganizationPermApplyPermission(CodeDogUserPermission):
    """团队审批单权限判断
    仅ORG_PERM_ADMINS的超管可审批，否则仅可查看
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(OrganizationPermApplyPermission, self).has_permission(request, view)
        if not result:
            return False
        return (request.method in permissions.SAFE_METHODS or request.user.username in settings.ORG_PERM_ADMINS) \
            and bool(request.user and request.user.is_staff)
