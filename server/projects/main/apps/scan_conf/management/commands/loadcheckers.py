# # -*- coding: utf-8 -*-
"""获取指定工具的所有规则并存入库
"""
# 原生 import
import os
import json
import logging
from os import walk

# 第三方 import
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

# 项目内 import
from apps.scan_conf.utils import load_checkers, disable_checkers

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "load rules of tool"

    def add_arguments(self, parser):
        parser.add_argument("checktool_name", nargs="+", type=str)
        parser.add_argument("-dirname", "--dirname", type=str, help="load dirname path checker, default: checker_json")

    def check_saas_enable(self, checktool_info):
        """检查工具在saas版是否可用
        """
        if hasattr(settings, "CODEDOG_ENV") and settings.CODEDOG_ENV == "saas":
            return checktool_info.get("open_saas", False)
        else:
            return True

    def set_open_on_saas(self, checktool_info):
        """saas版可用工具均初始化为公开
        """
        if hasattr(settings, "CODEDOG_ENV") and settings.CODEDOG_ENV == "saas" \
                and checktool_info.get("open_saas") is True:
            checktool_info.update({"open_user": True})

    def handle(self, *args, **options):
        # 获取工具目录名称，默认为checker_json
        dirname = options.get("dirname") or "checker_json"
        # 获取平台管理员
        admins = []
        for username, _ in settings.ADMINS:
            user, _ = User.objects.get_or_create(username=username)
            admins.append(user)
        admin_names = ",".join([u.username for u in admins])
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
        failed_names = []
        for tool in tools:
            self.stdout.write("loading tool [%s] ..." % tool)
            try:
                file_name = tool + ".json"
                file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
                with open(file_path, "r") as fd:
                    checker_info = json.load(fd)
                # 如果是json数组则只取第一项
                if isinstance(checker_info, list) and len(checker_info) > 0:
                    checker_info = checker_info[0]
                if not self.check_saas_enable(checker_info):
                    self.stdout.write("tool [%s] disable at saas env" % tool)
                    disable_checkers(checker_info)
                self.set_open_on_saas(checker_info)
                # 执行工具load
                checktool = load_checkers(checker_info)
                if not checktool.owners.exists():
                    self.stdout.write("tool [%s] has no owners, add admins[%s] to owners..." % (tool, admin_names))
                    checktool.owners.add(*admins)
            except Exception as e:
                logger.error(e)
                failed_names.append(tool)
        # 检查执行完毕
        tool_names = ""
        for tool in tools:
            tool_names = tool_names + tool + ";"
        self.stdout.write("Finish load [%s]" % tool_names)
        if failed_names:
            self.stdout.write("ERROR!!! Faided tools: [%s]" % " ".join(failed_names))
