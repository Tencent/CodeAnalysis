# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地任务结果状态status，对应scan_status.json中的status字段
"""


class StatusType(object):
    # 成功
    SUCCESS = "success"

    # 异常
    ERROR = "error"
