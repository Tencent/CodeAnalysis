# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util.permissions
"""

import logging

from rest_framework import permissions
from django.shortcuts import get_object_or_404

from apps.scan_conf.models import CheckProfile, CheckRule, CheckPackage, CheckTool


logger = logging.getLogger(__name__)


class CheckProfilePermission(permissions.BasePermission):
    """
    项目权限校验，通过url的checkprofile_id来判定用户是否有权限访问
    """

    def has_permission(self, request, view):
        checkprofile_id = view.kwargs.get("checkprofile_id")
        if not checkprofile_id:
            return False  # url中必须包含checkprofile_id
        checkprofile = get_object_or_404(CheckProfile, id=checkprofile_id)
        admins = checkprofile.get_admins()
        # 如果是SAFE_METHODS则都有权限，否则需要创建者/成员或者超级管理员
        return request.user and request.user.is_authenticated and \
            (request.method in permissions.SAFE_METHODS or request.user.is_superuser or
            request.user.has_perm(CheckProfile.PermissionNameEnum.CHANGE_PROFILE_PERM, checkprofile)
            or request.user == checkprofile.creator or request.user in admins)


class CheckPackagePermission(permissions.BasePermission):
    """
    项目权限校验，通过url的checkpackage_id来判定用户是否有权限访问
    """

    def has_permission(self, request, view):
        checkpackage_id = view.kwargs.get("checkpackage_id")
        if not checkpackage_id:
            return False  # url中必须包含project_id
        checkpackage = get_object_or_404(CheckPackage, id=checkpackage_id)
        # 如果是SAFE_METHODS则都有权限，否则需要创建者/成员或者超级管理员
        # checkpackage.checkprofile可能回抛出异常，如果抛出异常，说明有逻辑漏洞导致自定义规则包没有关联规则集
        return request.user and request.user.is_authenticated and \
            (request.method in permissions.SAFE_METHODS or
             request.user == checkpackage.creator or request.user.is_superuser or
             (checkpackage.package_type == CheckPackage.PackageTypeEnum.CUSTOM and
              request.user.has_perm(CheckProfile.PermissionNameEnum.CHANGE_PROFILE_PERM, checkpackage.checkprofile)))


class CheckRulePermission(permissions.BasePermission):
    """
    规则权限校验
    """

    def has_permission(self, request, view):
        checkrule_id = view.kwargs.get("checkrule_id")
        if not checkrule_id:
            return False
        checkrule = get_object_or_404(CheckRule, id=checkrule_id)
        # 如果是SAFE_METHODS则都有权限，否则需要规则负责人、规则工具负责人、超级管理员有权限
        checktool_owners = checkrule.checktool.owners.all()
        return request.user and request.user.is_authenticated and \
            (request.method in permissions.SAFE_METHODS or \
            request.user.is_superuser or request.user.username == checkrule.owner or \
            request.user in checktool_owners)


class CheckToolPermission(permissions.BasePermission):
    """
    工具权限校验
    get 使用成员、协同成员、负责成员、superuser
    put、post、del 负责成员、superuser
    """

    def has_permission(self, request, view):
        checktool_id = view.kwargs.get("checktool_id")
        if not checktool_id:
            return False
        checktool = get_object_or_404(CheckTool, id=checktool_id)
        owners = checktool.owners.all()
        if request.user and request.user.is_authenticated and request.method in permissions.SAFE_METHODS:
            # if checktool.is_public():  # 公开工具
            #     return True
            if checktool.is_public() and checktool.show_display_name:  # 公开工具&show_display_name为True
                return True
            allusers = checktool.get_all_users()
            return request.user.is_superuser or request.user in allusers
        # 编辑操作仅允许工具负责人、超级管理员访问
        return request.user in owners or (request.user and request.user.is_superuser)


class CheckToolRulePermission(permissions.BasePermission):
    """
    工具规则权限校验，用于ListCreateAPIView
    """

    def has_permission(self, request, view):
        checktool_id = view.kwargs.get("checktool_id")
        if not checktool_id:
            return False
        checktool = get_object_or_404(CheckTool, id=checktool_id)
        owners = checktool.owners.all()
        # 协同成员
        co_owners = checktool.co_owners.all()
        if request.user and request.user.is_authenticated and request.method in permissions.SAFE_METHODS:
            if checktool.is_public():  # 公开工具
                return True
            # 可用成员
            users = checktool.users.all()
            # 私有工具仅允许工具负责人、协同成员、可用成员、超级管理员访问
            return request.user.is_superuser or (request.user in owners) or \
                (request.user in co_owners) or \
                (request.user in users)
        # 规则创建操作仅允许工具负责人、协同成员、所有人可协同、超级管理员访问
        return (request.user and request.user.is_superuser) or (request.user in owners) or \
            (request.user in co_owners) or checktool.open_maintain

