# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - toollib core
"""
import logging

# 第三方
from django.db.models import Q
from rest_framework.exceptions import ParseError

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core.basemgr import ModelManager
from apps.authen.models import Organization
from util.exceptions import DragSortError, CheckToolLibAddError, errcode
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class BaseLibManager(object):
    """工具依赖管理 base模块
    """

    class LibKeyEnum(object):
        SYSTEM = "system"

    @classmethod
    def create_or_update(cls, name, lib_key, user, instance=None, **kwargs):
        """创建、更新工具依赖
        :param name: str, 依赖名称
        :param lib_key: str, 依赖 key
        :param user: User, 操作用户
        :param instance: ToolLib, 工具依赖
        :param kwargs: dict, 其他参数
        :return: instance, created
        """
        ignore_log = kwargs.pop("ignore_log", False)
        instance, created = ModelManager.create_or_update(models.ToolLib, instance=instance,
                                                          user=user, name=name, lib_key=lib_key,
                                                          update_data={"name": name, **kwargs})
        if not ignore_log:
            action = "更新工具依赖"
            message = "依赖名称：%s，其他参数：%s" % (name, kwargs)
            if created:
                action = "创建工具依赖"
                message = ""
            OperationRecordHandler.add_toollib_operation_recorod(instance, action, user, message)
        return instance, created

    @classmethod
    def get_lib_key(cls, **kwargs):
        """获取lib key
        """
        raise NotImplementedError

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选可用工具依赖
        """
        raise NotImplementedError


class ToolLibManager(BaseLibManager):
    """工具依赖管理
    """

    @classmethod
    def get_lib_key(cls, **kwargs):
        """获取工具依赖key值
        :kwargs:
            org, Organization, 团队，必填参数
        :return: org_{org_id}
        """
        org = kwargs.get("org", None)
        if not org:
            raise Exception("未获取到团队 ，无法获取工具依赖key值")
        return "org_%s" % org.id

    @classmethod
    def get_org(cls, lib_key):
        """根据工具依赖key值获取团队，可为None
        :param lib_key: str, 工具依赖key
        :return: Organization
        """
        try:
            org_id = int(lib_key.split("org_")[-1])
        except ValueError:
            return None
        return Organization.objects.filter(id=org_id).first()

    @classmethod
    def create_or_update(cls, name, user, instance=None, **kwargs):
        """创建、更新工具依赖
        :param name: str, 依赖名称
        :param user: User, 操作用户
        :param instance: ToolLib, 工具依赖
        :param kwargs: dict, 其他参数
            lib_key 或 org 为必传参数
        :return: instance, created
        """
        # 如果没有传递工具依赖key则从org中获取，兼容本地脚本load工具依赖
        lib_key = kwargs.pop("lib_key", None)
        if not lib_key:
            org = kwargs.pop("org", None)
            lib_key = cls.get_lib_key(org=org)
        return super().create_or_update(name, lib_key, user, instance=instance, **kwargs)

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选团队可用工具依赖
        :kwargs:
            org, Organization, 团队，必填参数
        :return: toollib qs
        """
        lib_key = cls.get_lib_key(**kwargs)
        public_lib_type = models.ToolLib.LibTypeEnum.PUBLIC
        # 公开依赖 + 团队依赖
        return models.ToolLib.objects.filter(Q(lib_key=lib_key) | Q(lib_type=public_lib_type)) \
            .distinct().order_by('-modified_time')

    @classmethod
    def check_usable_perm(cls, org, toollib, user):
        """校验用户是否具备该工具依赖的使用权限
        :param org: Organization, 团队
        :param toollib: ToolLib, 工具依赖
        :param user: User, 访问用户
        :return: bool

        公共依赖、团队依赖可使用
        """
        if toollib.lib_type == models.ToolLib.LibTypeEnum.PUBLIC:
            return True
        lib_key = cls.get_lib_key(org=org)
        return toollib.lib_key == lib_key and user.has_perm(Organization.PermissionNameEnum.VIEW_ORG_PERM, org)

    @classmethod
    def check_edit_perm(cls, org, toollib, user):
        """校验用户是否具备该工具依赖的编辑权限
        """
        lib_key = cls.get_lib_key(org=org)
        return toollib.lib_key == lib_key and user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, org)


class ToolLibMapManager(object):
    """工具依赖映射管理
    """

    POS_STEP_COUNT = 65536

    class DragEnum:
        BEFORE = 'before'
        AFTER = 'after'

    DRAG_CHOICES = (
        (DragEnum.BEFORE, 'before'),
        (DragEnum.AFTER, 'after'),
    )

    @classmethod
    def create(cls, libscheme, toollib, user, **kwargs):
        """创建项目
        :param libscheme: ToolLibScheme, 工具依赖方案
        :param toollib: ToolLib, 工具依赖
        :param user: User, 访问用户
        :param kwargs: 其他参数
        :return: ToolLibMap
        """
        if models.ToolLibMap.objects.filter(libscheme=libscheme, toollib=toollib).exists():
            raise CheckToolLibAddError(code=errcode.E_SERVER_CHECKTOOL_LIB_EXIST, msg='已存在此依赖')
        # 为后续取中值法策略策略准备，默认创建标签按pos排序后，从最后一个+65536
        lib_map = models.ToolLibMap.objects.filter(libscheme=libscheme).order_by('pos').last()
        pos = lib_map.pos + cls.POS_STEP_COUNT if lib_map else cls.POS_STEP_COUNT
        instance = models.ToolLibMap.objects.create(libscheme=libscheme, toollib=toollib, pos=pos)
        # 日志记录
        message = "工具依赖方案%s添加依赖：%s" % (libscheme, toollib)
        OperationRecordHandler.add_checktool_operation_record(libscheme.checktool, "添加依赖", user, message)
        return instance

    @classmethod
    def delete(cls, instance, user):
        libscheme = instance.libscheme
        message = "工具依赖方案%s移除依赖：%s" % (libscheme, instance.toollib)
        OperationRecordHandler.add_checktool_operation_record(libscheme.checktool, "移除依赖", user, message)
        instance.delete()

    @classmethod
    def _compute_drag_pos(cls, target, drag_type):
        """计算拖拽排序后的pos，返回pos和是否重排
        :param target: ToolLibMap, 目标toollibmap
        :param drag_type: str, 拖拽类型，置于目标nav前或后
        :return: pos, is_reset
        """
        if drag_type == cls.DragEnum.BEFORE:
            # 将源nav置于目标nav前，存在两种情况：1. 首个；2. 中间
            before_nav = models.ToolLibMap.objects.filter(libscheme=target.libscheme,
                                                          pos__lt=target.pos).order_by("pos").last()
            if not before_nav:
                # 首个
                pos = int(target.pos / 2)
                return pos, not (pos < target.pos)
            else:
                pos = int((before_nav.pos + target.pos) / 2)
                return pos, not (pos < target.pos and pos > before_nav.pos)
        elif drag_type == cls.DragEnum.AFTER:
            # 将源nav置于目标nav后，存在两种情况：1. 末尾；2. 中间
            after_nav = models.ToolLibMap.objects.filter(libscheme=target.libscheme,
                                                         pos__gt=target.pos).order_by("pos").first()
            if not after_nav:
                # 末尾
                pos = target.pos + cls.POS_STEP_COUNT
                return pos, False
            else:
                pos = int((target.pos + after_nav.pos) / 2)
                return pos, not (pos < after_nav.pos and pos > target.pos)
        raise DragSortError(code=errcode.E_SERVER_DRAG_TYPE_NOT_EXIST, msg="请传入正确的排序拖拽类型")

    @classmethod
    def reset_sort(cls, libscheme):
        """重新设置排序pos
        :param libscheme: 工具依赖方案
        """
        lib_maps = models.ToolLibMap.objects.filter(libscheme=libscheme).order_by('pos')
        for idx, lib_map in enumerate(lib_maps):
            lib_map.pos = (idx + 1) * cls.POS_STEP_COUNT
            lib_map.save()

    @classmethod
    def drag_sort(cls, source, target, drag_type):
        """拖拽排序
        :param source: Label, 源label
        :param target: Label, 目标label
        :param drag_type: str, 拖拽类型，置于目标label前或后
        """
        try:
            if source.libscheme != target.libscheme:
                raise DragSortError(msg='依赖方案不一致，拖拽排序异常')
            pos, is_reset = cls._compute_drag_pos(target, drag_type)
            if is_reset:
                # 重排后再拖拽排序
                cls.reset_sort(target.project)
                cls.drag_sort(source, target, drag_type)
            else:
                source.pos = pos
                source.save()
        except Exception as e:
            logger.error(e)
            raise DragSortError(msg='拖拽排序异常，请联系平台管理员')


class ToolLibSchemeManager(object):
    """工具依赖方案管理
    """

    @classmethod
    def create_or_update(cls, checktool, user, tool_libs=None, instance=None, **kwargs):
        """创建/更新依赖方案
        :param checktool: CheckTool, 工具
        :param user: User, 用户
        :param tool_libs: list<ToolLib>, 工具依赖
        :param instance: ToolLibScheme, 工具依赖方案
        :param kwargs: 其他参数
        :return: ToolLibScheme
        """
        created = False
        if not instance:
            # 当工具没有依赖方案时，初次创建依赖方案设置
            if not models.ToolLibScheme.objects.filter(checktool=checktool).exists():
                kwargs.update({"default_flag": True})
            instance = models.ToolLibScheme.objects.create(checktool=checktool, user=user)
            created = True
        # 更新字段
        if kwargs.get("default_flag") is True:
            models.ToolLibScheme.objects.filter(checktool=checktool).update(default_flag=False)
            instance.default_flag = True
        instance.condition = kwargs.get("condition") or instance.condition
        instance.scheme_os = kwargs.get("scheme_os") or instance.scheme_os
        instance.save(user=user)
        # 创建，更新依赖，并进行排序
        if tool_libs:
            # 移除工具依赖方案中的无效依赖
            toollib_ids = [item.get("toollib").id for item in tool_libs]
            models.ToolLibMap.objects.filter(libscheme=instance).exclude(toollib_id__in=toollib_ids).delete()
            # 按pos排序
            tool_libs.sort(key=lambda toollib: toollib.get("pos", 0))
            pos = ToolLibMapManager.POS_STEP_COUNT
            toollibs = set()
            for item in tool_libs:
                toollib = item.get("toollib")
                # 避免重复lib
                if toollib not in toollibs:
                    models.ToolLibMap.objects.update_or_create(libscheme=instance, toollib=toollib,
                                                               defaults={"pos": pos})
                    pos += ToolLibMapManager.POS_STEP_COUNT
                    toollibs.add(toollib)
        action = "更新依赖方案"
        message = "更新依赖方案：%s，s，tool_libs：%s，其他参数：%s" % (instance, tool_libs, kwargs)
        if created:
            message = "工具添加依赖方案%s，tool_libs: %s" % (instance, tool_libs)
            action = "添加依赖方案"
        OperationRecordHandler.add_checktool_operation_record(instance.checktool, action, user, message)
        return instance, created

    @classmethod
    def delete(cls, instance, user):
        """删除工具依赖方案，真删除
        :param instance: ToolLibScheme, 工具依赖方案
        :param user: User, 用户
        """
        # 如果该方案是默认依赖方案，则需进行额外处理
        if instance.default_flag:
            # 且存在多个依赖方案
            if models.ToolLibScheme.objects.filter(checktool=instance.checktool).count() > 1:
                raise ParseError("无法删除默认依赖方案")
        message = "移除依赖方案：%s" % instance
        OperationRecordHandler.add_checktool_operation_record(instance.checktool, "移除依赖方案", user, message)
        # 真删除
        instance.delete(permanent=True)
