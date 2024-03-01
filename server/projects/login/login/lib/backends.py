# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

# 原生 import
import logging
from time import time
from hashlib import sha256

# 第三方 import
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 项目内 import
from login.lib.cdcrypto import decrypt
from login.models import UserInfo

logger = logging.getLogger(__name__)


class MainServerInternalAuthentication(BaseAuthentication):
    """Server API内部鉴权

    场景：通过指定密钥，用于访问服务内部接口，用于api接口
    """
    class FailedCodeEnum:
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
        user, _ = UserInfo.objects.get_or_create(uid="CodeDog")
        return (user, None)

    def authenticate_header(self, request):
        """鉴权返回的头部信息
        """
        return "main-internal-ticket"
