# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
login - v3 apis
"""
# 原生
import logging
import os

# 第三方
from django.conf import settings
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import filters, generics
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

# 项目内
from login import serializers
from login.lib import cdcrypto as crypto
from login.models import UserInfo, UserAuth
from login.core import UserManager

logger = logging.getLogger(__name__)


class UserListAPIView(generics.ListCreateAPIView):
    """用户列表接口
    """
    serializer_class = serializers.UserInfoSerializer
    authentication_classes = (JWTTokenUserAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = UserInfo.objects.all()

    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "register_userinfo"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("nickname",)
    SAFE_METHODS = ("get",)

    # 重写权限，post无须
    def get_permissions(self):
        if self.request.method == "POST":
            return []
        else:
            return [IsAuthenticated()]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data

            if request.oauth:
                auth = request.oauth
                if auth.user:
                    self.serializer_class = serializers.UserTokenObtainPairSerializer
                    serializer = self.get_serializer(data={
                        "uid": auth.uid
                    })
                    serializer.is_valid(raise_exception=True)
                    data["access_token"] = serializer.validated_data["access"]
                    data["isRegister"] = True
                    return Response(data)
                # 用户表
                user = UserInfo()

                params = cache.get(auth.uid)
                if not params:
                    logging.exception("第三方信息缓存获取失败")
                    raise Exception("注册失败，请重试")
                logging.info("%s 获取缓存" % params)
                user.nickname = params.get("nickname", "") or params.get("userid", "")
                user.avatar_url = params.get("avatar_url", "")
                user.gender_type = params.get("gender", 2)
                user.city = params.get("city", "")
                user.province = params.get("province", "")
                user.country = params.get("country", "")
                user.phone = params.get("phone", "")
                user.mail = params.get("mail", "")
                user.save()
                auth.user = user
                auth.save()

                self.serializer_class = serializers.UserTokenObtainPairSerializer
                serializer = self.get_serializer(data={"uid": auth.uid})
                serializer.is_valid(raise_exception=True)
                data["access_token"] = serializer.validated_data["access"]
                data["isRegister"] = True
            else:
                raise Exception("注册失败，Oauth鉴权信息过期或者没有")
        except Exception as e:
            logging.exception(e)
            return Response({"exception_message": e.args[0]}, status=status.HTTP_200_OK)

        return Response(data)


class UserDetailAPIView(generics.GenericAPIView):
    """用户详情接口
    """
    authentication_classes = (JWTTokenUserAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserInfoSerializer
    lookup_field = "uid"
    queryset = UserInfo.objects.all()

    def get_permissions(self):
        accept = self.request.META["HTTP_ACCEPT"]
        if "image" in accept and self.request.method == "GET":
            return []
        else:
            return [IsAuthenticated()]

    def get_object(self):
        obj = get_object_or_404(UserInfo, uid=self.kwargs.get("uid"))
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        """
        如果是image，重定向图片
        如果不是图片，只能查到自己
        """
        accept = request.META["HTTP_ACCEPT"]
        if "image" in accept:
            queryset = self.get_queryset()
            if queryset and queryset[0].avatar_url:
                return redirect(queryset[0].avatar_url.replace("http:", "https:"))
            else:
                imagepath = os.path.join(settings.BASE_DIR, "static/img/user.gif")
                with open(imagepath, "rb") as f:
                    image_data = f.read()
                return HttpResponse(image_data, content_type="image/gif")
        else:
            return Response({"exception_message": "不支持"})


class AccountInfoAPIView(generics.GenericAPIView):
    """账号信息接口
    """
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "associate_userinfo"
    authentication_classes = (JWTTokenUserAuthentication,)
    permission_classes = (IsAuthenticated,)

    # 重写权限，get请求跳过
    def get_permissions(self):
        if self.request.method == "GET":
            return []
        else:
            return [IsAuthenticated()]

    def post(self, request, *args, **kwargs):
        """
        关联账号
        """
        try:
            uid = request.user.id
            if request.oauth:
                instance = request.oauth
                if instance.user_id:
                    logging.exception("账号已关联")
                    raise Exception("关联失败,账号已关联")
                instance.user_id = uid
                instance.save()
            else:
                logging.exception("没有需要关联的信息，没有oauth请求头")
                raise Exception("关联失败")

            return Response({"msg": "关联成功"})
        except Exception as e:
            logging.exception(e)
            return Response({"exception_message": e.args[0]})

    def delete(self, request, *args, **kwargs):
        """
        解绑账号
        """
        uid = request.user.id
        instance = UserAuth.objects.filter(user=uid)
        instance.delete()
        return Response({"msg": "解绑成功"})


class OAInfoAPIView(TokenObtainPairView):
    """账号密码登录接口
    """
    serializer_class = serializers.UserTokenObtainPairSerializer
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "get_userinfo"

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            identifier = data.get("username", "")
            credential = data.get("password", "")
            params = {}
            logger.debug("Current Login User: %s" % identifier)

            auth = authenticate(username=identifier, password=credential)

            # 判断账号是否存在，如果不存在就创建
            if not (auth and UserManager.get_or_create_account(identifier)):
                auth = False

            if not auth:
                auth = UserAuth.objects.filter(identifier=identifier,
                                        identity_type="oapassword",
                                        credential=crypto.encrypt(credential, settings.PASSWORD_KEY)).first()

            if auth:
                auth = UserAuth.objects.filter(user=identifier).first()
                serializer = self.get_serializer(data={"uid": auth.uid})
                serializer.is_valid(raise_exception=True)
                params["access_token"] = serializer.validated_data["access"]
                params["isRegister"] = True
            else:
                raise NotAuthenticated("账号或密码不正确")
        except Exception as e:
            logger.exception("OAInfo登录失败: %s" % e)
            raise ParseError("登录失败，账户或密码错误或账户未注册")
        return Response(params)


class TokenUserDetailAPIView(generics.RetrieveUpdateAPIView):
    """根据token获取当前用户信息
    """
    authentication_classes = (JWTTokenUserAuthentication,)
    serializer_class = serializers.UserInfoSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        uid = self.request.user.id
        obj = get_object_or_404(UserInfo, uid=uid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            params = request.data
            user.nickname = params.get("nickname") or params.get("userid")
            user.avatar_url = params.get("avatar_url", "")
            user.gender_type = params.get("gender", 2)
            user.city = params.get("city", "")
            user.province = params.get("province", "")
            user.country = params.get("country", "")
            user.phone = params.get("phone", "")
            user.mail = params.get("mail", "")
            user.save()
            return Response(model_to_dict(user))
        except Exception as e:
            logging.exception(e)
            return Response({"exception_message": e.args[0]})
