# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - checkrule serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models
from apps.scan_conf.core import CheckToolManager, CheckPackageManager
from apps.base.serializers import ChoicesField

logger = logging.getLogger(__name__)


class CheckerRuleSerializer(serializers.ModelSerializer):
    """工具规则load序列化，用于loadcheckers时使用
    """
    labels = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Label.objects.all())
    languages = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Language.objects.all())
    severity = ChoicesField(choices=models.CheckRule.SEVERITY_ENG_CHOICES)
    category = ChoicesField(choices=models.CheckRule.CATEGORY_ENG_CHOICES)
    description = serializers.CharField(source="checkruledesc.desc", allow_blank=True, allow_null=True)
    custom = serializers.BooleanField(default=True)
    disable = serializers.BooleanField(default=False)

    class Meta:
        model = models.CheckRule
        fields = [
            "real_name", "display_name", "severity", "category", "rule_title",
            "rule_params", "custom", "languages", "solution", "owner",
            "labels", "description", "disable"
        ]


class CheckerToolLibMapSerializer(serializers.ModelSerializer):
    """工具依赖映射load序列化，用于loadcheckers时使用
    """

    name = serializers.CharField(source="toollib.name")
    source = serializers.CharField(source="toollib.lib_key")

    def validate(self, attrs):
        name = attrs["toollib"]["name"]
        lib_key = attrs["toollib"]["lib_key"]
        try:
            attrs["toollib"]  = models.ToolLib.objects.get(name=name, lib_key=lib_key)
            return attrs
        except models.ToolLib.DoesNotExist:
            raise serializers.ValidationError("指定工具依赖[%s - %s]不存在" % (name, lib_key))

    class Meta:
        model = models.ToolLibMap
        fields = ["name", "source"]


class CheckerSchemeSerializer(serializers.ModelSerializer):
    """工具依赖方案load序列化，用于loadcheckers时使用
    """
    tool_libs = CheckerToolLibMapSerializer(many=True, source="toollibmap")

    class Meta:
        model = models.ToolLibScheme
        fields = ["condition", "tool_libs", "scheme_os", "default_flag"]


class CheckerSerializer(serializers.ModelSerializer):
    """工具load序列化，用于loadcheckers时使用
    """
    libscheme_set = CheckerSchemeSerializer(many=True, source="libscheme", required=False)
    checkrule_set = CheckerRuleSerializer(many=True)
    task_processes = serializers.SlugRelatedField(slug_field='name', many=True, queryset=models.Process.objects.all())
    scan_app = serializers.SlugRelatedField(slug_field='name', queryset=models.ScanApp.objects.all())
    open_user = serializers.BooleanField(required=False)
    open_saas = serializers.BooleanField(required=False)

    def check_use_toollib_perm(self, toollib, checktool=None):
        """校验工具是否具有此依赖权限
        """
        if CheckToolManager.check_use_toollib_perm(checktool, toollib):
            return True
        view = self.context.get("view")
        if view.kwargs.get("org_sid") == toollib.lib_key.split("org_")[-1]:
            return True
        return False

    def validate_name(self, name):
        if self.instance:  # 更新操作
            if self.instance.name != name:  # 更新工具不一致
                raise serializers.ValidationError("工具名称name不能改变")
        elif models.CheckTool.objects.filter(name=name).exists():  # 创建操作，校验是否已存在工具
            raise serializers.ValidationError("该工具已存在")
        return name

    def validate_libscheme_set(self, libscheme_set):
        for libscheme in libscheme_set:
            toollibmap_set = libscheme.get("toollibmap")
            for libmap in toollibmap_set:
                toollib = libmap.get("toollib")
                if not self.check_use_toollib_perm(toollib, self.instance):
                    raise serializers.ValidationError("没有依赖%s权限" % toollib.name)
        return libscheme_set

    def validate(self, attrs):
        # 用于排除页面操作open_user，open_saas字段
        user = self.context.get("user", None)
        is_local_script = self.context.get("is_local_script", False)
        if not is_local_script and not (user and user.is_superuser):
            # 页面操作非超管不传递open_user， open_saas字段
            attrs.pop("open_user", False)
            attrs.pop("open_saas", False)
        return attrs

    class Meta:
        model = models.CheckTool
        fields = [
            "name", "display_name", "description", "license", "libscheme_set", "image_url",
            "task_processes", "scan_app", "scm_url", "run_cmd", "envs", "build_flag",
            "checkrule_set", "open_user", "open_saas", "virtual_name", "show_display_name"
        ]


class PackageMapJsonSerializer(serializers.ModelSerializer):
    """规则包-规则映射laod序列化，用于loadpackages时使用
    """
    checktool = serializers.CharField(source="checktool.name")
    checkrule = serializers.CharField(source="checkrule.real_name")
    checkrule_display_name = serializers.CharField(source="checkrule.display_name", read_only=True)
    checktool_display_name = serializers.CharField(source="checktool.display_name", read_only=True)
    checkrule_category = ChoicesField(choices=models.CheckRule.CATEGORY_ENG_CHOICES, source="checkrule.category",
                                      read_only=True)
    severity = ChoicesField(choices=models.CheckRule.SEVERITY_ENG_CHOICES)
    state = ChoicesField(choices=models.PackageMap.STATE_ENG_CHOICES)

    def validate(self, attrs):
        tool_name = attrs["checktool"]["name"]
        rule_name = attrs["checkrule"]["real_name"]
        try:
            attrs["checktool"] = models.CheckTool.objects.get(name=tool_name)
            attrs["checkrule"] = models.CheckRule.objects.get(real_name=rule_name, checktool=attrs["checktool"])
            return attrs
        except (models.CheckRule.DoesNotExist, models.CheckTool.DoesNotExist):
            raise serializers.ValidationError("指定工具规则[%s/ %s]不存在" % (tool_name, rule_name))

    class Meta:
        model = models.PackageMap
        fields = ["checktool", "checkrule", "severity", "rule_params", "state", "checkrule_category",
                  "checkrule_display_name", "checktool_display_name"]


class CheckPackageJsonSerializer(serializers.ModelSerializer):
    """规则包load序列化，用于loadpackages时使用
    """
    labels = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Label.objects.all())
    checkrule_set = PackageMapJsonSerializer(many=True, source="get_package_maps")
    package_type = ChoicesField(choices=models.CheckPackage.PACKAGETYPE_ENG_CHOICES, required=False,
                                default=models.CheckPackage.PackageTypeEnum.OFFICIAL)
    languages = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Language.objects.all())
    open_saas = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(choices=models.CheckPackage.STATUS_CHOICES,
                          default=models.CheckPackage.StatusEnum.RUNNING,
                          write_only=True, required=False)

    def validate_name(self, name):
        if self.instance:  # 更新操作
            if self.instance.name != name:  # 更新规则包名称不一致
                raise serializers.ValidationError("规则包名称name不能改变")
        elif models.CheckPackage.objects.filter(name=name).exists():  # 创建操作
            raise serializers.ValidationError("该规则包已存在")
        return name

    def create(self, validated_data):
        checkrules_data = validated_data.pop('get_package_maps')
        checkpackage = super().create(validated_data)
        CheckPackageManager.save_pms_by_script(checkpackage, checkrules_data)
        return checkpackage

    def update(self, checkpackage, validated_data):
        checkrules_data = validated_data.pop('get_package_maps')
        CheckPackageManager.save_pms_by_script(checkpackage, checkrules_data)
        return super().update(checkpackage, validated_data)

    class Meta:
        model = models.CheckPackage
        fields = ["name", "description", "revision", "package_type", "languages",
                  "labels", "checkrule_set", "open_saas", "envs", "status"]
