# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.scan_conf.tasks
celery tasks
"""
import logging

# 第三方
from codedog.celery import celery_app

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core import CheckToolManager, CheckPackageManager, CheckProfileManager
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


def _get_checkpackage_dict(packagemaps):
    """获取规则包-规则映射键值对
    :param packagemaps: list<PackageMap>, 规则包规则映射列表
    :return: dict checkpackge-packagemaps
    """
    checkpackage_dict = dict()
    for v in packagemaps:
        checkpackage = v.checkpackage
        if checkpackage not in checkpackage_dict:
            checkpackage_dict[checkpackage] = [v]
        else:
            checkpackage_dict[checkpackage].append(v)
    return checkpackage_dict


def _rm_checkpackage_packagemaps(checktool, checkpackage, packagemaps, op_type, username=None):
    """移除规则包规则
    :param checktool: CheckTool, 工具
    :param checkpackage: CheckPackage, 规则包
    :param packagemaps: list<PackageMap>, 规则包规则映射列表
    :param op_type: int, 操作类型
    ;param username: str, 操作人/团队
    """
    # 移除规则包的规则
    checkrule_names = []
    for packagemap in packagemaps:
        checkrule_names.append(packagemap.checkrule.display_name)
        packagemap.delete()
    # 记录message
    if op_type == models.CheckTool.OpEnum.DELRULE:  # 移除规则
        message = "因%s移除【%s[%s]】工具规则：%s，已将对应的规则移除" % (
            username, checktool.display_name, checktool.id, "; ".join(checkrule_names))
    elif op_type == models.CheckTool.OpEnum.DISABLETOOL:  # 下架工具
        message = "因%s下架【%s[%s]】工具，已将对应的规则移除：%s" % (
            username, checktool.display_name, checktool.id, "; ".join(checkrule_names))
    else:
        message = "因%s私有化【%s[%s]】工具，已将对应的规则移除：%s" % (
            username, checktool.display_name, checktool.id, "; ".join(checkrule_names))
    CheckPackageManager.operation_record(checkpackage, "移除规则", username, message)


@celery_app.task
def checktool_to_private(checktool_id, username):
    """私有化工具操作
    :param checktool_id: int, 工具ID
    :param username: str, 操作人/团队
    """
    checktool = models.CheckTool.objects.filter(id=checktool_id).first()
    if checktool:
        checkrules = models.CheckRule.everything.filter(checktool=checktool)
        packagemaps = models.PackageMap.objects.filter(checkrule__in=checkrules)
        checkpackage_dict = _get_checkpackage_dict(packagemaps)
        for (checkpackage, packagemaps) in checkpackage_dict.items():
            try:
                # 存在checkprofile则为规则配置自定义规则包
                checkprofile = checkpackage.checkprofile
                # 获取规则配置所属团队，以及tool_key
                org = CheckProfileManager.get_org(checkprofile)
                tool_key = CheckToolManager.get_tool_key(org=org) if org else None
                # 校验是否具备使用该工具规则的权限，具备则不删除，否则移除
                if CheckPackageManager.check_add_tool_rules_perm(checktool, checkpackage=checkpackage,
                                                                 tool_key=tool_key):
                    continue
            except models.CheckProfile.DoesNotExist:
                # 不存在checkprofile则为官方规则包
                # 需要移除官方规则包的私有工具规则，保证官方规则包规则都为公共工具规则
                pass
            _rm_checkpackage_packagemaps(checktool, checkpackage, packagemaps,
                                            models.CheckTool.OpEnum.PRIVATETOOL, username)


@celery_app.task
def checktool_to_disable(checktool_id, username):
    """工具下架，下架工具需要移除规则包，规则配置中对应规则
    :param checktool_id: int, 工具ID
    :param username: str, 操作人/团队
    """
    checktool = models.CheckTool.objects.filter(id=checktool_id).first()
    if checktool:
        checkrules = models.CheckRule.everything.filter(checktool=checktool)
        packagemaps = models.PackageMap.objects.filter(checkrule__in=checkrules)
        checkpackage_dict = _get_checkpackage_dict(packagemaps)
        for (checkpackage, packagemaps) in checkpackage_dict.items():
            _rm_checkpackage_packagemaps(checktool, checkpackage, packagemaps,
                                         models.CheckTool.OpEnum.DISABLETOOL, username)


@celery_app.task
def checktool_to_delrule(checktool_id, checkrule_ids, username):
    """工具移除规则，需要移除规则包，规则配置中对应规则
    :param checktool_id: int, 工具ID
    :param checkrule_ids: int List, 规则ID列表
    :param username: str, 操作人/团队
    """
    checktool = models.CheckTool.objects.filter(id=checktool_id).first()
    if checktool:
        checkrules = models.CheckRule.everything.filter(id__in=checkrule_ids)
        packagemaps = models.PackageMap.objects.filter(checkrule__in=checkrules)
        checkpackage_dict = _get_checkpackage_dict(packagemaps)
        for (checkpackage, packagemaps) in checkpackage_dict.items():
            _rm_checkpackage_packagemaps(checktool, checkpackage, packagemaps,
                                         models.CheckTool.OpEnum.DELRULE, username)

        checkrule_names = []
        for checkrule in checkrules:
            checkrule_names.append('%s(%s)' % (checkrule.display_name, checkrule.real_name))
            # 真删除
            checkrule.delete(permanent=True)
        # 更新工具适用语言
        CheckToolManager.update_languages(checktool)
        OperationRecordHandler.add_checktool_operation_record(
            checktool=checktool, action="移除规则",
            username=username, message="移除规则：%s" % ("; ".join(checkrule_names)))
