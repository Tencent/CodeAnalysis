# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - pkg,profile models
"""
# 第三方
from django.db import models, IntegrityError
from django.contrib.auth.models import User, Group
from guardian.shortcuts import assign_perm

# 项目内
from apps.scan_conf.models.base import Language, Label
from apps.scan_conf.models.rule import CheckRule
from apps.scan_conf.models.tool import CheckTool
from apps.base.basemodel import CDBaseModel


class CheckPackage(CDBaseModel):
    """规则包表
    """

    class PackageTypeEnum:
        CUSTOM = 1
        OFFICIAL = 2

    PACKAGETYPE_CHOICES = (
        (PackageTypeEnum.CUSTOM, "自定义"),
        (PackageTypeEnum.OFFICIAL, "官方"),
    )

    PACKAGETYPE_ENG_CHOICES = (
        (PackageTypeEnum.CUSTOM, "custom"),
        (PackageTypeEnum.OFFICIAL, "official"),
    )

    class StatusEnum:
        RUNNING = 1
        TESTING = 2
        HIDDEN = 3
        DISABLED = 9

    STATUS_CHOICES = (
        (StatusEnum.RUNNING, "已启用"),
        (StatusEnum.TESTING, "测试中"),
        (StatusEnum.HIDDEN, "隐藏中"),
        (StatusEnum.DISABLED, "已禁用"),
    )

    name = models.CharField(max_length=64, unique=True, help_text='规则包名称')
    description = models.CharField(max_length=512, blank=True, null=True, help_text='规则包描述')
    package_type = models.IntegerField(choices=PACKAGETYPE_CHOICES, help_text="规则包类型")
    languages = models.ManyToManyField(Language, blank=True, help_text='适用语言')
    labels = models.ManyToManyField(Label, blank=True, help_text='标签')
    checkrule = models.ManyToManyField(CheckRule, through='PackageMap',
                                       related_name="checkpackage", help_text='工具规则')
    checktool = models.ManyToManyField(CheckTool, help_text='分析工具')
    revision = models.CharField(max_length=32, blank=True, null=True, help_text='版本号')
    open_saas = models.BooleanField(default=False, help_text="公有云是否可用")
    status = models.IntegerField(choices=STATUS_CHOICES, default=StatusEnum.RUNNING, help_text="规则包状态")
    disable = models.BooleanField(default=False, help_text="规则包是否可用")
    envs = models.TextField(blank=True, null=True, help_text="环境变量")

    @classmethod
    def filter_usable(cls, queryset):
        """筛选可用的规则包
        :param: queryset, CheckPackage queryset
        :return: queryset
        """
        # 暂时仍旧保留disable，后续会移除
        return queryset.filter(disable=False).exclude(status=cls.StatusEnum.DISABLED)

    @classmethod
    def user_objects(cls, user):
        """规则包筛选
        """
        if user.is_superuser:
            return cls.objects.all()
        else:
            return cls.objects.exclude(status=CheckPackage.StatusEnum.HIDDEN)

    def is_usable(self):
        """判断当前规则包是否可使用
        """
        if self.status > self.StatusEnum.TESTING:
            return False
        else:
            return True

    def get_package_maps(self):
        return PackageMap.objects.filter(checkpackage=self)

    def __str__(self):
        return "%s" % self.name


class PackageReleaseLog(CDBaseModel):
    """规则包版本记录表
    """
    checkpackage = models.ForeignKey(CheckPackage, help_text='规则包', on_delete=models.CASCADE)
    revision = models.CharField(max_length=32, help_text='版本号')
    message = models.TextField(verbose_name='发布内容')


class PackageMap(models.Model):
    """规则包表和规则的映射表，规则中指明用户对规则的级别定义
    """

    class StateEnum:
        ENABLED = 1
        DISABLED = 2

    STATE_CHOICES = (
        (StateEnum.ENABLED, "生效中"),
        (StateEnum.DISABLED, "已屏蔽"),
    )

    STATE_ENG_CHOICES = (
        (StateEnum.ENABLED, "enabled"),
        (StateEnum.DISABLED, "disabled"),
    )
    checkpackage = models.ForeignKey(CheckPackage, related_name="relation", on_delete=models.CASCADE,
                                     help_text='规则包')
    checkrule = models.ForeignKey(CheckRule, related_name="relation", on_delete=models.CASCADE, help_text='规则')
    checktool = models.ForeignKey(CheckTool, null=True, on_delete=models.CASCADE, help_text='工具')
    severity = models.IntegerField(choices=CheckRule.SEVERITY_CHOICES, blank=True, null=True, help_text='严重级别')
    rule_params = models.TextField(null=True, blank=True, help_text='规则参数')
    state = models.IntegerField(choices=STATE_CHOICES, default=StateEnum.ENABLED, help_text='状态')

    def __str__(self):
        return "packagemap-%s-%s" % (self.checkpackage_id, self.checkrule_id)


class CheckProfile(CDBaseModel):
    """规则集表
    """

    class PermissionNameEnum:
        CHANGE_PROFILE_PERM = "change_checkprofile"
        VIEW_PROFILE_PERM = "view_checkprofile"

    class PermissionEnum:
        ADMIN = 0

    PERMISSION_CHOICES = (
        (PermissionEnum.ADMIN, 'admin'),
    )

    class ProfileType:
        DEFAULT = 1
        RECOMMEND = 2
        PRIVATE = 3

    PROFILETYPE_CHOICES = (
        (ProfileType.DEFAULT, "默认"),
        (ProfileType.RECOMMEND, "推荐"),
        (ProfileType.PRIVATE, "项目专用")
    )

    class OperationTypeEnum:
        UPDATE = 1
        ALLUPDATE = 2
        DELETE = 3
        ALLDELETE = 4

    OPERATIONTYPE_CHOICES = (
        (OperationTypeEnum.UPDATE, "批量更新/添加"),
        (OperationTypeEnum.ALLUPDATE, "移除已有，批量添加"),
        (OperationTypeEnum.DELETE, "批量移除"),
        (OperationTypeEnum.ALLDELETE, "移除所有")
    )

    name = models.CharField(max_length=64, help_text='规则集名称', unique=True)
    checkpackages = models.ManyToManyField(CheckPackage, help_text='规则包', related_name="used_checkprofiles")
    custom_checkpackage = models.OneToOneField(CheckPackage, help_text='自定义规则包', on_delete=models.CASCADE,
                                               blank=True, null=True, related_name="checkprofile")

    def get_checktools(self):
        """ 获取规则集工具，返回的是一个QuerySet对象
        """
        package_ids = list(self.checkpackages.all().values_list("id", flat=True))
        package_ids.append(self.custom_checkpackage.id)
        checktool_ids = list(PackageMap.objects.filter(
            checkpackage_id__in=package_ids).values_list('checktool', flat=True).distinct())
        return CheckTool.objects.filter(id__in=checktool_ids)

    def get_checkpackage_envs(self):
        """获取规则集全部规则包的环境变量配置
        """
        envs_list = CheckPackage.filter_usable(self.checkpackages.all()).filter(
            envs__isnull=False).values_list("envs", flat=True)
        return ' \n'.join(envs_list)

    def get_checkrules(self):
        """ 获取规则集去重后的所有规则列表，会以自定义规则包覆盖官方包
            会一次性取出所有规则，所以不建议前端接口使用
            返回的是一个List对象
        """
        package_ids = list(CheckPackage.filter_usable(self.checkpackages.all()).values_list("id", flat=True))
        custom_pms = PackageMap.objects.filter(checkpackage=self.custom_checkpackage).select_related(
            'checkrule', 'checktool')
        custom_rule_ids = list(custom_pms.values_list("checkrule", flat=True).distinct())
        official_pms = PackageMap.objects.filter(checkpackage_id__in=package_ids).exclude(
            checkrule_id__in=custom_rule_ids).select_related('checkrule', 'checktool').order_by('checkrule_id')
        return (official_pms | custom_pms).distinct()

    def get_admins(self):
        """获取规则集admins，开源版规则集无单独权限
        """
        return []

    def get_custom_checkpackage_content(self):
        """自定义规则包内容
        """
        package_maps = PackageMap.objects.filter(checkpackage=self.custom_checkpackage)
        content = []
        for item in package_maps:
            content.append({
                "checkrule_id": item.checkrule_id,
                "checktool_id": item.checktool_id,
                "severity": item.severity,
                "rule_params": item.rule_params or item.checkrule.rule_params,
                "state": item.state
            })
        return content

    def _get_group(self, perm):
        permission_choices = dict(self.PERMISSION_CHOICES)
        group_name = '_'.join(
            ('checkprofile', str(self.id), permission_choices[perm]))
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            if perm == self.PermissionEnum.ADMIN:
                assign_perm(self.PermissionNameEnum.CHANGE_PROFILE_PERM, group, self)
            assign_perm(self.PermissionNameEnum.VIEW_PROFILE_PERM, group, self)
        return group

    def get_members(self, perm):
        group = self._get_group(perm)
        users = group.user_set.all()
        return users

    def assign_perm(self, username, perm):
        group = self._get_group(perm)
        user, _ = User.objects.get_or_create(username=username)
        try:
            user.groups.add(group)
        except IntegrityError:
            pass

    def remove_perm(self, username, perm):
        group = self._get_group(perm)
        user, _ = User.objects.get_or_create(username=username)
        try:
            user.groups.remove(group)
        except IntegrityError:
            pass

    def __str__(self):
        return self.name
