# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""apps.base的tasks模块
"""
# 原生 import
import logging

# 第三方 import
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def server_health_check():
    """main服务异步任务执行状态监测
    """
    logger.info("[MainServerStatusCheck] status is normal")
    return