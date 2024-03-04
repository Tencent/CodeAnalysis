# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""服务鉴权
"""

import logging
from hashlib import sha256
from time import time

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed

from utils.cdcrypto import decrypt

logger = logging.getLogger(__name__)


class MainServerInternalAuthentication(BaseAuthentication):
    """MainServer内部请求鉴权 - Main Server内部请求
    """

    class FailedCodeEnum:
        """错误码类型
        """
        NO_TICKET = -1
        TICKET_INVALID = -2
        TICKET_EXPIRED = -3

    def check_ticket(self, ticket):
        """检查ticket
        """
        try:
            ticket_data_str = decrypt(ticket, settings.API_TICKET_SALT)
            ticket_timestamp, ticket_signature = ticket_data_str.split('$#$')
        except Exception:
            logger.warning("get ticket failed: %s" % ticket)
            raise AuthenticationFailed("鉴权失败")
        token = settings.API_TICKET_TOKEN
        ticket_string = "%s,%s,%s" % (ticket_timestamp, token, ticket_timestamp)
        validate_time = 20 * 60  # 20分钟有效期
        if abs(time() - int(ticket_timestamp)) > validate_time:
            logger.warning("Ticket expired")
            raise AuthenticationFailed("鉴权失败")
        elif sha256(ticket_string.encode("utf-8")).hexdigest().upper() != ticket_signature:
            logger.warning("Ticket invalid")
            raise AuthenticationFailed("鉴权失败")

    def authenticate(self, request):
        """鉴权，校验HTTP_SERVER_TICKET字段有效性
        """
        server_ticket = request.META.get("HTTP_SERVER_TICKET", None)
        # 不使用Server API鉴权时返回None
        if server_ticket is None:
            return
        logger.debug("[CodeDog Main] using mainserver internal authen")
        self.check_ticket(server_ticket)
        User = get_user_model()
        user = User.objects.get_or_create(nickname="codedog")[0]
        return (user, None)

    def authenticate_header(self, request):
        """鉴权返回的头部信息
        """
        return "main-internal-ticket"


class MainProxyAuthentication(MainServerInternalAuthentication):
    """Main服务代理鉴权
    """

    def authenticate(self, request):
        """鉴权，判断HTTP_X_CODEDOG_USER、HTTP_X_CODEDOG_TICKET字段值有效性
        """
        username = request.META.get("HTTP_X_CODEDOG_USER", None)
        proxy_ticket = request.META.get("HTTP_X_CODEDOG_TICKET", None)
        if not username and not proxy_ticket:
            return
        logger.debug("[User: %s] using mainserver proxy authen" % username)
        self.check_ticket(proxy_ticket)
        User = get_user_model()
        user = User.objects.get_or_create(nickname=username)[0]
        return (user, None)

    def authenticate_header(self, request):
        """鉴权返回的头部信息
        """
        return "main-proxy-ticket"
