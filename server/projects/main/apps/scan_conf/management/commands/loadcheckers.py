# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""获取指定工具json入库
"""
import os
import json
import logging
from os import walk

# 第三方 import
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

# 项目内 import
from apps.scan_conf.utils import CheckToolLoadManager

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "load rules of tool"

    def add_arguments(self, parser):
        parser.add_argument("checktool_name", nargs="+", type=str)
        parser.add_argument("-dirname", "--dirname", type=str, help="load dirname path checker, default: checker_json")

    def handle(self, *args, **options):
        # 获取工具目录名称，默认为checker_json
        dirname = options.get("dirname") or "checker_json"
        # 获取平台管理员
        admins = []
        for username, _ in settings.ADMINS:
            user, _ = User.objects.get_or_create(username=username)
            admins.append(user)
        # 获取需要load的工具文件名称列表，all表示全部，带_new的文件忽略
        tools = options["checktool_name"]
        tool_list = []
        if tools == ["all"]:
            folder_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname)
            for _, _, filenames in walk(folder_path):
                for filename in filenames:
                    if filename.endswith(".json") and "_new" not in filename:
                        tool_list.append(filename[:-5])
            tools = tool_list
        # 执行工具load
        checktool_json_list = []
        tool_kv = dict()
        failed_names = []
        for tool in tools:
            try:
                file_name = tool + ".json"
                file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
                with open(file_path, "r") as fd:
                    checktool_json = json.load(fd)
                # 如果是json数组则只取第一项
                if isinstance(checktool_json, list) and len(checktool_json) > 0:
                    checktool_json = checktool_json[0]
                tool_kv[checktool_json["name"]] = tool
                checktool_json_list.append(checktool_json)
            except Exception as e:
                logger.error(e)
                failed_names.append(tool)
        load_res_list = CheckToolLoadManager.loadchecker_by_workers(checktool_json_list, admins)
        for status, checktool_name in load_res_list:
            if not status:
                failed_names.append(tool_kv[checktool_name])
        # 检查执行完毕
        tool_names = ""
        for tool in tools:
            tool_names = tool_names + tool + ";"
        self.stdout.write("Finish load [%s]" % tool_names)
        if failed_names:
            self.stdout.write("ERROR!!! Faided tools: [%s]" % " ".join(failed_names))
