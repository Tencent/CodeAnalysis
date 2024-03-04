# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.nodemgr.permission 模块
"""

import logging

from django.shortcuts import get_object_or_404
from rest_framework import permissions

from apps.authen.models import Organization
from apps.authen.permissions import CodeDogUserPermission
from apps.nodemgr.models import Node

logger = logging.getLogger(__name__)


class OrganizationNodeAdminPermission(CodeDogUserPermission):
    """团队管理员节点权限判断

    仅适用于管理员或节点管理员可操作接口

    > 需团队验证通过，当前用户仅团队管理员可操作
    """

    def has_permission(self, request, view):
        """检查当前用户是否有当前组织操作权限
        """
        result = super(OrganizationNodeAdminPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        if not org_sid:
            return False
        node_id = view.kwargs.get("node_id")
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        node = get_object_or_404(Node, id=node_id, org_sid=org_sid)
        return self.is_check_adminuser(request.user) or \
               (request.method in permissions.SAFE_METHODS and
                request.user.has_perm(org.PermissionNameEnum.VIEW_ORG_PERM, org)) or \
               request.user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org) or \
               node.check_user_admin_permission(request.user)
