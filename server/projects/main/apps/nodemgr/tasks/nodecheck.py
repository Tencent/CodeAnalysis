# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""nodemgr的tasks模块
"""
# 原生 import
import logging

# 第三方 import
from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now

# 项目内 import
from apps.job.models import KillingTask, Task, TaskProcessRelation
from apps.nodemgr.models import Node
from codedog.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def check_node_active():
    """检查节点是否在线
    """
    offline_nodes = Node.objects.filter(enabled=Node.EnabledEnum.ACTIVE).filter(
        Q(last_beat_time__lt=now() - settings.NODE_ACTIVE_TIMEOUT) | Q(
            last_beat_time=None))
    if offline_nodes.count() > 0:
        node_ids = list(offline_nodes.values_list("id", flat=True).distinct())
        Task.objects.filter(state=Task.StateEnum.RUNNING, node_id__in=node_ids).update(state=Task.StateEnum.WAITING)
        # 将任务放入回收队列，使用TaskProcessRelation可以支持同个任务在多个节点（且都掉线）执行时都会被放入回收队列
        killing_tasks = TaskProcessRelation.objects.filter(state=TaskProcessRelation.StateEnum.RUNNING,
                                                           node_id__in=node_ids).values_list("task_id",
                                                                                             "node_id").distinct()
        for task_id, node_id in killing_tasks:
            if not node_id:
                continue
            kt = KillingTask.objects.filter(task_id=task_id, node_id=node_id)
            if not kt:
                KillingTask.objects.create(task_id=task_id, node_id=node_id)
        TaskProcessRelation.objects.filter(state=TaskProcessRelation.StateEnum.RUNNING, node_id__in=node_ids).update(
            state=Task.StateEnum.WAITING)
        offline_nodes.update(enabled=Node.EnabledEnum.OFFLINE, executor_used_num=0)
