# # -*- coding: utf-8 -*-
"""获取指定规则包并存入库
"""
# 原生 import
import json
import logging
import os
from os import walk

from django.conf import settings
# 第三方 import
from django.core.management.base import BaseCommand

from apps.scan_conf.models import CheckPackage
# 项目内 import
from apps.scan_conf.utils import load_checkpackages, disable_checkpackages

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "load rules of package"

    def add_arguments(self, parser):
        parser.add_argument("file_names", nargs="+", type=str)
        parser.add_argument("-dirname", "--dirname", type=str, help="load dirname path package")

    def check_saas_enable(self, checkpackage_info):
        """检查工具在saas版是否可用
        """
        if hasattr(settings, "CODEDOG_ENV") and settings.CODEDOG_ENV == "saas":
            return checkpackage_info.get("open_saas", False)
        else:
            return True

    def set_open_on_saas(self, checkpackage_info):
        """saas版可用规则包均初始化为公开
        """
        if hasattr(settings, "CODEDOG_ENV") and settings.CODEDOG_ENV == "saas" \
                and checkpackage_info.get("open_saas") is True:
            # 无status或为disabled则更新为running
            if not checkpackage_info.get("status") or checkpackage_info.get(
                    "status") == CheckPackage.StatusEnum.DISABLED:
                checkpackage_info.update({"status": CheckPackage.StatusEnum.RUNNING})

    def handle(self, *args, **options):
        # 获取规则包目录名称，默认为checkpackage_json
        dirname = options.get("dirname") or "checkpackage_json"
        file_names = options["file_names"]
        package_list = []
        # 获取需要load的规则包文件名称列表，all表示全部，带_new的文件忽略
        if file_names == ["all"]:
            folder_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname)
            for _, _, filenames in walk(folder_path):
                for filename in filenames:
                    if filename.endswith(".json") and "_new" not in filename:
                        package_list.append(filename[:-5])
            file_names = package_list
        # 执行规则包load
        failed_names = []
        for fn in file_names:
            self.stdout.write("loading package [%s] ..." % fn)
            try:
                file_name = fn + ".json"
                file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
                with open(file_path, "r") as fd:
                    checkpackage_info = json.load(fd)
                # 如果是json数组则只取第一项
                if isinstance(checkpackage_info, list) and len(checkpackage_info) > 0:
                    checkpackage_info = checkpackage_info[0]
                if not self.check_saas_enable(checkpackage_info):
                    self.stdout.write("package[%s] disable at saas env" % fn)
                    disable_checkpackages(checkpackage_info)
                self.set_open_on_saas(checkpackage_info)
                # 执行规则包load
                checkpackage = load_checkpackages(checkpackage_info)
                if checkpackage.package_type != CheckPackage.PackageTypeEnum.OFFICIAL:
                    self.stdout.write("package[%s] is not official set to official..." % checkpackage.name)
                    checkpackage.package_type = CheckPackage.PackageTypeEnum.OFFICIAL
                    checkpackage.save()
            except Exception as e:
                logging.exception(e)
                failed_names.append(fn)
        # 检查执行完毕
        self.stdout.write("Finish load [%s]" % "; ".join(file_names))
        if failed_names:
            self.stdout.write("ERROR!!! Faided packages: [%s]" % " ".join(failed_names))
