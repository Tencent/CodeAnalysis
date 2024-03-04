# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""增加默认过滤路径
包含内容：
1. 常见语言的第三方库存放路径
2. scm相关路径
3. ...
"""

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.codeproj.models import DefaultScanPath

logger = logging.getLogger(__name__)

EXCLUDE_PATHS = [
    # scm相关路径
    ".*/\\.svn/.*",
    "\\.svn/.*",
    ".*/\\.git/.*",
    "\\.git/.*",
    ".*/pinpoint_piggy/.*",
    ".*/\\.git",
    # 第三方库路径
    ".*/thirdparty/.*",
    "thirdparty/.*",
    ".*/google\\.golang\\.org/.*",
    ".*/externlibs/.*",
    "externlibs/.*",
    "lua/jit/.*",
    ".*/lua/jit/.*",
    ".*/third/.*",
    "third/.*",
    ".*/.*\\.dll",
    ".*/gopkg\\.in/.*",
    "gopkg\\.in/.*",
    ".*/tdrbuf/.*",
    "tdrbuf/.*",
    ".*/third_party/.*",
    "third_party/.*",
    ".*/tools/.*",
    "tools/.*",
    ".*/third-party/.*",
    "third-party/.*",
    ".*/3rd/.*",
    "3rd/.*",
    ".*/highcharts.*.js",
    ".*/pbprotocol/.*",
    "pbprotocol/.*",
    ".*/boost/.*",
    "boost/.*",
    ".*/jquery.*\\.js",
    ".*/tinyxml/.*",
    "tinyxml/.*",
    ".*/.*\\.exe",
    ".*/lib_3rd/.*",
    "lib_3rd/.*",
    ".*/github\\.com/.*",
    ".*/node_modules/.*",
    "node_modules/.*",
    ".*/3rdParty/.*",
    "3rdParty/.*",
    ".*/tinyxml2/.*",
    "tinyxml2/.*",
    ".*/universaldetector\\.py",
    ".*/demo/.*",
    "demo/.*",
    ".*/mobdebug\\.lua",
    ".*/external/.*",
    "external/.*",
    ".*/3rdparty/.*",
    "3rdparty/.*",
    ".*/ProgramFiles/.*",
    ".*/.*\\.pb\\.cc",
    ".*\\.min\\.js",
    ".*/tool/.*",
    "tool/.*",
    ".*/3rdlib/.*",
    "3rdlib/.*",
    ".*/.*\\.svg",
    ".*/ProgramFiles\\(x86\\)/.*",
    ".*/luajit/jit/.*",
    ".*/protobuf/.*",
    "protobuf/.*",
    ".*/extensions/.*",
    "extensions/.*",
    ".*/Tdr/.*",
    "Tdr/.*",
    ".*/ThirdPart/.*",
    "ThirdPart/.*",
    ".*/ThirdParty/.*",
    "ThirdParty/.*",
    ".*/lib/.*",
    "lib/.*",
    ".*/echarts.*.js",
    ".*/gtest/.*",
    "gtest/.*",
    ".*/curl/.*",
    "curl/.*",
    ".*/lib3rd/.*",
    "lib3rd/.*",
    ".*/\\.temp/.*",
    ".*/.*\\.tar",
    ".*/New3rdpartylib/.*",
    "New3rdpartylib/.*",
    ".*/vendors/.*",
    "vendors/.*",
    ".*/ThirdPartyCode/.*",
    "ThirdPartyCode/.*",
    ".*/Plugins/.*",
    "Plugins/.*",
    ".*/third_lib/.*",
    "third_lib/.*",
    ".*/vue.*\\.js",
    ".*/golang\\.org/.*",
    ".*/TDRExported/.*",
    "TDRExported/.*",
    ".*/.*\\.pb\\.cpp",
    ".*/.*\\.pb\\.h",
    "pinpoint_piggy/.*",
    ".*/R\\.java",
    ".*/main\\.dart\\.js",
    ".*/vendor/.*",
    "vendor/.*"
]


class Command(BaseCommand):
    """默认路径加载
    """
    help = 'initialize default exclude paths'

    def handle(self, *args, **options):
        """执行入口
        """
        self.stdout.write('新增默认过滤路径...')
        default_paths = []
        # 获取用户
        user, _ = User.objects.get_or_create(username=settings.DEFAULT_USERNAME)
        for path in EXCLUDE_PATHS:
            default_paths.append(DefaultScanPath(
                dir_path=path, path_type=DefaultScanPath.PathTypeEnum.REGULAR, creator=user))
        # 批量创建路径
        DefaultScanPath.objects.bulk_create(default_paths, ignore_conflicts=True)
        # 批量删除不存在的路径
        to_delete_paths = DefaultScanPath.everything.exclude(
            dir_path__in=EXCLUDE_PATHS, path_type=DefaultScanPath.PathTypeEnum.REGULAR
        )
        self.stdout.write('删除不存在列表的默认过滤路径...')
        self.stdout.write('路径列表为: %s, 数量为: %s' % (list(to_delete_paths), to_delete_paths.count()))
        to_delete_paths.delete()
