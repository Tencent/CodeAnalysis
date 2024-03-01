# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checktool core
"""
import logging

# 第三方
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ParseError

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core.basemgr import ModelManager
from apps.scan_conf.core.rulemgr import CheckRuleManager
from apps.scan_conf.core.toollibmgr import ToolLibManager, ToolLibSchemeManager
from apps.authen.models import Organization
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class BaseToolManager(object):
    """工具管理 base模块
    """

    class ToolKeyEnum(object):
        DEFAULT = "default"
        CUSTOM = "custom"

    @classmethod
    def update_languages(cls, checktool):
        """更新工具包含的语言
        :param checktool: CheckTool, 工具
        """
        rule_ids = CheckRuleManager.filter_tool_all(checktool).values_list('id', flat=True)
        languages = models.Language.objects.filter(checkrule__id__in=list(rule_ids)).distinct()
        checktool.languages.set(languages)

    @classmethod
    def update_open_status(cls, checktool, open_maintain, open_user, user):
        """更新工具公开状态，返回工具、旧的工具公开状态、新的工具公开状态
        :param checktool: CheckTool, 工具
        :param open_maintain: bool, 可协同
        :param open_user: bool, 可使用
        :return: checktool, old_public, new_public
        """
        old_open_maintain = checktool.open_maintain
        old_open_user = checktool.open_user
        checktool.open_maintain = open_maintain
        checktool.open_user = open_user
        checktool.save(user=user)
        message = "根据工具负责人需求，TCA 更新该工具的所有人可协同状态为：%s；所有人可使用状态为：%s" % (
            checktool.open_maintain, checktool.open_user)
        OperationRecordHandler.add_checktool_operation_record(checktool, "更新工具",
                                                              username=user.username, message=message)
        old_public = old_open_maintain or old_open_user
        new_public = checktool.open_user or checktool.open_maintain
        return checktool, old_public, new_public

    @classmethod
    def update_status(cls, checktool, status, user):
        """更新工具状态
        :param checktool: CheckTool, 工具
        :param status: int, 工具状态
        :param user: str，修改人
        :return: CheckTool
        """
        checktool.status = status
        checktool.save(user=user)
        status_dict = dict(models.CheckTool.STATUS_CHOICES)
        message = "更新工具运营状态为：%s" % status_dict[status]
        OperationRecordHandler.add_checktool_operation_record(checktool, "更新工具",
                                                              username=user.username, message=message)
        # 如果工具状态变为已下架，暂不需删除相应规则配置和规则包中的规则，在传递给客户端前过滤掉该种工具规则即可
        return checktool

    @classmethod
    def create_or_update(cls, name, user, checktool=None, is_script=False, **kwargs):
        """创建/更新工具
        :param name: str，工具真实名称
        :param user: str，创建人
        :param checktool: CheckTool, 存在则为更新
        :param is_script: bool, 是否脚本执行，脚本执行忽略日志记录
        :params kwargs, 其他工具参数
        :return: CheckTool
        """
        # 子进程单独配置，如未传递则配置默认的子进程
        task_processes = kwargs.pop("task_processes", None) or \
                         models.Process.objects.filter(name__in=["analyze", "datahandle"])
        # 工具key兼容处理，仅在创建工具时需要
        tool_key = kwargs.pop("tool_key")
        if not checktool:
            kwargs.update({"tool_key": tool_key})
        # 创建或更新工具
        checktool, created = ModelManager.create_or_update(models.CheckTool, instance=checktool,
                                                           user=user, name=name,
                                                           update_data={"name": name, **kwargs})
        # 特殊字段单独配置
        checktool.virtual_name = kwargs.get("virtual_name") or checktool.virtual_name or checktool.id
        checktool.scan_app = kwargs.get("scan_app") or checktool.scan_app or \
                             models.ScanApp.objects.filter(name="codelint").first()
        checktool.save(user=user)

        # 子进程配置，更新进程，可创建不存在的进程，然后set，会删除表单没有的进程
        for process in task_processes:
            tool_process_relation, _ = models.ToolProcessRelation.objects.get_or_create(
                checktool=checktool, process=process)
            tool_process_relation.priority = process.priority
            tool_process_relation.save()
        checktool.task_processes.set(task_processes)

        # 日志记录
        if created:
            action = "创建工具"
            message = ""
            # 每次创建工具时，设置工具可用白名单
            cls.add_white_key(tool_key, checktool.id)
        else:
            action = "更新工具"
            message = "工具名称: %s, 子进程配置: %s, 其他参数: %s" % (name, task_processes, kwargs)
        if not is_script:
            OperationRecordHandler.add_checktool_operation_record(checktool, action, user.username, message)
        return checktool

    @classmethod
    def create_or_update_rule(cls, checktool, real_name, user, checkrule=None, is_script=False, **kwargs):
        """创建或更新工具规则
        :param checktool: CheckTool, 工具
        :param real_name: str, 规则真实名称
        :param user: User, 操作用户
        :param checkrule: CheckRule, 规则，None创建、存在则更新
        :param is_script: bool, 是否脚本执行，脚本执行忽略每次更新工具语言和规则的日志记录
        :params kwargs: kwargs 其他规则参数
        :return: checkrule
        """
        # 创建工具规则时需校验该规则名是否存在
        if not checkrule and models.CheckRule.objects.filter(checktool=checktool, real_name=real_name).exists():
            raise ParseError("已存在同名规则")
        # 规则描述
        checkruledesc = kwargs.pop("checkruledesc", None)
        # 工具规则tool_key兼容处理，仅在创建工具规则时需要
        tool_key = kwargs.pop("tool_key")
        if not checkrule:
            kwargs.update({"tool_key": tool_key})
        # 创建或更新工具规则
        checkrule, created = ModelManager.create_or_update(models.CheckRule, instance=checkrule, user=user,
                                                           checktool=checktool, real_name=real_name, update_data={
                "real_name": real_name,
                **kwargs
            })

        # 失效，单独处理
        disable = kwargs.get("disable")
        if not checkrule.disable and disable:
            checkrule.disabled_time = timezone.now()
        if disable:
            checkrule.disabled_reason = kwargs.get("disabled_reason", checkrule.disabled_reason)
        else:
            checkrule.disabled_reason = None
            checkrule.disabled_time = None
        checkrule.save(user=user)

        # 更新规则描述
        if checkruledesc and checkruledesc.get("desc"):
            check_rule_desc, _ = models.CheckRuleDesc.objects.get_or_create(
                checkrule=checkrule, defaults={"desc_type": models.CheckRuleDesc.Desctype.MARKDOWN})
            check_rule_desc.desc = checkruledesc.get('desc')
            check_rule_desc.save()

        if created:
            action = "添加规则"
            message = "规则：%s(%s)" % (checkrule.display_name, checkrule.real_name)
        else:
            action = "更新规则"
            message = "规则名称: %s, 规则描述: %s, 其他参数：%s" % (real_name, checkruledesc, kwargs)
        # 仅在非脚本且工具自身规则更新时更新工具语言，记录日志
        if not is_script and checkrule.tool_key == cls.ToolKeyEnum.DEFAULT:
            cls.update_languages(checktool)
            OperationRecordHandler.add_checktool_operation_record(checktool, action, user, message)
        return checkrule

    @classmethod
    def create_libscheme_by_script(cls, checktool, libscheme_set, user):
        """通过脚本一键创建工具依赖方案，默认会先移除全部其他方案，再根据脚本内容创建方案
        :param checktool: CheckTool, 工具
        :param libscheme_set: list, 依赖方案列表
        :param user: User, 用户
        """
        # 当libscheme_set=[]时，会清空工具依赖方案
        if isinstance(libscheme_set, list):
            # 移除工具全部依赖
            models.ToolLibScheme.objects.filter(checktool=checktool).delete(permanent=True)
            # 创建工具依赖
            for libscheme in libscheme_set:
                tool_libs = libscheme.pop("toollibmap", [])
                ToolLibSchemeManager.create_or_update(checktool, user, tool_libs, instance=None, **libscheme)

    @classmethod
    def load_by_script(cls, name, user, checktool=None, **kwargs):
        """根据脚本创建/更新工具
        :param name: 工具名称
        :param user: User, 操作用户
        :param checktool: CheckTool, 工具，存在则为更新操作
        :params kwargs, 执行工具脚本参数
        :return: checktool
        """
        # 日志记录
        if not checktool:
            action = "脚本创建工具"
            message = "通过JSON脚本创建工具&工具规则"
        else:
            action = "脚本更新工具"
            message = "通过JSON脚本更新工具&工具规则"
        # 获取工具依赖方案
        libscheme_set = kwargs.pop('libscheme', [])
        # 获取工具规则
        checkrules_data = kwargs.pop('checkrule_set', [])
        # 工具key兼容处理，脚本执行工具load都为default
        kwargs.update({"tool_key": cls.ToolKeyEnum.DEFAULT})
        # 创建or更新工具
        checktool = cls.create_or_update(name, user, checktool=checktool, is_script=True, **kwargs)
        if user:  # 存在user则将其加入工具负责人列表
            checktool.owners.add(user)
        # 执行工具规则创建or更新
        for checkrule_data in checkrules_data:
            real_name = checkrule_data.pop('real_name')
            checkrule = models.CheckRule.objects.filter(checktool=checktool, real_name=real_name).first()
            cls.create_or_update_rule(checktool, real_name, user,
                                      checkrule=checkrule, is_script=True, **checkrule_data)

        # 更新工具语言
        cls.update_languages(checktool)

        # 执行工具依赖创建
        cls.create_libscheme_by_script(checktool, libscheme_set, user)

        # 日志记录
        OperationRecordHandler.add_checktool_operation_record(checktool, action, username=user, message=message)
        return checktool

    @classmethod
    def is_add_rule_perm(cls, checktool, users):
        """校验users是否具有添加工具规则权限
        :param checktool: CheckTool, 工具
        :param users: User List, 用户
        :return: bool, 有权限True，无权限False
        """
        allusers = checktool.get_all_users()
        usernames = [user.username for user in users]
        return allusers.filter(username__in=usernames).exists()

    @classmethod
    def get_tool_key(cls, tool_key):
        """获取工具Key值
        """
        raise NotImplementedError

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选可用的工具
        """
        raise NotImplementedError

    @classmethod
    def add_white_key(cls, tool_key, tool_id):
        """添加工具key白名单
        """
        return None, False

    @classmethod
    def check_use_toollib_perm(cls, checktool, toollib):
        """校验工具使用依赖权限
        """
        return toollib.lib_type == models.ToolLib.LibTypeEnum.PUBLIC


class CheckToolManager(BaseToolManager):

    @classmethod
    def get_tool_key(cls, **kwargs):
        """获取工具key
        :kwargs:
            org, Organization, 团队，必填参数
        :return: org_{org_id}
        """
        org = kwargs.get("org", None)
        if not org:
            raise Exception("未获取到团队，无法获取工具key值")
        return "org_%s" % org.id

    @classmethod
    def get_org(cls, tool_key):
        """根据工具key值获取团队，可为None
        :param tool_key: str, 工具key
        :return: Organization
        """
        try:
            org_id = int(tool_key.split("org_")[-1])
        except ValueError:
            return None
        return Organization.objects.filter(id=org_id).first()

    @classmethod
    def get_org_detail(cls, checktool):
        """根据工具tool_key获取团队详情
        :param checktool: str, 工具key
        :return: {"name": "xxx"}
        """
        if checktool.tool_key == cls.ToolKeyEnum.DEFAULT:
            return {"name": "由平台提供"}
        org = cls.get_org(checktool.tool_key)
        if org:
            return {"name": org.name, "org_sid": org.org_sid}
        return None

    @classmethod
    def add_white_key(cls, tool_key, tool_id):
        """添加工具key白名单
        :param tool_key: str, 工具key
        :param tool_id: str, 工具ID
        :return: (CheckToolWhiteKey, created)
        """
        if tool_key == cls.ToolKeyEnum.DEFAULT or not tool_key:
            return None, False
        return models.CheckToolWhiteKey.objects.get_or_create(tool_key=tool_key, tool_id=tool_id)

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选团队可用工具
        :kwargs:
            org, Organization, 团队，必填参数
        :return: checktool qs
        """
        tool_key = cls.get_tool_key(**kwargs)
        # 白名单工具
        tool_ids = models.CheckToolWhiteKey.objects.filter(tool_key=tool_key).values_list("tool_id", flat=True)
        return models.CheckTool.objects.filter(Q(open_maintain=True) | Q(open_user=True) | Q(id__in=tool_ids)) \
            .distinct().order_by('-modified_time')

    @classmethod
    def create_or_update(cls, name, user, checktool=None, is_script=False, **kwargs):
        # 如果没有传递工具key则从org中获取，兼容本地脚本load工具
        if not kwargs.get("tool_key"):
            org = kwargs.pop("org", None)
            kwargs["tool_key"] = cls.get_tool_key(org=org)
        return super().create_or_update(name, user, checktool=checktool, is_script=is_script, **kwargs)

    @classmethod
    def create_or_update_rule(cls, checktool, real_name, user, checkrule=None, is_script=False, **kwargs):
        """创建或更新工具规则
        :param checktool: CheckTool, 工具
        :param real_name: str, 规则真实名称
        :param user: User, 操作用户
        :param checkrule: CheckRule, 规则，None创建、存在则更新
        :param is_script: bool, 是否脚本执行，脚本执行忽略每次更新工具语言和规则的日志记录
        :params kwargs: kwargs 其他规则参数
        :return checkrule
        """
        # 如果传递了org，那么相当于是团队自定义工具规则
        org = kwargs.pop("org", None)
        if not org:
            kwargs["tool_key"] = cls.ToolKeyEnum.DEFAULT
        else:
            kwargs["tool_key"] = cls.get_tool_key(org=org)
            if not checkrule:
                real_name = "%s_%s" % (real_name, kwargs["tool_key"])
        return super().create_or_update_rule(checktool, real_name, user, checkrule=checkrule,
                                             is_script=is_script, **kwargs)

    @classmethod
    def check_maintain_edit_perm(cls, org, checktool, user):
        """校验协同工具的操作权限
        :param org: Organization, 团队
        :param checktool: CheckTool, 工具
        :param user: User, 访问用户
        :return: bool
        注：协同工具且当前用户为团队管理员可操作自定义规则。该权限仅控制自定义规则
        """
        return checktool.open_maintain and user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, org)

    @classmethod
    def check_edit_perm(cls, org, checktool, user):
        """校验用户是否具有工具的编辑权限
        :param org: Organization, 团队
        :param checktool: CheckTool, 工具
        :param user: User, 访问用户
        :return: bool
        注：工具tool_key对应团队的管理员可操作
        """
        if cls.get_tool_key(org=org) == checktool.tool_key:
            return user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, org)
        return False

    @classmethod
    def check_rule_edit_perm(cls, org, checkrule, user):
        """校验用户是否具有工具规则的编辑权限
        :param org: Organization, 团队
        :param checkrule: CheckRule, 规则
        :param user: User, 访问用户
        :return: bool
        注：规则tool_key对应团队的管理员可操作
        """
        if cls.get_tool_key(org=org) == checkrule.tool_key:
            return user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, org)
        return False

    @classmethod
    def check_usable_perm(cls, org, checktool, user):
        """校验用户是否具备该工具的使用权限
        :param org: Organization, 团队
        :param checktool: CheckTool, 工具
        :param user: User, 访问用户
        :return: bool
        注：可编辑不一定可使用，可使用仅与公开和白名单有关。默认创建自定义工具时会将负责团队加入白名单中。
        """
        if checktool.is_public():
            # 公开工具
            return True
        # 白名单工具
        tool_key = cls.get_tool_key(org=org)
        if models.CheckToolWhiteKey.objects.filter(tool_key=tool_key, tool_id=checktool.id).exists():
            return user.has_perm(Organization.PermissionNameEnum.VIEW_ORG_PERM, org)
        return False

    @classmethod
    def check_use_toollib_perm(cls, checktool, toollib):
        """校验工具使用依赖权限
        """
        return super().check_use_toollib_perm(checktool, toollib) or \
               checktool and cls.get_org(checktool.tool_key) == ToolLibManager.get_org(toollib.lib_key)
