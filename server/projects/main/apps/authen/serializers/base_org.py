# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
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
from apps.authen.serializers.base import UserSimpleSerializer
from apps.authen.core import OrganizationManager, OrganizationPermApplyManager
from apps.base.serializers import CDBaseModelSerializer
from apps.codeproj.models import ProjectTeam, Repository

logger = logging.getLogger(__name__)


class OrganizationSimpleSerializer(CDBaseModelSerializer):
    """团队简单序列化
    """

    class Meta:
        model = models.Organization
        fields = ["org_sid", "name", "certificated", "status", "level"]


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
        return Repository.objects.filter(project_team__organization=instance).count()

    def get_team_count(self, instance):
        return ProjectTeam.objects.filter(organization=instance).count()

    def get_user_count(self, instance):
        admins = instance.get_members(models.Organization.PermissionEnum.ADMIN)
        users = instance.get_members(models.Organization.PermissionEnum.USER)
        return (admins | users).distinct().count()

    def create(self, validated_data):
        user = self.context["request"].user
        name = validated_data.pop("name")
        apply_msg = validated_data.pop("apply_msg", None)
        return OrganizationManager.create_org(name, user, apply_msg=apply_msg, **validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        apply_msg = validated_data.pop("apply_msg", None)
        OrganizationPermApplyManager.update_org_apply(instance, user, apply_msg)
        return super().update(instance, validated_data)

    class Meta:
        model = models.Organization
        exclude = ["db_key"]
        read_only_fields = ["org_sid", "certificated", "status", "level", "admins"]

