# -*- coding:utf-8 -*-
"""刷新oapassword密码，加密
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
    help = '刷新oapassword密码，加密'

    def handle(self, *args, **options):
        self.stdout.write('刷新oapassword密码，给密码加密')
        uas = UserAuth.objects.filter(identity_type="oapassword")
        for ua in uas:
            ua.credential = crypto.encrypt(ua.credential, settings.PASSWORD_KEY)
            ua.save()
            self.stdout.write(ua.identifier)
        self.stdout.write('刷新完毕')
