# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - apis for v3
"""
# python 原生import
import logging
import uuid

# 第三方 import
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

# 项目内 import
from apps.authen import models
from apps.authen.api_filters import base as base_filters
from apps.authen.core import OauthManager
from apps.authen.core import OrganizationManager
from apps.authen.permissions import CodeDogSuperVipUserLevelPermission, CodeDogUserPermission, \
    OrganizationDefaultPermission, OrganizationDetailUpdatePermission
from apps.authen.serializers import base_org
from apps.authen.serializers.base import ScmAccountSerializer, ScmSshInfoSerializer, ScmSshInfoUpdateSerializer, \
    UserSerializer, UserSimpleSerializer, ScmAuthInfoSerializer
from apps.codeproj.core import ScmAuthManager
from apps.codeproj.models import ProjectTeam, Repository
from util import scm
from util.authticket import TempTokenTicket
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class UserInfoApiView(generics.RetrieveUpdateAPIView):
    """用户信息
    ### GET
    应用场景：获取用户信息

    ### PUT
    应用场景：更新用户信息
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserTokenView(APIView):
    """用户信息API

    ### GET

    应用场景：获取当前登录用户Token

    ### POST

    应用场景：更新当前用户Token
    """
    permission_classes = [CodeDogSuperVipUserLevelPermission]

    def get(self, request):
        """
        ### 接口: 返回当前登录用户信息
        """
        logger.info("hello, %s" % request.user)
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response(data={"token": token.key, "tca_ut": TempTokenTicket.generate_ticket(token.key)})

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

    ### GET
    应用场景：获取团队列表
    ```bash
    筛选参数：
    name: 团队名称，包含
    scope: 1 为我管理的
    ```

    ### POST
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

    ### GET
    应用场景：获取团队详情

    ### PUT
    应用场景：更新团队
    """
    permission_classes = [OrganizationDetailUpdatePermission]
    serializer_class = base_org.OrganizationSerializer
    queryset = models.Organization.objects.exclude(status=models.Organization.StatusEnum.FORBIDEN)
    lookup_field = "org_sid"


class OrganizationStatusApiView(generics.RetrieveUpdateAPIView):
    """团队状态变更接口

    ### GET
    应用场景：获取团队简要信息

    ### PUT
    应用场景：更新团队状态
    """
    permission_classes = [OrganizationDefaultPermission]
    serializer_class = base_org.OrganizationSimpleSerializer
    queryset = models.Organization.active_orgs.all()
    lookup_field = "org_sid"


class OrganizationMemberDeleteApiView(APIView):
    """删除团队成员

    ### DELETE
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

    ### GET
    应用场景：获取组织成员

    ### POST
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

    ### POST
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

    ### GET
    应用场景：获取当前用户全部账号，便于前端处理
    """
    permission_classes = [CodeDogUserPermission]

    def get(self, request):
        user = self.request.user
        accounts = models.ScmAccount.objects.filter(user=user).order_by("-id")
        sshs = models.ScmSshInfo.objects.filter(user=user).order_by("-id")
        oauths = models.ScmAuthInfo.objects.filter(user).order_by("-id")
        return Response({
            "ssh": ScmSshInfoSerializer(sshs, many=True).data,
            "account": ScmAccountSerializer(accounts, many=True).data,
            "oauth": ScmAuthInfoSerializer(oauths, many=True).data
        })


class ScmAccountListApiView(generics.ListCreateAPIView):
    """用户账号列表（用户名+密码）

    ### GET
    应用场景：获取用户账号列表

    ### POST
    应用场景：创建用户账号
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = ScmAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmAccount.objects.filter(user=user).order_by("-id")


class ScmAccountDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """用户账号列表（用户名+密码）

    ### GET
    应用场景：获取用户指定的账号

    ### PUT
    应用场景：更新用户指定的账号

    ### DELETE
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

    ### GET
    应用场景：获取用户SSH授权列表

    ### POST
    应用场景：创建用户SSH授权列表
    """
    permission_classes = [CodeDogUserPermission]
    serializer_class = ScmSshInfoSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmSshInfo.objects.filter(user=user).order_by("-id")


class ScmSSHInfoDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """用户SSH授权详情

    ### GET
    获取用户SSH授权详情

    ### PUT
    更新用户指定的SSH授权

    ### DELETE
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


class OauthSettingsStatusAPIView(generics.GenericAPIView):
    """获得平台oauth设置状态

    ### GET
    应用场景：获得各scm平台配置状态
    """

    def get(self, request):
        result = {}
        for scm_platform_name, scm_platform_num in scm.SCM_PLATFORM_NAME_AS_KEY.items():
            oauth_setting = models.ScmOauthSetting.objects.filter(scm_platform=scm_platform_num).first()
            if oauth_setting:
                result.update({scm_platform_name: True})
            else:
                result.update({scm_platform_name: False})
        return Response(result)


class ScmAuthInfoCheckApiView(generics.GenericAPIView):
    """
    ### get
    应用场景：获取用户工蜂授权信息 (注：前端处理时需要修改state和redirect_uri)

    ### delete
    删除用户指定平台的授权信息
    """

    def get(self, request):
        scm_platform_name = request.query_params.get('scm_platform_name', None)
        if not scm_platform_name:
            # 获取各平台授权信息
            result = OauthManager.get_user_oauth_info(request.user)
            return Response(result)

        scm_platform = scm.SCM_PLATFORM_NAME_AS_KEY.get(scm_platform_name)
        oauth_setting = OauthManager.get_oauth_setting(scm_platform_name)
        if not oauth_setting:
            raise ParseError("wrong scm platform provided or no oauth setting")
        oauth_setting = oauth_setting.first()

        scm_auth_info = ScmAuthManager.get_scm_auth(user=request.user, scm_platform=scm_platform)
        git_authed = True if scm_auth_info and scm_auth_info.gitoa_access_token else False
        state_hash = str(uuid.uuid4())[0:8]
        git_auth_url = '%s?client_id=%s&response_type=' \
                       'code&state=%s&redirect_uri=%s&scope=%s' % (
                           oauth_setting.oauth_url,
                           oauth_setting.decrypted_client_id,
                           state_hash,
                           oauth_setting.redirect_uri,
                           "repo" if scm_platform == scm.ScmPlatformEnum.GITHUB else "")
        result = {
            'git': git_authed,
            'git_auth_url': git_auth_url
        }
        return Response(result)

    def delete(self, request):
        scm_platform_name = request.data.get("scm_platform_name")
        if not scm_platform_name:
            scm_platform_name = scm.SCM_PLATFORM_NUM_AS_KEY[scm.ScmPlatformEnum.GIT_OA]
        scm_auth_info = ScmAuthManager.get_scm_auth(user=request.user, scm_platform=scm_platform_name)
        if scm_auth_info:
            scm_auth_info.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScmAuthInfoListApiView(generics.ListAPIView):
    """用户授权列表

    ### GET
    获取用户的授权列表
    """
    serializer_class = ScmAuthInfoSerializer

    def get_queryset(self):
        user = self.request.user
        return models.ScmAuthInfo.objects.filter(user=user, gitoa_access_token__isnull=False).order_by("-id")


class GitCallbackPlatformByScmProxy(generics.GenericAPIView):
    """通过ScmProxy授权
    """

    def get(self, request, scm_platform_name):
        if not request.user:
            return Response("login required!", status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        authorization_code = request.query_params.get("code", None)
        if authorization_code:
            oauth_setting = OauthManager.get_oauth_setting(scm_platform_name)
            if not oauth_setting:
                raise ParseError("wrong scm platform provided or no oauth setting")
            oauth_setting = oauth_setting.first()
            data = {
                "grant_type": "authorization_code",
                "client_id": oauth_setting.decrypted_client_id,
                "client_secret": oauth_setting.decrypted_client_secret,
                "code": authorization_code,
                "redirect_uri": oauth_setting.redirect_uri
            }
            try:
                git_client = scm.ScmClient(Repository.ScmTypeEnum.GIT, scm_url="", auth_type="oauth",
                                           scm_platform=scm_platform_name)
                oauth_info = git_client.get_oauth(auth_info=data)
            except Exception as msg:
                logger.exception("oauth failed, err: %s" % msg)
                raise ParseError("oauth failed, err: %s" % msg)
            ScmAuthManager.create_or_update_scm_auth(
                user=user,
                access_token=oauth_info["access_token"],
                refresh_token=oauth_info.get("refresh_token", None),
                scm_platform=scm.SCM_PLATFORM_NAME_AS_KEY.get(scm_platform_name),
                expires_in=oauth_info.get("expires_in", None),
                created_at=oauth_info.get("created_at", None),
            )
            return Response(data={"msg": "Success"})
        else:
            raise ParseError("no authorization_code provided!")
