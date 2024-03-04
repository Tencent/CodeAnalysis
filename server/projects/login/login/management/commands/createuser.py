# -*- coding:utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""初始化数据
"""
# 原生
import logging

# 第三方
from django.conf import settings
from django.core.management.base import BaseCommand

# 项目内
from login.models import UserAuth, UserInfo
from login.lib import cdcrypto as crypto

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '创建用户'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, help='username')
        parser.add_argument('-p', '--password', type=str, help='password')

    def handle(self, *args, **options):
        self.stdout.write('注册用户')
        identifier = options.get('username')
        credential = options.get('password')

        if not identifier or not credential:
            self.stdout.write('用户名，密码无效，注册用户失败')
            return

        # 记录在auth表
        auth, _ = UserAuth.objects.get_or_create(identifier=identifier, identity_type="oapassword", defaults={
            "credential": crypto.encrypt(credential, settings.PASSWORD_KEY),
            "verified": 1,
        })
        if not auth.user:
            u = UserInfo.objects.create(nickname=identifier)
            auth.user = u
            auth.save()

        self.stdout.write('注册成功，用户名：%s' % identifier)
