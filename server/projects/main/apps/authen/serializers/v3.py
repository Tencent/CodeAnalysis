# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Serializers 定义：此处定义了供apis/v3.py接口使用的Serializers
"""
# python 原生import
import logging

# 第三方 import
from django.conf import settings
from rest_framework import serializers

# 项目内 import
from apps.authen import models
from util.cdcrypto import encrypt, decrypt
from util.scm import SCM_PLATFORM_CHOICES, SCM_PLATFORM_NUM_AS_KEY

logger = logging.getLogger(__name__)


class ScmOauthSettingsSerializer(serializers.ModelSerializer):
    """Oauth认证序列化类
    """

    client_id = serializers.CharField(max_length=128, help_text="客户端ID")
    client_secret = serializers.CharField(max_length=128, help_text="客户端密码")
    redirect_uri = serializers.CharField(max_length=64, help_text="回调地址")
    scm_platform = serializers.ChoiceField(choices=SCM_PLATFORM_CHOICES, help_text="代码库管理平台",
                                           required=True, allow_null=False)
    scm_platform_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ScmOauthSetting
        fields = "__all__"

    def to_representation(self, instance):
        """展示解密后的数据
        """
        response = super().to_representation(instance)
        if instance.client_id:
            response.update({"client_id": decrypt(instance.client_id, settings.PASSWORD_KEY)})
        if instance.client_secret:
            response.update({"client_secret": decrypt(instance.client_secret, settings.PASSWORD_KEY)})
        return response

    def get_scm_platform_name(self, oauth_setting):
        """获得scm平台类型名称
        """
        return SCM_PLATFORM_NUM_AS_KEY.get(oauth_setting.scm_platform)

    def validate_client_id(self, value):
        """对client_id加密
        """
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def validate_client_secret(self, value):
        """对client_secret加密
        """
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def create(self, validated_data):
        """创建各scm平台oauth授权配置信息
        """
        if models.ScmOauthSetting.objects.filter(
            scm_platform=validated_data.get("scm_platform"),
        ):
            raise serializers.ValidationError({"scm_platform": ["该平台已创建对应配置"]})
        oauth_setting = models.ScmOauthSetting.objects.create(
            scm_platform=validated_data.get("scm_platform"),
            client_id=validated_data.get("client_id"),
            client_secret=validated_data.get("client_secret"),
            redirect_uri=validated_data.get("redirect_uri"),
            scm_platform_desc=validated_data.get("scm_platform_desc")
        )
        return oauth_setting

