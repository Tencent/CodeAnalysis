# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - permissions
"""
import logging

# 第三方
from django.shortcuts import get_object_or_404
from rest_framework import permissions

# 项目内
from apps.scan_conf.models import CheckTool, CheckRule, ToolLib
from apps.scan_conf.core import ToolLibManager, CheckToolManager
from apps.authen.permissions import CodeDogUserPermission
from apps.authen.models import Organization

logger = logging.getLogger(__name__)


class CheckToolDefaultPermission(CodeDogUserPermission):
    """工具权限

    适用于更新、配置工具操作

    > 需团队验证通过，如果当前用户是团队管理员可操作属于自己的工具，否则可查看
    """

    def has_permission(self, request, view):
        result = super(CheckToolDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        checktool_id = view.kwargs.get("checktool_id")
        if not org_sid or not checktool_id:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        checktool = get_object_or_404(CheckTool, id=checktool_id)
        return self.is_check_adminuser(request.user) or \
               (request.method in permissions.SAFE_METHODS and
                CheckToolManager.check_usable_perm(org, checktool, request.user)) or \
               CheckToolManager.check_edit_perm(org, checktool, request.user)


class CheckToolAdminPermission(CodeDogUserPermission):
    """工具管理权限

    适用于仅能管理员查看、操作

    > 需团队验证通过，如果当前用户是所在团队管理员则可查看、管理工具
    """

    def has_permission(self, request, view):
        result = super(CheckToolAdminPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        checktool_id = view.kwargs.get("checktool_id")
        if not org_sid or not checktool_id:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        checktool = get_object_or_404(CheckTool, id=checktool_id)
        return self.is_check_adminuser(request.user) or CheckToolManager.check_edit_perm(org, checktool, request.user)


class CheckToolMaintainPermission(CodeDogUserPermission):
    """协同工具自定义规则权限

    适用于协同工具操作自定义规则

    > 需团队验证通过，如果当前用户是团队管理员则可操作协同工具自定义规则
    """

    def has_permission(self, request, view):
        result = super(CheckToolMaintainPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        checktool_id = view.kwargs.get("checktool_id")
        if not org_sid or not checktool_id:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        checktool = get_object_or_404(CheckTool, id=checktool_id)
        return self.is_check_adminuser(request.user) or \
               (request.method in permissions.SAFE_METHODS and
                CheckToolManager.check_usable_perm(org, checktool, request.user)) or \
               CheckToolManager.check_maintain_edit_perm(org, checktool, request.user)


class CheckToolRuleDetaultPermission(CodeDogUserPermission):
    """工具规则权限
    适用于更新、配置工具规则操作

    > 需团队验证通过，如果当前用户是团队管理员可操作属于自己的工具，或规则，否则可查看
    """

    def has_permission(self, request, view):
        result = super(CheckToolRuleDetaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        checktool_id = view.kwargs.get("checktool_id")
        checkrule_id = view.kwargs.get("checkrule_id")
        if not org_sid or not checktool_id or not checkrule_id:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        checkrule = get_object_or_404(CheckRule, id=checkrule_id, checktool_id=checktool_id)
        return self.is_check_adminuser(request.user) or \
               (request.method in permissions.SAFE_METHODS and
                CheckToolManager.check_usable_perm(org, checkrule.checktool, request.user)) or \
               CheckToolManager.check_edit_perm(org, checkrule.checktool, request.user)


class ToolLibDefaultPermission(CodeDogUserPermission):
    """工具依赖权限

    应用场景：需团队验证通过，如果当前用户是团队管理员则可操作工具依赖，否则可查看
    """

    def has_permission(self, request, view):
        result = super(ToolLibDefaultPermission, self).has_permission(request, view)
        if not result:
            return False
        org_sid = view.kwargs.get("org_sid")
        toollib_id = view.kwargs.get("toollib_id")
        if not org_sid or not toollib_id:
            return False
        org = get_object_or_404(Organization, org_sid=org_sid)
        if not org.validate_org_checked():
            return False
        toollib = get_object_or_404(ToolLib, id=toollib_id)
        return self.is_check_adminuser(request.user) or \
               (request.method in permissions.SAFE_METHODS and
                ToolLibManager.check_usable_perm(org, toollib, request.user)) or \
               ToolLibManager.check_edit_perm(org, toollib, request.user)
