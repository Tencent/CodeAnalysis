# -*- coding: utf-8 -*-
"""
公共实现方法，介于models/serializer 和apis之间
"""
import logging

# 项目内 
from apps.scan_conf import models
from apps.scan_conf.core import CheckToolManager, CheckPackageManager
from apps.scan_conf.serializers.base import CheckerSerializer, CheckPackageJsonSerializer, PackageMapJsonSerializer

logger = logging.getLogger(__name__)


def load_checkers(data):
    """load 工具json
    """
    checktool = models.CheckTool.objects.filter(name=data["name"]).first()
    slz = CheckerSerializer(instance=checktool, data=data, context={"is_local_script": True})
    slz.is_valid(raise_exception=True)
    logger.info("开始保存工具%s数据。。。" % (checktool.name if checktool else data["name"]))
    checktool_name = slz.validated_data.pop("name")
    tool_key = data.get('tool_key')
    return CheckToolManager.load_by_script(checktool_name, None, checktool=checktool, tool_key=tool_key,
                                           **slz.validated_data)


def disable_checkers(data):
    """工具私有化，用于saas，将工具状态调整为私有
    """
    checktool = models.CheckTool.objects.filter(name=data["name"]).first()
    if checktool:
        checktool.open_saas = False
        checktool.open_user = False
        checktool.open_maintain = False
        checktool.save()
        logger.info("禁用工具%s。。。" % checktool.name)


def get_checker_data(checktool_name):
    """获取工具json
    """
    checktool = models.CheckTool.objects.get(name=checktool_name)
    slz = CheckerSerializer(instance=checktool)
    return slz.data


def load_checkpackages(data):
    """load 官方规则包
    """
    checkpackage = models.CheckPackage.objects.filter(name=data["name"]).first()
    slz = CheckPackageJsonSerializer(instance=checkpackage, data=data)
    slz.is_valid(raise_exception=True)
    logger.info("开始保存规则包[%s]数据。。。" % (checkpackage.name if checkpackage else data["name"]))
    checkpackage_name = slz.validated_data.pop("name")
    return CheckPackageManager.load_by_script(checkpackage_name, None,
                                              checkpackage=checkpackage, **slz.validated_data)


def disable_checkpackages(data):
    CheckPackageManager.disable_by_script(data)


def get_checkpackage_data(checkpackage_id):
    """获取规则包json
    """
    checkpackage = models.CheckPackage.objects.get(id=checkpackage_id)
    slz = CheckPackageJsonSerializer(instance=checkpackage)
    return slz.data


def get_packagemap_data(packagemap):
    """获取规则包映射
    """
    slz = PackageMapJsonSerializer(instance=packagemap)
    return slz.data
