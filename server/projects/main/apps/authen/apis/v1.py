# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - apis for v1
"""
# python 原生import
import logging


# 第三方 import
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内 import
from util.authticket import ServerInternalTicket
from util.permissions import ProxyServerPermission

logger = logging.getLogger(__name__)


class ProxyServerAuthenticationAPIView(APIView):
    """ 代理服务器登录鉴权
    """

    permission_classes = [ProxyServerPermission]

    def get(self, request):
        original_uri = request.META.get("HTTP_X_ORIGINAL_URI")
        logger.info("proxy server authentication user[%s], original uri[%s]" % (request.user.username, original_uri))
        return Response("ok", headers={
            "X-CodeDog-User": request.user.username,
            "X-CodeDog-Ticket": ServerInternalTicket.generate_ticket()
        })
