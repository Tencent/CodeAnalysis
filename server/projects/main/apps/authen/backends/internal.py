# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - internal backend
"""
# 原生 import
import logging
from time import time
from hashlib import sha256

# 第三方 import
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 项目内 import
from apps.authen.core import CodeDogUserManager
from util.cdcrypto import decrypt


logger = logging.getLogger(__name__)


class ServerAPIAuthentication(BaseAuthentication):
    """Server API内部鉴权

    场景：通过指定密钥，用于访问服务内部接口，用于api接口
    """
    class FailedCodeEnum:
        NO_TICKET = -1
        TICKET_INVALID = -2
        TICKET_EXPIRED = -3

    def authenticate(self, request):
        server_ticket = request.META.get("HTTP_SERVER_TICKET", None)
        # 不使用Server API鉴权时返回None
        if server_ticket is None:
            return
        logger.info("using serverapi authen")
        try:
            ticket_data_str = decrypt(server_ticket, settings.API_TICKET_SALT)
            ticket_timestamp, ticket_signature = ticket_data_str.split("$#$")
        except Exception:
            logger.error("get ticket failed: %s" % server_ticket)
            raise AuthenticationFailed({"code": self.FailedCodeEnum.TICKET_INVALID, "msg": "鉴权失败"})
        token = settings.API_TICKET_TOKEN
        ticket_string = "%s,%s,%s" % (ticket_timestamp, token, ticket_timestamp)
        validate_time = 20 * 60  # 20分钟有效期
        if abs(time() - int(ticket_timestamp)) > validate_time:
            raise AuthenticationFailed({"code": self.FailedCodeEnum.TICKET_EXPIRED, "msg": "ticket过期"})
        elif sha256(ticket_string.encode("utf-8")).hexdigest().upper() != ticket_signature:
            raise AuthenticationFailed({"code": self.FailedCodeEnum.TICKET_INVALID, "msg": "鉴权失败"})
        user = User.objects.get_or_create(username=settings.DEFAULT_USERNAME)[0]
        CodeDogUserManager.get_codedog_user(user)
        return (user, None)

    def authenticate_header(self, request):
        return "ticket"
