# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - apis for v3
"""
# python 原生import
import logging

# 第三方 import
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

# 项目内 import
from apps.authen import models
from apps.authen.api_filters import base as base_filters
from apps.authen.core import OrganizationManager
from apps.authen.permissions import CodeDogSuperVipUserLevelPermission, CodeDogUserPermission, \
    OrganizationDefaultPermission, OrganizationDetailUpdatePermission
from apps.authen.serializers import base_org
from apps.authen.serializers.base import ScmAccountSerializer, ScmSshInfoSerializer, ScmSshInfoUpdateSerializer, \
    UserSerializer, UserSimpleSerializer
from apps.codeproj.models import ProjectTeam
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class UserInfoApiView(generics.RetrieveUpdateAPIView):
    """用户信息
    ### get
    应用场景：获取用户信息

    ### put
    应用场景：更新用户信息
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserTokenView(APIView):
    """用户信息API

    ### get

    应用场景：获取当前登录用户Token

    ### post

    应用场景：更新当前用户Token
    """
    permission_classes = [CodeDogSuperVipUserLevelPermission]

    def get(self, request):
        """
        ### 接口: 返回当前登录用户信息
        """
        logger.info("hello, %s" % request.user)
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response(data={"token": token.key}, status=status.HTTP_200_OK)

    def put(self, request):
        """
        ### 接口: 更新当前用户的信息
        """
        token = get_object_or_404(Token, user=request.user)
        token.delete()
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response(data={"token": token.key}, status=status.HTTP_200_OK)


class OrganizationListApiView(generics.ListCreateAPIView):
    """团队列表

    ### get
    应用场景：获取团队列表
    ```bash
    筛选参数：
    name: 团队名称，包含
    scope: 1 为我管理的
    ```

    ### post
    应用场景：创建团队
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = base_org.OrganizationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.OrganizationFilter

    def get_queryset(self):
        try:
            scope = int(self.request.query_params.get("scope"))
        except (ValueError, TypeError):
            scope = None
        if scope == models.Organization.PermissionEnum.ADMIN:
            # 获取我管理的团队
            return OrganizationManager.get_user_orgs(self.request.user, scope)
        # 默认获取有权限的团队
        return OrganizationManager.get_user_orgs(self.request.user)


class OrganizationDetailApiView(generics.RetrieveUpdateAPIView):
    """团队详情

    ### get
    应用场景：获取团队详情

    ### put
    应用场景：更新团队
    """
    permission_classes = [OrganizationDetailUpdatePermission]
    serializer_class = base_org.OrganizationSerializer
    queryset = models.Organization.objects.all()
    lookup_field = 'org_sid'


class OrganizationMemberDeleteApiView(APIView):
    """删除团队成员

    ### delete
    应用场景：删除团队成员
    """
    permission_classes = [OrganizationDefaultPermission]

    def delete(self, request, org_sid, role, username):
        org = get_object_or_404(models.Organization, org_sid=org_sid)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("成员不存在")
        if role == models.Organization.PermissionEnum.ADMIN:
            admins = org.get_members(role)
            if user in admins and admins.count() <= 1:
                raise ValidationError("团队不可无管理员，成员移除无效")
        if role == models.Organization.PermissionEnum.ADMIN or role == models.Organization.PermissionEnum.USER:
            # 移除对应角色用户
            org.remove_perm(user, role)
            admins = org.get_members(models.Organization.PermissionEnum.ADMIN)
            users = org.get_members(models.Organization.PermissionEnum.USER)
            if not (user in admins or user in users):
                pts = ProjectTeam.objects.filter(organization=org)
                for pt in pts:
                    pt.remove_perm(user, ProjectTeam.PermissionEnum.ADMIN)
                    pt.remove_perm(user, ProjectTeam.PermissionEnum.USER)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("角色类型错误")


class OrganizationMemberInviteApiView(APIView):
    """组织成员权限管理

    ### get
    应用场景：获取组织成员

    ### post
    应用场景：邀请成员，得到 一个邀请码
    ```python
    {
      "role": 1, # 1为管理员，2为成员
    }
    ```
    """
    permission_classes = [OrganizationDefaultPermission]

    def get(self, request, org_sid):
        org = get_object_or_404(models.Organization, org_sid=org_sid)
        admins = org.get_members(models.Organization.PermissionEnum.ADMIN)
        users = org.get_members(models.Organization.PermissionEnum.USER)
        return Response({
            "admins": [UserSimpleSerializer(instance=user).data for user in admins],
            "users": [UserSimpleSerializer(instance=user).data for user in users],
        })

    def post(self, request, org_sid):
        org = get_object_or_404(models.Organization, org_sid=org_sid)
        role = request.data.get("role")
        if role not in dict(models.Organization.PERMISSION_CHOICES):
            raise ValidationError({"role": "没有该角色"})
        invite_code = OrganizationManager.get_invite_code(org, perm=role, user=request.user)
        return Response({"invite_code": invite_code})


class OrganizationMemberConfInvitedApiView(generics.GenericAPIView):
    """组织成员邀请

    ### post
    应用场景：根据邀请码将用户添加到组织内
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = base_org.OrganizationSerializer

    def post(self, request, code):
        org_id, perm, inviter_username = OrganizationManager.decode_invite_code(code)
        org = get_object_or_404(models.Organization, id=org_id)
        org.assign_perm(request.user, perm)
        OperationRecordHandler.add_organization_operation_record(
            org, "邀请成员", inviter_username, "邀请%s加入团队，角色为%s" % (request.user, perm))
        slz = self.get_serializer(instance=org)
        return Response(slz.data)


class ScmAllAcountListApiView(generics.GenericAPIView):
    """展示用户全部账号列表

    ### get
    应用场景：获取当前用户全部账号，便于前端处理
    """
    permission_classes = [CodeDogUserPermission]

    def get(self, request):
        user = self.request.user
        accounts = models.ScmAccount.objects.filter(user=user).order_by("-id")
        sshs = models.ScmSshInfo.objects.filter(user=user).order_by("-id")
        return Response({
            "ssh": ScmSshInfoSerializer(sshs, many=True).data,
            "account": ScmAccountSerializer(accounts, many=True).data,
        })


class ScmAccountListApiView(generics.ListCreateAPIView):
    """用户账号列表（用户名+密码）

    ### get
    应用场景：获取用户账号列表

    ### post
    应用场景：创建用户账号
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = ScmAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmAccount.objects.filter(user=user).order_by("-id")


class ScmAccountDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """用户账号列表（用户名+密码）

    ### get
    应用场景：获取用户指定的账号

    ### put
    应用场景：更新用户指定的账号

    ### delete
    应用场景：删除用户指定的账号
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = ScmAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmAccount.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        return get_object_or_404(models.ScmAccount, user=user, id=self.kwargs["account_id"])


class ScmSSHInfoListApiView(generics.ListCreateAPIView):
    """用户SSH授权列表

    ### get
    应用场景：获取用户SSH授权列表

    ### post
    应用场景：创建用户SSH授权列表
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = ScmSshInfoSerializer

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
    permission_classes = [CodeDogUserPermission]
    serializer_class = ScmSshInfoUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmSshInfo.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        return get_object_or_404(models.ScmSshInfo, user=user, id=self.kwargs["sshinfo_id"])
