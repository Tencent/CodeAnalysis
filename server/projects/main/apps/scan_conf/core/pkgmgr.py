# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checkpackage core
"""
import logging

# 第三方
from rest_framework.exceptions import ParseError

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core.basemgr import ModelManager
from apps.scan_conf.core.toolmgr import CheckRuleManager
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class BasePkgManager(object):
    """规则包管理 base模块
    """

    @classmethod
    def operation_record(cls, checkpackage, action, user, message=None):
        """规则包日志记录，自定义规则包存入规则配置
        :param checkpackage: CheckPackage, 规则包
        :param action: str, 操作
        :param user: User, 操作人
        :param message: 信息
        """
        try:
            # 自定义规则包
            checkprofile = checkpackage.checkprofile
            OperationRecordHandler.add_checkprofile_operation_record(checkprofile, action, user, message)
        except models.CheckProfile.DoesNotExist:
            # 官方规则包
            OperationRecordHandler.add_checkpackage_operation_record(checkpackage, action, user, message)

    @classmethod
    def create_or_update(cls, name, package_type, user, instance=None, **kwargs):
        """创建/更新规则包
        :param name: str, 规则包名称
        :param package_type: int, 规则包类型
        :param user: User, 操作用户
        :param instance: CheckPackage, 存在即为更新
        :params kwargs: 其他参数
        :return: checkpackage
        """
        instance, created = ModelManager.create_or_update(models.CheckPackage, instance=instance, user=user,
                                                          name=name, package_type=package_type, update_data={
                "name": name,
                **kwargs
            })
        # 兼容处理，如果规则包调整status，则对应将disable调整
        instance.disable = not instance.is_usable()
        instance.save()
        if created:
            action = "创建规则包"
            message = ""
        else:
            action = "更新规则包"
            message = "名称：%s，其他参数：%s" % (name, kwargs)
        cls.operation_record(instance, action, user, message=message)
        return instance

    @classmethod
    def update_checktool(cls, checkpackage, user=None):
        """更新规则包包含的工具
        :param checkpackage: CheckPackage, 规则包
        :param user: User, 操作人
        """
        tool_ids = list(models.PackageMap.objects.filter(
            checkpackage=checkpackage).values_list("checktool_id", flat=True).distinct())
        exist_tool_ids = list(checkpackage.checktool.all().values_list("id", flat=True).distinct())
        add_tools = models.CheckTool.objects.filter(id__in=tool_ids).exclude(id__in=exist_tool_ids)
        if add_tools:
            tool_names = []
            for tool in add_tools:
                checkpackage.checktool.add(tool)
                tool_names.append(tool.name)
            message = "%s" % (";".join(tool_names))
            cls.operation_record(checkpackage, "添加工具", user, message)
        del_tools = checkpackage.checktool.exclude(id__in=tool_ids)
        if del_tools:
            tool_names = []
            for tool in del_tools:
                checkpackage.checktool.remove(tool)
                tool_names.append(tool.name)
            message = "%s" % (";".join(tool_names))
            cls.operation_record(checkpackage, "移除工具", user, message)

    @classmethod
    def _add_checktool_rules_done(cls, checkpackage, checktool, checkrules, user=None):
        """添加工具规则到pm
        :param checkpackage: CheckPackage, 规则包
        :param checktool: CheckTool, 工具
        :param checkrules: CheckRule List, 工具全部规则
        :param user, User, 操作人
        """
        packagemap_models = [models.PackageMap(checkpackage=checkpackage, checktool=checktool, checkrule=rule,
                                               rule_params=rule.rule_params, severity=rule.severity,
                                               state=models.PackageMap.StateEnum.ENABLED) for rule in checkrules]
        # 批量操作
        models.PackageMap.objects.bulk_create(packagemap_models, 1000, ignore_conflicts=True)
        message = "一键添加工具：%s的所有规则" % checktool.name
        cls.operation_record(checkpackage, "批量添加规则", user, message)
        cls.update_checktool(checkpackage, user)

    @classmethod
    def check_add_rule_perm(cls, checkrule, **kwargs):
        """校验规则包添加该规则是否具有权限
        """
        raise NotImplementedError

    @classmethod
    def check_add_tool_rules_perm(cls, checktool, **kwargs):
        """校验规则包添加工具规则是否具有权限
        """
        raise NotImplementedError

    @classmethod
    def add_rules(cls, checkpackage, checkrules, user=None, **kwargs):
        """添加规则
        :param checkpackage: CheckPackage, 规则包
        :param checkrules: CheckRule List, 规则列表
        :param user, User, 操作人
        :return: err_messages, 未添加的规则异常信息集合
        """
        err_messages = []
        # 忽略已添加规则
        pkg_checkrules = checkpackage.checkrule.all()
        checkrules = [v for v in checkrules if v not in pkg_checkrules]
        if not checkrules:
            return

        # checkprofile 存在则为自定义规则包
        checkprofile_admins = []
        try:
            checkprofile = checkpackage.checkprofile
            checkprofile_admins = checkprofile.get_admins()
        except models.CheckProfile.DoesNotExist:
            checkprofile = None

        # 增加新增的规则，删除移除的规则
        new_packagemaps = []
        nrows = 0
        for rule in checkrules:  # 修改为单次新增，避免rc问题
            # 如果规则已失效，则不添加
            if rule.disable:
                err_messages.append("未添加规则[%s]，该规则已失效" % rule.display_name)
                continue

            # 校验是否具有权限添加
            if not cls.check_add_rule_perm(rule, users=checkprofile_admins, **kwargs):
                err_messages.append("未添加规则[%s]，无添加此规则权限" % rule.display_name)
                continue

            # 开始添加规则，get_or_create避免并发
            pm, created = models.PackageMap.objects.get_or_create(checkpackage=checkpackage,
                                                                  checkrule=rule,
                                                                  checktool=rule.checktool)

            # # 赋予规则状态到packgemap
            # if pm.state == models.PackageMap.StateEnum.DISABLED or not pm.severity or not pm.rule_params:
            #     pm.state = models.PackageMap.StateEnum.ENABLED
            #     pm.severity = pm.severity or rule.severity
            #     pm.rule_params = pm.rule_params or rule.rule_params
            #     pm.save()
            # if created:
            #     new_packagemaps.append(pm)
            #     nrows += 1

            # 与旧版保持一致，仅赋予严重级别
            if created:
                pm.severity = rule.severity
                pm.save()
                new_packagemaps.append(pm)
                nrows += 1

        new_rules = [packagemap.checkrule.display_name for packagemap in new_packagemaps]
        if new_rules and user:
            message = "增加%d条规则如下： %s" % (nrows, ";".join(new_rules))
            cls.operation_record(checkpackage, "批量添加规则", user, message)
        cls.update_checktool(checkpackage, user)
        return err_messages

    @classmethod
    def add_checktool_rules(cls, checkpackage, checktool, user=None, **kwargs):
        """添加工具规则到规则包
        :param checkpackage: CheckPackage, 规则包
        :param checktool: CheckTool, 工具
        :param user: User, 操作人
        """
        if not cls.check_add_tool_rules_perm(checktool, checkpackage=checkpackage, **kwargs):
            raise ParseError("没有权限添加该工具规则")
        # 1. 公开工具，所有规则可直接添加到规则包
        # 2. 规则配置admins在工具allusers，则具有权限添加规则
        pkg_rule_ids = list(checkpackage.checkrule.all().values_list("id", flat=True))
        checkrules = CheckRuleManager.filter_tool_all(checktool).exclude(id__in=pkg_rule_ids)
        cls._add_checktool_rules_done(checkpackage, checktool, checkrules, user)

    @classmethod
    def _add_pms(cls, checkpackage, packagemaps, user=None, **kwargs):
        """添加packagemaps，同时会更新最新的packagemap
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List,
        :param user: User, 操作人
        :return: checkrules, 规则
        """
        checkrules = []
        new_pms = []
        for pm in packagemaps:
            if pm.severity != pm.checkrule.severity or pm.rule_params != pm.checkrule.rule_params:
                # pms存在和checkrule不一致，需要同步更新
                new_pms.append(pm)
            checkrules.append(pm.checkrule)
        cls.add_rules(checkpackage, checkrules, user=user, **kwargs)
        # 同步更新
        for pm in new_pms:
            packagemap = models.PackageMap.objects.filter(
                checkpackage=checkpackage, checkrule_id=pm.checkrule_id).first()
            if packagemap and packagemap.id != pm.id:
                packagemap.severity = pm.severity
                packagemap.rule_params = pm.rule_params
                packagemap.save()
        return checkrules

    @classmethod
    def _update_pms(cls, checkpackage, packagemaps, user=None, **kwargs):
        """更新规则包规则
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List, 规则包规则
        :param user: User, 操作人
        :params kwargs: 更新PackageMap的参数
        :return: update_num, display_names
        """
        if not packagemaps:
            return 0, []
        # 新增kwargs后的兼容处理，保证packagemaps update不受**kwargs影响
        pkg_map_dict = {}
        keys = kwargs.keys()
        for key in ["severity", "rule_params", "state"]:
            if key in keys:
                pkg_map_dict[key] = kwargs.pop(key)
        # package不存在packagemap，则先进行增加该规则操作
        checkrules = cls._add_pms(checkpackage, packagemaps, user, **kwargs)
        # 更新
        packagemaps = models.PackageMap.objects.filter(checkpackage=checkpackage, checkrule__in=checkrules)
        update_num = packagemaps.update(**pkg_map_dict)
        display_names = list(packagemaps.values_list("checkrule__display_name", flat=True).distinct())
        return update_num, display_names

    @classmethod
    def update_pms(cls, checkpackage, packagemaps, severity, rule_params, state, user=None, **kwargs):
        """规则包批量修改规则信息
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List, 规则
        :param severity: SEVERITY_CHOICES, 规则严重级别
        :param rule_params: str, 规则参数
        :param state: STATE_CHOICES, 规则状态
        :param user: User, 操作人
        """
        update_num, display_names = cls._update_pms(checkpackage, packagemaps, user=user, severity=severity,
                                                    rule_params=rule_params, state=state, **kwargs)
        severity_dict = dict(models.CheckRule.SEVERITY_CHOICES)
        state_dict = dict(models.PackageMap.STATE_CHOICES)
        message = "修改%d个规则，严重级别为%s，规则参数为%s，状态为%s： %s" % (update_num, severity_dict[severity],
                                                         rule_params, state_dict[state], display_names)
        cls.operation_record(checkpackage, "批量更新规则", user, message)

    @classmethod
    def update_pms_severity(cls, checkpackage, packagemaps, severity, user=None, **kwargs):
        """规则包批量修改规则严重级别
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List, 规则
        :param severity: SEVERITY_CHOICES, 规则严重级别
        :param user: User, 操作人
        """
        update_num, display_names = cls._update_pms(checkpackage, packagemaps, user=user, severity=severity, **kwargs)
        severity_dict = dict(models.CheckRule.SEVERITY_CHOICES)
        message = "规则严重级别更新为：%s。共%d条规则，%s" % (severity_dict[severity], update_num, display_names)
        cls.operation_record(checkpackage, "批量更新规则", user, message)

    @classmethod
    def update_pms_state(cls, checkpackage, packagemaps, state, user=None, **kwargs):
        """规则包批量修改规则状态
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List, 规则
        :param state: STATE_CHOICES, 规则状态
        :param user: User, 操作人
        """
        update_num, display_names = cls._update_pms(checkpackage, packagemaps, user=user, state=state, **kwargs)
        state_dict = dict(models.PackageMap.STATE_CHOICES)
        remark = kwargs.get('remark', '')
        message = "规则状态更新为：%s。共%d条规则，%s，remark: %s" % (state_dict[state], update_num, display_names, remark)
        cls.operation_record(checkpackage, "批量更新规则", user, message)

    @classmethod
    def update_pms_params(cls, checkpackage, packagemaps, rule_params, user=None, **kwargs):
        """规则包中量修改规则的规则参数
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List, 规则
        :param rule_params: str, 规则参数
        :param user: User, 操作人
        """
        update_num, display_names = cls._update_pms(checkpackage, packagemaps, user=user, rule_params=rule_params,
                                                    **kwargs)
        message = "修改%d个规则的参数为%s。规则： %s" % (update_num, rule_params, display_names)

        cls.operation_record(checkpackage, "批量更新规则", user, message)

    @classmethod
    def delete_pms(cls, checkpackage, packagemaps, reason, user=None):
        """规则包批量移除规则
        :param checkpackage: CheckPackage, 规则包
        :param packagemaps: PackageMap List, 规则
        :param reason: str, 移除原因
        :param user: User, 操作人
        """
        checkrules = [packagemap.checkrule for packagemap in packagemaps]
        packagemaps = models.PackageMap.objects.filter(checkpackage=checkpackage, checkrule__in=checkrules)
        display_names = [pm.checkrule.display_name for pm in packagemaps]
        delete_num, _ = packagemaps.delete()
        message = "因【%s】移除%d条规则，%s" % (reason, delete_num, display_names)
        cls.operation_record(checkpackage, "批量移除规则", user, message)
        cls.update_checktool(checkpackage, user)

    @classmethod
    def save_pms_by_script(cls, checkpackage, package_maps):
        current_ids = []
        for pm_data in package_maps:
            # 避免同名规则的出现
            checkrule = models.CheckRule.objects.filter(checktool=pm_data["checktool"],
                                                        real_name=pm_data["checkrule"].real_name).first()
            if not checkrule:
                continue
            pm, created = models.PackageMap.objects.get_or_create(
                checkpackage=checkpackage, checktool=pm_data["checktool"],
                checkrule=checkrule, defaults=pm_data)
            if not created:
                pm.severity = pm_data["severity"]
                pm.rule_params = pm_data["rule_params"]
                pm.state = pm_data["state"]
                pm.save()
            current_ids.append(pm.id)
        # 移除不存在的规则
        models.PackageMap.objects.filter(checkpackage=checkpackage).exclude(id__in=current_ids).delete()

        # 添加工具/语言到规则包
        checkpackage.checktool.set(
            models.PackageMap.objects.filter(checkpackage=checkpackage).values_list("checktool", flat=True).distinct()
        )

    @classmethod
    def load_by_script(cls, name, user, checkpackage=None, **kwargs):
        """根据脚本创建/更新规则包
        :param name: 规则包名称
        :param user: User, 操作用户
        :param checkpackage: CheckPackage, 规则包，存在则为更新操作
        :param kwargs: 规则包相关参数
        :return: checkpackage
        """
        # 日志记录
        if not checkpackage:
            action = "脚本创建规则包"
            message = "通过JSON脚本创建规则包"
        else:
            action = "脚本更新规则包"
            message = "通过JSON脚本更新规则包"
        checkrules_data = kwargs.pop('get_package_maps', [])
        package_type = kwargs.pop('package_type', models.CheckPackage.PackageTypeEnum.OFFICIAL)
        checkpackage = cls.create_or_update(name, package_type, user, instance=checkpackage, **kwargs)
        cls.save_pms_by_script(checkpackage, checkrules_data)
        cls.operation_record(checkpackage, action, user, message=message)
        return checkpackage

    @classmethod
    def disable_by_script(cls, checkpackage_json, user=None):
        """通过脚本禁用规则包
        :param checkpackage_json: 规则包json
        :param user: User, 操作用户
        """
        # 如果是json数组则只取第一项
        if isinstance(checkpackage_json, list) and len(checkpackage_json) > 0:
            checkpackage_json = checkpackage_json[0]
        name = checkpackage_json.get("name")
        checkpackage = models.CheckPackage.objects.filter(name=name).first()
        if checkpackage:
            checkpackage.open_saas = False
            checkpackage.status = models.CheckPackage.StatusEnum.DISABLED
            # 暂时仍然保留disable
            checkpackage.disable = True
            checkpackage.save()
            message = "禁用规则包%s。。。" % checkpackage.name
            cls.operation_record(checkpackage, "脚本更新规则包", user, message=message)
            logger.info(message)

    @classmethod
    def filter_usable(cls, **kwargs):
        """筛选可用的官方规则包，即官方且未失效的规则包
        :return: qs
        """
        # 暂时仍旧保留disable，后续会移除
        official_type = models.CheckPackage.PackageTypeEnum.OFFICIAL
        disabled_status = models.CheckPackage.StatusEnum.DISABLED
        return models.CheckPackage.objects.filter(package_type=official_type, disable=False) \
            .exclude(status=disabled_status).order_by("-modified_time")

    @classmethod
    def get_office_checkpackages(cls, languages=None, labels=None):
        """筛选官方规则包
        :param languages: Language list，语言列表
        :param labels: Label list，标签列表
        :return: qs
        注：原来某个地方需要调用，调整到具体的BasePkgManager里面
        """
        official_type = models.CheckPackage.PackageTypeEnum.OFFICIAL
        checkpackages = models.CheckPackage.objects.filter(package_type=official_type).order_by("id")
        if languages:
            checkpackages = checkpackages.filter(languages__in=languages)
        if labels:
            checkpackages = checkpackages.filter(labels__in=labels)
        return checkpackages

    @classmethod
    def get_checkrules_by_checkpackages(cls, checkpackages):
        """通过规则包列表获取规则列表
        """
        package_ids = [pkg.id for pkg in checkpackages]
        all_pms = models.PackageMap.objects.filter(checkpackage_id__in=package_ids).select_related(
            'checkrule', 'checktool').order_by('checkrule_id')
        return all_pms.distinct()


class CheckPackageManager(BasePkgManager):

    @classmethod
    def check_add_rule_perm(cls, checkrule, **kwargs):
        """校验规则包添加规则是否具备权限
        1. 如果该规则为公开工具规则则规则包可添加此规则
        2. 如果该规则为团队自定义规则，且对应工具为协同工具，则规则包可添加此规则
        3. 如果该规则为私有工具规则，且该团队可使用此工具，则规则包可添加此规则
        :param checkrule: CheckRule, 规则
        :params kwargs:
            tool_key: str, 规则的tool_key，为工具规则时默认为default
        """
        checktool = checkrule.checktool
        tool_key = kwargs.get("tool_key", None)
        if checktool.is_public() and checkrule.tool_key == CheckRuleManager.ToolKeyEnum.DEFAULT:
            return True
        if tool_key:
            if checkrule.tool_key == tool_key and checktool.open_maintain:
                return True
            if checkrule.tool_key == CheckRuleManager.ToolKeyEnum.DEFAULT and \
                    models.CheckToolWhiteKey.objects.filter(tool_key=tool_key, tool_id=checktool.id).exists():
                return True
        return False

    @classmethod
    def check_add_tool_rules_perm(cls, checktool, **kwargs):
        """校验规则包添加工具规则是否具备权限
        1. 如果工具为公开工具则都有权限
        2. 如果为私有工具，团队具备使用该工具则有权限
        :param checktool: CheckTool, 工具
        :params kwargs:
            tool_key: str, 工具的tool_key
        """
        if checktool.is_public():
            return True
        tool_key = kwargs.get("tool_key", None)
        if tool_key and models.CheckToolWhiteKey.objects.filter(tool_key=tool_key, tool_id=checktool.id).exists():
            return True
        return False
