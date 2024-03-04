# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
初始化数据脚本
用于平台启动的初始化数据，包括以下内容：
- 标签、语言
- 工具类型、工具进程
- 成员列表、成员权限
"""

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from apps.base.models import Origin
from apps.nodemgr.models import ExecTag
from apps.scan_conf import models as conf_models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "initialize db data"

    def handle(self, *args, **options):
        """初始化数据：
        - 标签、语言
        - 工具类型、工具进程
        - 成员列表、成员权限
        """
        self.stdout.write("新增执行环境标签...")
        tag_names = ["Codedog_Mac", "Codedog_Linux", "Codedog_Windows"]
        for name in tag_names:
            ExecTag.objects.get_or_create(name=name)
        ExecTag.objects.filter(name__in=tag_names).update(public=True)
        self.stdout.write("新增规则标签...")
        label_names = ["基础", "推荐", "通用", "开源", "规范", "安全", "增强"]
        for name in label_names:
            conf_models.Label.objects.get_or_create(name=name)
        self.stdout.write("初始化语言...")
        for item in dir(conf_models.Language.LanguageEnum):
            if item.isupper():
                conf_models.Language.objects.get_or_create(name=getattr(conf_models.Language.LanguageEnum, item))
        self.stdout.write("初始化来源数据...")
        Origin.objects.get_or_create(name=settings.DEFAULT_ORIGIN_ID)
        self.stdout.write("初始化/更新Process...")
        processes = [("compile", 0), ("analyze", 1), ("datahandle", 2)]
        for name, priority in processes:
            process, created = conf_models.Process.objects.get_or_create(
                name=name, defaults={"display_name": name, "priority": priority})
            if not created:
                process.priority = priority
                process.save()
        self.stdout.write("初始化Scan App...")
        scan_apps = [{
            "name": "codelint",
            "label": "代码检查",
            "desc": "代码检查"
        }, {
            "name": "codemetric",
            "label": "代码度量",
            "desc": "代码度量"
        }]
        for scan_app in scan_apps:
            try:
                app = conf_models.ScanApp.objects.get(name=scan_app["name"])
                app.label = scan_app["label"]
                app.desc = scan_app["desc"]
                app.save()
            except conf_models.ScanApp.DoesNotExist:
                conf_models.ScanApp.objects.create(
                    name=scan_app["name"], label=scan_app["label"], desc=scan_app["desc"])
        self.stdout.write("创建CodeDog并使用默认token")
        codedog, _ = User.objects.get_or_create(username=settings.DEFAULT_USERNAME)
        codedog.is_staff = True
        codedog.is_superuser = True
        codedog.save()
        if hasattr(settings, "CODEDOG_TOKEN") and settings.CODEDOG_TOKEN:
            Token.objects.get_or_create(user=codedog, defaults={"key": settings.CODEDOG_TOKEN})
            Token.objects.filter(user=codedog).update(key=settings.CODEDOG_TOKEN)
        self.stdout.write("将Admins设置为超级管理员...")
        for username, _ in settings.ADMINS:
            user, created = User.objects.get_or_create(username=username,
                                                       defaults={"is_superuser": True, "is_staff": True})
            if not created:
                user.is_superuser = True
                user.save()
        self.stdout.write("数据化初始成功")
