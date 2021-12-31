# -*- coding: utf-8 -*-
"""
login - v1 apis
"""
# 原生
import logging

# 第三方
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内
from login.core import UserManager
from login.lib import cdcrypto as crypto
from login.lib.backends import MainServerInternalAuthentication

logger = logging.getLogger(__name__)


class UserListApiView(APIView):
    """用户列表接口

    ### post
    应用场景：创建用户，用于main服务创建用户，可批量创建
    """

    authentication_classes = (MainServerInternalAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        users = request.data.get("users", [])
        data = []
        for username in users:
            if username:
                _, password, user = UserManager.get_or_create_account(username)
                data.append({
                    "username": user.uid,
                    "nickname": username,
                    "password": password
                })
        return Response(data)


class UserDetailApiView(APIView):
    """用户详情接口

    ### put
    应用场景：更新用户，用于main服务更新用户密码
    """
    authentication_classes = (MainServerInternalAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, uid):
        userauth, _, userinfo = UserManager.get_or_create_account(uid)
        nickname = request.data.get("nickname", None)
        credential = request.data.get("password", None)
        # 用户昵称变更
        if nickname:
            userinfo.nickname = nickname
            userinfo.save()
        # 密码变更
        if credential:
            credential = crypto.encrypt(credential, settings.PASSWORD_KEY)
            userauth.credential = credential
            userauth.save()
        return Response({"username": userinfo.uid, "nickname": userinfo.nickname,
                         "password": crypto.decrypt(userauth.credential, settings.PASSWORD_KEY)})
