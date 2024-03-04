# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""获取指定规则包json入库
"""
import os
import json
import logging
from os import walk

# 第三方
from django.core.management.base import BaseCommand

# 项目内
from apps.scan_conf.utils import CheckPackageLoadManager

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "load rules of package"

    def add_arguments(self, parser):
        parser.add_argument("file_names", nargs="+", type=str)
        parser.add_argument("-dirname", "--dirname", type=str, help="load dirname path package")

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
        checkpackage_json_list = []
        pkg_kv = dict()
        failed_names = []
        for fn in file_names:
            try:
                file_name = fn + ".json"
                file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
                with open(file_path, "r") as fd:
                    checkpackage_json = json.load(fd)
                # 如果是json数组则只取第一项
                if isinstance(checkpackage_json, list) and len(checkpackage_json) > 0:
                    checkpackage_json = checkpackage_json[0]
                pkg_kv[checkpackage_json["name"]] = fn
                checkpackage_json_list.append(checkpackage_json)
            except Exception as e:
                logger.error(e)
                failed_names.append(fn)
        load_res_list = CheckPackageLoadManager.loadpkg_by_workers(checkpackage_json_list)
        for status, checkpackage_json in load_res_list:
            if not status:
                failed_names.append(pkg_kv[checkpackage_json])
        # 检查执行完毕
        self.stdout.write("Finish load [%s]" % "; ".join(file_names))
        if failed_names:
            self.stdout.write("ERROR!!! Faided packages: [%s]" % " ".join(failed_names))
