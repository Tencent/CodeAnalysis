# -*- coding: utf-8 -*-
"""
Coding
"""
# python 原生import
import logging

# 第三方 import
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

# 项目内 import
from apps.authen import models
from apps.authen.serializers import base as base_serializer
from apps.base.apimixins import CustomSerilizerMixin
from util.webclients import LoginProxyClient

logger = logging.getLogger(__name__)


class ScmAccountListApiView(generics.ListCreateAPIView):
    """用户账号列表
    ### get
    获取用户账号列表

    ### post
    创建用户账号
    """
    serializer_class = base_serializer.ScmAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmAccount.objects.filter(user=user).order_by("-id")


class ScmAccountDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """用户账号列表
    ### get
    获取用户指定的账号

    ### put
    更新用户指定的账号

    ### delete
    删除用户指定的账号
    """
    serializer_class = base_serializer.ScmAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmAccount.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        return get_object_or_404(models.ScmAccount, user=user, id=self.kwargs["account_id"])


class ScmSSHInfoListApiView(generics.ListCreateAPIView):
    """用户SSH授权列表
    ### get
    获取用户SSH授权列表

    ### post
    创建用户SSH授权列表
    """
    serializer_class = base_serializer.ScmSshInfoSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmSshInfo.objects.filter(user=user).order_by("-id")


class ScmSSHInfoDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """用户SSH授权详情

    ### get
    获取用户SSH授权详情

    ### put
    更新用户指定的SSH授权

    ### delete
    创建用户SSH授权列表
    """

    serializer_class = base_serializer.ScmSshInfoUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmSshInfo.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        return get_object_or_404(models.ScmSshInfo, user=user, id=self.kwargs["sshinfo_id"])


class UserListApiView(CustomSerilizerMixin, generics.ListCreateAPIView):
    """main服务平台全员信息接口

    ### get
    应用场景：获取main服务全员信息

    ### post
    应用场景：创建用户，会先到login服务中创建，并返回随机密码
    """

    permission_classes = [IsAdminUser]
    serializer_class = base_serializer.UserFullSerializer
    post_serializer_class = base_serializer.UserCreateSerializer
    queryset = models.User.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        validated_data = slz.validated_data
        is_superuser = validated_data.get("is_superuser", False)
        codedog_users = validated_data.get("codedog_users", [])

        # 登录服务需要创建的用户
        users = []
        codedoguser_dict = {}
        for codedog_user in codedog_users:
            nickname = codedog_user.get("nickname")
            users.append(nickname)
            codedoguser_dict[nickname] = codedog_user

        result = None
        try:
            data = {"users": users}
            logger.info("回调数据: %s" % data)
            result = LoginProxyClient().api("create_user_task", data=data)
        except Exception as err:
            logger.error("Login Proxy Client create user task failed: %s" % (err))
            pass
        res = [] # 返回结果
        # Login 服务创建的账户返回结果
        if result:
            login_users = result.get("data").get("results")
            for login_user in login_users:
                username = login_user.get("username")
                nickname = login_user.get("nickname")
                password = login_user.get("password")
                # 根据登录服务的uid创建用户
                user, _ = models.User.objects.get_or_create(username=username, defaults={
                  "is_superuser": is_superuser,
                  "is_staff": is_superuser
                })
                models.CodeDogUser.objects.filter(user=user).update(**codedoguser_dict[nickname])
            res = login_users
        else:
            for codedog_user in codedog_users:
                nickname = codedog_user.get("nickname")
                user, _ = models.User.objects.get_or_create(username=nickname, defaults={
                  "is_superuser": is_superuser,
                  "is_staff": is_superuser
                })
                models.CodeDogUser.objects.filter(user=user).update(**codedog_user)
                res.append({"username": user.username, "nickname": nickname})
        return Response(res)


class UserDetailApiView(generics.RetrieveUpdateAPIView):
    """用户信息更新

    ### get
    应用场景：获取用户信息详情

    ### put
    应用场景：更新用户信息
    """
    permission_classes = [IsAdminUser]
    serializer_class = base_serializer.UserFullSerializer

    def get_object(self):
        username = self.kwargs["username"]
        return get_object_or_404(models.User, username=username)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        slz = self.get_serializer(instance=instance, data=request.data)
        slz.is_valid(raise_exception=True)
        password = slz.validated_data.pop("password", None)
        instance = slz.save()
        # 同步更新is_superuser和is_staff
        if instance.is_superuser != instance.is_staff:
            instance.is_staff = instance.is_superuser
            instance.save()
        # 登录服务更新用户
        nickname = instance.codedoguser.nickname
        result = None
        try:
            data = {"nickname": nickname, "password": password}
            logger.info("回调数据: %s" % data)
            result = LoginProxyClient().api("update_user_task", path_params=(instance.username), data=data)
            if result:
                return Response(result.get("data"))
        except Exception as err:
            logger.error("Login Proxy Client update user task failed: %s" % (err))
            pass
        return Response({"username": instance.username, "nickname": nickname})
