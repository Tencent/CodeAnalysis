# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
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
from apps.base.serializers import CDBaseModelSerializer, OnlySuperAdminReadField, ChoicesField

logger = logging.getLogger(__name__)


class CheckRuleDescSerializer(serializers.ModelSerializer):
    """规则描述序列化
    """

    class Meta:
        model = models.CheckRuleDesc
        fields = ["desc_type", "desc"]


class CheckToolSimpleSerializer(serializers.ModelSerializer):
    """工具简单序列化
    """
    display_name = serializers.SerializerMethodField()
    scope = serializers.SerializerMethodField()
    name = OnlySuperAdminReadField()

    def get_display_name(self, checktool):
        """获取工具展示名称
        """
        request = self.context.get("request")
        user = request.user if request else None
        return checktool.get_show_name(user=user)

    def get_scope(self, checktool):
        """公有True/私有False工具
        """
        if checktool.is_public():
            return models.CheckTool.ScopeEnum.PUBLIC
        return models.CheckTool.ScopeEnum.PRIVATE

    class Meta:
        model = models.CheckTool
        fields = ["id", "name", "display_name", "scope", "status", "show_display_name", "build_flag"]


class CheckRuleSerializer(CDBaseModelSerializer):
    """规则序列化
    """

    class SelectStateTypeEnum:
        UNSELECT = 0  # 未选中
        CUSTOMSELECT = 1  # 自定义包规则已选中
        OFFICIALSELECT = 2  # 官方包规则已选中

    checkruledesc = CheckRuleDescSerializer(help_text="规则描述")
    labels = serializers.SlugRelatedField(help_text="关联标签", slug_field="name", many=True,
                                          queryset=models.Label.objects.all(), required=False)
    languages = serializers.SlugRelatedField(help_text="适用语言", slug_field="name", many=True,
                                             queryset=models.Language.objects.all())
    category_name = serializers.CharField(source="get_category_display", read_only=True)
    severity_name = serializers.CharField(source="get_severity_display", read_only=True)
    checktool = CheckToolSimpleSerializer(read_only=True)
    select_state = serializers.SerializerMethodField()

    def get_select_state(self, checkrule):
        """规则选中状态，用于规则包或规则集中获取所有规则时，标记该条规则是否被官方规则包或规则集的自定义规则包标记
        """
        view = self.context.get("view")
        checkprofile_id = view.kwargs.get("checkprofile_id", None)
        checkpackage_id = view.kwargs.get("checkpackage_id", None)
        packages_ids = []
        if checkprofile_id and checkpackage_id is None:
            # 规则配置-自定义规则时添加规则操作，查看所有规则
            checkprofile = models.CheckProfile.objects.filter(id=checkprofile_id).first()
            if checkprofile:
                if models.PackageMap.objects.filter(checkpackage=checkprofile.custom_checkpackage,
                                                    checkrule=checkrule).exists():
                    # 自定义规则包含该规则，返回1
                    return self.SelectStateTypeEnum.CUSTOMSELECT
                else:
                    # 获取规则配置的官方规则包，用于判断官方包中是否有匹配的规则，有则返回2，否则0
                    packages_ids = checkprofile.checkpackages.all().values_list('id', flat=True)
        elif checkprofile_id is None and checkpackage_id:  # 官方规则包的添加规则操作，查看所有规则
            packages_ids.append(checkpackage_id)
        else:  # 查看所有规则
            return self.SelectStateTypeEnum.UNSELECT
        # 匹配官方规则包中规则是否已被选中
        if models.PackageMap.objects.filter(checkpackage_id__in=packages_ids, checkrule=checkrule).exists():
            return self.SelectStateTypeEnum.OFFICIALSELECT
        return self.SelectStateTypeEnum.UNSELECT

    class Meta:
        model = models.CheckRule
        fields = "__all__"
