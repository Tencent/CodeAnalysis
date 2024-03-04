# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - base backend
"""
# 原生 import
import logging
import time
from urllib import parse

# 第三方 import
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from jwt import decode as jwt_decode
from jwt.exceptions import ExpiredSignatureError
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

# 项目内 import
from apps.authen.models import CodeDogUser
from util.cdcrypto import decrypt

logger = logging.getLogger(__name__)


class TiyanLoginBackend(BaseAuthentication):
    """体验版登陆鉴权

    场景：通过Login服务，用于登陆Web平台
    """

    def authenticate(self, request):
        """鉴权
        """
        authorization = request.META.get("HTTP_AUTHORIZATION", None)
        if not authorization:
            return
        if not settings.AUTHORIZATION_PUBKEY:
            return
        if not authorization.startswith("CodeDog"):
            return
        pub_key = settings.AUTHORIZATION_PUBKEY
        try:
            auth_data = jwt_decode(authorization.replace("CodeDog ", ""),
                                   pub_key, algorithms=["RS256"])
        except ExpiredSignatureError:  # 未覆盖所有的error情况，需要调整，避免500
            raise AuthenticationFailed({"msg": "鉴权失效"})
        except Exception as err:
            logger.exception("tiyan login exception: %s" % err)
            raise AuthenticationFailed({"msg": "鉴权失效"})
        user, _ = User.objects.get_or_create(username=auth_data.get("user_id"))
        codedog_user, _ = CodeDogUser.objects.get_or_create(
            user=user, defaults={"nickname": auth_data.get("nickname", user.username)})
        codedog_user.refresh_login_time()
        codedog_user.save()
        return (user, None)

    def authenticate_header(self, request):
        return "tiyan-auth"


class TCANodeTokenBackend(TokenAuthentication):
    """TCA 节点Token鉴权

    场景：通过Token鉴权，用于访问对外开放接口，用于api、api_v1的节点专用接口
    """

    def authenticate(self, request):
        """鉴权
        """
        node_identity = request.META.get("HTTP_NODE_IDENTITY")
        if not node_identity:
            return
        return super(TCANodeTokenBackend, self).authenticate(request)

    def authenticate_header(self, request):
        return "tca-node-auth"


class TCATempUserTokenBackend(BaseAuthentication):
    """TCA 临时Token鉴权
    """

    def get_temp_token_from_url(self, url_path):
        """通过url获取临时token
        """
        if not url_path:
            return
        query = parse.urlsplit(url_path).query
        if not query:
            return
        query = dict(parse.parse_qs(query))
        temp_token = query.get("tut")
        if not temp_token:
            return
        else:
            logger.info("[TCA Temp Token Auth] get tca user token from original url")
            return temp_token[0]

    def authenticate(self, request):
        """鉴权
        """
        url = request.META.get("HTTP_X_ORIGINAL_URI")
        tca_user_token = request.query_params.get("tut") or self.get_temp_token_from_url(url)
        if not tca_user_token:
            return
        try:
            tca_token_str = decrypt(tca_user_token, settings.API_TICKET_SALT)
            token_timestamp, token, token_timestamp = tca_token_str.split("$#$")
        except Exception:
            logger.error("[TCA Temp Token Auth] get tca user token failed: %s" % tca_user_token)
            raise AuthenticationFailed("Authentication failed")
        current_time = time.time()
        if abs(current_time - int(token_timestamp)) > 24 * 3600:
            logger.error("[TCA Temp Token Auth] token expired: %s" % str(current_time - int(token_timestamp)))
            raise AuthenticationFailed("Authentication failed")
        token = Token.objects.filter(key=token).first()
        if not token:
            logger.warning("[TCA Temp Token Auth] token does not exist: %s" % token)
            raise AuthenticationFailed("Authentication failed")
        return (token.user, None)

    def authenticate_header(self, request):
        return "tca-temp-user-token"
