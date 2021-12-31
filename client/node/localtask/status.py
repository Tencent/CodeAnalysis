# -*- encoding: utf-8 -*-
"""
本地任务结果状态status，对应scan_status.json中的status字段
"""


class StatusType(object):
    # 成功
    SUCCESS = "success"

    # 异常
    ERROR = "error"
