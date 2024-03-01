# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
公共实现方法，介于models/serializer 和apis之间
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core import CheckToolManager, CheckPackageManager, ToolLibManager
from apps.scan_conf.serializers.base import CheckerSerializer, CheckPackageJsonSerializer, ToolLibEditSerializer
from apps.codeproj.core import ScmAuthManager

logger = logging.getLogger(__name__)


class ToolLibLoadManager(object):
    """工具依赖load管理
    """

    @classmethod
    def preload_handler(cls, toollib_json):
        """工具依赖json前置处理
        :param toollib_json: dict, 工具依赖json
        :return: toollib_json
        """
        return toollib_json

    @classmethod
    def postload_handler(cls, toollib, scm_auth, user):
        """工具依赖后置处理
        :param toollib: ToolLib, 工具依赖
        :param scm_auth: ScmAuth, 凭证
        :param user: User, 用户
        :return: toollib_name
        """
        # 当工具依赖存在scm_auth时，保存凭证信息
        if toollib.scm_type != models.ToolLib.ScmTypeEnum.LINK and scm_auth:
            ScmAuthManager.create_toollib_auth(
                toollib, user, scm_auth_type=scm_auth.get("auth_type"),
                scm_account=scm_auth.get("scm_account"),
                scm_ssh_info=scm_auth.get("scm_ssh")
            )
        return toollib.name

    @classmethod
    def loadlib(cls, toollib_json, user):
        """工具依赖json load
        :param toollib_json: dict, 工具依赖json
        :param user: User, 用户
        :return: status, toollib_name
        """
        toollib_name = toollib_json["name"]
        # 默认load工具依赖是系统依赖
        lib_key = ToolLibManager.LibKeyEnum.SYSTEM
        try:
            data = cls.preload_handler(toollib_json)
            toollib = models.ToolLib.objects.filter(name=toollib_name, lib_key=lib_key).first()
            slz = ToolLibEditSerializer(instance=toollib, data=data, context={"is_local_script": True, "user": user})
            slz.is_valid(raise_exception=True)
            logger.info("开始保存工具依赖%s数据。。。" % toollib_name)
            scm_auth = slz.validated_data.pop("scm_auth", None)
            toollib_name = slz.validated_data.pop("name")
            toollib, _ = ToolLibManager.create_or_update(toollib_name, user, instance=toollib,
                                                        lib_key=lib_key, **slz.validated_data)
            return True, cls.postload_handler(toollib, scm_auth=scm_auth, user=user)
        except Exception as e:
            logger.error(e)
            return False, toollib_name

    @classmethod
    def loadlib_by_workers(cls, toollib_json_list, user, workers=10):
        """并发执行工具依赖json load
        :param toollib_json_list: list<dict>, 工具依赖json列表
        :param user: User, 用户
        :param workers: int, 并发数, 默认10
        :return: list<status, toollib_name>
        """
        load_res_list = []
        toollib_count = len(toollib_json_list)
        for i_idx in range(0, toollib_count, workers):
            with ThreadPoolExecutor(max_workers=workers) as t_thread:
                all_task = []
                for j_idx in range(0, workers):
                    index = i_idx + j_idx
                    # 超出索引跳过
                    if index >= toollib_count:
                        break
                    toollib_json = toollib_json_list[i_idx+j_idx]
                    logger.info('--> [%s/%s], toollib name: %s' % (
                        toollib_count, index+1, toollib_json["name"]))
                    task = t_thread.submit(cls.loadlib, toollib_json, user)
                    all_task.append(task)
                for future in as_completed(all_task):
                    load_res_list.append(future.result())
        return load_res_list


class CheckToolLoadManager(object):
    """工具load管理
    """

    @classmethod
    def preload_handler(cls, checktool_json):
        """工具json前置处理
        :param checktool_json: dict, 工具json
        :return: checktool_json
        """
        return checktool_json

    @classmethod
    def postload_handler(cls, checktool, admins=None):
        """工具后置处理
        :param checktool: CheckTool, 工具
        :param admins: list<User>, 管理员
        :return: checktool_name
        """
        if admins and not checktool.owners.exists():
            # 如果工具owners不存在
            checktool.owners.add(*admins)
        return checktool.name

    @classmethod
    def loadchecker(cls, checktool_json, admins=None):
        """工具json load
        :param checktool_json: dict, 工具json
        :param admins: list<User>, 管理员
        :return: status, checktool_name
        """
        checktool_name = checktool_json["name"]
        try:
            data = cls.preload_handler(checktool_json)
            if data:
                checktool = models.CheckTool.objects.filter(name=checktool_name).first()
                slz = CheckerSerializer(instance=checktool, data=data, context={"is_local_script": True})
                slz.is_valid(raise_exception=True)
                logger.info("开始保存工具%s数据。。。" % checktool_name)
                checktool_name = slz.validated_data.pop("name")
                tool_key = data.get('tool_key')
                checktool = CheckToolManager.load_by_script(checktool_name, None, checktool=checktool,
                                                tool_key=tool_key, **slz.validated_data)
                return True, cls.postload_handler(checktool, admins=admins)
            return True, checktool_name
        except Exception as e:
            logger.error(e)
            return False, checktool_name

    @classmethod
    def loadchecker_by_workers(cls, checktool_json_list, admins=None, workers=10):
        """并发执行工具json load
        :param checktool_json_list: list<dict>, 工具json列表
        :param admins: list<User>, 管理员
        :param workers: int, 并发数, 默认10
        :return: list<status, checktool_name>
        """
        load_res_list = []
        checktool_count = len(checktool_json_list)
        for i_idx in range(0, checktool_count, workers):
            with ThreadPoolExecutor(max_workers=workers) as t_thread:
                all_task = []
                for j_idx in range(0, workers):
                    index = i_idx + j_idx
                    # 超出索引跳过
                    if index >= checktool_count:
                        break
                    checktool_json = checktool_json_list[i_idx+j_idx]
                    logger.info('--> [%s/%s], checktool name: %s' % (
                        checktool_count, index+1, checktool_json["name"]))
                    task = t_thread.submit(cls.loadchecker, checktool_json, admins)
                    all_task.append(task)
                for future in as_completed(all_task):
                    load_res_list.append(future.result())
        return load_res_list

    @classmethod
    def getchecker(cls, checktool_name):
        """
        :param checktool_name: str, 工具名称
        :return: checktool_json
        """
        checktool = models.CheckTool.objects.get(name=checktool_name)
        slz = CheckerSerializer(instance=checktool)
        return slz.data


class CheckPackageLoadManager(object):
    """规则包load管理
    """

    @classmethod
    def preload_handler(cls, checkpackage_json):
        """工具json前置处理
        :param checkpackage_json: dict, 工具json
        :return: checkpackage_json
        """
        return checkpackage_json

    @classmethod
    def postload_handler(cls, checkpackage):
        """工具后置处理
        :param checkpackage: CheckPackage, 规则包
        :return: checkpackage_name
        """
        # 通过load的规则包默认都为官方规则包
        if checkpackage.package_type != models.CheckPackage.PackageTypeEnum.OFFICIAL:
            logger.info("package[%s] is not official set to official..." % checkpackage.name)
            checkpackage.package_type = models.CheckPackage.PackageTypeEnum.OFFICIAL
            checkpackage.save()
        return checkpackage.name

    @classmethod
    def loadpkg(cls, checkpackage_json):
        """规则包json load
        :param checkpackage_json: dict, 规则包json
        :return: status, checkpackage_name
        """
        checkpackage_name = checkpackage_json["name"]
        try:
            data = cls.preload_handler(checkpackage_json)
            if data:
                checkpackage = models.CheckPackage.objects.filter(name=checkpackage_name).first()
                slz = CheckPackageJsonSerializer(instance=checkpackage, data=data)
                slz.is_valid(raise_exception=True)
                logger.info("开始保存规则包[%s]数据。。。" % checkpackage_name)
                checkpackage_name = slz.validated_data.pop("name")
                checkpackage = CheckPackageManager.load_by_script(checkpackage_name, None,
                                                checkpackage=checkpackage, **slz.validated_data)
                return True, cls.postload_handler(checkpackage)
            return True, checkpackage_name
        except Exception as e:
            logger.error(e)
            return False, checkpackage_name

    @classmethod
    def loadpkg_by_workers(cls, checkpackage_json_list, workers=10):
        """并发执行工具json load
        :param checkpackage_json_list: list<dict>, 规则包json列表
        :param workers: int, 并发数, 默认10
        :return: list<status, checkpackage_name>
        """
        load_res_list = []
        checkpackage_count = len(checkpackage_json_list)
        for i_idx in range(0, checkpackage_count, workers):
            with ThreadPoolExecutor(max_workers=workers) as t_thread:
                all_task = []
                for j_idx in range(0, workers):
                    index = i_idx + j_idx
                    # 超出索引跳过
                    if index >= checkpackage_count:
                        break
                    checkpackage_json = checkpackage_json_list[i_idx+j_idx]
                    logger.info('--> [%s/%s], checkpackage name: %s' % (
                        checkpackage_count, index+1, checkpackage_json["name"]))
                    task = t_thread.submit(cls.loadpkg, checkpackage_json)
                    all_task.append(task)
                for future in as_completed(all_task):
                    load_res_list.append(future.result())
        return load_res_list

    @classmethod
    def getpkg(cls, checkpackage_id):
        """获取规则包json
        :param checkpackage_id: int, 规则包ID
        :return: checkpackage_json
        """
        checkpackage = models.CheckPackage.objects.get(id=checkpackage_id)
        slz = CheckPackageJsonSerializer(instance=checkpackage)
        return slz.data
