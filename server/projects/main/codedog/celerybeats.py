# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
celery 定时任务列表
"""

from datetime import timedelta

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

    # 启动定时扫描，每隔10分钟执行1次
    "handle-scheduled-projects-setting": {
        "task": "apps.codeproj.tasks.base.handle_scheduled_projects",
        "schedule": timedelta(minutes=10),
    },

    # 启动节点状态定时监控，每隔3分钟执行1次
    "check-node-active": {
        "task": "apps.nodemgr.tasks.nodecheck.check_node_active",
        "schedule": timedelta(minutes=3),
    },

    # 启动任务超时定时监控，每隔10分钟执行一次
    "handle-expired-job": {
        "task": "apps.job.tasks.jobcheck.handle_expired_job",
        "schedule": timedelta(minutes=10),
    },

    # 启动OAuth过期刷新监控，每隔30分支执行一次
    "refresh-oauth-token": {
        "task": "apps.authen.tasks.authstat.refresh_oauth_token",
        "schedule": timedelta(minutes=30),
    },

    # 启动任务初始化超时监控，每隔5分钟执行一次
    "monitor-initing-job": {
        "task": "apps.job.tasks.jobcheck.monitor_initing_job",
        "schedule": timedelta(minutes=5),
    },

    # 监控运行中的任务，每半个小时执行一次，将未正常关闭的任务进行关闭
    "monitor-running-job": {
        "task": "apps.job.tasks.jobcheck.monitor_running_job",
        "schedule": timedelta(minutes=30),
    },

    # 启动任务入库超时监控，每隔30分钟执行一次，将未正常入库的任务进行取消
    "monitor-closing-job": {
        "task": "apps.job.tasks.jobcheck.monitor_closing_job",
        "schedule": timedelta(minutes=30),
    }
}

