# -*- encoding: utf-8 -*-
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
