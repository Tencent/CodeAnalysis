# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""工具管理相关脚本处理
"""
import logging
import time

# 第三方
from django.core.management.base import BaseCommand

# 项目内
from apps.authen.models import Organization
from apps.scan_conf.models import CheckTool, CheckToolWhiteKey
from apps.scan_conf.core import CheckToolManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "工具管理相关脚本处理"

    def add_arguments(self, parser):
        parser.add_argument("-func", "--func", type=str, help="方法名称")
        parser.add_argument("-params", "--params", nargs="+", type=str, help="参数")

    def tool_to_private(self, tool_names, org_sid):
        """将工具私有化
        :param tool_names: str, 工具名称，,分隔
        :param org_sid: str, 组织sid
        """
        tool_names = tool_names.split(",")
        self.stdout.write("tool_name count: %d" % len(tool_names))
        checktools = CheckTool.objects.filter(name__in=tool_names)
        self.stdout.write("checktool count: %d" % checktools.count())
        org = Organization.objects.get(org_sid=org_sid)
        tool_key = CheckToolManager.get_tool_key(org=org)
        checktools.update(tool_key=tool_key, open_user=False)
        for checktool in checktools:
            CheckToolWhiteKey.objects.get_or_create(tool_key=tool_key, tool_id=checktool.id)

    def tool_add_org(self, tool_names, org_sid):
        """工具添加到团队，即工具增加团队白名单
        :param tool_names: str, 工具名称，,分隔
        :param org_sid: str, 组织sid
        """
        tool_names = tool_names.split(",")
        self.stdout.write("tool_name count: %d" % len(tool_names))
        checktools = CheckTool.objects.filter(name__in=tool_names)
        self.stdout.write("checktool count: %d" % checktools.count())
        org = Organization.objects.get(org_sid=org_sid)
        tool_key = CheckToolManager.get_tool_key(org=org)
        for checktool in checktools:
            CheckToolWhiteKey.objects.get_or_create(tool_key=tool_key, tool_id=checktool.id)

    def handle(self, *args, **options):
        func = options.get("func")
        params = options.get("params") or []
        self.stdout.write("===========开始执行脚本===========")
        self.stdout.write("func: %s" % func)
        self.stdout.write("params: %s" % params)
        start_time = time.time()
        getattr(self, func)(*params)
        use_time = time.time() - start_time
        self.stdout.write("use time: %s" % use_time)
        self.stdout.write("=========== ^_^ 脚本执行完毕 ^_^ ===========")
