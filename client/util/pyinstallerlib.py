# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2023 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
pyinstaller相关的共用类库
"""

import sys
import logging

logger = logging.getLogger(__name__)


class PyinstallerUtil(object):
    @staticmethod
    def is_running_in_bundle():
        """
        检查是否在pyinstaller打包的程序中运行
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return True
        else:
            return False
