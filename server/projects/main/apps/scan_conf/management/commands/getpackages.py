# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""获取指定规则并以json格式存入本地
"""
import os
import json
import logging

# 第三方
from django.core.management.base import BaseCommand

# 项目内
from apps.scan_conf.models import CheckPackage
from apps.scan_conf.utils import CheckPackageLoadManager

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "get checkpackage json file"

    def add_arguments(self, parser):
        parser.add_argument("checkpackage_id", nargs="+", type=int)
        parser.add_argument("-dirname", "--dirname", type=str, help="get dirname path pkg, default: checker_json")

    def handle(self, *args, **options):
        # 获取规则包目录名称，默认为checkpackage_json
        dirname = options.get("dirname") or "checkpackage_json"
        package_ids = options["checkpackage_id"]
        if package_ids == [0]:
            package_ids = list(CheckPackage.objects.filter(
                package_type=CheckPackage.PackageTypeEnum.OFFICIAL).values_list("id", flat=True))
        for package_id in package_ids:
            self.stdout.write("正在下载规则包[%s]..." % package_id)
            file_name = "package_%d_new.json" % package_id
            file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
            result = CheckPackageLoadManager.getpkg(package_id)
            with open(file_path, "w") as fd:
                fd.write(json.dumps([result], indent=2, ensure_ascii=False))
                self.stdout.write("规则包[%s] 线上规则已经加载到文件: %s" % (package_id, file_path))
        # 检查执行完毕
        package_names = "; ".join(["package_%d" % pid for pid in package_ids])
        self.stdout.write(
            "成功加载规则包[%s]到本地文件 *_new.json，请检查修改重命名为 *.json 再上传。" % package_names)
