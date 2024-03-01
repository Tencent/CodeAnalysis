# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
middleware - loginmiddleware
"""
import logging
from datetime import datetime

import jwt
from django.conf import settings
from rest_framework.response import Response

from login import models

logger = logging.getLogger(__name__)


class ResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.handle_auth_authorization(request)

    def process_exception(self, request, exception):
        logger.exception(exception)
        return Response({"message": exception.args[0], "status": -1})

    def handle_auth_authorization(self, request):
        """
        处理auth的请求头，临时oauth鉴权信息处理
        附在request上
        {
            'identifier':'openid',
            "identity_type":"wework",
            "time":'生成时间'
        }
        :identifier,'identity_type':identity_type,'time'
        """
        try:
            authorization = request.META.get('HTTP_OAUTHAUTHORIZATION', '')
            auth_type = settings.OAUTH_JWT['AUTH_HEADER_TYPES'][0]
            pub_key = settings.OAUTH_JWT['VERIFYING_KEY']
            life_time = settings.OAUTH_JWT['ACCESS_TOKEN_LIFETIME']
            now_time = datetime.now()

            if auth_type in authorization:
                access_token = authorization.replace('%s ' % auth_type, '')
                decoded_jwt = jwt.decode(access_token, pub_key, algorithm='RS256')
                jwt_time = decoded_jwt.get('time', None)
                if jwt_time:
                    last_time = datetime.strptime(decoded_jwt.get('time', ''), '%Y-%m-%d %H:%M:%S.%f')
                else:
                    logger.exception('该oauth token不合法，缺少时间')
                    request.oauth = None
                    return

                if now_time - last_time > life_time:
                    logger.exception('该oauth token超时')
                    request.oauth = None
                    return
                auth = models.UserAuth.objects.filter(identifier=decoded_jwt.get('identifier', ''),
                                                      identity_type=decoded_jwt.get('identity_type', ''))
                if auth.exists():
                    request.oauth = auth.first()
                else:
                    request.oauth = None
            else:
                logger.warning("[auth_type: %s] auth type not in authorization" % auth_type)
                request.oauth = None
        except Exception as e:
            logger.exception(e)
            return Response({"exception_message": "鉴权失败", "status": -1})
