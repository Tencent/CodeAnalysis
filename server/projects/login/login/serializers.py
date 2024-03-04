# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
login - serializers
"""
# 原生
import logging

# 第三方
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer, RefreshToken

# 项目内
from login.models import UserInfo, UserAuth

logger = logging.getLogger(__name__)


class UserInfoSerializer(serializers.ModelSerializer):
    uid = serializers.PrimaryKeyRelatedField(read_only=True)
    create_time = serializers.DateTimeField(read_only=True)
    avatar_url = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    province = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    mail = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserInfo
        exclude = ("password", "last_login", "is_active")

    def create(self, validated_data):
        app = UserInfo.objects.create(**validated_data)
        return app

    def update(self, instance, validated_data):
        instance.update_time = validated_data.get(
            "update_time", timezone.now())
        instance.save()
        return super().update(instance, validated_data)


class UserTokenObtainPairSerializer(TokenObtainSerializer):
    """
    支持密码字段可不传
    """
    username_field = "uid"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(min_length=1)
        self.fields["password"] = serializers.CharField(required=False)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = {}
        user = UserAuth.objects.get(uid=attrs["uid"]).user
        logger.debug("用户编号: %s" % user.uid)
        refresh = self.get_token(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
