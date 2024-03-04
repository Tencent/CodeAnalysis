# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""apps.base的tasks模块
"""
# 原生 import
import os
import logging

# 第三方 import
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def server_health_check(file_name):
    """main服务异步任务执行状态监测
    """
    current_path = os.getcwd()
    logger.info("[MainServerStatusCheck] write file healthcheck_%s.txt" % file_name)
    if not os.path.exists(os.path.join(current_path, "healthcheck_%s.txt" % file_name)):
        f = open(os.path.join(current_path, "healthcheck_%s.txt" % file_name), "w")
        f.write("main server health check: celery and asynchronous task check")
    return
