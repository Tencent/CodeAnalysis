# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
permissions - user permission
"""

import logging

from rest_framework import permissions

from apps.authen.core import CodeDogUserManager


logger = logging.getLogger(__name__)


class CodeDogUserIsCheckedPermission(permissions.BasePermission):
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
            logger.error("[User: %s] 没有权限访问TCA，当前用户状态：%s" % (
                request.user, codedog_user.get_status_display()))
            return False
        else:
            return True


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a super user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
            (request.method in permissions.SAFE_METHODS or request.user.is_superuser)
