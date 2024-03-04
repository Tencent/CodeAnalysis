# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - base serializer
"""
# python 原生import
import logging

# 第三方 import
from rest_framework import serializers

# 项目内 import
from apps.authen.core import UserManager
from apps.base.serializers import CDBaseModelSerializer
from apps.nodemgr import models
from apps.nodemgr.serializers.base import NodeSerializer

logger = logging.getLogger(__name__)


class OrgExecTagSerializer(CDBaseModelSerializer):
    """团队标签序列化
    """
    display_name = serializers.CharField(help_text="标签展示名称", max_length=128)
    tag_type = serializers.IntegerField(
        help_text="标签类型", default=models.ExecTag.TypeEnum.PRIVATE, required=False)
    name = serializers.ReadOnlyField()
    public = serializers.ReadOnlyField()
    org_sid = serializers.ReadOnlyField()
    official = serializers.ReadOnlyField()

    def validate_tag_type(self, tag_type):
        """验证标签类型
        """
        if not tag_type:
            return tag_type
        if tag_type not in [models.ExecTag.TypeEnum.PRIVATE, models.ExecTag.TypeEnum.DISABLED]:
            raise serializers.ValidationError({"tag_type": "tag_type的值只能为2、99"})
        return tag_type

    class Meta:
        model = models.ExecTag
        fields = "__all__"

    def create(self, validated_data):
        """创建标签
        """
        user = self.context.get("request").user
        org_sid = self.context.get("view").kwargs.get("org_sid")
        display_name = validated_data.pop("display_name")
        name = "%s_%s" % (org_sid, display_name)
        tag, _ = models.ExecTag.objects.get_or_create(name=name, defaults={
            "creator": user, "org_sid": org_sid, "display_name": display_name,
            "tag_type": models.ExecTag.TypeEnum.PRIVATE, "public": False,
            "official": False, **validated_data
        })
        return tag

    def update(self, instance, validated_data):
        """更新标签
        """
        user = self.context.get("request").user
        instance.display_name = validated_data.get("display_name", instance.display_name)
        instance.desc = validated_data.get("desc", instance.desc)
        instance.tag_type = validated_data.get("tag_type", instance.tag_type)
        instance.save(user=user)
        return instance


class OrgNodeSerializer(NodeSerializer):
    """团队节点序列化
    """

    org_sid = serializers.ReadOnlyField()

    def validate_exec_tags(self, exec_tags):
        """校验标签
        """
        org_sid = self.context.get("view").kwargs.get("org_sid")
        invalidated_tags = []
        for exec_tag in exec_tags:
            if exec_tag.org_sid != org_sid:
                invalidated_tags.append(exec_tag)
        if len(invalidated_tags) > 0:
            tags = ";".join([tag.name for tag in invalidated_tags])
            raise serializers.ValidationError({"cd_error": "当前团队没有包含%s标签" % tags})
        return exec_tags

    def validate_related_managers(self, related_managers):
        """校验关注人
        """
        org_sid = self.context.get("view").kwargs.get("org_sid")
        org = models.Organization.objects.get(org_sid=org_sid)
        for user in related_managers:
            if not user.has_perm(models.Organization.PermissionNameEnum.VIEW_ORG_PERM, org):
                raise serializers.ValidationError({"cd_error": "当前团队没有包含%s成员" % UserManager.get_username(user)})
        return related_managers
