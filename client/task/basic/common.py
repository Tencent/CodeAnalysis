# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
公共处理函数存放点
"""

import socket
import logging

logger = logging.getLogger(__name__)


def subprocc_log(line):
    """调用subprocc时通过此回调函数输出信息到log"""
    logger.info(line)


if __name__ == "__main__":
    pass
