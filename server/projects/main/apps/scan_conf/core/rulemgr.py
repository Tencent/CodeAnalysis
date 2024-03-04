# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checkrule core
"""
import logging

# 第三方
from django.db.models import Q

# 项目内
from apps.authen.models import Organization
from apps.scan_conf.models import CheckRule, CheckTool, CheckToolWhiteKey

logger = logging.getLogger(__name__)


class BaseRuleManager(object):
    """规则管理 base模块
    """

    class ToolKeyEnum(object):
        DEFAULT = "default"

    @classmethod
    def all(cls):
        """获取全部规则
        """
        raise NotImplementedError

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选可用规则qs
        """
        raise NotImplementedError

    @classmethod
    def filter_pkg_usable(cls, **kwargs):
        """筛选规则包可用规则qs
        """
        raise NotImplementedError

    @classmethod
    def filter_tool_all(cls, checktool):
        """筛选工具内全部规则qs
        """
        raise NotImplementedError


class CheckRuleManager(BaseRuleManager):
    """规则manager
    """

    @classmethod
    def all(cls, **kwargs):
        """获取全部工具规则
        """
        # 工具规则的tool_key为default，自定义规则的tool_key为该工具的tool_key
        return CheckRule.objects.filter(tool_key__isnull=False)

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
    def get_org_detail(cls, checkrule):
        """根据工具tool_key获取团队详情，用于显示自定义规则来源
        :param checktool: str, 工具key
        :return: {"name": "xxx"}
        """
        if checkrule.tool_key == cls.ToolKeyEnum.DEFAULT:
            return None
        org = cls.get_org(checkrule.tool_key)
        if org:
            return {"name": org.name, "org_sid": org.org_sid}
        return None

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选可用规则qs
        1. 获取所有公开工具(正常运营、体验运营)且未失效的规则
        2. 获取团队白名单工具且未失效的规则
        3. 获取团队自定义且未失效规则
        :params kwargs:
            tool_keys: str list, 工具key集合
        :return: qs
        """
        tool_keys = kwargs.get("tool_keys", [])
        tool_ids = []
        if tool_keys:
            tool_ids = list(CheckToolWhiteKey.objects.filter(tool_key__in=tool_keys).values_list("tool_id", flat=True))
        tool_status = [CheckTool.StatusEnum.RUNNING, CheckTool.StatusEnum.TRIAL]  
        # 获取所有公开工具(正常运营、体验运营)、白名单工具且未失效的规则
        rules = CheckRule.objects.filter(
                    tool_key=cls.ToolKeyEnum.DEFAULT, disable=False,
                    checktool__status__in=tool_status
                ).filter(
                    Q(checktool__open_user=True) |
                    Q(checktool__open_maintain=True) |
                    Q(checktool__in=tool_ids)
                )
        # 自定义规则且未失效规则
        custom_rules = CheckRule.objects.filter(tool_key__in=tool_keys, disable=False,
                                                checktool__status__in=tool_status)
        return (rules | custom_rules).distinct().order_by("display_name")

    @classmethod
    def filter_pkg_usable(cls, **kwargs):
        """在规则包内添加规则时使用，获取该规则包能够添加的规则qs
        1. 获取所有公开工具(正常运营、体验运营)且未失效的规则
        2. 获取团队白名单工具且未失效的规则
        3. 获取团队自定义且未失效规则
        :params kwargs:
            tool_keys: str list, 工具key集合
        :return: qs
        """
        return cls.filter_usable(**kwargs)

    @classmethod
    def filter_tool_all(cls, checktool):
        """筛选工具全部规则，仅获取工具自身规则
        :param checktool: CheckTool, 工具
        :return: qs
        """
        # 工具本身的规则
        rules = CheckRule.objects.filter(checktool=checktool, tool_key=cls.ToolKeyEnum.DEFAULT)
        return rules.order_by("-id")
