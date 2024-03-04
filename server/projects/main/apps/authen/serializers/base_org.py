# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - base serializer for org
Serializers 定义：此处定义了供apis.py接口使用的Serializers
"""
# python 原生import
import logging

# 第三方 import
from rest_framework import serializers

# 项目内 import
from apps.authen import models
from apps.authen.core import OrganizationManager
from apps.authen.serializers.base import UserSimpleSerializer
from apps.base.serializers import CDBaseModelSerializer
from apps.codeproj.models import ProjectTeam, Repository
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class OrganizationSimpleSerializer(CDBaseModelSerializer):
    """团队简单序列化
    """

    def validated_status(self, value):
        """校验状态
        """
        if value and value not in [models.Organization.StatusEnum.ACTIVE, models.Organization.StatusEnum.DISACTIVE]:
            raise serializers.ValidationError("状态字段只能是1（活跃）与99（禁止）")
        return value

    def update(self, instance, validated_data):
        status = validated_data.get("status")
        if status == instance.status or status is None:
            return instance
        user = self.context["request"].user
        instance.status = validated_data["status"]
        instance.save()
        OperationRecordHandler.add_organization_operation_record(
            instance, "团队状态调整", user,
            "状态调整为: %s-%s" % (status, models.Organization.STATUSENUM_DICT[status]))
        return instance

    class Meta:
        model = models.Organization
        fields = ["org_sid", "name", "certificated", "status", "level"]
        read_only_fields = ["org_sid", "name", "certificated", "level"]


class OrganizationSerializer(CDBaseModelSerializer):
    """团队序列化
    """
    admins = serializers.SerializerMethodField(help_text="团队管理员")
    repo_count = serializers.SerializerMethodField(help_text="团队分析任务数量")
    team_count = serializers.SerializerMethodField(help_text="团队项目数量")
    user_count = serializers.SerializerMethodField(help_text="团队成员数量")
    owner = serializers.CharField(help_text="团队负责人")
    tel_number = serializers.CharField(help_text="团队联系方式")

    def get_admins(self, instance):
        admins = instance.get_members(models.Organization.PermissionEnum.ADMIN)
        return [UserSimpleSerializer(instance=user).data for user in admins]

    def get_repo_count(self, instance):
        # 未删除的分析任务数量
        return Repository.objects.filter(
            project_team__organization=instance, project_team__status=ProjectTeam.StatusEnum.ACTIVE).count()

    def get_team_count(self, instance):
        return ProjectTeam.active_pts.filter(organization=instance).count()

    def get_user_count(self, instance):
        admins = instance.get_members(models.Organization.PermissionEnum.ADMIN)
        users = instance.get_members(models.Organization.PermissionEnum.USER)
        return (admins | users).distinct().count()

    def create(self, validated_data):
        user = self.context["request"].user
        name = validated_data.pop("name")
        return OrganizationManager.create_org(name, user, **validated_data)

    class Meta:
        model = models.Organization
        exclude = ["db_key"]
        read_only_fields = ["org_sid", "certificated", "status", "level", "admins"]


class OrganizationStatusSerializer(serializers.Serializer):
    """团队状态序列化，用于团队状态审核
    """
    status = serializers.ChoiceField(choices=models.Organization.STATUSENUM_CHOICES, help_text="团队状态")
