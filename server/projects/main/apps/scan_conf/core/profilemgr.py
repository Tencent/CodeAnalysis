# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checkprofile core
"""
import logging

# 项目内
from apps.codeproj.models import LintBaseSetting
from apps.scan_conf import models
from apps.scan_conf.core.basemgr import ModelManager
from apps.scan_conf.core.pkgmgr import CheckPackageManager
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class CheckProfileManager(object):
    """规则配置manager
    """

    @classmethod
    def after_updating_profile(cls, checkprofile):
        """更新规则集后
        """
        tool_ids = list(checkprofile.get_checktools().values_list("id", flat=True))
        lintsetting = LintBaseSetting.objects.filter(checkprofile_id=checkprofile).first()
        if not lintsetting:
            return
        scheme = lintsetting.scan_scheme
        scheme.checktool_ids = tool_ids
        scheme.save()

    @classmethod
    def create_or_update(cls, name, user, instance=None, **kwargs):
        """创建/更新规则配置
        :param name: str, 规则配置名称
        :param user, User, 操作人
        :param instance: CheckProfile, 规则配置，存在则为更新
        :params kwargs: 其他参数
        :return: checkprofile, created
        """
        checkprofile, created = ModelManager.create_or_update(
            models.CheckProfile, instance=instance,
            ignore_conflict=kwargs.pop("ignore_conflict", False),
            user=user, name=name, update_data={
                "name": name,
                **kwargs
            }, )
        if not checkprofile.custom_checkpackage:
            checkpackage, _ = models.CheckPackage.objects.get_or_create(
                name="profile[%d]自定义规则包" % checkprofile.id,
                defaults={"package_type": models.CheckPackage.PackageTypeEnum.CUSTOM})
            checkprofile.custom_checkpackage = checkpackage
            checkprofile.save(user=user)
        # 日志记录
        if created:
            # 增加授权，
            # 由于依赖代码库权限，可不单独设置权限
            # checkprofile.assign_perm(user.username, models.CheckProfile.PermissionEnum.ADMIN)
            action = "创建规则配置"
            message = ""
        else:
            action = "更新规则配置"
            message = "规则配置名称: %s, 其他参数: %s" % (name, kwargs)
        OperationRecordHandler.add_checkprofile_operation_record(checkprofile, action, user.username, message)
        cls.after_updating_profile(checkprofile)
        return checkprofile, created

    @classmethod
    def add_official_pkgs(cls, checkprofile, checkpackages, user=None):
        """添加官方规则包
        :param checkprofile: CheckProfile, 规则配置
        :param checkpackages: CheckPackage List, 官方规则包
        :param user: User, 操作人
        """
        checkprofile.checkpackages.add(*checkpackages)
        checkpackage_names = [checkpackage.name for checkpackage in checkpackages]
        message = "添加%d条规则包：%s" % (len(checkpackage_names), checkpackage_names)
        cls.after_updating_profile(checkprofile)
        OperationRecordHandler.add_checkprofile_operation_record(checkprofile, "添加官方规则包", user, message)

    @classmethod
    def rm_official_pkgs(cls, checkprofile, checkpackages, user=None):
        """移除官方规则包
        :param checkprofile: CheckProfile, 规则配置
        :param checkpackages: CheckPackage List, 官方规则包
        :param user: User, 操作人
        """
        checkprofile.checkpackages.remove(*checkpackages)
        checkpackage_names = [checkpackage.name for checkpackage in checkpackages]
        message = "移除%d条规则包：%s" % (len(checkpackage_names), checkpackage_names)
        cls.after_updating_profile(checkprofile)
        OperationRecordHandler.add_checkprofile_operation_record(checkprofile, "移除官方规则包", user, message)

    @classmethod
    def v1_pkg_and_pms_save(cls, checkprofile, **kwargs):
        """用于v1接口，支持规则配置的规则包和规则增删改查
        :param checkprofile: CheckProfile, 规则配置
        :params kwargs: 其他参数
        """
        checkpackage_list = kwargs.get("checkpackages", [])
        checkpackage_names = ";".join(["[%s]%s" % (checkpackage.id, checkpackage.name)
                                       for checkpackage in checkpackage_list])
        checkrule_list = kwargs.get("checkrules", [])
        operation_type = kwargs.get("operation_type")
        user = kwargs.get("user", None)
        if operation_type == models.CheckProfile.OperationTypeEnum.ALLDELETE:  # 删除所有规则包的自定义规则
            checkprofile.custom_checkpackage.get_package_maps().delete()
            checkprofile.checkpackages.clear()
            cls.after_updating_profile(checkprofile)
            OperationRecordHandler.add_checkprofile_operation_record(checkprofile, "api批量移除规则配置", user,
                                                                     message="批量移除所有官方规则包和自定义规则")
            return
        if not (checkrule_list or checkpackage_list):
            # 对于其他操作，如果没有传递规则包或自定义规则则跳过
            return
        if operation_type == models.CheckProfile.OperationTypeEnum.DELETE:  # 按传递的规则包或规则批量移除
            if checkpackage_list:
                checkprofile.checkpackages.remove(*checkpackage_list)
            if checkrule_list:
                checkrules = [checkrule_dict.get("checkrule") for checkrule_dict in checkrule_list]
                models.PackageMap.objects.filter(checkpackage=checkprofile.custom_checkpackage,
                                                 checkrule__in=checkrules).delete()
            cls.after_updating_profile(checkprofile)
            OperationRecordHandler.add_checkprofile_operation_record(
                checkprofile, "api批量移除规则配置", user, message="批量移除官方规则包：%s。移除自定义规则：%s" % (
                    checkpackage_names, checkrule_list))
            return
        else:
            if checkpackage_list:
                if operation_type == models.CheckProfile.OperationTypeEnum.ALLUPDATE:
                    checkprofile.checkpackages.set(checkpackage_list)
                else:
                    checkprofile.checkpackages.add(*checkpackage_list)
            if checkrule_list:
                custom_checkpackage = checkprofile.custom_checkpackage
                if operation_type == models.CheckProfile.OperationTypeEnum.ALLUPDATE:  # 需先移除所有规则
                    custom_checkpackage.get_package_maps().delete()
                checkrules = [checkrule_dict.get("checkrule") for checkrule_dict in checkrule_list]
                # 规则添加到自定义规则包
                CheckPackageManager.add_rules(custom_checkpackage, checkrules, user)
                # 修改packagemap
                for checkrule_dict in checkrule_list:
                    checkrule = checkrule_dict.get("checkrule")
                    packagemap = models.PackageMap.objects.filter(checkpackage=custom_checkpackage,
                                                                  checkrule=checkrule).first()
                    if packagemap:
                        packagemap.severity = checkrule_dict.get("severity", packagemap.severity)
                        packagemap.rule_params = checkrule_dict.get("rule_params", packagemap.rule_params)
                        packagemap.state = checkrule_dict.get("state", packagemap.state)
                        packagemap.save()
            cls.after_updating_profile(checkprofile)
            OperationRecordHandler.add_checkprofile_operation_record(
                checkprofile, "api批量更新规则配置", user, message="操作类型：%s。官方规则包：%s。自定义规则：%s" % (
                    operation_type, checkpackage_names, checkrule_list))
            return

    @classmethod
    def create_temp_checkprofile(cls, scan_scheme_template, user=None):
        """创建分析方案模板规则配置
        :param scan_scheme_template: ScanScheme, 分析方案模板
        :param user: User, 操作人
        :returns: checkprofile
        注：原create_checkprofile_by_scanscheme_template方法，原来某个地方需要调用，调整到具体的CheckProfileManager里面
        """
        checkprofile_name = "ScanSchemeTemplate[%d]规则集" % scan_scheme_template.id
        checkprofile, _ = cls.create_or_update(checkprofile_name, user)
        OperationRecordHandler.add_checkprofile_operation_record(checkprofile=checkprofile,
                                                                 action="创建分析方案模版规则配置",
                                                                 username=user.username,
                                                                 message={})
        return checkprofile

    @classmethod
    def create_scheme_checkprofile(cls, scan_scheme, user=None, labels=None):
        """创建分析方案规则配置
        :param scan_scheme: ScanScheme, 分析方案
        :param user: User, 操作人
        :param labels: Label list, 标签
        :returns: checkprofile
        注：原create_checkprofiles_by_scanscheme方法，原来某个地方需要调用，调整到具体的CheckProfileManager里面
        """
        checkprofile_name = "ScanScheme[%d]规则集" % scan_scheme.id
        checkprofile, _ = cls.create_or_update(checkprofile_name, user, ignore_conflict=True)
        languages = scan_scheme.languages.all()
        if not labels:
            labels = models.Label.objects.filter(name="基础")
        official_packages = CheckPackageManager.filter_usable().filter(languages__in=languages, labels__in=labels)
        # official_packages = models.CheckPackage.objects.filter(
        #     package_type=models.CheckPackage.PackageTypeEnum.OFFICIAL,
        #     languages__in=languages,
        #     labels__in=labels)
        checkprofile.checkpackages.set(official_packages)
        cls.after_updating_profile(checkprofile)
        if user:
            message = "官方规则集设置为：%s" % ";".join(
                official_packages.values_list("name", flat=True).distinct())
            OperationRecordHandler.add_checkprofile_operation_record(checkprofile=checkprofile,
                                                                     action="根据扫描方案配置官方规则集",
                                                                     username=user.username,
                                                                     message=message)
        return checkprofile

    @classmethod
    def copy_from_checkprofile(cls, checkprofile, from_checkprofile, user=None):
        """从from_checkprofile拷贝规则配置
        :param checkprofile: CheckProfile, 规则配置
        """
        # 清空原规则配置
        if checkprofile.custom_checkpackage:
            checkprofile.custom_checkpackage.get_package_maps().delete()
        checkprofile.checkpackages.clear()

        # 赋予规则包
        checkprofile.checkpackages.set(from_checkprofile.checkpackages.all())
        # 赋予自定义规则
        new_packagemaps = []
        for packagemap in models.PackageMap.objects.filter(checkpackage=from_checkprofile.custom_checkpackage):
            new_packagemaps.append(
                models.PackageMap(checkpackage=checkprofile.custom_checkpackage,
                                  checkrule=packagemap.checkrule,
                                  checktool=packagemap.checktool,
                                  severity=packagemap.severity,
                                  rule_params=packagemap.rule_params,
                                  state=packagemap.state)
            )
        models.PackageMap.objects.bulk_create(new_packagemaps, 1000)
        cls.after_updating_profile(checkprofile)
        if user:
            message = "拷贝规则集[%s]的所有内容到规则集[%s]内" % (from_checkprofile.id, checkprofile.id)
            OperationRecordHandler.add_checkprofile_operation_record(checkprofile=checkprofile,
                                                                     action="拷贝规则集",
                                                                     username=user.username,
                                                                     message=message)
        return checkprofile

    @classmethod
    def create_from_checkprofile(cls, name, from_checkprofile, user=None):
        """通过from_checkprofile新建或更新一个规则集
        :param name: str, 规则集名称
        :param from_checkprofile: CheckProfile, 拷贝的规则集
        :param user: User: 操作用户
        :return: CheckProfile, 创建的规则集
        """
        checkprofile, created = cls.create_or_update(name, user)
        if not created:
            logger.info("checkprofile %s exist" % name)
            return checkprofile
        return cls.copy_from_checkprofile(checkprofile, from_checkprofile, user)

    @classmethod
    def get_org(cls, checkprofile):
        """获取规则配置对应的团队
        :param checkprofile: CheckProfile, 规则配置
        :return: org
        """
        lintbasesetting = LintBaseSetting.objects.filter(checkprofile=checkprofile).first()
        if lintbasesetting:
            scan_scheme = lintbasesetting.scan_scheme
            repo = scan_scheme.repo
            if repo:
                return repo.organization
