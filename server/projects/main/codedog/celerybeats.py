# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
celery 定时任务列表
"""

from celery.schedules import crontab


CELERY_BEAT_TASKS = {

    # 启动规则包与规则编号关系同步，每天晚上11点执行一次
    "sync-pkg-rule-map": {
        "task": "apps.codeproj.tasks.base.sync_pkg_rule_map",
        "schedule": crontab(hour=23, minute=0)
    },

    # 启动项目失活检测，每天下午 14:30 点执行一次
    "check-project-active": {
        "task": "apps.codeproj.tasks.base.check_project_active",
        "schedule": crontab(hour=14, minute=30)
    },
}
