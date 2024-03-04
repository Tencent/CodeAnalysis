# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util.operationrecord 增加敏感操作记录
"""

from copy import deepcopy

from apps.base.models import OperationRecord


def add_operation_record(scenario_key, action, username, message=None):
    if isinstance(message, dict):
        message = deepcopy(message)
        for key in message.keys():
            if "password" in key or "pwd" in key:
                message.update({key: "****"})
    OperationRecord.objects.create(scenario_key=scenario_key,
                                   action=action,
                                   creator=str(username),
                                   message=message)


class OperationRecordHandler(object):

    @classmethod
    def add_operation_record(cls, scenario_key, action, username, message=None):
        if isinstance(message, dict):
            message = deepcopy(message)
            for key in message.keys():
                if "password" in key or "pwd" in key:
                    message.update({key: "****"})
        OperationRecord.objects.create(scenario_key=scenario_key,
                                       action=action,
                                       creator=str(username),
                                       message=message)

    @classmethod
    def add_organization_operation_record(cls, organization, action, username, message=None):
        """
        统一处理组织操作相关的记录，默认scenario_key为 "organization_%d" % organization.id
        """
        add_operation_record("organization_%d" % organization.id, action, username, message)

    @classmethod
    def add_projectteam_operation_record(cls, project_team, action, username, message=None):
        """
        统一处理项目组操作相关的记录，默认scenario_key为 "projectteam_%d"% project_team.id
        """
        add_operation_record("projectteam_%d" % project_team.id, action, username, message)

    @classmethod
    def add_project_operation_record(cls, project, action, username, message=None):
        """
        统一处理项目操作相关的记录，默认scenario_key为 "project_%d"%project.id
        """
        add_operation_record("project_%d" % project.id, action, username, message)

    @classmethod
    def add_scanscheme_operation_record(cls, scanscheme, action, username, message=None):
        """
        统一处理扫描方案操作相关的记录，默认scenario_key为 "scanscheme_%d"%scanscheme.id
        """
        add_operation_record("scanscheme_%d" % scanscheme.id, action, username, message)

    @classmethod
    def add_repo_operation_record(cls, repository, action, username, message=None):
        """
        统一处理代码库操作相关的记录，默认scenario_key为 "repository_%d"%repository.id
        """
        add_operation_record("repository_%d" % repository.id, action, username, message)

    @classmethod
    def add_checkprofile_operation_record(cls, checkprofile, action, username, message=None):
        """
        统一处理规则集操作相关的记录，默认scenario_key为 "checkprofile_%d" % checkprofile.id
        """
        add_operation_record("checkprofile_%d" % checkprofile.id, action, username, message)

    @classmethod
    def add_schemetemplate_operation_record(cls, schemetemplate, action, username, message=None):
        """
        统一处理扫描方案模板操作相关记录，默认scenario_key为 "schemetemplate_%d" % schemetemplate.id
        """
        add_operation_record("schemetemplate_%d" % schemetemplate.id, action, username, message)

    @classmethod
    def add_checktool_operation_record(cls, checktool, action, username, message=None):
        """
        统一处理工具操作相关的记录，默认scenario_key为 "checktool_%d" % checktool.id
        """
        add_operation_record("checktool_%d" % checktool.id, action, username, message)

    @classmethod
    def add_checkpackage_operation_record(cls, checkpackage, action, username, message=None):
        """
        统一处理规则集操作相关的记录，默认scenario_key为 "checkpackage_%d" % checkpackage.id
        """
        add_operation_record("checkpackage_%d" % checkpackage.id, action, username, message)

    @classmethod
    def add_codedoguser_operation_record(cls, codedoguser, action, username, message=None):
        """
        统一处理codedog用户操作相关记录
        """
        add_operation_record("codedoguser_%d" % codedoguser.user_id, action, username, message)

    @classmethod
    def add_toollib_operation_recorod(cls, toollib, action, username, message=None):
        """
        统一处理工具依赖操作相关记录
        """
        add_operation_record("toollib_%d" % toollib.id, action, username, message)
