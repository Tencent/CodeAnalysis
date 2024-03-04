# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""获取指定工具并以json格式存入本地
"""
import os
import json
import logging

# 第三方
from django.core.management.base import BaseCommand

# 项目内
from apps.scan_conf.models import CheckTool
from apps.scan_conf.utils import CheckToolLoadManager

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "get checktool json file"

    def add_arguments(self, parser):
        parser.add_argument("checktool_name", nargs="+", type=str)
        parser.add_argument("-dirname", "--dirname", type=str, help="get dirname path checker, default: checker_json")

    def handle(self, *args, **options):
        # 获取工具目录名称，默认为checker_json
        dirname = options.get("dirname") or "checker_json"
        tools = options["checktool_name"]
        if tools == ["all"]:
            tools = list(CheckTool.objects.all().values_list("name", flat=True))
        for tool in tools:
            self.stdout.write("正在下载工具[%s]..." % tool)
            file_name = tool + "_new.json"
            file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
            result = CheckToolLoadManager.getchecker(tool)
            with open(file_path, "w") as fd:
                fd.write(json.dumps([result], indent=2, ensure_ascii=False))
                self.stdout.write("工具[%s] 线上规则已经加载到文件: %s" %
                                  (tool, file_path))
        # 检查执行完毕
        tool_names = ""
        for tool in tools:
            tool_names = tool_names + tool + ";"
        self.stdout.write(
            "成功加载工具[%s]到本地文件 *_new.json，请检查修改重命名为 *.json 再上传。" % tool_names)
