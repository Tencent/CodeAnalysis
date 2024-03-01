# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
login - core
"""
# 原生
import logging

# 第三方
from django.conf import settings

from login.lib import cdcrypto as crypto, utils
# 项目内
from login.models import UserAuth, UserInfo

logger = logging.getLogger(__name__)


class UserManager(object):
    """用户管理
    """

    @classmethod
    def get_or_create_account(cls, identifier):
        """创建、获取账户
        :param identifier: str, 账户
        :return: auth, password, user
        """
        # 随机6位密码
        credential = utils.id_generator()
        auth, _ = UserAuth.objects.get_or_create(identifier=identifier, identity_type="oapassword", defaults={
            "credential": crypto.encrypt(credential, settings.PASSWORD_KEY),
            "verified": 1,
        })
        # 关联用户
        if not auth.user:
            u, _ = UserInfo.objects.get_or_create(uid=identifier, defaults={"nickname": identifier})
            auth.user = u
            auth.save()

        return auth, crypto.decrypt(auth.credential, settings.PASSWORD_KEY), auth.user
