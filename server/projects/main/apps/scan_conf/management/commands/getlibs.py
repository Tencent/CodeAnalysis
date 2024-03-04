# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""获取指定工具依赖并以json格式存入本地
"""
import os
import json
import logging

# 第三方
from django.core.management.base import BaseCommand

# 项目内
from apps.scan_conf.models import ToolLib
from apps.scan_conf.core import ToolLibManager

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "get toollib"

    def add_arguments(self, parser):
        parser.add_argument("lib_name_list", type=str, nargs="+", help="需要get的工具依赖列表")
        parser.add_argument("-dirname", "--dirname", type=str, default="toollib_json",
                            help="load dirname path toollib, default: toollib_json")

    def get_toollib_data(self, toollib):
        return {
          "name": toollib.name,
          "description": toollib.description,
          "envs": toollib.envs,
          "lib_type": toollib.lib_type,
          "lib_os": toollib.lib_os,
          "scm_url": toollib.scm_url,
          "scm_type": toollib.scm_type,
          "extra_data": toollib.extra_data,
          "lib_key": toollib.lib_key
        }

    def handle(self, *args, **options):
        # 获取工具依赖目录名称，默认为toollib_json
        dirname = options.get("dirname")
        # 获取需要load的工具依赖文件名称
        lib_name_list = options.get("lib_name_list")
        if lib_name_list == ["all"]:
            toollibs = ToolLib.objects.all()
        else:
            toollibs = ToolLib.objects.filter(name__in=lib_name_list)
        for toollib in toollibs:
            self.stdout.write("正在下载工具依赖[%s]-[%s]..." % (toollib.name, toollib.lib_key))
            if toollib.lib_key == ToolLibManager.LibKeyEnum.SYSTEM:
                file_name = "%s_new.json" % toollib.name.lower()
            else:
                file_name = "%s-%s_new.json" % (toollib.name.lower(), toollib.lib_key)
            file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, file_name)
            result = self.get_toollib_data(toollib)
            with open(file_path, "w") as fd:
                fd.write(json.dumps(result, indent=2, ensure_ascii=False))
                self.stdout.write("线上工具依赖[%s-%s]已经加载到文件: %s" % (toollib.name, toollib.lib_key, file_path))
        # 检查执行完毕
        self.stdout.write("成功加载[%d]个工具依赖到本地文件 *_new.json" % toollibs.count())
