# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
任务运行场景类型定义
"""


class TaskScene(object):
    # 本地启动的任务
    LOCAL = "localtask"
    # 通过server启动的任务
    NORMAL = "servertask"
    # 本地测试任务
    TEST = "testtask"
