# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - base serializers
"""
# python 原生import

import logging
from uuid import uuid4

# 第三方 import
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

# 项目内 import
from apps.authen import models
from util.cdcrypto import encrypt
from util.scm import SCM_PLATFORM_CHOICES, SCM_PLATFORM_NUM_AS_KEY, ScmPlatformEnum

logger = logging.getLogger(__name__)


class CodeDogSimpleUserSerializer(serializers.ModelSerializer):
    """CodeDog用户简单序列化，避免暴露关键信息
    """
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = models.CodeDogUser
        exclude = ["user", "tel_number", "email", "chinese_name", "level"]
        read_only_fields = ["username", "status"]


class CodeDogUserSerializer(serializers.ModelSerializer):
    """CodeDog用户序列化，仅适用于登录用户
    """
    username = serializers.CharField(source="user.username", read_only=True)
    is_superuser = serializers.BooleanField(source="user.is_superuser", read_only=True)

    class Meta:
        model = models.CodeDogUser
        exclude = ["user"]
        read_only_fields = ["username", "status", "level"]


class CodeDogFullUserSerializer(serializers.ModelSerializer):
    """CodeDog用户序列化，仅适用于管理员操作
    """
    username = serializers.CharField(source="user.username", read_only=True)
    is_superuser = serializers.BooleanField(source="user.is_superuser", read_only=True)

    class Meta:
        model = models.CodeDogUser
        exclude = ["user"]
        read_only_fields = ["username"]


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单序列化
    """

    class LoginUserTypeEnum:
        CODEDOG_USER = 'codedog_user'

    codedog_serializer = CodeDogSimpleUserSerializer
    codedog_user = CodeDogSimpleUserSerializer(required=False)

    class Meta:
        model = User
        fields = ["codedog_user"]

    def to_representation(self, instance):
        # 根据配置展示不同的user序列化内容
        if hasattr(settings, "LOGIN_USER_TYPE") and settings.LOGIN_USER_TYPE == self.LoginUserTypeEnum.CODEDOG_USER:
            try:
                data = self.codedog_serializer(instance=instance.codedoguser).data
                # 非超管访问此序列化，排除is_superuser字段
                request = self.context.get("request")
                if not (request and request.user and request.user.is_staff):
                    data.pop('is_superuser', '')
                return data
            except models.CodeDogUser.DoesNotExist:
                pass
        return instance.username

    def codedog_user_save(self, instance, validated_data):
        try:
            codedoguser = instance.codedoguser
            serializer = self.codedog_serializer(instance=codedoguser, data=validated_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except models.CodeDogUser.DoesNotExist:
            pass

    def update(self, instance, validated_data):
        if hasattr(settings, "LOGIN_USER_TYPE") and settings.LOGIN_USER_TYPE == self.LoginUserTypeEnum.CODEDOG_USER:
            codedog_user = validated_data.pop("codedog_user", None)
            if codedog_user:
                self.codedog_user_save(instance, codedog_user)
        return super().update(instance, validated_data)


class UserSerializer(UserSimpleSerializer):
    """用户序列化，专用于登录用户序列化，提供更新
    """
    codedog_serializer = CodeDogUserSerializer
    codedog_user = CodeDogUserSerializer(required=False)


class UserFullSerializer(UserSimpleSerializer):
    """用户序列化，提供给superuser操作
    """
    codedog_serializer = CodeDogFullUserSerializer
    codedog_user = CodeDogFullUserSerializer(required=False)
    password = serializers.CharField(max_length=64, write_only=True, help_text="账号密码", required=False)

    class Meta:
        model = User
        fields = ["codedog_user", "password", "is_superuser"]


class UserCreateSerializer(serializers.Serializer):
    is_superuser = serializers.BooleanField(help_text="是否为超管", default=False)
    codedog_users = CodeDogFullUserSerializer(many=True)


class CodedogUserInfoSerializer(serializers.ModelSerializer):
    """Codedog用户序列化
    """
    uid = serializers.CharField(source="username", read_only=True)
    nickname = serializers.CharField(source="codedoguser.nickname", read_only=True)
    chinese_name = serializers.CharField(source="codedoguser.chinese_name", read_only=True)
    email = serializers.EmailField(source="codedoguser.email", read_only=True)
    status = serializers.IntegerField(source="codedoguser.status", read_only=True)
    level = serializers.IntegerField(source="codedoguser.level", read_only=True)
    avatar = serializers.URLField(source="codedoguser.avatar", read_only=True)
    tel_number = serializers.CharField(source="codedoguser.tel_number", read_only=True)
    expired_time = serializers.DateTimeField(source="codedoguser.expired_time", read_only=True)

    class Meta:
        model = User
        fields = ["uid", "is_superuser", "nickname", "chinese_name",
                  "email", "status", "level", "avatar", "tel_number", "expired_time"]
        read_only_fields = ["is_superuser"]


class ScmAccountSerializer(serializers.ModelSerializer):
    """代码库账号授权序列化 - 展示代码库账号简要信息
    """

    user = UserSimpleSerializer(read_only=True)
    auth_origin = serializers.StringRelatedField()
    scm_password = serializers.CharField(max_length=64, write_only=True, help_text="账号密码")
    display_scm_platform = serializers.CharField(source="get_scm_platform_display", read_only=True)

    class Meta:
        model = models.ScmAccount
        fields = "__all__"

    def validate_scm_password(self, value):
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def create(self, validated_data):
        """创建代码库账号
        """
        request = self.context.get("request")
        current_user = request.user if request else None

        # 判断Codedog上是否创建了同名账号
        if models.ScmAccount.objects.filter(
                user=current_user,
                scm_username=validated_data.get("scm_username"),
                auth_origin_id=settings.DEFAULT_ORIGIN_ID,
                scm_platform=validated_data.get("scm_platform")):
            raise serializers.ValidationError({"scm_username": ["该账号已存在"]})
        scm_account = models.ScmAccount.objects.create(
            user=current_user,
            scm_username=validated_data.get("scm_username"),
            scm_password=validated_data.get("scm_password"),
            auth_origin_id=settings.DEFAULT_ORIGIN_ID,
            scm_platform=validated_data.get("scm_platform")
        )
        # 用于补充平台信息，如针对其他平台增加说明，便于日后增加平台
        if validated_data.get("scm_platform_desc"):
            scm_account.scm_platform_desc = validated_data.get("scm_platform_desc")
            scm_account.save()
        return scm_account

    def update(self, instance, validated_data):
        """更新代码库密码
        """
        instance.scm_password = validated_data.get("scm_password", instance.scm_password)
        instance.save()
        return instance


class ScmSshInfoSerializer(serializers.ModelSerializer):
    """代码库SSH授权序列化 - 展示代码库SSH简要信息
    """
    user = UserSimpleSerializer(read_only=True)
    auth_origin = serializers.StringRelatedField()
    indentity = serializers.ReadOnlyField()
    git_token = serializers.CharField(max_length=128, write_only=True, help_text="代码库私钥",
                                      required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(max_length=64, write_only=True, help_text="代码库SSH密钥口令",
                                     allow_null=True, allow_blank=True)
    ssh_private_key = serializers.CharField(write_only=True, help_text="代码库SSH密钥")
    display_scm_platform = serializers.CharField(source="get_scm_platform_display", read_only=True)

    class Meta:
        model = models.ScmSshInfo
        fields = "__all__"

    def validate_git_token(self, value):
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def validate_password(self, value):
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def validate_ssh_private_key(self, value):
        if value:
            value = encrypt(value, settings.PASSWORD_KEY)
        return value

    def create(self, validated_data):
        """创建代码库SSH授权
        """
        request = self.context.get("request")
        current_user = request.user if request else None

        indentity = str(uuid4())

        instance = models.ScmSshInfo.objects.create(
            user=current_user,
            indentity=indentity,
            name=validated_data.get("name"),
            git_token=validated_data.get("git_token"),
            ssh_private_key=validated_data.get("ssh_private_key"),
            password=validated_data.get("password"),
            auth_origin_id=settings.DEFAULT_ORIGIN_ID,
            scm_platform=validated_data.get("scm_platform")
        )
        # 用于补充平台信息，如针对其他平台增加说明，便于日后增加平台
        if validated_data.get("scm_platform_desc"):
            instance.scm_platform_desc = validated_data.get("scm_platform_desc")
            instance.save()
        return instance


class ScmAuthInfoSerializer(serializers.ModelSerializer):
    """代码库OAuth授权序列化 - 展示代码库授权简要信息
    """
    user = UserSimpleSerializer(read_only=True)
    auth_origin = serializers.StringRelatedField()
    scm_platform_name = serializers.SerializerMethodField()

    def get_scm_platform_name(self, instance):
        return SCM_PLATFORM_NUM_AS_KEY.get(instance.scm_platform)

    class Meta:
        model = models.ScmAuthInfo
        exclude = ["gitoa_access_token", "gitoa_refresh_token"]


class ScmSshInfoUpdateSerializer(ScmSshInfoSerializer):
    """代码库SSH授权更新序列化 - 展示代码库SSH简要信息
    """
    git_token = serializers.CharField(max_length=128, write_only=True, help_text="代码库私钥",
                                      required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(max_length=64, write_only=True, help_text="代码库SSH密钥口令",
                                     required=False, allow_null=True, allow_blank=True)
    ssh_private_key = serializers.CharField(write_only=True, help_text="代码库SSH密钥", required=False)


class ScmAuthSerializer(serializers.ModelSerializer):
    """代码授权序列化 - 展示代码授权信息详情
    """
    scm_account = ScmAccountSerializer(read_only=True)
    scm_oauth = ScmAuthInfoSerializer(read_only=True)
    scm_ssh = ScmSshInfoSerializer(read_only=True)

    class Meta:
        model = models.ScmAuth
        fields = "__all__"


class ScmAuthCreateSerializer(serializers.ModelSerializer):
    """代码授权序列化 - 展示代码授权信息详情
    """
    scm_account = serializers.PrimaryKeyRelatedField(queryset=models.ScmAccount.objects.all(), help_text="账号密码",
                                                     required=False, allow_null=True, allow_empty=True)
    scm_ssh = serializers.PrimaryKeyRelatedField(queryset=models.ScmSshInfo.objects.all(), help_text="账号密码",
                                                 required=False, allow_null=True, allow_empty=True)
    scm_oauth = serializers.PrimaryKeyRelatedField(queryset=models.ScmAuthInfo.objects.all(), help_text="oauth授权",
                                                   required=False, allow_null=True, allow_empty=True)
    scm_platform = serializers.ChoiceField(choices=SCM_PLATFORM_CHOICES, help_text="代码库管理平台",
                                           required=False, allow_null=True,
                                           default=ScmPlatformEnum.GIT_OA, write_only=True)

    class Meta:
        model = models.ScmAuth
        fields = "__all__"
        read_only_fields = ["auth_key"]
