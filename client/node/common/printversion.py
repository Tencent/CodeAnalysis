# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
打印客户端版本号
"""

import sys

from node.app import settings
from tool.util.pythontool import PythonTool
from util.exceptions import ConfigError
from util.logutil import LogPrinter
from util.pyinstallerlib import PyinstallerUtil


class RunningType(object):
    SourceCode = 5
    ExeP = 3
    ExeN = 4


class VersionPrinter(object):
    @staticmethod
    def print_client_version():
        running_type = VersionPrinter.get_running_type()
        star_str = "*" * running_type
        equal_sign_cnt = 31 + len(settings.EDITION.name) + running_type * 2
        equal_sign_str = "=" * equal_sign_cnt
        LogPrinter.info(equal_sign_str)
        LogPrinter.info(f"{star_str} TCA Client v{settings.VERSION}({settings.EDITION.name} Beta) {star_str}")
        LogPrinter.info(equal_sign_str)

    @staticmethod
    def get_running_type():
        if sys.argv[0].endswith(".py"):
            return RunningType.SourceCode
        elif PyinstallerUtil.is_running_in_bundle():
            return RunningType.ExeP
        else:
            return RunningType.ExeN

    @staticmethod
    def check_python_version():
        """如果是源码执行，检查python版本是否符合"""
        if RunningType.SourceCode == VersionPrinter.get_running_type():
            # 源码执行时，检查是否为python3.7版本
            if not PythonTool.is_local_python_command_available("python3", python_version="3.7"):
                raise ConfigError("python3 command(Python Version 3.7) is not available, please install it first.")
