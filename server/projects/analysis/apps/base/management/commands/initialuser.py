# -*- coding:utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""获取指定工具的所有规则并存入库，支持可以多次执行
"""

import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'initialize codedog user'

    def handle(self, *args, **options):
        codedog, _ = User.objects.get_or_create(username="CodeDog")
        codedog.is_superuser = True
        codedog.is_staff = True
        codedog.save()
        self.stdout.write('用户数据初始成功')
