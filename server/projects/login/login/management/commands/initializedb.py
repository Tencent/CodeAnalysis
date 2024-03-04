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
    help = "initialize db data"

    def handle(self, *args, **options):
        self.stdout.write("创建CodeDog作为超级管理员")
        identifier = settings.TCA_DEFAULT_ADMIN
        credential = settings.TCA_DEFAULT_PASSWORD
        if not identifier or not credential:
            self.stdout.write("用户名，密码无效，注册用户失败")
            return

        # 记录在auth表
        auth, _ = UserAuth.objects.get_or_create(identifier=identifier, identity_type="oapassword", defaults={
            "credential": crypto.encrypt(credential, settings.PASSWORD_KEY),
            "verified": 1,
        })
        if not auth.user:
            u, _ = UserInfo.objects.get_or_create(uid=identifier, defaults={
              "nickname": identifier
            })
            auth.user = u
            auth.save()
        self.stdout.write("数据化初始成功")
